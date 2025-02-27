import logging
from pathlib import Path
from sqlite3 import Connection
from typing import Iterator
from src.features.tracks.repository import TracksRepository
from src.features.tracks.services.mp3 import MP3Services
from src.features.tracks.services.tracks import TracksServices

logger = logging.getLogger(__name__)


class Headless:
    def __init__(self, musicDirectory: str, connection: Connection):
        self.mp3 = MP3Services(Path(musicDirectory))
        self.tracks_repository = TracksRepository(connection)
        self.tracks = TracksServices(self.tracks_repository, self.mp3)
        self.filepath: Iterator[Path] = self.tracks.populate_database()

    def run(self):
        for path in self.filepath:
            logger.info(f"Current file: {path}")
