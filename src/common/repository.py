# src.common.repository
import sqlite3
import logging
import json
from typing import Generic, TypeVar, Any, Type, cast
from pydantic import BaseModel

# Generic type for Pydantic models
T = TypeVar("T", bound=BaseModel)

logger = logging.getLogger(__name__)


class DatabaseRepository(Generic[T]):
    """Base repository for SQLite database operations."""

    def __init__(self, conn: sqlite3.Connection, model_class: Type[T], table_name: str):
        self.conn = conn
        self.model_class = model_class
        self.table_name = table_name
        self.logger = logging.getLogger(f"{__name__}.{table_name}")
        self.logger.debug(f"Repository initialized for table: {table_name}")

    def _execute_query(self, query: str, params: tuple = ()) -> int | None:
        """Executes a SQL query that doesn't return rows (e.g., INSERT, UPDATE, DELETE)."""
        try:
            with self.conn:  # Use a context manager for transactions
                cursor = self.conn.cursor()
                cursor.execute(query, params)
                return cursor.lastrowid  # Return the ID of last insert
        except sqlite3.Error as e:
            self.logger.error(
                f"Error executing query: {query} with params {params}: {e}",
                exc_info=True,
            )
            raise

    def _execute_select_query(
        self, query: str, params: tuple = (), fetchone=False
    ) -> sqlite3.Row | list[sqlite3.Row] | None:
        """Executes a SQL query that returns rows (SELECT)."""
        try:
            with self.conn:
                cursor = self.conn.cursor()
                cursor.execute(query, params)
                if fetchone:
                    return cursor.fetchone()
                else:
                    return cursor.fetchall()
        except sqlite3.Error as e:
            self.logger.error(
                f"Error executing query: {query} with params {params}: {e}",
                exc_info=True,
            )
            raise

    def _row_to_model(self, row: sqlite3.Row) -> T:
        """Converts a database row to a Pydantic model instance."""
        row_dict = dict(row)  # Convert sqlite3.Row to a dictionary
        for key in ("fileprops", "tags", "tags_lower", "app_data", "raw_metadata"):
            if key in row_dict and row_dict[key] is not None:
                row_dict[key] = json.loads(row_dict[key])
        return self.model_class.model_validate(row_dict)

    def find_by_id(self, id: int) -> T | None:
        query = f"SELECT * FROM {self.table_name} WHERE id = ?"
        row = self._execute_select_query(query, (id,), fetchone=True)
        return self._row_to_model(row) if row else None  # type: ignore

    def find_one(self, query_dict: dict[str, Any]) -> T | None:
        """Finds a single record matching criteria.  Simplified for SQLite."""
        where_clauses = " AND ".join(f"{key} = ?" for key in query_dict)
        query = f"SELECT * FROM {self.table_name} WHERE {where_clauses} LIMIT 1"
        params = tuple(query_dict.values())
        row = self._execute_select_query(query, params, fetchone=True)
        return self._row_to_model(row) if row else None  # type: ignore

    def find_many(
        self,
        query_dict: dict[str, Any] | None = None,
        sort: list[tuple] | None = None,
        limit: int | None = None,
        skip: int | None = None,
    ) -> list[T]:
        """Finds multiple records matching criteria, with sorting, limit, and skip."""
        query = f"SELECT * FROM {self.table_name}"
        params: list[Any] = []

        if query_dict:
            where_clauses = " AND ".join(f"{key} = ?" for key in query_dict)
            query += f" WHERE {where_clauses}"
            params.extend(query_dict.values())

        if sort:
            # assuming (field, "ASC" or "DESC") tuples,
            # todo: dedicated type
            sort_clauses = ", ".join(
                f"{field} {direction}" for field, direction in sort
            )
            query += f" ORDER BY {sort_clauses}"

        if limit is not None:
            query += " LIMIT ?"
            params.append(limit)

        if skip is not None:
            query += " OFFSET ?"
            params.append(skip)

        rows = self._execute_select_query(query, tuple(params))  # Use the select query
        return [self._row_to_model(row) for row in rows] if rows else []  # type: ignore

    def count(self, query_dict: dict[str, Any] | None = None) -> int:
        query = f"SELECT COUNT(*) FROM {self.table_name}"
        params: list[Any] = []
        if query_dict:
            where_clauses = " AND ".join(f"{key} = ?" for key in query_dict)
            query += f" WHERE {where_clauses}"
            params.extend(query_dict.values())

        row = self._execute_select_query(query, tuple(params), fetchone=True)
        return cast(int, row[0]) if row else 0

    def insert(self, model: T) -> int | None:
        """Inserts a new record."""
        data = model.model_dump(exclude={"id"})  # Exclude auto-incrementing ID

        # Serialize JSON fields
        for key in ("fileprops", "tags", "tags_lower", "app_data", "raw_metadata"):
            if key in data and data[key] is not None:
                data[key] = json.dumps(data[key])

        fields = ", ".join(data.keys())
        placeholders = ", ".join("?" * len(data))
        query = f"INSERT INTO {self.table_name} ({fields}) VALUES ({placeholders})"
        last_row_id = self._execute_query(query, tuple(data.values()))
        return last_row_id

    def update(self, id: int, model: T) -> bool:
        """Updates an existing record by ID."""
        data = model.model_dump(exclude={"id"})

        # Serialize JSON fields
        for key in ("fileprops", "tags", "tags_lower", "app_data", "raw_metadata"):
            if key in data and data[key] is not None:
                data[key] = json.dumps(data[key])

        set_clauses = ", ".join(f"{key} = ?" for key in data)
        query = f"UPDATE {self.table_name} SET {set_clauses} WHERE id = ?"
        params = tuple(data.values()) + (id,)
        self._execute_query(query, params)
        return True  # SQLite doesn't easily give us rows affected

    def upsert(self, query_dict: dict[str, Any], model: T) -> int | None:
        """Updates if exists or inserts if not."""
        existing_record = self.find_one(query_dict)
        if existing_record:
            self.update(existing_record.id, model)  # type: ignore
            return existing_record.id  # type: ignore
        else:
            return self.insert(model)

    def delete(self, id: int) -> bool:
        """Deletes a record by ID."""
        query = f"DELETE FROM {self.table_name} WHERE id = ?"
        self._execute_query(query, (id,))
        return True  # SQLite doesn't easily give us rows affected

    def delete_many(self, query_dict: dict[str, Any]) -> int:
        """Deletes multiple records matching criteria."""
        where_clauses = " AND ".join(f"{key} = ?" for key in query_dict)
        query = f"DELETE FROM {self.table_name} WHERE {where_clauses}"
        params = tuple(query_dict.values())
        self._execute_query(query, params)
        return 0  #  # SQLite doesn't easily give us rows affected

    def aggregate(self, pipeline: list[dict[str, Any]]):
        """Not implemented for SQLite repository."""
        raise NotImplementedError("Aggregation not implemented for SQLite")
