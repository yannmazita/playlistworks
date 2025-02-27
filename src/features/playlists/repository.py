# src.features.playlists.repository
import sqlite3
from src.features.playlists.schemas import Playlist
from src.common.repository import DatabaseRepository


class PlaylistsRepository(DatabaseRepository):
    def __init__(self, connection: sqlite3.Connection):
        super().__init__(connection, Playlist, "playlists")
