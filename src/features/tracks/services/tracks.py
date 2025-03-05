# src.features.tracks.services.tracks
from collections.abc import Iterator
import logging
from pathlib import Path
import time
from typing import Callable

from mutagen._file import File, FileType
from mutagen._util import MutagenError

from src.features.tracks.schemas import (
    AppData,
    Track,
)
from src.features.tracks.repository import TracksRepository
from src.features.tracks.utils.metadata import get_audio_properties, get_tags

logger = logging.getLogger(__name__)


class TracksServices:
    """
    Class for track-related operations.

    Attributes:
        repository: The tracks repository to be used for operations.
        get_time: time callable
    """

    def __init__(
        self,
        library_path: Path,
        repository: TracksRepository,
        get_time: Callable[[], float] = time.time,
    ) -> None:
        self.library_path = library_path
        self.repository = repository
        self._get_time = get_time
        self._paths: Iterator[Path] = self.library_path.rglob("*")
        self._loaded_audio_file: FileType | None = None
        self._current_file_path: Path | None = None
        self._audio_file_count: int = 0

    def populate_database(self) -> list[tuple[Path, Exception]]:
        logger.info("Populating metadata database")
        error_paths: list[tuple[Path, Exception]] = []

        for path in self._paths:
            if path.is_file():
                try:
                    self._loaded_audio_file = File(path)
                except MutagenError as e:
                    error_paths.append((path, e))

                if self._loaded_audio_file is not None:
                    self._audio_file_count += 1

                    fileprops = get_audio_properties(self._loaded_audio_file, path)
                    tags = get_tags(self._loaded_audio_file)
                    app_data = AppData(added_date=time.time())
                    track: Track = Track(
                        path=str(path),
                        fileprops=fileprops,
                        tags=tags,
                        app_data=app_data,
                    )
                    self.repository.insert(track)
            else:
                continue

        logger.debug(f"Audio files found {self._audio_file_count}")
        return error_paths
