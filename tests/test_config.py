"""Tests for JVM configuration system."""

from pathlib import Path
from unittest.mock import patch

from jvm.config import Config


class TestConfig:
    """Test Config class functionality."""

    def test_default_config(self) -> None:
        """Test default configuration values."""
        config = Config(java_version="17", deps={}, classpath=[])

        assert config.java_version == "17"
        assert config.deps == {}
        assert config.classpath == []

    def test_config_with_values(self) -> None:
        """Test config with custom values."""
        deps = {"maven": ["org.apache.commons:commons-lang3:3.12.0"]}
        classpath = ["test.jar", "another.jar"]

        config = Config(java_version="11", deps=deps, classpath=classpath)

        assert config.java_version == "11"
        assert config.deps == deps
        assert config.classpath == classpath

    def test_from_pyproject_valid_file(self, temp_directory: Path) -> None:
        """Test loading config from valid pyproject.toml."""
        pyproject_content = """
[project]
name = "test-project"
version = "0.1.0"

[tool.jvm]
java-version = "11"
classpath = ["lib/test.jar", "lib/another.jar"]

[tool.jvm.deps]
maven = ["org.junit:junit:4.13.2"]
"""
        pyproject_path = temp_directory / "pyproject.toml"
        pyproject_path.write_text(pyproject_content)

        with patch(
            "jvm.config.Config._find_pyproject_toml", return_value=pyproject_path
        ):
            config = Config.from_pyproject()

        assert config.java_version == "11"
        assert config.classpath == ["lib/test.jar", "lib/another.jar"]
        assert config.deps == {"maven": ["org.junit:junit:4.13.2"]}

    def test_from_pyproject_missing_file(self) -> None:
        """Test behavior when pyproject.toml is not found."""
        with patch("jvm.config.Config._find_pyproject_toml", return_value=None):
            config = Config.from_pyproject()

        # Should return default configuration
        assert config.java_version == "17"
        assert config.deps == {}
        assert config.classpath == []

    def test_from_pyproject_invalid_toml(self, temp_directory: Path) -> None:
        """Test handling of invalid TOML file."""
        pyproject_path = temp_directory / "pyproject.toml"
        pyproject_path.write_text("invalid toml content [[[")

        with patch(
            "jvm.config.Config._find_pyproject_toml", return_value=pyproject_path
        ):
            config = Config.from_pyproject()

        # Should return default configuration on parse error
        assert config.java_version == "17"
        assert config.deps == {}
        assert config.classpath == []

    def test_from_pyproject_missing_tool_jvm_section(
        self, temp_directory: Path
    ) -> None:
        """Test config when [tool.jvm] section is missing."""
        pyproject_content = """
[project]
name = "test-project"
version = "0.1.0"

[tool.other]
option = "value"
"""
        pyproject_path = temp_directory / "pyproject.toml"
        pyproject_path.write_text(pyproject_content)

        with patch(
            "jvm.config.Config._find_pyproject_toml", return_value=pyproject_path
        ):
            config = Config.from_pyproject()

        # Should use default values
        assert config.java_version == "17"
        assert config.deps == {}
        assert config.classpath == []

    def test_from_pyproject_partial_config(self, temp_directory: Path) -> None:
        """Test config with only some values specified."""
        pyproject_content = """
[tool.jvm]
java-version = "21"
"""
        pyproject_path = temp_directory / "pyproject.toml"
        pyproject_path.write_text(pyproject_content)

        with patch(
            "jvm.config.Config._find_pyproject_toml", return_value=pyproject_path
        ):
            config = Config.from_pyproject()

        assert config.java_version == "21"
        assert config.deps == {}
        assert config.classpath == []

    def test_from_pyproject_with_search_path(self, temp_directory: Path) -> None:
        """Test loading config with custom search path."""
        pyproject_content = """
[tool.jvm]
java-version = "19"
classpath = ["custom.jar"]
"""
        pyproject_path = temp_directory / "pyproject.toml"
        pyproject_path.write_text(pyproject_content)

        config = Config.from_pyproject(str(temp_directory))

        assert config.java_version == "19"
        assert config.classpath == ["custom.jar"]


class TestFindPyprojectToml:
    """Test _find_pyproject_toml method."""

    def test_find_pyproject_toml_current_directory(self, temp_directory: Path) -> None:
        """Test finding pyproject.toml in current directory."""
        pyproject_path = temp_directory / "pyproject.toml"
        pyproject_path.write_text("[project]\nname = 'test'")

        with patch("pathlib.Path.cwd", return_value=temp_directory):
            found_path = Config._find_pyproject_toml()

        assert found_path == pyproject_path

    def test_find_pyproject_toml_parent_directory(self, temp_directory: Path) -> None:
        """Test finding pyproject.toml in parent directory."""
        parent_dir = temp_directory
        child_dir = parent_dir / "subdir"
        child_dir.mkdir()

        pyproject_path = parent_dir / "pyproject.toml"
        pyproject_path.write_text("[project]\nname = 'test'")

        with patch("pathlib.Path.cwd", return_value=child_dir):
            found_path = Config._find_pyproject_toml()

        assert found_path == pyproject_path

    def test_find_pyproject_toml_not_found(self, temp_directory: Path) -> None:
        """Test behavior when pyproject.toml is not found."""
        with patch("pathlib.Path.cwd", return_value=temp_directory):
            found_path = Config._find_pyproject_toml()

        assert found_path is None

    def test_find_pyproject_toml_with_search_path(self, temp_directory: Path) -> None:
        """Test finding pyproject.toml with custom search path."""
        pyproject_path = temp_directory / "pyproject.toml"
        pyproject_path.write_text("[project]\nname = 'test'")

        found_path = Config._find_pyproject_toml(str(temp_directory))

        assert found_path == pyproject_path

    def test_find_pyproject_toml_search_up_tree(self, temp_directory: Path) -> None:
        """Test searching up directory tree."""
        # Create nested directory structure
        level1 = temp_directory / "level1"
        level2 = level1 / "level2"
        level3 = level2 / "level3"
        level3.mkdir(parents=True)

        # Place pyproject.toml at level1
        pyproject_path = level1 / "pyproject.toml"
        pyproject_path.write_text("[project]\nname = 'test'")

        # Search from level3
        found_path = Config._find_pyproject_toml(str(level3))

        assert found_path == pyproject_path

    def test_find_pyproject_toml_entry_directory_priority(
        self, temp_directory: Path
    ) -> None:
        """Test that entry directory (sys.path[0]) takes priority."""
        # Create two directories with pyproject.toml
        entry_dir = temp_directory / "entry"
        entry_dir.mkdir()
        current_dir = temp_directory / "current"
        current_dir.mkdir()

        entry_pyproject = entry_dir / "pyproject.toml"
        entry_pyproject.write_text("[tool.jvm]\njava-version = 'entry'")

        current_pyproject = current_dir / "pyproject.toml"
        current_pyproject.write_text("[tool.jvm]\njava-version = 'current'")

        with patch("sys.path", [str(entry_dir)]):
            found_path = Config._find_pyproject_toml(str(current_dir))

        # Should find entry directory first
        assert found_path == entry_pyproject

    def test_find_pyproject_toml_empty_sys_path(self, temp_directory: Path) -> None:
        """Test behavior when sys.path[0] is empty."""
        pyproject_path = temp_directory / "pyproject.toml"
        pyproject_path.write_text("[project]\nname = 'test'")

        with patch("sys.path", [""]):
            with patch("pathlib.Path.cwd", return_value=temp_directory):
                found_path = Config._find_pyproject_toml()

        assert found_path == pyproject_path


class TestConfigEdgeCases:
    """Test edge cases and error conditions."""

    def test_config_with_complex_deps(self, temp_directory: Path) -> None:
        """Test config with complex dependency structure."""
        pyproject_content = """
[tool.jvm]
java-version = "17"
classpath = ["lib/*.jar", "build/classes"]

[tool.jvm.deps]
maven = [
    "org.apache.commons:commons-lang3:3.12.0",
    "junit:junit:4.13.2"
]
gradle = ["implementation 'com.google.guava:guava:31.1-jre'"]
"""
        pyproject_path = temp_directory / "pyproject.toml"
        pyproject_path.write_text(pyproject_content)

        with patch(
            "jvm.config.Config._find_pyproject_toml", return_value=pyproject_path
        ):
            config = Config.from_pyproject()

        assert config.java_version == "17"
        assert config.classpath == ["lib/*.jar", "build/classes"]
        assert len(config.deps["maven"]) == 2
        assert "org.apache.commons:commons-lang3:3.12.0" in config.deps["maven"]
        assert "gradle" in config.deps

    def test_config_empty_values(self, temp_directory: Path) -> None:
        """Test config with empty values."""
        pyproject_content = """
[tool.jvm]
java-version = ""
classpath = []
deps = {}
"""
        pyproject_path = temp_directory / "pyproject.toml"
        pyproject_path.write_text(pyproject_content)

        with patch(
            "jvm.config.Config._find_pyproject_toml", return_value=pyproject_path
        ):
            config = Config.from_pyproject()

        assert config.java_version == ""
        assert config.classpath == []
        assert config.deps == {}

    def test_config_dataclass_equality(self) -> None:
        """Test Config dataclass equality."""
        config1 = Config(java_version="17", deps={}, classpath=["test.jar"])
        config2 = Config(java_version="17", deps={}, classpath=["test.jar"])
        config3 = Config(java_version="11", deps={}, classpath=["test.jar"])

        assert config1 == config2
        assert config1 != config3

    def test_config_dataclass_representation(self) -> None:
        """Test Config dataclass string representation."""
        config = Config(
            java_version="17",
            deps={"maven": ["test:artifact:1.0"]},
            classpath=["test.jar"],
        )

        repr_str = repr(config)
        assert "Config" in repr_str
        assert "java_version='17'" in repr_str
        assert "maven" in repr_str
        assert "test.jar" in repr_str
