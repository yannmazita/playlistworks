# src.features.library.services.library
from collections.abc import Iterator
import logging
from pathlib import Path
import time
from typing import Callable

from PySide6.QtCore import QObject
from mutagen._file import File, FileType
from mutagen._util import MutagenError

from src.features.library.models import SongModel
from src.features.library.schemas import (
    AppData,
    Song,
)
from src.features.library.repository import SongsRepository
from src.features.library.utils.metadata import get_audio_properties, get_tags

logger = logging.getLogger(__name__)


class LibraryServices(QObject):
    """Handles song-related operations, primarily scanning and database population.

    Attributes:
        _song_model: The song table model.
        _library_path: The path to the music library.
        _repository: The songs repository.
        _get_time: A function that returns the current time.
        _paths: An iterator for traversing the library path.
        _loaded_audio_file: The currently loaded audio file.
        _current_file_path: The path to the current file.
        _audio_file_count: The number of audio files found.
    """

    def __init__(
        self,
        song_model: SongModel,
        library_path: Path,
        repository: SongsRepository,
        get_time: Callable[[], float] = time.time,
    ) -> None:
        """Initializes the LibraryServices.

        Args:
            song_model: The song table model.
            library_path: The path to the music library.
            repository: The songs repository.
            get_time: A function that returns the current time.
                Defaults to time.time.
        """
        super().__init__()
        self._song_model = song_model
        self._library_path = library_path
        self._repository = repository
        self._get_time = get_time
        self._paths: Iterator[Path] = self._library_path.rglob("*")
        self._loaded_audio_file: FileType | None = None
        self._current_file_path: Path | None = None
        self._audio_file_count: int = 0

    def populate_database(self) -> list[tuple[Path, Exception]]:
        """Scans the library path and populates the database with song information.

        Iterates through all files in the library path, extracts metadata
        from audio files, and inserts song information into the database.

        Returns:
            A list of tuples. Each tuple contains the Path of a file
            that failed to be processed and the corresponding Exception.
        """
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
                    song: Song = Song(
                        path=str(path),
                        fileprops=fileprops,
                        tags=tags,
                        app_data=app_data,
                    )
                    self._repository.insert(song)
            else:
                continue

        logger.debug(f"Audio files found {self._audio_file_count}")
        return error_paths
