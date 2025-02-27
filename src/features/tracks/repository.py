# src.features.tracks.repository
import sqlite3
from src.features.tracks.schemas import Track
from src.common.repository import DatabaseRepository


class TracksRepository(DatabaseRepository):
    """
    Repository for performing database queries on tracks.
    """

    def __init__(self, connection: sqlite3.Connection):
        super().__init__(connection, Track, "tracks")
