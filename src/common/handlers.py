# src.common.services.directory_handler
from PySide6.QtCore import QObject, Slot
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class DirectoryHandler(QObject):
    @Slot(str)
    def handleDirectorySelected(self, path_str: str) -> str:
        """Validates and normalizes directory paths from QML"""
        try:
            path = Path(path_str.replace("file://", "").strip())
            if not path.exists():
                logger.warning(f"Path does not exist: {path_str}")
                return ""
            if not path.is_dir():
                logger.warning(f"Path is not directory: {path_str}")
                return ""
            return str(path.resolve())
        except Exception as e:
            logger.error(f"Directory validation failed: {e}", exc_info=True)
            return ""
