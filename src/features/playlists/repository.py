# src.features.playlists.repository
import sqlite3
import logging
from src.features.library.repository import SongsRepository
from src.features.library.schemas import Song, Playlist, PlaylistSong
from src.common.repository import DatabaseRepository

logger = logging.getLogger(__name__)


class PlaylistsRepository(DatabaseRepository):
    def __init__(self, connection: sqlite3.Connection):
        super().__init__(connection, Playlist, "playlists")

    def delete(self, id: int) -> bool:
        """Delete a playlist and its songs"""
        query1 = "DELETE FROM playlist_songs WHERE playlist_id = ?"
        query2 = "DELETE FROM playlists WHERE id = ?"

        self._execute_query(query1, (id,))
        self._execute_query(query2, (id,))
        return True


class PlaylistSongRepository(DatabaseRepository):
    def __init__(
        self,
        connection: sqlite3.Connection,
        playlists_repository: PlaylistsRepository,
        songs_repository: SongsRepository,
    ):
        super().__init__(connection, PlaylistSong, "playlist_songs")
        self._playlist_repository = playlists_repository
        self._songs_repository = songs_repository

    # Todo: fix position logic, this will NOT work
    def insert(self, model: PlaylistSong) -> int | None:
        """Add a song to a playlist"""
        data = model.model_dump(exclude={"id"})  # Exclude auto-incrementing ID
        playlist_id = data["playlist_id"]

        if data["position"] is None:
            select_query = (
                "SELECT MAX(position) FROM playlist_songs WHERE playlist_id = ?"
            )
            row = self._execute_select_query(select_query, (playlist_id,), True)
            if row is not None:
                data["position"] = 1 if row is None else row["position"] + 1

        fields = ", ".join(data.keys())
        placeholders = ", ".join("?" * len(data))
        insert_query = f"INSERT INTO playlist_songs ({fields}) VALUES ({placeholders})"

        last_row_id = self._execute_query(insert_query, tuple(data.values()))
        return last_row_id

    def get_playlist_songs(self, playlist_id: int) -> list[Song]:
        """Get all songs in a playlist"""
        playlist_info = self._playlist_repository.find_by_id(playlist_id)

        if playlist_info is not None:
            if playlist_info["is_dynamic"] and playlist_info["query"]:
                # For dynamic playlists, execute the saved query
                return self._songs_repository.search_songs(playlist_info["query"])
            else:
                # For static playlists, get songs from playlist_songs
                select_query = """
                SELECT s.* FROM songs s
                JOIN playlist_songs ps ON s.id = ps.song_id
                WHERE ps.playlist_id = ?
                ORDER BY ps.position
                """
                rows = self._execute_select_query(select_query, (id,))
                return [self._row_to_model(row) for row in rows] if rows else []  # type: ignore
        return []

    def remove_song_from_playlist(self, playlist_id: int, song_id: int):
        """Remove a song from a playlist"""
        self._execute_query(
            """
        DELETE FROM playlist_songs 
        WHERE playlist_id = ? AND song_id = ?
        """,
            (playlist_id, song_id),
        )

    def update_song_position(
        self, playlist_id: int, song_id: int, new_position: int
    ) -> bool:
        """Update a song's position within a playlist"""
        try:
            # Shift existing positions
            self._execute_query(
                """
                UPDATE playlist_songs 
                SET position = position + 1 
                WHERE playlist_id = ? AND position >= ?
            """,
                (playlist_id, new_position),
            )

            # Update target position
            self._execute_query(
                """
                UPDATE playlist_songs 
                SET position = ? 
                WHERE playlist_id = ? AND song_id = ?
            """,
                (new_position, playlist_id, song_id),
            )

            return True
        except sqlite3.Error:
            logger.exception("Error updating position", stack_info=True)
            return False
