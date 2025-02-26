# src.common.repository
from typing import Generic, TypeVar, Any, Type
from pydantic import BaseModel
from pymongo.collection import Collection
from bson import ObjectId
import logging

# Generic type for Pydantic models
T = TypeVar("T", bound=BaseModel)


class BaseRepository(Generic[T]):
    """
    Base repository providing common operations for MongoDB collections.

    Attributes:
        T: Must be a Pydantic BaseModel.
    """

    def __init__(self, collection: Collection, model_class: Type[T]):
        """
        Initialize the repository with a MongoDB collection and a Pydantic model class.

        Args:
            collection: MongoDB collection
            model_class: Pydantic model class for this repository
        """
        self.collection = collection
        self.model_class = model_class
        self.logger = logging.getLogger(f"{__name__}.{collection.name}")
        self.logger.debug(f"Repository initialized for collection: {collection.name}")

    def find_by_id(self, id: str) -> T | None:
        """
        Find a document by its ID.

        Args:
            id: The ID of the document to find.

        Returns:
            The found document as a Pydantic model, or None if not found.
        """
        self.logger.debug(f"Attempting to find document by ID: {id}")
        try:
            doc = self.collection.find_one({"_id": ObjectId(id)})
            if doc:
                validated_doc = self.model_class.model_validate(doc)
                self.logger.info(f"Found document with ID: {id}")
                return validated_doc
            else:
                self.logger.info(f"Document with ID {id} not found.")
                return None
        except Exception as e:
            self.logger.error(
                f"Error finding document by ID: {id}, Error: {e}", exc_info=True
            )
            return None

    def find_one(self, query: dict[str, Any]) -> T | None:
        """
        Find a single document matching the query.

        Args:
            query: A dictionary representing the MongoDB query.

        Returns:
            The found document as a Pydantic model, or None if not found.
        """
        self.logger.debug(f"Attempting to find one document with query: {query}")
        try:
            doc = self.collection.find_one(query)
            if doc:
                validated_doc = self.model_class.model_validate(doc)
                self.logger.info(f"Found document with query: {query}")
                return validated_doc
            else:
                self.logger.info(f"No document found with query: {query}")
                return None
        except Exception as e:
            self.logger.error(
                f"Error finding document with query: {query}, Error: {e}", exc_info=True
            )
            return None

    def find_many(
        self,
        query: dict[str, Any],
        sort: list[tuple] | None = None,
        limit: int | None = None,
        skip: int | None = None,
    ) -> list[T]:
        """
        Find all documents matching the query with optional sorting and pagination.

        Args:
            query: MongoDB query dict.
            sort: list of (field, direction) tuples for sorting.
            limit: Maximum number of documents to return.
            skip: Number of documents to skip.

        Returns:
            list of model instances.
        """
        self.logger.debug(
            f"Attempting to find many documents with query: {query}, sort: {sort}, limit: {limit}, skip: {skip}"
        )
        try:
            cursor = self.collection.find(query)

            if sort:
                cursor = cursor.sort(sort)

            if skip:
                cursor = cursor.skip(skip)

            if limit:
                cursor = cursor.limit(limit)

            validated_docs = [self.model_class.model_validate(doc) for doc in cursor]
            self.logger.info(
                f"Found {len(validated_docs)} documents with query: {query}"
            )
            return validated_docs
        except Exception as e:
            self.logger.error(
                f"Error finding documents with query: {query}, Error: {e}",
                exc_info=True,
            )
            return []

    def count(self, query: dict[str, Any]) -> int:
        """
        Count documents matching the query.

        Args:
            query: A dictionary representing the MongoDB query.

        Returns:
            The number of documents matching the query.
        """
        self.logger.debug(f"Attempting to count documents with query: {query}")
        try:
            count = self.collection.count_documents(query)
            self.logger.info(f"Counted {count} documents with query: {query}")
            return count
        except Exception as e:
            self.logger.error(
                f"Error counting documents with query: {query}, Error: {e}",
                exc_info=True,
            )
            return 0

    def insert(self, model: T) -> str | None:
        """
        Insert a new document and return its ID.

        Args:
            model: The Pydantic model instance to insert.

        Returns:
            The ID of the inserted document as a string, or None on failure.
        """
        self.logger.debug(f"Attempting to insert document: {model}")
        try:
            data = model.model_dump(exclude={"id"})
            result = self.collection.insert_one(data)
            inserted_id = str(result.inserted_id)
            self.logger.info(f"Inserted document with ID: {inserted_id}")
            return inserted_id
        except Exception as e:
            self.logger.error(
                f"Error inserting document: {model}, Error: {e}", exc_info=True
            )
            return None

    def update(self, id: str, model: T) -> bool:
        """
        Update an existing document by ID.

        Args:
            id: The ID of the document to update.
            model: The Pydantic model instance containing the updated data.

        Returns:
            True if the document was updated, False otherwise.
        """
        self.logger.debug(f"Attempting to update document with ID: {id}, Data: {model}")
        try:
            data = model.model_dump(exclude={"id"})
            result = self.collection.replace_one({"_id": ObjectId(id)}, data)
            if result.modified_count > 0:
                self.logger.info(f"Updated document with ID: {id}")
                return True
            else:
                self.logger.info(f"Document with ID {id} not found for update.")
                return False
        except Exception as e:
            self.logger.error(
                f"Error updating document with ID: {id}, Error: {e}", exc_info=True
            )
            return False

    def upsert(self, query: dict[str, Any], model: T) -> bool:
        """
        Update if exists or insert if not.

        Args:
            query:  The filter to find the document to update.  If no documents match, insert the update as a new document.
            model: The Pydantic model instance containing the updated or new data.

        Returns:
            True if a document was updated or inserted, False otherwise.
        """
        self.logger.debug(
            f"Attempting to upsert document with query: {query}, Data: {model}"
        )
        try:
            data = model.model_dump(exclude={"id"})
            result = self.collection.replace_one(query, data, upsert=True)
            if result.modified_count > 0:
                self.logger.info(f"Upserted (updated) document with query: {query}")
            elif result.upserted_id is not None:
                self.logger.info(
                    f"Upserted (inserted) document with ID: {result.upserted_id} and query: {query}"
                )
            return result.modified_count > 0 or result.upserted_id is not None
        except Exception as e:
            self.logger.error(
                f"Error upserting document with query: {query}, Error: {e}",
                exc_info=True,
            )
            return False

    def delete(self, id: str) -> bool:
        """
        Delete a document by ID.

        Args:
            id: The ID of the document to delete.

        Returns:
            True if the document was deleted, False otherwise.
        """
        self.logger.debug(f"Attempting to delete document with ID: {id}")
        try:
            result = self.collection.delete_one({"_id": ObjectId(id)})
            if result.deleted_count > 0:
                self.logger.info(f"Deleted document with ID: {id}")
                return True
            else:
                self.logger.info(f"Document with ID {id} not found for deletion.")
                return False

        except Exception as e:
            self.logger.error(
                f"Error deleting document with ID: {id}, Error: {e}", exc_info=True
            )
            return False

    def delete_many(self, query: dict[str, Any]) -> int:
        """
        Delete all documents matching the query and return count.

        Args:
            query: A dictionary representing the MongoDB query.

        Returns:
            The number of documents deleted.
        """
        self.logger.debug(f"Attempting to delete many documents with query: {query}")
        try:
            result = self.collection.delete_many(query)
            deleted_count = result.deleted_count
            self.logger.info(f"Deleted {deleted_count} documents with query: {query}")
            return deleted_count
        except Exception as e:
            self.logger.error(
                f"Error deleting documents with query: {query}, Error: {e}",
                exc_info=True,
            )
            return 0

    def aggregate(self, pipeline: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Run an aggregation pipeline and return raw results.

        Args:
            pipeline: A list of dictionaries representing the aggregation pipeline stages.

        Returns:
            A list of dictionaries containing the results of the aggregation.
        """
        self.logger.debug(f"Attempting to run aggregation pipeline: {pipeline}")
        try:
            result = list(self.collection.aggregate(pipeline))
            self.logger.info(
                f"Aggregation pipeline completed. Returned {len(result)} documents."
            )
            return result
        except Exception as e:
            self.logger.error(
                f"Error running aggregation pipeline: {pipeline}, Error: {e}",
                exc_info=True,
            )
            return []
