# src.features.library.repository
import logging
import sqlite3
from datetime import datetime

from src.common.repository import DatabaseRepository
from src.features.library.schemas import Song
from src.features.library.services.query import QueryLexer, QueryParser, SQLGenerator

logger = logging.getLogger(__name__)


class SongsRepository(DatabaseRepository):
    """
    Repository for performing database queries on songs.
    """

    def __init__(self, connection: sqlite3.Connection):
        super().__init__(connection, Song, "songs")

    def search_songs(self, query: str) -> list[Song]:
        """
        Parse and execute a complex search query with support for parentheses,
        logical operators, and field-specific comparisons.
        """
        if not query or query.strip() == "":
            return self.find_many()

        try:
            # Parse the query into an expression tree
            lexer = QueryLexer(query)
            parser = QueryParser(lexer)
            expression = parser.parse()

            # Generate SQL from the expression tree
            sql_generator = SQLGenerator()
            where_clause, params = sql_generator.generate(expression)

            # Execute the query
            sql = f"SELECT * FROM songs WHERE {where_clause}"
            # logger.debug(f"sql: {sql}")
            # logger.debug(f"params: {params}")
            rows = self._execute_select_query(sql, tuple(params))
            # logger.debug(f"rows empty: {rows == []}")
            return [self._row_to_model(row) for row in rows] if rows else []  # type: ignore
        except sqlite3.Error:
            logger.exception("Query parsing error", stack_info=True)
            # On error, return all songs (or could return empty list)
            return self.find_many()

    def update_song_playcount(self, song_id):
        """Update a song's play count and last played timestamp."""
        self.conn.execute(
            """
            UPDATE songs
            SET app_data = json_set(app_data, '$.play_count', json_extract(app_data, '$.play_count') + 1)
            WHERE id = ?
        """,
            (datetime.now(), song_id),
        )
        self.conn.commit()
