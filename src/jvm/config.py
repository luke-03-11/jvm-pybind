from __future__ import annotations

import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class Config:
    """JVM設定"""

    java_version: str
    deps: Dict[str, List[str]]
    classpath: List[str]

    @classmethod
    def from_pyproject(cls, search_path: Optional[str] = None) -> Config:
        """pyproject.toml設定読み込み"""
        pyproject_path = cls._find_pyproject_toml(search_path)

        if not pyproject_path:
            return cls(java_version="17", deps={}, classpath=[])

        try:
            with open(pyproject_path, "rb") as f:
                data = tomllib.load(f)

            tool_jvm = data.get("tool", {}).get("jvm", {})

            java_version = tool_jvm.get("java-version", "17")
            deps = tool_jvm.get("deps", {})
            classpath = tool_jvm.get("classpath", [])

            return cls(java_version=java_version, deps=deps, classpath=classpath)

        except Exception:
            return cls(java_version="17", deps={}, classpath=[])

    @staticmethod
    def _find_pyproject_toml(search_path: Optional[str] = None) -> Optional[Path]:
        """pyproject.toml検索"""
        entry_dir = Path(sys.path[0]) if sys.path[0] else Path.cwd()
        entry_pyproject = entry_dir / "pyproject.toml"
        if entry_pyproject.exists():
            return entry_pyproject

        if search_path:
            current_dir = Path(search_path)
        else:
            current_dir = Path.cwd()

        while True:
            pyproject_path = current_dir / "pyproject.toml"
            if pyproject_path.exists():
                return pyproject_path

            parent = current_dir.parent
            if parent == current_dir:
                break
            current_dir = parent

        return None
