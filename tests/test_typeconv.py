"""Tests for type conversion functionality."""

from unittest.mock import Mock

import pytest

from jvm.typeconv import to_java, to_python


class TestToJava:
    """Test Python to Java type conversion."""

    def test_to_java_string(self, mock_jvm: Mock) -> None:
        """Test converting Python string to Java String."""
        python_value = "test string"
        mock_java_string = 0x12345678

        mock_jvm.jni.NewStringUTF.return_value = mock_java_string

        result = to_java(mock_jvm, python_value)

        assert result == mock_java_string
        mock_jvm.jni.NewStringUTF.assert_called_once_with(python_value)

    def test_to_java_empty_string(self, mock_jvm: Mock) -> None:
        """Test converting empty Python string to Java String."""
        python_value = ""
        mock_java_string = 0x12345678

        mock_jvm.jni.NewStringUTF.return_value = mock_java_string

        result = to_java(mock_jvm, python_value)

        assert result == mock_java_string
        mock_jvm.jni.NewStringUTF.assert_called_once_with("")

    def test_to_java_unicode_string(self, mock_jvm: Mock) -> None:
        """Test converting Unicode Python string to Java String."""
        python_value = "Hello 世界 🌍"
        mock_java_string = 0x12345678

        mock_jvm.jni.NewStringUTF.return_value = mock_java_string

        result = to_java(mock_jvm, python_value)

        assert result == mock_java_string
        mock_jvm.jni.NewStringUTF.assert_called_once_with(python_value)

    def test_to_java_boolean_true(self, mock_jvm: Mock) -> None:
        """Test converting Python True to Java Boolean."""
        python_value = True
        mock_boolean_class = 0x11111111
        mock_method_id = 0x22222222
        mock_java_boolean = 0x33333333

        mock_jvm._find_class.return_value = mock_boolean_class
        mock_jvm.jni.GetStaticMethodID.return_value = mock_method_id
        mock_jvm.jni.CallStaticObjectMethod.return_value = mock_java_boolean

        result = to_java(mock_jvm, python_value)

        assert result == mock_java_boolean
        mock_jvm._find_class.assert_called_once_with("java/lang/Boolean")
        mock_jvm.jni.GetStaticMethodID.assert_called_once_with(
            mock_boolean_class, "valueOf", "(Z)Ljava/lang/Boolean;"
        )
        mock_jvm.jni.CallStaticObjectMethod.assert_called_once_with(
            mock_boolean_class, mock_method_id, True
        )

    def test_to_java_boolean_false(self, mock_jvm: Mock) -> None:
        """Test converting Python False to Java Boolean."""
        python_value = False
        mock_boolean_class = 0x11111111
        mock_method_id = 0x22222222
        mock_java_boolean = 0x33333333

        mock_jvm._find_class.return_value = mock_boolean_class
        mock_jvm.jni.GetStaticMethodID.return_value = mock_method_id
        mock_jvm.jni.CallStaticObjectMethod.return_value = mock_java_boolean

        result = to_java(mock_jvm, python_value)

        assert result == mock_java_boolean
        mock_jvm.jni.CallStaticObjectMethod.assert_called_once_with(
            mock_boolean_class, mock_method_id, False
        )

    def test_to_java_integer_positive(self, mock_jvm: Mock) -> None:
        """Test converting positive Python int to Java Integer."""
        python_value = 42
        mock_integer_class = 0x11111111
        mock_method_id = 0x22222222
        mock_java_integer = 0x33333333

        mock_jvm._find_class.return_value = mock_integer_class
        mock_jvm.jni.GetStaticMethodID.return_value = mock_method_id
        mock_jvm.jni.CallStaticObjectMethod.return_value = mock_java_integer

        result = to_java(mock_jvm, python_value)

        assert result == mock_java_integer
        mock_jvm._find_class.assert_called_once_with("java/lang/Integer")
        mock_jvm.jni.GetStaticMethodID.assert_called_once_with(
            mock_integer_class, "valueOf", "(I)Ljava/lang/Integer;"
        )
        mock_jvm.jni.CallStaticObjectMethod.assert_called_once_with(
            mock_integer_class, mock_method_id, 42
        )

    def test_to_java_integer_negative(self, mock_jvm: Mock) -> None:
        """Test converting negative Python int to Java Integer."""
        python_value = -123
        mock_integer_class = 0x11111111
        mock_method_id = 0x22222222
        mock_java_integer = 0x33333333

        mock_jvm._find_class.return_value = mock_integer_class
        mock_jvm.jni.GetStaticMethodID.return_value = mock_method_id
        mock_jvm.jni.CallStaticObjectMethod.return_value = mock_java_integer

        result = to_java(mock_jvm, python_value)

        assert result == mock_java_integer
        mock_jvm.jni.CallStaticObjectMethod.assert_called_once_with(
            mock_integer_class, mock_method_id, -123
        )

    def test_to_java_integer_zero(self, mock_jvm: Mock) -> None:
        """Test converting zero to Java Integer."""
        python_value = 0
        mock_integer_class = 0x11111111
        mock_method_id = 0x22222222
        mock_java_integer = 0x33333333

        mock_jvm._find_class.return_value = mock_integer_class
        mock_jvm.jni.GetStaticMethodID.return_value = mock_method_id
        mock_jvm.jni.CallStaticObjectMethod.return_value = mock_java_integer

        result = to_java(mock_jvm, python_value)

        assert result == mock_java_integer
        mock_jvm.jni.CallStaticObjectMethod.assert_called_once_with(
            mock_integer_class, mock_method_id, 0
        )

    def test_to_java_unsupported_type_float(self, mock_jvm: Mock) -> None:
        """Test converting unsupported type (float) returns value unchanged."""
        python_value = 3.14

        result = to_java(mock_jvm, python_value)

        assert result == python_value
        # Should not call any JNI methods for unsupported types
        mock_jvm.jni.NewStringUTF.assert_not_called()
        mock_jvm._find_class.assert_not_called()

    def test_to_java_unsupported_type_list(self, mock_jvm: Mock) -> None:
        """Test converting unsupported type (list) returns value unchanged."""
        python_value = [1, 2, 3]

        result = to_java(mock_jvm, python_value)

        assert result == python_value
        mock_jvm.jni.NewStringUTF.assert_not_called()
        mock_jvm._find_class.assert_not_called()

    def test_to_java_none(self, mock_jvm: Mock) -> None:
        """Test converting None returns None unchanged."""
        python_value = None

        result = to_java(mock_jvm, python_value)

        assert result is None
        mock_jvm.jni.NewStringUTF.assert_not_called()
        mock_jvm._find_class.assert_not_called()


class TestToPython:
    """Test Java to Python type conversion."""

    def test_to_python_null_object(self, mock_jvm: Mock) -> None:
        """Test converting null Java object to Python None."""
        java_object = None

        result = to_python(mock_jvm, java_object)

        assert result is None
        mock_jvm.jni.GetObjectClass.assert_not_called()

    def test_to_python_java_string(self, mock_jvm: Mock) -> None:
        """Test converting Java String to Python string."""
        java_string = 0x12345678
        mock_string_class = 0x87654321
        python_string = "test string"

        mock_jvm.jni.GetObjectClass.return_value = mock_string_class
        mock_jvm._find_class.return_value = mock_string_class
        mock_jvm.jni.IsInstanceOf.return_value = True
        mock_jvm.jni.GetStringUTFChars.return_value = python_string

        result = to_python(mock_jvm, java_string)

        assert result == python_string
        mock_jvm.jni.GetObjectClass.assert_called_once_with(java_string)
        mock_jvm._find_class.assert_called_once_with("java/lang/String")
        mock_jvm.jni.IsInstanceOf.assert_called_once_with(
            java_string, mock_string_class
        )
        mock_jvm.jni.GetStringUTFChars.assert_called_once_with(java_string)

    def test_to_python_java_string_empty(self, mock_jvm: Mock) -> None:
        """Test converting empty Java String to Python string."""
        java_string = 0x12345678
        mock_string_class = 0x87654321

        mock_jvm.jni.GetObjectClass.return_value = mock_string_class
        mock_jvm._find_class.return_value = mock_string_class
        mock_jvm.jni.IsInstanceOf.return_value = True
        mock_jvm.jni.GetStringUTFChars.return_value = None  # Simulate empty string

        result = to_python(mock_jvm, java_string)

        assert result == ""

    def test_to_python_java_boolean_true(self, mock_jvm: Mock) -> None:
        """Test converting Java Boolean(true) to Python bool."""
        java_boolean = 0x12345678
        mock_object_class = 0x11111111
        mock_boolean_class = 0x22222222
        mock_method_id = 0x33333333

        mock_jvm.jni.GetObjectClass.return_value = mock_object_class
        mock_jvm._find_class.side_effect = [
            0x99999999,  # String class (not a match)
            mock_boolean_class,  # Boolean class (match)
        ]
        mock_jvm.jni.IsInstanceOf.side_effect = [False, True]  # Not String, is Boolean
        mock_jvm.jni.GetMethodID.return_value = mock_method_id
        mock_jvm.jni.CallBooleanMethod.return_value = True

        result = to_python(mock_jvm, java_boolean)

        assert result is True
        mock_jvm.jni.GetMethodID.assert_called_once_with(
            mock_boolean_class, "booleanValue", "()Z"
        )
        mock_jvm.jni.CallBooleanMethod.assert_called_once_with(
            java_boolean, mock_method_id
        )

    def test_to_python_java_boolean_false(self, mock_jvm: Mock) -> None:
        """Test converting Java Boolean(false) to Python bool."""
        java_boolean = 0x12345678
        mock_object_class = 0x11111111
        mock_boolean_class = 0x22222222
        mock_method_id = 0x33333333

        mock_jvm.jni.GetObjectClass.return_value = mock_object_class
        mock_jvm._find_class.side_effect = [
            0x99999999,  # String class (not a match)
            mock_boolean_class,  # Boolean class (match)
        ]
        mock_jvm.jni.IsInstanceOf.side_effect = [False, True]  # Not String, is Boolean
        mock_jvm.jni.GetMethodID.return_value = mock_method_id
        mock_jvm.jni.CallBooleanMethod.return_value = False

        result = to_python(mock_jvm, java_boolean)

        assert result is False

    def test_to_python_java_integer_positive(self, mock_jvm: Mock) -> None:
        """Test converting Java Integer to Python int."""
        java_integer = 0x12345678
        mock_object_class = 0x11111111
        mock_integer_class = 0x33333333
        mock_method_id = 0x44444444

        mock_jvm.jni.GetObjectClass.return_value = mock_object_class
        mock_jvm._find_class.side_effect = [
            0x99999999,  # String class (not a match)
            0x88888888,  # Boolean class (not a match)
            mock_integer_class,  # Integer class (match)
        ]
        mock_jvm.jni.IsInstanceOf.side_effect = [
            False,
            False,
            True,
        ]  # Not String, not Boolean, is Integer
        mock_jvm.jni.GetMethodID.return_value = mock_method_id
        mock_jvm.jni.CallIntMethod.return_value = 42

        result = to_python(mock_jvm, java_integer)

        assert result == 42
        mock_jvm.jni.GetMethodID.assert_called_once_with(
            mock_integer_class, "intValue", "()I"
        )
        mock_jvm.jni.CallIntMethod.assert_called_once_with(java_integer, mock_method_id)

    def test_to_python_java_integer_negative(self, mock_jvm: Mock) -> None:
        """Test converting negative Java Integer to Python int."""
        java_integer = 0x12345678
        mock_object_class = 0x11111111
        mock_integer_class = 0x33333333
        mock_method_id = 0x44444444

        mock_jvm.jni.GetObjectClass.return_value = mock_object_class
        mock_jvm._find_class.side_effect = [
            0x99999999,  # String class (not a match)
            0x88888888,  # Boolean class (not a match)
            mock_integer_class,  # Integer class (match)
        ]
        mock_jvm.jni.IsInstanceOf.side_effect = [False, False, True]
        mock_jvm.jni.GetMethodID.return_value = mock_method_id
        mock_jvm.jni.CallIntMethod.return_value = -123

        result = to_python(mock_jvm, java_integer)

        assert result == -123

    def test_to_python_java_integer_zero(self, mock_jvm: Mock) -> None:
        """Test converting Java Integer(0) to Python int."""
        java_integer = 0x12345678
        mock_object_class = 0x11111111
        mock_integer_class = 0x33333333
        mock_method_id = 0x44444444

        mock_jvm.jni.GetObjectClass.return_value = mock_object_class
        mock_jvm._find_class.side_effect = [
            0x99999999,  # String class (not a match)
            0x88888888,  # Boolean class (not a match)
            mock_integer_class,  # Integer class (match)
        ]
        mock_jvm.jni.IsInstanceOf.side_effect = [False, False, True]
        mock_jvm.jni.GetMethodID.return_value = mock_method_id
        mock_jvm.jni.CallIntMethod.return_value = 0

        result = to_python(mock_jvm, java_integer)

        assert result == 0

    def test_to_python_unsupported_java_object(self, mock_jvm: Mock) -> None:
        """Test converting unsupported Java object returns object unchanged."""
        java_object = 0x12345678
        mock_object_class = 0x87654321

        mock_jvm.jni.GetObjectClass.return_value = mock_object_class
        mock_jvm._find_class.side_effect = [
            0x99999999,  # String class (not a match)
            0x88888888,  # Boolean class (not a match)
            0x77777777,  # Integer class (not a match)
        ]
        mock_jvm.jni.IsInstanceOf.side_effect = [
            False,
            False,
            False,
        ]  # Not any known type

        result = to_python(mock_jvm, java_object)

        assert result == java_object
        # Should not call any value extraction methods
        mock_jvm.jni.GetStringUTFChars.assert_not_called()
        mock_jvm.jni.CallBooleanMethod.assert_not_called()
        mock_jvm.jni.CallIntMethod.assert_not_called()


class TestTypeConversionEdgeCases:
    """Test edge cases and error conditions in type conversion."""

    def test_to_java_string_jni_failure(self, mock_jvm: Mock) -> None:
        """Test to_java when JNI string creation fails."""
        python_value = "test"
        mock_jvm.jni.NewStringUTF.return_value = None  # JNI failure

        result = to_java(mock_jvm, python_value)

        assert result is None

    def test_to_java_boolean_class_not_found(self, mock_jvm: Mock) -> None:
        """Test to_java when Boolean class is not found."""
        python_value = True
        mock_jvm._find_class.side_effect = Exception("Class not found")

        with pytest.raises(Exception, match="Class not found"):
            to_java(mock_jvm, python_value)

    def test_to_java_integer_method_not_found(self, mock_jvm: Mock) -> None:
        """Test to_java when Integer.valueOf method is not found."""
        python_value = 42
        mock_integer_class = 0x11111111

        mock_jvm._find_class.return_value = mock_integer_class
        mock_jvm.jni.GetStaticMethodID.return_value = None  # Method not found

        with pytest.raises(Exception):
            to_java(mock_jvm, python_value)

    def test_to_python_string_get_chars_failure(self, mock_jvm: Mock) -> None:
        """Test to_python when GetStringUTFChars fails."""
        java_string = 0x12345678
        mock_string_class = 0x87654321

        mock_jvm.jni.GetObjectClass.return_value = mock_string_class
        mock_jvm._find_class.return_value = mock_string_class
        mock_jvm.jni.IsInstanceOf.return_value = True
        mock_jvm.jni.GetStringUTFChars.return_value = None

        result = to_python(mock_jvm, java_string)

        assert result == ""  # Should return empty string on failure

    def test_to_python_boolean_method_call_failure(self, mock_jvm: Mock) -> None:
        """Test to_python when Boolean.booleanValue() call fails."""
        java_boolean = 0x12345678
        mock_object_class = 0x11111111
        mock_boolean_class = 0x22222222

        mock_jvm.jni.GetObjectClass.return_value = mock_object_class
        mock_jvm._find_class.side_effect = [0x99999999, mock_boolean_class]
        mock_jvm.jni.IsInstanceOf.side_effect = [False, True]
        mock_jvm.jni.GetMethodID.return_value = None  # Method not found

        with pytest.raises(Exception):
            to_python(mock_jvm, java_boolean)

    def test_to_python_integer_method_call_failure(self, mock_jvm: Mock) -> None:
        """Test to_python when Integer.intValue() call fails."""
        java_integer = 0x12345678
        mock_object_class = 0x11111111
        mock_integer_class = 0x33333333

        mock_jvm.jni.GetObjectClass.return_value = mock_object_class
        mock_jvm._find_class.side_effect = [0x99999999, 0x88888888, mock_integer_class]
        mock_jvm.jni.IsInstanceOf.side_effect = [False, False, True]
        mock_jvm.jni.GetMethodID.return_value = None  # Method not found

        with pytest.raises(Exception):
            to_python(mock_jvm, java_integer)

    def test_roundtrip_conversion_string(self, mock_jvm: Mock) -> None:
        """Test round-trip conversion: Python str -> Java String -> Python str."""
        original_value = "test string"
        mock_java_string = 0x12345678

        # Setup to_java mocks
        mock_jvm.jni.NewStringUTF.return_value = mock_java_string

        # Setup to_python mocks
        mock_string_class = 0x87654321
        mock_jvm.jni.GetObjectClass.return_value = mock_string_class
        mock_jvm._find_class.return_value = mock_string_class
        mock_jvm.jni.IsInstanceOf.return_value = True
        mock_jvm.jni.GetStringUTFChars.return_value = original_value

        # Perform round-trip
        java_result = to_java(mock_jvm, original_value)
        python_result = to_python(mock_jvm, java_result)

        assert python_result == original_value

    def test_roundtrip_conversion_boolean(self, mock_jvm: Mock) -> None:
        """Test round-trip conversion: Python bool -> Java Boolean -> Python bool."""
        original_value = True
        mock_java_boolean = 0x12345678

        # Setup to_java mocks
        mock_boolean_class = 0x11111111
        mock_method_id = 0x22222222
        mock_jvm._find_class.return_value = mock_boolean_class
        mock_jvm.jni.GetStaticMethodID.return_value = mock_method_id
        mock_jvm.jni.CallStaticObjectMethod.return_value = mock_java_boolean

        # Setup to_python mocks
        mock_jvm.jni.GetObjectClass.return_value = mock_boolean_class
        mock_jvm.jni.IsInstanceOf.side_effect = [False, True]  # Not String, is Boolean
        mock_jvm.jni.GetMethodID.return_value = mock_method_id
        mock_jvm.jni.CallBooleanMethod.return_value = original_value

        # Perform round-trip
        java_result = to_java(mock_jvm, original_value)
        python_result = to_python(mock_jvm, java_result)

        assert python_result == original_value

    def test_roundtrip_conversion_integer(self, mock_jvm: Mock) -> None:
        """Test round-trip conversion: Python int -> Java Integer -> Python int."""
        original_value = 42
        mock_java_integer = 0x12345678

        # Setup to_java mocks
        mock_integer_class = 0x11111111
        mock_method_id = 0x22222222
        mock_jvm._find_class.return_value = mock_integer_class
        mock_jvm.jni.GetStaticMethodID.return_value = mock_method_id
        mock_jvm.jni.CallStaticObjectMethod.return_value = mock_java_integer

        # Setup to_python mocks
        mock_jvm.jni.GetObjectClass.return_value = mock_integer_class
        mock_jvm.jni.IsInstanceOf.side_effect = [
            False,
            False,
            True,
        ]  # Not String, not Boolean, is Integer
        mock_jvm.jni.GetMethodID.return_value = mock_method_id
        mock_jvm.jni.CallIntMethod.return_value = original_value

        # Perform round-trip
        java_result = to_java(mock_jvm, original_value)
        python_result = to_python(mock_jvm, java_result)

        assert python_result == original_value
