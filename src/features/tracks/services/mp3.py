# src.features.tracks.services.mp3
import logging
from collections.abc import Iterator
from pathlib import Path

from mutagen.id3 import ID3
from mutagen.mp3 import MP3

from src.core.types import ID3Keys
from src.features.tracks.schemas import FileProperties

logger = logging.getLogger(__name__)


class MP3Services:
    """
    Class for MP3 specific operations.
    """

    def __init__(self, library_path: Path):
        self.__library_path: Path = library_path
        self.__paths: Iterator[Path] | None = None
        self.__current_file_path: Path = Path("")
        self.__current_mp3_file: MP3 | None = None
        self.__current_mp3_tags: ID3 | None = None

    @property
    def current_file_path(self) -> Path:
        """File path of current loaded audio file"""
        return self.__current_file_path

    def _get_paths(self) -> Iterator[Path]:
        """Get the iterator of MP3 file paths."""
        if self.__paths is None:
            self.__paths = self.__library_path.rglob("*.mp3")
        return self.__paths

    def load_next_file(self) -> bool:
        """Loads the next audio file from paths in instance.

        Returns:
            True if a file was loaded, False otherwise.
        """
        try:
            self.__current_file_path = next(self._get_paths())
            self.__current_mp3_file = MP3(self.__current_file_path)
            self.__current_mp3_tags = ID3(self.__current_file_path)
            try:
                # Adding an empty ID3 tag if none exist for future manipulation
                # self.__current_mp3.add_tags()
                pass
            except Exception:
                logger.info(f"No ID3 header found for {self.__current_file_path}")
        except StopIteration:
            self.__current_mp3_file = None
            self.__current_mp3_tags = None
            return False
        except Exception as e:
            logger.exception(e, stack_info=True)
            self.__current_mp3_file = None
            self.__current_mp3_file = None
            return self.load_next_file()

        return True

    def get_tags(self) -> dict[str, list[str]]:
        """Gets tags from loaded file.

        Returns:
            Dictionary of ID3Keys and their frames.
        """
        if self.__current_mp3_tags is None:
            return {}

        tags: dict[str, list[str]] = {}

        for frame in ID3Keys:
            try:
                frames = list(map(str, self.__current_mp3_tags.getall(frame.value)))
                if frames:
                    tags[frame.name] = frames
            except (IndexError, KeyError):
                pass
            except Exception as e:
                logger.exception(e, stack_info=True)

        # for key, value in self.__current_mp3.tags.items():
        #    tags[key] = value

        return tags

    def get_audio_properties(self) -> FileProperties | None:
        """Get audio properties like bitrate, sample rate, etc."""
        if self.__current_mp3_file is None:
            return None
        mpeg_info = self.__current_mp3_file.info
        file_stats = self.__current_file_path.stat()
        # only length is known by lsp in mpeg_info
        return FileProperties(
            size=file_stats.st_size,
            bitrate=mpeg_info.bitrate // 1000,  # Convert to kbps
            sample_rate=mpeg_info.sample_rate,
            channels=mpeg_info.channels,
            length=mpeg_info.length,
            mtime=file_stats.st_mtime,
        )
