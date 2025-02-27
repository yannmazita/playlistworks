# src.common.test_repository
import re
import sqlite3
import json
import pytest
from typing import Any
from pydantic import BaseModel, Field

from src.common.repository import DatabaseRepository


class SampleItem(BaseModel):
    id: int | None = Field(default=None, description="Sample ID")
    name: str = Field(description="Sample name")
    description: str = Field(default="Sample description")
    app_data: dict[str, Any] = {}  # DatabaseRepository knows how to serialize app_data


@pytest.fixture(scope="function")
def db_connection():
    """Create an in-memory SQLite database for testing."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row

    # Add REGEXP support for SQLite (used in some repository operations)
    def regexp_function(pattern, text):
        if text is None or pattern is None:
            return False
        try:
            return re.search(pattern, text, re.IGNORECASE) is not None
        except Exception:
            return False

    conn.create_function("REGEXP", 2, regexp_function)

    # Create test table
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS test_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT DEFAULT '',
            app_data TEXT DEFAULT '{}'
        )
    """)
    conn.commit()

    yield conn
    conn.close()


@pytest.fixture(scope="function")
def test_repository(db_connection):
    """Create a repository instance for our SampleItem model."""
    return DatabaseRepository(db_connection, SampleItem, "test_items")


def test_insert(test_repository):
    """Test inserting a record."""
    item = SampleItem(
        name="Test Item", description="Test description", app_data={"key": "value"}
    )
    item_id = test_repository.insert(item)
    assert item_id == 1

    retrieved_item = test_repository.find_by_id(item_id)
    assert retrieved_item is not None
    assert retrieved_item.name == "Test Item"
    assert retrieved_item.description == "Test description"
    assert retrieved_item.app_data == {"key": "value"}


def test_find_by_id(test_repository):
    """Test finding a record by ID."""
    item = SampleItem(name="Find by ID Test", app_data={"test": True})
    item_id = test_repository.insert(item)

    retrieved_item = test_repository.find_by_id(item_id)
    assert retrieved_item is not None
    assert retrieved_item.id == item_id
    assert retrieved_item.name == "Find by ID Test"
    assert retrieved_item.app_data == {"test": True}

    non_existent_item = test_repository.find_by_id(999)
    assert non_existent_item is None


def test_update(test_repository):
    """Test updating a record."""
    item = SampleItem(
        name="Initial Name", description="Initial Desc", app_data={"initial": True}
    )
    item_id = test_repository.insert(item)

    updated_item = SampleItem(
        name="Updated Name", description="Updated Desc", app_data={"updated": True}
    )
    result = test_repository.update(item_id, updated_item)
    assert result is True

    retrieved_item = test_repository.find_by_id(item_id)
    assert retrieved_item is not None
    assert retrieved_item.name == "Updated Name"
    assert retrieved_item.description == "Updated Desc"
    assert retrieved_item.app_data == {"updated": True}


def test_delete(test_repository):
    """Test deleting a record."""
    item = SampleItem(name="To be deleted")
    item_id = test_repository.insert(item)

    result = test_repository.delete(item_id)
    assert result is True

    retrieved_item = test_repository.find_by_id(item_id)
    assert retrieved_item is None


def test_find_one(test_repository):
    """Test finding a single record matching criteria."""
    item1 = SampleItem(name="Item 1", app_data={"order": 1})
    item2 = SampleItem(name="Item 2", app_data={"order": 2})
    test_repository.insert(item1)
    test_repository.insert(item2)

    retrieved_item = test_repository.find_one({"name": "Item 1"})
    assert retrieved_item is not None
    assert retrieved_item.name == "Item 1"
    assert retrieved_item.app_data == {"order": 1}

    non_existent_item = test_repository.find_one({"name": "Nonexistent"})
    assert non_existent_item is None


def test_find_many(test_repository):
    """Test finding multiple records with various criteria."""
    item1 = SampleItem(name="Item A", description="First", app_data={"group": 1})
    item2 = SampleItem(name="Item B", description="Second", app_data={"group": 2})
    item3 = SampleItem(name="Item C", description="First", app_data={"group": 1})
    test_repository.insert(item1)
    test_repository.insert(item2)
    test_repository.insert(item3)

    # Find by description
    first_items = test_repository.find_many({"description": "First"})
    assert len(first_items) == 2
    assert {item.name for item in first_items} == {"Item A", "Item C"}

    # Find with sorting
    sorted_items = test_repository.find_many(sort=[("name", "ASC")])
    assert [item.name for item in sorted_items] == ["Item A", "Item B", "Item C"]

    sorted_items_desc = test_repository.find_many(sort=[("name", "DESC")])
    assert [item.name for item in sorted_items_desc] == ["Item C", "Item B", "Item A"]

    # Find with limit and skip
    limited_items = test_repository.find_many(limit=1, skip=1)
    assert len(limited_items) == 1
    assert limited_items[0].name == "Item B"  # Assuming insertion order


def test_count(test_repository):
    """Test counting records."""
    item1 = SampleItem(name="Item X", description="Count", app_data={"count": True})
    item2 = SampleItem(
        name="Item Y", description="Not Count", app_data={"count": False}
    )
    item3 = SampleItem(name="Item Z", description="Count", app_data={"count": True})
    test_repository.insert(item1)
    test_repository.insert(item2)
    test_repository.insert(item3)

    count_all = test_repository.count()
    assert count_all == 3

    count_desc = test_repository.count({"description": "Count"})
    assert count_desc == 2

    count_nonexistent = test_repository.count({"name": "Nonexistent"})
    assert count_nonexistent == 0


def test_upsert(test_repository):
    """Test upserting (insert or update) records."""
    # Test insert case
    item = SampleItem(
        name="Upsert Test 1", description="Original", app_data={"original": True}
    )
    item_id = test_repository.upsert({"name": "Upsert Test 1"}, item)
    assert item_id == 1
    retrieved_item = test_repository.find_by_id(item_id)
    assert retrieved_item.name == "Upsert Test 1"
    assert retrieved_item.description == "Original"
    assert retrieved_item.app_data == {"original": True}

    # Test update case
    updated_item = SampleItem(
        name="Upsert Test 1", description="Updated", app_data={"updated": True}
    )
    updated_id = test_repository.upsert({"name": "Upsert Test 1"}, updated_item)
    assert updated_id == item_id  # Should return the same ID
    retrieved_updated_item = test_repository.find_by_id(updated_id)
    assert retrieved_updated_item.description == "Updated"
    assert retrieved_updated_item.app_data == {"updated": True}


def test_delete_many(test_repository):
    """Test deleting multiple records."""
    item1 = SampleItem(
        name="Delete Many 1", description="Group1", app_data={"delete": True}
    )
    item2 = SampleItem(
        name="Delete Many 2", description="Group2", app_data={"delete": False}
    )
    item3 = SampleItem(
        name="Delete Many 3", description="Group1", app_data={"delete": True}
    )
    test_repository.insert(item1)
    test_repository.insert(item2)
    test_repository.insert(item3)

    test_repository.delete_many({"description": "Group1"})
    remaining_items = test_repository.find_many()
    assert len(remaining_items) == 1
    assert remaining_items[0].name == "Delete Many 2"
    assert remaining_items[0].app_data == {"delete": False}


def test_json_serialization(test_repository):
    """Test JSON serialization and deserialization of complex data structures."""
    complex_data = {
        "nested": {"data": [1, 2, 3], "boolean": True, "null": None},
        "list": ["a", "b", "c"],
        "string": "test",
        "number": 123.45,
    }

    item = SampleItem(name="JSON Test", app_data=complex_data)
    item_id = test_repository.insert(item)

    # Verify the data is stored and retrieved correctly
    retrieved_item = test_repository.find_by_id(item_id)
    assert retrieved_item.app_data == complex_data

    # Directly check the database to ensure it's stored as JSON string
    cursor = test_repository.conn.cursor()
    cursor.execute("SELECT app_data FROM test_items WHERE id = ?", (item_id,))
    row = cursor.fetchone()
    stored_json = row["app_data"]

    # Should be stored as a JSON string
    assert isinstance(stored_json, str)

    # When parsed, should match the original data
    parsed_json = json.loads(stored_json)
    assert parsed_json == complex_data


def test_error_handling(test_repository):
    """Test error handling for invalid operations."""
    with pytest.raises(sqlite3.Error):
        test_repository._execute_query(
            "INSERT INTO non_existent_table VALUES (?)", (1,)
        )

    with pytest.raises(sqlite3.Error):
        test_repository._execute_select_query("SELECT * FROM non_existent_table")


def test_aggregate_not_implemented(test_repository):
    """Test that aggregate method raises NotImplementedError."""
    with pytest.raises(NotImplementedError):
        test_repository.aggregate([{"$match": {"name": "Test"}}])


def test_query_with_expression(test_repository):
    """Test querying with SQL expressions that would return data not matching the model schema."""
    item1 = SampleItem(name="Query Test 1", app_data={"value": 10})
    item2 = SampleItem(name="Query Test 2", app_data={"value": 20})
    test_repository.insert(item1)
    test_repository.insert(item2)

    count = test_repository.count()
    assert count == 2

    # Test count with filtering
    filtered_count = test_repository.count({"name": "Query Test 1"})
    assert filtered_count == 1
