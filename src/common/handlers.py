# src.common.services.handlers
from PySide6.QtCore import QObject, Slot
import logging

from src.common.services.backend import BackendServices

logger = logging.getLogger(__name__)


class DirectoryHandler(QObject):
    def __init__(self, backend_services: BackendServices):
        super(DirectoryHandler, self).__init__()
        self.backend = backend_services

    @Slot(str)  # type: ignore
    def handleDirectorySelected(self, folder_url: str):
        library_path = folder_url
        if library_path.startswith("file:///"):
            library_path = library_path[7:]
        elif library_path.startswith("file:/"):
            library_path = library_path[5:]
        elif library_path.startswith("file:"):
            library_path = library_path[5:]

        try:
            self.backend.set_library_path(library_path)
            logger.info(f"Library path set to: {library_path}")
        except Exception as e:
            logger.exception(e, stack_info=True)
