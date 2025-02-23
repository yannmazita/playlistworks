# src.features.tracks.services.id3
from collections.abc import Iterator
from pathlib import Path

from mutagen.id3 import ID3
from mutagen.mp3 import MP3

from src.core.types import ID3Keys


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

        self.__current_mp3_file = MP3(self.__current_mp3_file)
        self.__current_mp3_tags = ID3(self.__current_file_path)

        return True

    def get_tags(self) -> dict[ID3Keys, list[str]]:
        """Gets ID3 tags from loaded file.

        Returns:
            Dictionary of ID3Keys and their frames.
        """
        tags: dict[ID3Keys, list[str]] = {}

        for frame in ID3Keys:
            try:
                frames = list(map(str, self.__current_mp3_tags.getall(frame.value)))
                tags[frame] = frames
            except IndexError:
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

    def get_duration(self) -> int:
        return self.__current_mp3_file.info.length
