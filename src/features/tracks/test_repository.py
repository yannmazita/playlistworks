# src.features.tracks.test_repository
import re
import sqlite3
import pytest
from src.common.database import initialize_database
from src.features.tracks.repository import TracksRepository
from src.features.tracks.schemas import Track


@pytest.fixture(scope="function")
def db_connection():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row

    def regexp_function(pattern, text):
        if text is None or pattern is None:
            return False
        try:
            return re.search(pattern, text, re.IGNORECASE) is not None
        except Exception:
            return False

    conn.create_function("REGEXP", 2, regexp_function)

    initialize_database(conn)
    yield conn
    conn.close()


@pytest.fixture(scope="function")
def track_repository(db_connection):
    return TracksRepository(db_connection)


def test_insert_track(track_repository):
    pass


def test_find_track_by_id(track_repository):
    pass


def test_update_track(track_repository):
    pass


def test_delete_playlist(track_repository):
    pass


def test_find_one(track_repository):
    pass


def test_find_many(track_repository):
    pass


def test_count(track_repository):
    pass


def test_upsert(track_repository):
    pass


def test_delete_many(track_repository):
    pass
