# src.common.services.backend_worker
import logging
from pathlib import Path
from PySide6.QtCore import QObject, Signal, Slot

from src.common.database import get_db_connection
from src.features.tracks.repository import TracksRepository
from src.features.tracks.services.mp3 import MP3Services
from src.features.tracks.services.tracks import TracksServices

logger = logging.getLogger(__name__)


class BackendWorker(QObject):
    """Worker object that will be moved to a separate thread to handle long-running operations."""

    # Signals for library scanning
    scanStarted = Signal()
    scanProgress = Signal(int, int)  # current, total
    scanFinished = Signal()
    scanError = Signal(str)

    def __init__(self):
        super().__init__()
        self.tracks_repository = None
        self.mp3_services = None
        self.tracks_services = None
        self.is_running = False

    def initialize_services(self, library_path: Path):
        """Initialize services with the given library path."""
        if not library_path.is_dir():
            self.scanError.emit(f"Invalid library path: {library_path}")
            return False

        try:
            # Using thread-specific connection (and repository) because sqlite is not thread-safe
            connection = get_db_connection()
            self.tracks_repository = TracksRepository(connection)
            self.mp3_services = MP3Services(library_path)
            self.tracks_services = TracksServices(
                self.tracks_repository, self.mp3_services
            )
            return True
        except Exception as e:
            self.scanError.emit(f"Error initializing services: {str(e)}")
            logger.exception(e, stack_info=True)
            return False

    @Slot(object)
    def scan_library(self, library_path):
        """Scan the library and populate the database with track information."""
        if self.is_running:
            logger.warning("Already running a scan operation")
            return

        self.is_running = True
        self.scanStarted.emit()

        try:
            if not self.initialize_services(library_path):
                self.is_running = False
                return

            if not self.tracks_services:
                self.scanError.emit("Tracks services not initialized")
                self.is_running = False
                return

            # Execute the scan
            self.tracks_services.populate_database()
            self.scanFinished.emit()

        except Exception as e:
            logger.exception(e, stack_info=True)
            self.scanError.emit(f"Error scanning library: {str(e)}")
        finally:
            self.is_running = False
