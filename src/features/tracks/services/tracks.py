# src.features.tracks.services.tracks
from collections.abc import Iterator
import logging
from pathlib import Path

from sqlalchemy.orm import Session
from src.features.tracks.models import Track
from src.features.tracks.repository import TracksRepository
from src.features.tracks.schemas import TrackCreate
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

    def populate_database(self, session: Session) -> Iterator[Path]:
        logger.info("Populating database")
        while self.mp3.load_next_file() is not None:
            yield self.mp3.current_file_path
            title = self.mp3.get_title()
            artist = self.mp3.get_artist()

            if title is None or artist is None:
                logger.warning(
                    f"{self.mp3.current_file_path} has no title or artist name, skipping"
                )
            else:
                track_data: TrackCreate = TrackCreate(
                    title=title,
                    artist=artist,
                    album=self.mp3.get_album(),
                    genre=self.mp3.get_genre(),
                    duration=self.mp3.get_duration(),
                    path=str(self.mp3.current_file_path),
                    id3_metadata=self.mp3.get_tags(),
                )
                track: Track = self.repository.create(session, track_data)
                logger.debug(f"Added {track} to database")
