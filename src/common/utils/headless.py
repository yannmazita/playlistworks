import logging
from pathlib import Path
from src.features.tracks.repository import TracksRepository
from src.features.tracks.services.mp3 import MP3Services
from src.features.tracks.services.tracks import TracksServices

logger = logging.getLogger(__name__)


class Headless:
    def __init__(self, musicDirectory: str):
        self.mp3 = MP3Services(Path(musicDirectory))
        self.tracks_repository = TracksRepository()
        self.tracks = TracksServices(self.tracks_repository, self.mp3)
