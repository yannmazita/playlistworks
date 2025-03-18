# src.features.playlists.repository
import sqlite3
import logging
from src.features.library.repository import SongsRepository
from src.features.library.schemas import Song, Playlist, PlaylistSong
from src.common.repository import DatabaseRepository
from src.features.library.services.query import QueryLexer, QueryParser, SQLGenerator

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

    def insert(self, model: PlaylistSong) -> int | None:
        """Add a song to a playlist"""
        data = model.model_dump(exclude={"id"})  # Exclude auto-incrementing ID
        playlist_id = data["playlist_id"]

        if data["position"] is None:
            select_query = (
                "SELECT MAX(position) FROM playlist_songs WHERE playlist_id = ?"
            )
            row = self._execute_select_query(select_query, (playlist_id,), True)
            row_model = self._row_to_model(row)  # type: ignore
            if row is not None:
                data["position"] = 1 if row is None else row_model.position + 1

        fields = ", ".join(data.keys())
        placeholders = ", ".join("?" * len(data))
        insert_query = f"INSERT INTO playlist_songs ({fields}) VALUES ({placeholders})"

        last_row_id = self._execute_query(insert_query, tuple(data.values()))
        return last_row_id

    def get_playlist_songs(self, playlist_id: int) -> list[Song]:
        """Get all songs in a playlist"""
        playlist_info = self._playlist_repository.find_by_id(playlist_id)

        if playlist_info is not None:
            data = playlist_info.model_dump()
            if data["is_dynamic"] and data["query"]:
                # For dynamic playlists, execute the saved query
                return self._songs_repository.search_songs(data["query"])
            else:
                # For static playlists, get songs from playlist_songs
                select_query = """
                SELECT s.* FROM songs s
                JOIN playlist_songs ps ON s.id = ps.song_id
                WHERE ps.playlist_id = ?
                ORDER BY ps.position
                """
                rows = self._execute_select_query(select_query, (playlist_id,))
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

    def search_songs(self, query: str, playlist_id: int) -> list[Song]:
        """
        Search for songs within a specific playlist based on a query.
        """
        playlist_songs = self.get_playlist_songs(playlist_id)

        if not query or query.strip() == "":
            return playlist_songs

        try:
            # Parse the query into an expression tree
            lexer = QueryLexer(query)
            parser = QueryParser(lexer)
            expression = parser.parse()

            # Generate SQL from the expression tree
            sql_generator = SQLGenerator()
            where_clause, params = sql_generator.generate(expression)

            # Create a temporary table to hold playlist songs
            temp_table_query = """
            CREATE TEMP TABLE temp_playlist_songs AS
            SELECT s.* FROM songs s
            JOIN playlist_songs ps ON s.id = ps.song_id
            WHERE ps.playlist_id = ?
            """
            self._execute_query(temp_table_query, (playlist_id,))

            # Execute the search query within the playlist songs
            sql = f"SELECT * FROM temp_playlist_songs WHERE {where_clause}"
            rows = self._execute_select_query(sql, tuple(params))

            return [self._row_to_model(row) for row in rows] if rows else []  # type: ignore
        except sqlite3.Error:
            logger.exception("Query parsing error", stack_info=True)
            # On error, return all playlist songs (or could return empty list
            return playlist_songs
