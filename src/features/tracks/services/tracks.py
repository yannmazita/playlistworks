# src.features.tracks.services.tracks
from collections.abc import Iterator
import logging
from pathlib import Path
import time

from src.features.tracks.schemas import AppData, Track
from src.features.tracks.repository import TracksRepository
from src.features.tracks.services.mp3 import MP3Services

logger = logging.getLogger(__name__)


class TracksServices:
    """
    Class for track-related operations.

    Attributes:
        repository: The tracks repository to be used for operations.
    """

    def __init__(self, repository: TracksRepository, mp3: MP3Services) -> None:
        self.repository = repository
        self.mp3 = mp3

    def populate_database(self) -> Iterator[Path]:
        logger.info("Populating metadata database")
        while self.mp3.load_next_file() is not False:
            yield self.mp3.current_file_path

            path = self.mp3.current_file_path
            fileprops = self.mp3.get_audio_properties()
            tags = self.mp3.get_tags()
            app_data = AppData(added_date=time.time())

            track: Track = Track(
                path=str(path), fileprops=fileprops, tags=tags, app_data=app_data
            )

            self.repository.insert(track)
