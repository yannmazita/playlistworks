# src.features.tracks.services.tracks
from collections.abc import Iterator
import logging
import time
from typing import Callable

from src.features.tracks.schemas import AppData, Track
from src.features.tracks.repository import TracksRepository
from src.features.tracks.services.mp3 import MP3Services

logger = logging.getLogger(__name__)


class TracksServices:
    """
    Class for track-related operations.

    Attributes:
        repository: The tracks repository to be used for operations.
        mp3: MP3 services
        get_time: time callable
    """

    def __init__(
        self,
        repository: TracksRepository,
        mp3: MP3Services,
        get_time: Callable[[], float] = time.time,
    ) -> None:
        self.repository = repository
        self.mp3 = mp3
        self._get_time = get_time

    def _iter_tracks(self) -> Iterator[Track]:
        while self.mp3.load_next_file():
            path = self.mp3.current_file_path
            fileprops = self.mp3.get_audio_properties()
            tags = self.mp3.get_tags()
            app_data = AppData(added_date=time.time())
            if fileprops is None:
                continue

            track: Track = Track(
                path=str(path), fileprops=fileprops, tags=tags, app_data=app_data
            )

            yield track

    def populate_database(self):
        logger.info("Populating metadata database")
        for track in self._iter_tracks():
            self.repository.insert(track)
