"""Pytest configuration and fixtures for JVM-PyBind tests."""

import tempfile
from pathlib import Path
from typing import Any, Generator
from unittest.mock import Mock

import pytest

from jvm.config import Config
from jvm.jvm import JVM, JavaClass, JavaField, JavaMethod
from jvm.loader import JVMLoader


@pytest.fixture
def mock_jvm() -> Mock:
    """Create a mock JVM instance for testing."""
    from unittest.mock import Mock

    mock = Mock()
    mock.find_class.return_value = Mock()
    return mock


@pytest.fixture
def temp_pyproject() -> Generator[Path, None, None]:
    """Create a temporary pyproject.toml file for testing."""
    content = """
[project]
name = "test-project"
version = "0.1.0"

[tool.jvm]
java-version = "17"
classpath = ["test.jar", "another.jar"]

[tool.jvm.deps]
maven = ["org.apache.commons:commons-lang3:3.12.0"]
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
        f.write(content)
        temp_path = Path(f.name)

    try:
        yield temp_path
    finally:
        temp_path.unlink(missing_ok=True)


@pytest.fixture
def temp_directory() -> Generator[Path, None, None]:
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def sample_java_methods() -> list[JavaMethod]:
    """Create sample Java methods for testing."""
    return [
        JavaMethod(
            name="println",
            parameters=["java.lang.String"],
            return_type="void",
            is_static=False,
        ),
        JavaMethod(
            name="print",
            parameters=["java.lang.String"],
            return_type="void",
            is_static=False,
        ),
        JavaMethod(
            name="println", parameters=[], return_type="void", is_static=False
        ),  # Overload
        JavaMethod(
            name="valueOf",
            parameters=["int"],
            return_type="java.lang.String",
            is_static=True,
        ),
        JavaMethod(
            name="valueOf",
            parameters=["boolean"],
            return_type="java.lang.String",
            is_static=True,
        ),
    ]


@pytest.fixture
def sample_java_fields() -> list[JavaField]:
    """Create sample Java fields for testing."""
    return [
        JavaField(name="out", type="java.io.PrintStream", is_static=True),
        JavaField(name="err", type="java.io.PrintStream", is_static=True),
        JavaField(name="in", type="java.io.InputStream", is_static=True),
        JavaField(name="value", type="java.lang.String", is_static=False),
    ]


@pytest.fixture
def sample_java_class(
    sample_java_methods: list[JavaMethod], sample_java_fields: list[JavaField]
) -> JavaClass:
    """Create a sample Java class for testing."""
    return JavaClass(
        name="java.lang.System",
        methods=sample_java_methods,
        fields=sample_java_fields,
    )


@pytest.fixture(scope="session")
def jvm_instance() -> Generator[JVM, None, None]:
    """Create a real JVM instance for all tests."""
    try:
        config = Config(java_version="17", deps={}, classpath=[])
        loader = JVMLoader(config)
        jvm = loader.start()
        yield jvm
    except Exception as e:
        pytest.fail(f"Could not start JVM for tests: {e}")
    finally:
        pass


@pytest.fixture
def mock_platform(monkeypatch: pytest.MonkeyPatch) -> dict[str, Any]:
    """Mock platform information for testing."""
    platform_info = {
        "system": "Linux",
        "machine": "x86_64",
    }

    def mock_system() -> str:
        return platform_info["system"]

    def mock_machine() -> str:
        return platform_info["machine"]

    monkeypatch.setattr("platform.system", mock_system)
    monkeypatch.setattr("platform.machine", mock_machine)

    return platform_info


@pytest.fixture
def mock_os_path_exists(monkeypatch: pytest.MonkeyPatch) -> Mock:
    """Mock os.path.exists for testing file discovery."""
    mock_exists = Mock(return_value=True)
    monkeypatch.setattr("os.path.exists", mock_exists)
    return mock_exists


@pytest.fixture
def mock_ctypes_cdll(monkeypatch: pytest.MonkeyPatch) -> Mock:
    """Mock ctypes.CDLL for testing library loading."""
    mock_cdll = Mock()
    mock_lib = Mock()
    mock_lib.JNI_CreateJavaVM.return_value = 0  # Success
    mock_cdll.return_value = mock_lib
    monkeypatch.setattr("ctypes.CDLL", mock_cdll)
    return mock_cdll


@pytest.fixture(autouse=True)
def reset_import_hooks() -> Generator[None, None, None]:
    """Reset import hooks after each test to prevent interference."""
    import sys

    original_meta_path = sys.meta_path.copy()
    yield
    sys.meta_path[:] = original_meta_path


@pytest.fixture
def capture_logs(caplog: pytest.LogCaptureFixture) -> pytest.LogCaptureFixture:
    """Configure logging capture for tests."""
    import logging

    caplog.set_level(logging.DEBUG, logger="jvm")
    return caplog


# Test markers
def pytest_configure(config: pytest.Config) -> None:
    """Configure pytest markers."""
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "unit: marks tests as unit tests")
    config.addinivalue_line("markers", "slow: marks tests as slow running")


def pytest_collection_modifyitems(
    config: pytest.Config, items: list[pytest.Item]
) -> None:
    """Modify test collection to add markers."""
    for item in items:
        # Mark integration tests
        if "integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        elif "test_integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        else:
            item.add_marker(pytest.mark.unit)

        # Mark slow tests
        if any(keyword in item.nodeid for keyword in ["integration", "jvm_instance"]):
            item.add_marker(pytest.mark.slow)
