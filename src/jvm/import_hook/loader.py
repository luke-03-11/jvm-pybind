from importlib.abc import Loader
from importlib.machinery import ModuleSpec
from types import ModuleType
from typing import Any, Optional

from ..jvm import JVM
from ..proxy import ClassProxy, PackageProxy


class JavaLoader(Loader):
    """Javaローダー"""

    def __init__(self, jvm: JVM, fullname: str):
        self.jvm = jvm
        self.fullname = fullname

    def create_module(self, spec: Optional[ModuleSpec]) -> ModuleType:
        if spec is None:
            raise ValueError("ModuleSpec cannot be None")
        return ModuleType(spec.name)

    def exec_module(self, module: ModuleType) -> None:
        parts = self.fullname.split(".")
        if len(parts) == 1:  # ルートパッケージ
            module.__path__ = []
            setattr(
                module,
                "__getattr__",
                lambda name: PackageProxy(self.jvm, f"java.{name}"),
            )
            setattr(module, "__repr__", lambda: "<Java root package>")
            return

        # サブパッケージ処理
        pkg_path = ".".join(parts[:-1])
        leaf = parts[-1]

        _ = (pkg_path, leaf)

        # クラスorパッケージ判定
        def _lazy_attr(name: str) -> Any:
            fqcn = f"{self.fullname}.{name}"
            try:
                self.jvm.find_class(fqcn.replace(".", "/"))
                return ClassProxy(self.jvm, fqcn)
            except Exception:
                return PackageProxy(self.jvm, fqcn)

        setattr(module, "__getattr__", _lazy_attr)
        setattr(module, "__repr__", lambda: f"<Java package {self.fullname}>")
