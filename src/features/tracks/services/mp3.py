# src.features.tracks.services.mp3
import logging
from collections.abc import Iterator
from pathlib import Path
from typing import Any

from mutagen.id3 import ID3
from mutagen.mp3 import MP3

from src.core.types import ID3Keys

logger = logging.getLogger(__name__)


class MP3Services:
    """
    Class for MP3 specific operations.
    """

    def __init__(self, musicDirectory: Path):
        self.__current_file_path: Path = Path("")
        self.__paths: Iterator[Path] = Path(musicDirectory).rglob("*.mp3")
        self.__current_mp3_file: MP3 = MP3()
        self.__current_mp3_tags: ID3 = ID3()

    @property
    def current_file_path(self) -> Path:
        """File path of current loaded audio file"""
        return self.__current_file_path

    def load_next_file(self) -> bool:
        """Loads next audio file from paths in instance.

        Returns:
            A boolean, true if file was loaded, false otherwise.
        """
        try:
            self.__current_file_path = Path(next(self.__paths))
        except StopIteration:
            return False

        try:
            self.__current_mp3_file = MP3(self.__current_file_path)
            self.__current_mp3_tags = ID3(self.__current_file_path)
        except Exception as e:
            logger.error(f"Error loading {self.__current_file_path}", e, exc_info=True)
            logger.debug("Trying next file")
            return self.load_next_file()

        return True

    def get_tags(self) -> dict[ID3Keys, list[str]]:
        """Gets ID3 tags from loaded file.

        Returns:
            Dictionary of ID3Keys and their frames.
        """
        tags: dict[ID3Keys, list[str]] = {}

        for frame in ID3Keys:
            try:
                if frame.value:
                    frames = list(map(str, self.__current_mp3_tags.getall(frame.value)))
                    if frames:
                        tags[frame] = frames
            except (IndexError, KeyError):
                pass

        return tags

    def get_title(self) -> list[str] | None:
        try:
            return self.__current_mp3_tags.getall(ID3Keys.TITLE)
        except IndexError:
            return None

    def get_artist(self) -> list[str] | None:
        try:
            return self.__current_mp3_tags.getall(ID3Keys.ARTIST)
        except IndexError:
            return None

    def get_album(self) -> list[str] | None:
        try:
            return self.__current_mp3_tags.getall(ID3Keys.ALBUM)
        except IndexError:
            return None

    def get_genre(self) -> list[str] | None:
        try:
            return self.__current_mp3_tags.getall(ID3Keys.GENRE)
        except IndexError:
            return None

    def get_track_number(self) -> str | None:
        try:
            return self.__current_mp3_tags.getall(ID3Keys.TRACK_NUM)[0]
        except IndexError:
            return None

    def get_duration(self) -> float:
        """Get track duration in seconds"""
        return self.__current_mp3_file.info.length

    def get_audio_properties(self) -> dict[str, Any]:
        """Get audio properties like bitrate, sample rate, etc."""
        info = self.__current_mp3_file.info
        # only length is known by lsp
        return {
            "length": info.length,
            "bitrate": info.bitrate // 1000,  # Convert to kbps
            "samplerate": info.sample_rate,
            "channels": info.channels,
            "codec": "mp3",
        }
