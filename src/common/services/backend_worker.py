# src.common.services.backend_worker
import logging
from pathlib import Path
from PySide6.QtCore import QObject, Signal, Slot

from src.common.database import get_db_connection
from src.features.tracks.models import TrackTableModel
from src.features.tracks.repository import TracksRepository
from src.features.tracks.services.tracks import TracksServices

logger = logging.getLogger(__name__)


class BackendWorker(QObject):
    """Performs tasks in a separate thread.

    Signals:
        scanStarted: Emitted when the library scan starts.
        scanProgress: Emitted during the scan to indicate progress.
        scanFinished: Emitted when the scan finishes.
        scanError: Emitted if an error occurs during the scan.

    Attributes:
        track_model: Model for the GUI track table.
        tracks_repository: Repository for track database operations.
        tracks_services: Service for track-related logic.
        is_running: A boolean, True if scan is running
    """

    scanStarted = Signal()
    scanProgress = Signal(int)  # Number of audio files added
    scanFinished = Signal(list)  # List of non-critical errors when scanning files
    scanError = Signal(str)

    def __init__(self):
        """Initializes the BackendWorker."""
        super().__init__()
        self.track_model = None
        self.tracks_repository = None
        self.tracks_services = None
        self.is_running = False

    def initialize_services(self, library_path: Path) -> bool:
        """Initialize services with the given library path.

        Args:
            library_path (Path): The path to the music library.

        Returns:
            bool: True if initialization was successful. False if library_path is invalid
                or if there was an exception.
        """
        if not library_path.is_dir():
            self.scanError.emit(f"Invalid library path: {library_path}")
            return False

        try:
            # Using thread-specific connection (and repository) because sqlite is not thread-safe
            connection = get_db_connection()
            self.tracks_repository = TracksRepository(connection)
            self.track_model = TrackTableModel(self.tracks_repository)
            self.tracks_services = TracksServices(
                self.track_model, library_path, self.tracks_repository
            )
            return True
        except Exception as e:
            self.scanError.emit(f"Error initializing services: {str(e)}")
            logger.exception(e, stack_info=True)
            return False

    @Slot(Path)  # type: ignore
    def scan_library(self, library_path: Path):
        """Scans the library and populates the database with track information.

        Emits `scanStarted` when the scan begins.
        Emits 'scanProgress' with number of audio files added.
        Emits `scanFinished` when the scan is complete, along with a list of
        any non-critical errors encountered.
        Emits `scanError` if a critical error occurs.

        Args:
            library_path (Path): The path to the music library.
        """
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
            error_paths = self.tracks_services.populate_database()
            self.scanFinished.emit(error_paths)
            return

        except Exception as e:
            self.scanError.emit(f"Error scanning library: {str(e)}")
            logger.exception(e, stack_info=True)
            return
        finally:
            self.is_running = False
