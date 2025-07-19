import threading
from importlib.abc import MetaPathFinder
from importlib.machinery import ModuleSpec
from typing import Any, Optional, Sequence

from ..config import Config
from ..jvm import JVM
from ..loader import JVMLoader
from ..logger import logger
from .loader import JavaLoader


class JavaFinder(MetaPathFinder):
    """Javaパッケージファインダー"""

    _PREFIXES = ("java.", "javax.", "jdk.")

    def __init__(self) -> None:
        self._jvm: Optional[JVM] = None
        self._jvm_lock = threading.Lock()
        self._shutdown_registered = False

    def _get_jvm(self) -> JVM:
        """遅延JVM初期化"""
        if self._jvm is None:
            with self._jvm_lock:
                if self._jvm is None:
                    logger.info("Initializing JVM...")
                    _cfg = Config.from_pyproject()
                    self._jvm = JVMLoader(_cfg).start()
                    logger.info("JVM initialized")

        return self._jvm

    def find_spec(
        self, fullname: str, path: Optional[Sequence[str]], target: Optional[Any] = None
    ) -> Optional[ModuleSpec]:
        if fullname == "java" or fullname.startswith(self._PREFIXES):
            jvm = self._get_jvm()
            return ModuleSpec(
                name=fullname,
                loader=JavaLoader(jvm, fullname),
                is_package="." in fullname,
            )
        return None
