# src.common.services.backend
import logging
from pathlib import Path
from sqlite3 import Connection

from PySide6.QtCore import Property, QObject, QThread, Signal, Slot

from src.features.player.services.playback import PlaybackService
from src.features.library.models import MusicLibrary
from src.features.library.repository import SongsRepository
from src.features.library.services.library import LibraryServices
from src.common.services.backend_worker import BackendWorker
from src.features.playlists.repository import (
    PlaylistSongRepository,
    PlaylistsRepository,
)

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
        playlists_repository: Repository for playlist database operations.
        playlist_song_repository: Repository for playlist_song database operations.
        library_services: Service for song-related logic.
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
        self._library_path: Path | None = None
        self._songs_repository: SongsRepository = SongsRepository(connection)
        self._playlists_repository: PlaylistsRepository = PlaylistsRepository(
            connection
        )
        self._playlist_song_repository: PlaylistSongRepository = PlaylistSongRepository(
            connection, self._playlists_repository, self._songs_repository
        )
        self._library = MusicLibrary(
            self._songs_repository,
            self._playlists_repository,
            self._playlist_song_repository,
        )
        self._library_services: LibraryServices | None = None
        self._playback_service: PlaybackService = PlaybackService(self._library)

        # Setup worker thread
        self._worker_thread = QThread()
        self._worker = BackendWorker()
        self._worker.moveToThread(self._worker_thread)

        # Connect worker signals to local signals for forwarding
        self._worker.scanStarted.connect(self.scanStarted)
        self._worker.scanProgress.connect(self.scanProgress)
        self._worker.scanFinished.connect(self.scanFinished)
        self._worker.scanError.connect(self.scanError)

        # Connect scan start signal to worker slot
        self._startScan.connect(self._worker.scan_library)

        self._worker_thread.start()

    def __del__(self):
        """Clean up the worker thread."""
        if hasattr(self, "worker_thread") and self._worker_thread.isRunning():
            self._worker_thread.quit()
            self._worker_thread.wait()

    def _initialize_services(self):
        """Initialize services with the current library path."""
        if self._library_path:
            self._library_services = LibraryServices(
                self._library_path,
                self._songs_repository,
            )

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
        self._library_path = path
        self._initialize_services()

    @Slot()
    def scan_library(self):
        """Starts a library scan in the background thread.

        Emits scanError if the library path is not set. Otherwise,
        emits the _startScan signal to trigger the scan in the worker thread.
        """
        if not self._library_path:
            self.scanError.emit(
                "Library path not set. Please set a library path first."
            )
            return

        self._startScan.emit(self._library_path)

    def get_library(self):
        return self._library

    library = Property(QObject, fget=get_library, fset=None, constant=True)  # type: ignore

    def get_playback(self):
        return self._playback_service

    playback = Property(QObject, fget=get_playback, fset=None, constant=True)  # type: ignore
