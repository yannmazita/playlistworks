# src.common.database
import re
import sqlite3
import logging
from src.common.utils.settings import settings

logger = logging.getLogger(__name__)


def get_db_connection() -> sqlite3.Connection:
    """Creates a database connection to the SQLite database."""
    try:
        conn = sqlite3.connect(settings.database_filename)
        conn.row_factory = (
            sqlite3.Row
        )  # SQLite returns results as Row objects with named-field access

        def regexp_function(pattern, text):
            if text is None or pattern is None:
                return False
            try:
                return re.search(pattern, text, re.IGNORECASE) is not None
            except Exception as e:
                logger.error(f"REGEXP error: {e}, pattern={pattern}, text={text}")
                return False

        conn.create_function("REGEXP", 2, regexp_function)
        logger.info(f"Connected to SQLite database: {settings.database_filename}")
        return conn
    except sqlite3.Error as e:
        logger.error(f"Error connecting to database: {e}", exc_info=True)
        raise


def initialize_database(conn: sqlite3.Connection):
    """Initializes the database (creates tables and indexes)."""
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS tracks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                path TEXT UNIQUE NOT NULL,
                fileprops TEXT NOT NULL,
                tags TEXT NOT NULL,
                app_data TEXT NOT NULL,
                raw_metadata TEXT
            )
        """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS playlists (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT DEFAULT '',
                query TEXT DEFAULT '',
                playlist_type TEXT NOT NULL CHECK(playlist_type IN ('static', 'dynamic'))
            )
        """
        )

        cursor.execute("CREATE INDEX IF NOT EXISTS idx_path ON tracks (path)")
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_tags_artist ON tracks (json_extract(tags, '$.ARTIST'))"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_tags_artistsort ON tracks (json_extract(tags, '$.ARTIST_SORT'))"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_tags_album ON tracks (json_extract(tags, '$.ALBUM'))"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_tags_albumartistsort ON tracks (json_extract(tags, '$.ALBUM_ARTIST_SORT'))"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_tags_title ON tracks (json_extract(tags, '$.TITLE'))"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_tags_genre ON tracks (json_extract(tags, '$.GENRE'))"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_app_data_play_count ON tracks (json_extract(app_data, '$.play_count'))"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_app_data_last_played ON tracks (json_extract(app_data, '$.last_played'))"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_app_data_rating ON tracks (json_extract(app_data, '$.rating'))"
        )

        conn.commit()
        logger.info("Database initialized successfully.")
    except sqlite3.Error as e:
        logger.error(f"Error initializing database: {e}", exc_info=True)
        conn.rollback()
        raise


def close_db_connection(conn: sqlite3.Connection):
    if conn:
        conn.close()
        logger.info("Database connection closed.")
