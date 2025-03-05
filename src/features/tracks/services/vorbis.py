# src.features.tracks.services.vorbis
import logging
from collections.abc import Iterator
from pathlib import Path

from mutagen.flac import FLAC

from src.features.tracks.schemas import FileProperties

logger = logging.getLogger(__name__)


class VorbisServices:
    """
    Class for Vorbis specific operations
    """

    def __init__(self, library_path: Path):
        pass
