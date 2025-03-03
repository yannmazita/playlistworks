# src.common.test_database
import re
import sqlite3
import pytest
from unittest.mock import patch
from src.common.database import (
    get_db_connection,
    initialize_database,
    close_db_connection,
)


@pytest.fixture
def mock_settings():
    with patch("src.common.database.settings") as mock_settings:
        mock_settings.database_filename = ":memory:"
        yield mock_settings


@pytest.fixture
def db_connection():
    """Create an in-memory SQLite database connection."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.create_function(
        "REGEXP", 2, lambda x, y: re.search(y, x, re.IGNORECASE) is not None
    )
    yield conn
    if conn:
        conn.close()


def test_get_db_connection():
    """Test that get_db_connection returns a valid SQLite connection."""
    conn = get_db_connection()

    # Test connection is valid
    assert conn is not None
    assert isinstance(conn, sqlite3.Connection)

    # Test row_factory is set to sqlite3.Row
    assert conn.row_factory == sqlite3.Row

    # Test REGEXP function - drop the table first if it exists
    conn.execute("DROP TABLE IF EXISTS test_regexp")
    conn.execute("CREATE TABLE test_regexp (value TEXT)")
    conn.execute("INSERT INTO test_regexp VALUES ('Hello World')")
    conn.execute("INSERT INTO test_regexp VALUES ('Goodbye')")

    cursor = conn.execute("SELECT * FROM test_regexp WHERE value REGEXP ?", ("world",))
    results = cursor.fetchall()
    assert len(results) == 1
    assert results[0]["value"] == "Hello World"

    conn.close()


def test_get_db_connection_error():
    """Test that get_db_connection handles errors properly."""
    with patch("src.common.database.settings") as mock_settings:
        # Set an invalid database path to force an error
        mock_settings.database_filename = "/nonexistent/directory/db.sqlite"

        with patch("src.common.database.logger") as mock_logger:
            with pytest.raises(sqlite3.Error):
                get_db_connection()

            mock_logger.exception.assert_called_once()


def test_initialize_database(db_connection):
    """Test that initialize_database creates the expected tables and indexes."""
    initialize_database(db_connection)

    # Get a list of all tables
    cursor = db_connection.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row["name"] for row in cursor.fetchall()]

    # Verify tables exist
    assert "tracks" in tables
    assert "playlists" in tables

    # Check tracks table schema
    cursor = db_connection.execute("PRAGMA table_info(tracks)")
    columns = {row["name"]: row for row in cursor.fetchall()}

    assert "id" in columns
    assert "path" in columns
    assert "fileprops" in columns
    assert "tags" in columns
    assert "tags_lower" in columns
    assert "app_data" in columns
    assert "raw_metadata" in columns

    # Check constraints
    assert columns["id"]["pk"] == 1  # Primary key
    assert columns["path"]["notnull"] == 1  # NOT NULL

    # Check playlists table schema
    cursor = db_connection.execute("PRAGMA table_info(playlists)")
    columns = {row["name"]: row for row in cursor.fetchall()}

    assert "id" in columns
    assert "name" in columns
    assert "description" in columns
    assert "query" in columns
    assert "playlist_type" in columns

    # Check indexes
    cursor = db_connection.execute("SELECT name FROM sqlite_master WHERE type='index'")
    indexes = [row["name"] for row in cursor.fetchall()]

    assert "idx_path" in indexes
    assert "idx_tags_lower_artist" in indexes
    assert "idx_tags_lower_album" in indexes
    assert "idx_tags_lower_title" in indexes
    assert "idx_app_data_rating" in indexes


def test_close_db_connection():
    """Test that close_db_connection properly closes a connection."""
    conn = sqlite3.connect(":memory:")

    assert conn is not None

    with patch("src.common.database.logger") as mock_logger:
        close_db_connection(conn)

        with pytest.raises(sqlite3.ProgrammingError):
            conn.execute("SELECT 1")

        mock_logger.info.assert_called_once()


def test_close_db_connection_none():
    """Test that close_db_connection safely handles None connections."""
    with patch("src.common.database.logger") as mock_logger:
        conn = None
        close_db_connection(conn)

        # No info log should be called since there was no connection
        mock_logger.info.assert_not_called()
