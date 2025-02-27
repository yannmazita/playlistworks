# src.features.playlists.test_repository
import re
import sqlite3
import pytest
from src.features.playlists.repository import PlaylistsRepository
from src.features.playlists.schemas import Playlist
from src.common.database import initialize_database


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
def playlist_repository(db_connection):
    return PlaylistsRepository(db_connection)


def test_insert_playlist(playlist_repository):
    playlist = Playlist(
        name="My Playlist", description="Test description", playlist_type="static"
    )
    playlist_id = playlist_repository.insert(playlist)
    assert playlist_id == 1

    retrieved_playlist = playlist_repository.find_by_id(playlist_id)
    assert retrieved_playlist is not None
    assert retrieved_playlist.name == "My Playlist"
    assert retrieved_playlist.description == "Test description"
    assert retrieved_playlist.playlist_type == "static"
    assert retrieved_playlist.query == ""  # Default value


def test_find_playlist_by_id(playlist_repository):
    playlist = Playlist(name="Test Playlist", playlist_type="dynamic", query=".*")
    playlist_id = playlist_repository.insert(playlist)

    retrieved_playlist = playlist_repository.find_by_id(playlist_id)
    assert retrieved_playlist is not None
    assert retrieved_playlist.id == playlist_id
    assert retrieved_playlist.name == "Test Playlist"

    non_existent_playlist = playlist_repository.find_by_id(999)
    assert non_existent_playlist is None


def test_update_playlist(playlist_repository):
    playlist = Playlist(
        name="Initial Name", description="Initial Desc", playlist_type="static"
    )
    playlist_id = playlist_repository.insert(playlist)

    updated_playlist = Playlist(
        name="Updated Name",
        description="Updated Desc",
        playlist_type="dynamic",
        query="new_query",
    )
    playlist_repository.update(playlist_id, updated_playlist)

    retrieved_playlist = playlist_repository.find_by_id(playlist_id)
    assert retrieved_playlist is not None
    assert retrieved_playlist.name == "Updated Name"
    assert retrieved_playlist.description == "Updated Desc"
    assert retrieved_playlist.playlist_type == "dynamic"
    assert retrieved_playlist.query == "new_query"


def test_delete_playlist(playlist_repository):
    playlist = Playlist(name="To be deleted", playlist_type="static")
    playlist_id = playlist_repository.insert(playlist)

    playlist_repository.delete(playlist_id)
    retrieved_playlist = playlist_repository.find_by_id(playlist_id)
    assert retrieved_playlist is None


def test_find_one(playlist_repository):
    playlist1 = Playlist(name="Playlist 1", playlist_type="static")
    playlist2 = Playlist(name="Playlist 2", playlist_type="dynamic", query=".*")
    playlist_repository.insert(playlist1)
    playlist_repository.insert(playlist2)

    retrieved_playlist = playlist_repository.find_one({"name": "Playlist 1"})
    assert retrieved_playlist is not None
    assert retrieved_playlist.name == "Playlist 1"

    retrieved_playlist = playlist_repository.find_one({"playlist_type": "dynamic"})
    assert retrieved_playlist is not None
    assert retrieved_playlist.name == "Playlist 2"  # Assuming insertion order

    non_existent_playlist = playlist_repository.find_one({"name": "Nonexistent"})
    assert non_existent_playlist is None


def test_find_many(playlist_repository):
    playlist1 = Playlist(name="Playlist A", playlist_type="static")
    playlist2 = Playlist(name="Playlist B", playlist_type="dynamic", query=".*")
    playlist3 = Playlist(name="Playlist C", playlist_type="static")
    playlist_repository.insert(playlist1)
    playlist_repository.insert(playlist2)
    playlist_repository.insert(playlist3)

    # Find all static playlists
    static_playlists = playlist_repository.find_many({"playlist_type": "static"})
    assert len(static_playlists) == 2
    assert {p.name for p in static_playlists} == {"Playlist A", "Playlist C"}

    # Find with sorting
    sorted_playlists = playlist_repository.find_many(sort=[("name", "ASC")])
    assert [p.name for p in sorted_playlists] == [
        "Playlist A",
        "Playlist B",
        "Playlist C",
    ]

    sorted_playlists_desc = playlist_repository.find_many(sort=[("name", "DESC")])
    assert [p.name for p in sorted_playlists_desc] == [
        "Playlist C",
        "Playlist B",
        "Playlist A",
    ]

    # Find with limit and skip
    limited_playlists = playlist_repository.find_many(limit=1, skip=1)
    assert len(limited_playlists) == 1
    assert limited_playlists[0].name == "Playlist B"  # Assuming insertion order


def test_count(playlist_repository):
    playlist1 = Playlist(name="Playlist X", playlist_type="static")
    playlist2 = Playlist(name="Playlist Y", playlist_type="dynamic", query=".*")
    playlist3 = Playlist(name="Playlist Z", playlist_type="static")
    playlist_repository.insert(playlist1)
    playlist_repository.insert(playlist2)
    playlist_repository.insert(playlist3)

    count_all = playlist_repository.count()
    assert count_all == 3

    count_static = playlist_repository.count({"playlist_type": "static"})
    assert count_static == 2

    count_nonexistent = playlist_repository.count({"name": "Nonexistent"})
    assert count_nonexistent == 0


def test_upsert(playlist_repository):
    # Test insert
    playlist = Playlist(name="Upsert Test 1", playlist_type="static")
    playlist_id = playlist_repository.upsert({"name": "Upsert Test 1"}, playlist)
    assert playlist_id == 1
    retrieved_playlist = playlist_repository.find_by_id(playlist_id)
    assert retrieved_playlist.name == "Upsert Test 1"

    # Test update
    updated_playlist = Playlist(
        name="Upsert Test 1", description="Updated", playlist_type="dynamic", query=".*"
    )
    updated_id = playlist_repository.upsert({"name": "Upsert Test 1"}, updated_playlist)
    assert updated_id == 1  # Should return the same ID
    retrieved_updated_playlist = playlist_repository.find_by_id(updated_id)
    assert retrieved_updated_playlist.description == "Updated"
    assert retrieved_updated_playlist.playlist_type == "dynamic"


def test_delete_many(playlist_repository):
    playlist1 = Playlist(name="Delete Many 1", playlist_type="static")
    playlist2 = Playlist(name="Delete Many 2", playlist_type="dynamic")
    playlist3 = Playlist(name="Delete Many 3", playlist_type="static")
    playlist_repository.insert(playlist1)
    playlist_repository.insert(playlist2)
    playlist_repository.insert(playlist3)

    playlist_repository.delete_many({"playlist_type": "static"})
    remaining_playlists = playlist_repository.find_many()
    assert len(remaining_playlists) == 1
    assert remaining_playlists[0].name == "Delete Many 2"
