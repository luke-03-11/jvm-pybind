"""Tests for JVM management functionality."""

import pytest

from jvm.jvm import JVM, JavaClass, JNIException


class TestJVMInitialization:
    """Test JVM initialization and basic functionality."""

    def test_jvm_initialization(self, jvm_instance: JVM) -> None:
        """Test JVM initialization."""
        jvm = jvm_instance

        assert jvm.jvm is not None
        assert jvm.env is not None
        assert jvm.jni is not None
        assert jvm._shutdown_complete is False
        assert isinstance(jvm._class_cache, dict)

    def test_jvm_graceful_shutdown_not_started(self, jvm_instance: JVM) -> None:
        """Test graceful shutdown when already completed."""
        original_state = jvm_instance._shutdown_complete
        jvm_instance._shutdown_complete = True

        jvm_instance.graceful_shutdown()

        jvm_instance._shutdown_complete = original_state

    def test_jvm_find_class_basic(self, jvm_instance: JVM) -> None:
        """Test basic class finding functionality."""
        java_class = jvm_instance.find_class("java/lang/String")

        assert isinstance(java_class, JavaClass)
        assert java_class.name == "java/lang/String"
        assert len(java_class.methods) > 0
        assert any(method.name == "toString" for method in java_class.methods)

    def test_jvm_jni_version(self, jvm_instance: JVM) -> None:
        """Test JNI version retrieval."""
        version = jvm_instance.jni.GetVersion()

        assert version > 0
        assert version >= 0x00010001


class TestJVMClassOperations:
    """Test JVM class-related operations."""

    def test_find_class_string(self, jvm_instance: JVM) -> None:
        """Test finding String class."""
        java_class = jvm_instance.find_class("java/lang/String")

        assert isinstance(java_class, JavaClass)
        assert java_class.name == "java/lang/String"

        method_names = [method.name for method in java_class.methods]
        assert "toString" in method_names
        assert "length" in method_names

    def test_find_class_object(self, jvm_instance: JVM) -> None:
        """Test finding Object class."""
        java_class = jvm_instance.find_class("java/lang/Object")

        assert isinstance(java_class, JavaClass)
        assert java_class.name == "java/lang/Object"

        method_names = [method.name for method in java_class.methods]
        assert "toString" in method_names
        assert "equals" in method_names
        assert "hashCode" in method_names

    def test_find_class_nonexistent(self, jvm_instance: JVM) -> None:
        """Test finding non-existent class."""
        with pytest.raises(JNIException):
            jvm_instance.find_class("non.existent.Class")

    def test_class_caching(self, jvm_instance: JVM) -> None:
        """Test that classes are cached properly."""
        class1 = jvm_instance._find_class("java/lang/String")
        class2 = jvm_instance._find_class("java/lang/String")

        assert "java/lang/String" in jvm_instance._class_cache
        assert class1 == class2


class TestJVMStringOperations:
    """Test JVM string operations."""

    def test_string_creation(self, jvm_instance: JVM) -> None:
        """Test creating Java strings."""
        test_string = "Hello, JVM!"
        java_string = jvm_instance.jni.NewStringUTF(test_string)

        assert java_string is not None

        result = jvm_instance.jni.GetStringUTFChars(java_string)
        assert result == test_string

    def test_string_length(self, jvm_instance: JVM) -> None:
        """Test getting Java string length."""
        test_string = "Hello"
        java_string = jvm_instance.jni.NewStringUTF(test_string)

        length = jvm_instance.jni.GetStringLength(java_string)
        assert length == len(test_string)


class TestJVMBasicOperations:
    """Test basic JVM operations."""

    def test_exception_check(self, jvm_instance: JVM) -> None:
        """Test exception checking."""
        has_exception = jvm_instance.jni.ExceptionCheck()
        assert has_exception is False

    def test_local_frame_operations(self, jvm_instance: JVM) -> None:
        """Test local frame push/pop operations."""
        result = jvm_instance.jni.PushLocalFrame(10)
        assert result == 0

        jvm_instance.jni.PopLocalFrame(None)
