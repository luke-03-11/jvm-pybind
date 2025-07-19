from __future__ import annotations

from typing import Any

from .jvm import JVM, JavaClass
from .typeconv import to_java, to_python


class PackageProxy:
    """Javaパッケージプロキシ"""

    def __init__(self, jvm: JVM, pkg_name: str):
        self._jvm = jvm
        self._pkg = pkg_name

    def __getattr__(self, item: str) -> Any:
        fqcn = f"{self._pkg}.{item}"
        try:
            self._jvm.find_class(fqcn.replace(".", "/"))
            return ClassProxy(self._jvm, fqcn)
        except Exception:
            return PackageProxy(self._jvm, fqcn)

    def __repr__(self) -> str:
        return f"<Java package {self._pkg}>"


class ClassProxy:
    """Javaクラスプロキシ"""

    def __init__(self, jvm: JVM, fqcn: str):
        self._jvm = jvm
        self._fqcn = fqcn
        self._jclass = None
        self._class_info: JavaClass | None = None

    @property
    def _cls(self) -> Any:
        if self._jclass is None:
            self._jclass = self._jvm._find_class(self._fqcn.replace(".", "/"))
        return self._jclass

    @property
    def _info(self) -> JavaClass:
        if self._class_info is None:
            self._class_info = self._jvm.find_class(self._fqcn.replace(".", "/"))
        return self._class_info

    def __getattr__(self, item: str) -> Any:
        # 静的フィールド
        for f in self._info.fields:
            if f.name == item:
                try:
                    sig = _java_type_to_sig(f.type)
                    field_id = self._jvm.jni.GetStaticFieldID(self._cls, item, sig)
                    if not field_id:
                        raise RuntimeError(f"Field ID not found for {item}")

                    field_val = self._jvm.jni.GetStaticObjectField(self._cls, field_id)
                    return to_python(self._jvm, field_val)
                except Exception as e:
                    raise RuntimeError(f"Failed to access static field {item}: {e}")

        # 静的メソッド
        matches = [m for m in self._info.methods if m.name == item]
        if matches:
            return MethodProxy(self._jvm, self._cls, matches)

        raise AttributeError(item)

    def __repr__(self) -> str:
        return f"<Java class {self._fqcn}>"


class ObjectProxy:
    """Javaオブジェクトプロキシ"""

    def __init__(self, jvm: JVM, jobject: Any):
        self._jvm = jvm
        self._jobject = jobject
        self._class_info: Any = None

    @property
    def _info(self) -> Any:
        if self._class_info is None:
            try:
                obj_class = self._jvm.jni.GetObjectClass(self._jobject)
                if not obj_class:
                    self._class_info = type(
                        "EmptyJavaClass", (), {"methods": [], "fields": []}
                    )()
                    return self._class_info

                methods = self._jvm._extract_all_methods(obj_class)
                fields = self._jvm._extract_all_fields(obj_class)
                self._class_info = type(
                    "DynamicJavaClass", (), {"methods": methods, "fields": fields}
                )()

            except Exception:
                self._class_info = type(
                    "EmptyJavaClass", (), {"methods": [], "fields": []}
                )()

        return self._class_info

    def __getattr__(self, item: str) -> Any:
        matches = [m for m in self._info.methods if m.name == item]
        if matches:
            return InstanceMethodProxy(self._jvm, self._jobject, matches)
        raise AttributeError(item)

    def __repr__(self) -> str:
        return "<Java object>"


class InstanceMethodProxy:
    """Javaインスタンスメソッドプロキシ"""

    def __init__(self, jvm: JVM, jobject: Any, overloads: list[Any]):
        self._jvm = jvm
        self._jobject = jobject
        self._overloads = overloads

    def __call__(self, *args: Any) -> Any:
        cand = None
        try:
            j_args = [to_java(self._jvm, a) for a in args]

            cand = next(
                (o for o in self._overloads if len(o.parameters) == len(j_args)), None
            )
            if not cand:
                raise RuntimeError(
                    f"No matching method found for {len(j_args)} arguments"
                )

            sig = _build_sig(cand)

            obj_class = self._jvm.jni.GetObjectClass(self._jobject)
            mid = self._jvm.jni.GetMethodID(obj_class, cand.name, sig)
            if not mid:
                raise RuntimeError(f"MethodID resolve failed for {cand.name}")

            if cand.return_type == "void":
                self._jvm.jni.CallVoidMethod(self._jobject, mid, *j_args)
                return None
            else:
                res = self._jvm.jni.CallObjectMethod(self._jobject, mid, *j_args)
                return to_python(self._jvm, res)
        except Exception as e:
            method_name = cand.name if cand else "unknown"
            raise RuntimeError(f"Failed to call method {method_name}: {e}")

    def __repr__(self) -> str:
        ol = ", ".join(f"{m.name}/{len(m.parameters)}" for m in self._overloads)
        return f"<Java instance method [{ol}]>"


class MethodProxy:
    """Java静的メソッドプロキシ"""

    def __init__(self, jvm: JVM, jclass: Any, overloads: list[Any]):
        self._jvm = jvm
        self._jclass = jclass
        self._overloads = overloads

    def __call__(self, *args: Any) -> Any:
        j_args = [to_java(self._jvm, a) for a in args]

        def matches_signature(overload: Any, java_args: list[Any]) -> bool:
            if len(overload.parameters) != len(java_args):
                return False
            for param_type, arg in zip(overload.parameters, args):
                if param_type == "int" and not isinstance(arg, int):
                    return False
                elif param_type == "java.lang.String" and not isinstance(arg, str):
                    return False
            return True

        cand = next(o for o in self._overloads if matches_signature(o, j_args))
        sig = _build_sig(cand)
        mid = self._jvm.jni.GetStaticMethodID(self._jclass, cand.name, sig)
        if not mid:
            raise RuntimeError("MethodID resolve failed")

        res = self._jvm.jni.CallStaticObjectMethod(self._jclass, mid, *j_args)
        return to_python(self._jvm, res)

    def __repr__(self) -> str:
        ol = ", ".join(f"{m.name}/{len(m.parameters)}" for m in self._overloads)
        return f"<Java static method [{ol}]>"


def _java_type_to_sig(jtype: str) -> str:
    """Java型からJNIシグネチャ変換"""
    PRIM = {
        "int": "I",
        "long": "J",
        "float": "F",
        "double": "D",
        "boolean": "Z",
        "void": "V",
        "byte": "B",
        "char": "C",
        "short": "S",
    }
    if jtype in PRIM:
        return PRIM[jtype]
    return "L" + jtype.replace(".", "/") + ";"


def _build_sig(method: Any) -> str:
    """JNIシグネチャ構築"""
    params = "".join(_java_type_to_sig(t) for t in method.parameters)
    ret = _java_type_to_sig(method.return_type)
    return f"({params}){ret}"
