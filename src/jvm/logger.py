"""JVMロガー設定"""

import logging
import sys
from typing import Optional


class JVMLogger:
    """JVMロガー"""

    _instance: Optional["JVMLogger"] = None
    _logger: Optional[logging.Logger] = None

    def __new__(cls) -> "JVMLogger":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._setup_logger()
        return cls._instance

    def _setup_logger(self) -> None:
        """ログ設定初期化"""
        self._logger = logging.getLogger("JVM")
        self._logger.setLevel(logging.INFO)

        # ハンドラー既存チェック
        if not self._logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            handler.setLevel(logging.INFO)

            formatter = logging.Formatter(
                "%(asctime)s [%(name)s: %(levelname)s] %(message)s"
            )
            handler.setFormatter(formatter)

            self._logger.addHandler(handler)

    def info(self, message: str) -> None:
        """INFOログ"""
        if self._logger:
            self._logger.info(message)

    def debug(self, message: str) -> None:
        """DEBUGログ"""
        if self._logger:
            self._logger.debug(message)

    def warning(self, message: str) -> None:
        """WARNINGログ"""
        if self._logger:
            self._logger.warning(message)

    def error(self, message: str) -> None:
        """ERRORログ"""
        if self._logger:
            self._logger.error(message)

    def set_level(self, level: int) -> None:
        """ログレベル設定"""
        if self._logger:
            self._logger.setLevel(level)
            for handler in self._logger.handlers:
                handler.setLevel(level)


# シングルトン
logger = JVMLogger()
