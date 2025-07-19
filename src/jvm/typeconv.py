from __future__ import annotations

import ctypes
from typing import Any

from .jvm import JVM


def to_java(jvm: JVM, value: Any) -> object:
    """Python値をJava値に変換"""
    if isinstance(value, str):
        return jvm.jni.NewStringUTF(value)
    if isinstance(value, bool):
        bool_cls = jvm._find_class("java/lang/Boolean")
        mid = jvm.jni.GetStaticMethodID(bool_cls, "valueOf", "(Z)Ljava/lang/Boolean;")
        if mid is None:
            raise RuntimeError("Could not find Boolean.valueOf method")
        return jvm.jni.CallStaticObjectMethod(bool_cls, mid, value)
    if isinstance(value, int):
        int_cls = jvm._find_class("java/lang/Integer")
        mid = jvm.jni.GetStaticMethodID(int_cls, "valueOf", "(I)Ljava/lang/Integer;")
        if mid is None:
            raise RuntimeError("Could not find Integer.valueOf method")
        return jvm.jni.CallStaticObjectMethod(int_cls, mid, value)
    return value


def to_python(jvm: JVM, jobject: Any) -> object:
    """Java値をPython値に変換"""
    if not jobject:
        return None

    if isinstance(jobject, (dict, list, tuple, set)):
        return jobject

    try:
        cls = jvm.jni.GetObjectClass(jobject)  # noqa
    except (TypeError, ValueError, ctypes.ArgumentError):
        return jobject

    # String
    str_cls = jvm._find_class("java/lang/String")
    if jvm.jni.IsInstanceOf(jobject, str_cls):
        pystr = jvm.jni.GetStringUTFChars(jobject)
        return pystr or ""

    # Boolean
    bool_cls = jvm._find_class("java/lang/Boolean")
    if jvm.jni.IsInstanceOf(jobject, bool_cls):
        mid = jvm.jni.GetMethodID(bool_cls, "booleanValue", "()Z")
        if mid is None:
            raise RuntimeError("Could not find Boolean.booleanValue method")
        return bool(jvm.jni.CallBooleanMethod(jobject, mid))

    # Integer
    int_cls = jvm._find_class("java/lang/Integer")
    if jvm.jni.IsInstanceOf(jobject, int_cls):
        mid = jvm.jni.GetMethodID(int_cls, "intValue", "()I")
        if mid is None:
            raise RuntimeError("Could not find Integer.intValue method")
        return int(jvm.jni.CallIntMethod(jobject, mid))

    return jobject
