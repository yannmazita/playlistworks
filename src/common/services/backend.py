# src.common.services.backend
import logging
from pathlib import Path
from sqlite3 import Connection

from PySide6.QtCore import QObject, QThread, Signal, Slot

from src.features.tracks.repository import TracksRepository
from src.features.tracks.services.tracks import TracksServices
from src.common.services.backend_worker import BackendWorker

logger = logging.getLogger(__name__)


class BackendServices(QObject):
    # Forward signals from worker
    scanStarted = Signal()
    scanProgress = Signal(int, int)
    scanFinished = Signal()
    scanError = Signal(str)

    # Signal to trigger scan in worker thread
    _startScan = Signal(object)

    def __init__(self, connection: Connection):
        super().__init__()
        self.library_path: Path | None = None
        self.tracks_repository: TracksRepository = TracksRepository(connection)
        self.tracks_services: TracksServices | None = None

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
        if self.library_path:
            self.tracks_services = TracksServices(
                self.library_path, self.tracks_repository
            )

    def set_library_path(self, path: Path):
        if not path.is_dir():
            raise ValueError(f"Invalid library path: {path}")
        self.library_path = path
        self._initialize_services()

    @Slot()
    def scan_library(self):
        """Start a library scan in the background thread."""
        if not self.library_path:
            self.scanError.emit(
                "Library path not set. Please set a library path first."
            )
            return

        self._startScan.emit(self.library_path)
