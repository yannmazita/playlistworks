# src.features.library.repository
import sqlite3
from src.features.library.schemas import Song
from src.common.repository import DatabaseRepository


class SongsRepository(DatabaseRepository):
    """
    Repository for performing database queries on songs.
    """

    def __init__(self, connection: sqlite3.Connection):
        super().__init__(connection, Song, "songs")
