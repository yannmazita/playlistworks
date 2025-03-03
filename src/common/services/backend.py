# src.common.services.backend
import logging
from pathlib import Path
from sqlite3 import Connection

from src.features.tracks.repository import TracksRepository
from src.features.tracks.services.mp3 import MP3Services
from src.features.tracks.services.tracks import TracksServices

logger = logging.getLogger(__name__)


class BackendServices:
    def __init__(self, connection: Connection):
        self.libraryPath: Path | None = None
        self.tracks_repository: TracksRepository = TracksRepository(connection)
        self.mp3_services: MP3Services | None = None
        self.tracks_services: TracksServices | None = None

    def _initialize_services(self):
        if self.library_path:
            self.mp3_services = MP3Services(self.library_path)
            self.tracks_services = TracksServices(
                self.tracks_repository, self.mp3_services
            )

    def set_library_path(self, path: Path):
        if not path.is_dir():
            raise ValueError(f"Invalid library path: {path}")
        self.library_path = path
        self._initialize_services()

    def scan_library(self):
        if not self.tracks_services:
            raise ValueError(
                "Tracks services not initialized. Set a library path first."
            )
        self.tracks_services.populate_database()
