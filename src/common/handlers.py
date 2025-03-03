# src.common.services.handlers
from PySide6.QtCore import QObject, Slot
from pathlib import Path
import logging

from src.common.services.backend import BackendServices

logger = logging.getLogger(__name__)


class DirectoryHandler(QObject):
    def __init__(self, backend_services: BackendServices):
        super(DirectoryHandler, self).__init__()
        self.backend = backend_services

    @Slot(str)
    def handleDirectorySelected(self, folder_url: str):
        path = folder_url
        if path.startswith("file:///"):
            path = path[7:]
        elif path.startswith("file:/"):
            path = path[5:]
        elif path.startswith("file:"):
            path = path[5:]

        try:
            self.backend.set_library_path(Path(path))
            logger.info(f"Library path set to: {path}")
        except Exception as e:
            logger.exception(e, stack_info=True)
