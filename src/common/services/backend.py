# src.common.services.backend
import logging
from pathlib import Path
from sqlite3 import Connection

from PySide6.QtCore import QObject, QThread, Signal, Slot

from src.features.player.services.playback import PlaybackService
from src.features.library.models import SongModel
from src.features.library.repository import SongsRepository
from src.features.library.services.library import LibraryServices
from src.common.services.backend_worker import BackendWorker

logger = logging.getLogger(__name__)


class BackendServices(QObject):
    """Manages songs, playback, and communication with a worker thread.

    Signals:
        scanStarted: Emitted when the library scan starts.
        scanProgress: Emitted during the scan to indicate progress (int: number of files added).
        scanFinished: Emitted when the scan finishes (list: list of non-critical error paths).
        scanError: Emitted if a critical error occurs during the scan (str: error message).
        _startScan: Internal signal to trigger scan in worker thread (object: library path).

    Attributes:
        library_path: The path to the music library.
        songs_repository: Repository for song database operations.
        library_services: Service for song-related logic.
        song_model: Model for the GUI song table.
        playback_service: Service for audio playback.
        worker_thread: The worker thread for long-running operations.
        worker: The worker object that runs in the worker thread.
    """

    scanStarted = Signal()
    scanProgress = Signal(int)
    scanFinished = Signal(list)
    scanError = Signal(str)
    _startScan = Signal(object)

    def __init__(self, connection: Connection):
        """Initializes the BackendServices.

        Sets up the worker thread, connects signals, and initializes
        repositories and services.

        Args:
            connection: The database connection.
        """
        super().__init__()
        self.library_path: Path | None = None
        self.songs_repository: SongsRepository = SongsRepository(connection)
        self.library_services: LibraryServices | None = None
        self.song_model: SongModel = SongModel(self.songs_repository)
        self.playback_service: PlaybackService = PlaybackService(self.song_model)

        # Setup worker thread
        self.worker_thread = QThread()
        self.worker = BackendWorker()
        self.worker.moveToThread(self.worker_thread)

        # Connect worker signals to local signals for forwarding
        self.worker.scanStarted.connect(self.scanStarted)
        self.worker.scanProgress.connect(self.scanProgress)
        self.worker.scanFinished.connect(self.scanFinished)
        self.worker.scanError.connect(self.scanError)

        # Connect scan start signal to worker slot
        self._startScan.connect(self.worker.scan_library)

        self.worker_thread.start()

    def __del__(self):
        """Clean up the worker thread."""
        if hasattr(self, "worker_thread") and self.worker_thread.isRunning():
            self.worker_thread.quit()
            self.worker_thread.wait()

    def _initialize_services(self):
        """Initialize services with the current library path."""
        if self.library_path:
            self.library_services = LibraryServices(
                self.song_model, self.library_path, self.songs_repository
            )
        # self.playback_service = PlaybackService()

    @Slot(str)  # type: ignore
    def set_library_path(self, library_path: str):
        """Sets the library path.

        Args:
            library_path: The path to the music library.

        Raises:
            ValueError: If the provided path is not a valid directory.
        """
        path = Path(library_path)
        if not path.is_dir():
            raise ValueError(f"Invalid library path: {path}")
        self.library_path = path
        self._initialize_services()

    @Slot()
    def scan_library(self):
        """Starts a library scan in the background thread.

        Emits scanError if the library path is not set. Otherwise,
        emits the _startScan signal to trigger the scan in the worker thread.
        """
        if not self.library_path:
            self.scanError.emit(
                "Library path not set. Please set a library path first."
            )
            return

        self._startScan.emit(self.library_path)
