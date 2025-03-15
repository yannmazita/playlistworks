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
                logger.exception(e, stack_info=True)
                return False

        conn.create_function("REGEXP", 2, regexp_function)
        logger.info(f"Connected to SQLite database: {settings.database_filename}")
        return conn
    except sqlite3.Error as e:
        logger.exception(e, stack_info=True)
        raise


def initialize_database(conn: sqlite3.Connection):
    """Initializes the database (creates tables and indexes)."""
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS songs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                path TEXT UNIQUE NOT NULL,
                fileprops TEXT NOT NULL,
                tags TEXT NOT NULL,
                app_data TEXT NOT NULL
            )
        """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS playlists (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                description TEXT,
                query TEXT,
                is_dynamic BOOLEAN NOT NULL
            )
        """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS playlist_songs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                playlist_id INTEGER,
                song_id INTEGER,
                query TEXT,
                is_dynamic BOOLEAN NOT NULL,
                FOREIGN KEY (playlist_id) REFERENCES playlists(id),
                FOREIGN KEY (song_id) REFERENCES songs(id)
            )
        """
        )

        cursor.execute("CREATE INDEX IF NOT EXISTS idx_path ON songs (path)")
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_tags_artist ON songs (json_extract(tags, '$.ARTIST'))"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_tags_artistsort ON songs (json_extract(tags, '$.ARTIST_SORT'))"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_tags_album ON songs (json_extract(tags, '$.ALBUM'))"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_tags_albumartistsort ON songs (json_extract(tags, '$.ALBUM_ARTIST_SORT'))"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_tags_title ON songs (json_extract(tags, '$.TITLE'))"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_tags_genre ON songs (json_extract(tags, '$.GENRE'))"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_app_data_play_count ON songs (json_extract(app_data, '$.play_count'))"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_app_data_last_played ON songs (json_extract(app_data, '$.last_played'))"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_app_data_rating ON songs (json_extract(app_data, '$.rating'))"
        )

        conn.commit()
        logger.info("Database initialized successfully.")
    except sqlite3.Error as e:
        logger.exception(e, stack_info=True)
        conn.rollback()
        raise


def close_db_connection(conn: sqlite3.Connection):
    if conn:
        conn.close()
        logger.info("Database connection closed.")
