# src.features.songs.utils.metadata
from pathlib import Path
from typing import Any
from mutagen._file import FileType
from mutagen.id3 import ID3
from mutagen.mp4 import MP4Tags

from src.core.types import AppleKeys, ID3Keys
from src.features.library.schemas import FileProperties


def get_audio_properties(audio_file: FileType, audio_file_path: Path) -> FileProperties:
    """
    Get file properties like bitrate, sample rate, etc.
    Args:
        audio_file: The audio file.
        audio_file_path: The audio file path.
    Returns:
        Object describing audio file properties.
    """
    info = audio_file.info
    stats = audio_file_path.stat()

    return FileProperties(
        size=stats.st_size,
        bitrate=info.bitrate // 1000,  # Convert to kbps
        sample_rate=info.sample_rate,
        channels=info.channels,
        length=info.length,
        mtime=stats.st_mtime,
    )


def get_tags(audio_file: FileType) -> dict[str, list[Any]]:
    """
    Get tags from an audio file.
    When dealing with ID3 or MP4 metadata, known frame names are replaced
    by human readable strings defined in the src.core.types.ID3Keys and
    src.core.types.AppleKeys enums. Non-spec frames are ignored.
    Other metadata types are taken as is.

    Args:
        audio_file: The audio file
    Returns:
        Key-value pairs of frame names (key) and their data (value). Multi-frames are stored in the same key.
    """

    tags: dict[str, list[Any]] = {}

    if audio_file.tags is None:
        return tags

    if isinstance(audio_file.tags, ID3):
        for frame in ID3Keys:
            frames = list(map(str, audio_file.tags.getall(frame.value)))
            if frames:
                tags[frame.name] = frames

    elif isinstance(audio_file.tags, MP4Tags):
        for frame in AppleKeys:
            file_frame = audio_file.tags.get(frame.value)
            if file_frame:
                tags[frame.name] = file_frame
    else:
        # Todo: Handle vorbis comments
        pass

    return tags
