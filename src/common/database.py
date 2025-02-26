# src.common.database
import logging

from pymongo import ASCENDING, DESCENDING, TEXT, IndexModel, MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

from src.common.utils.settings import settings

logger = logging.getLogger(__name__)


def get_database() -> Database:
    """Initializes and returns a MongoDB database connection."""
    logger.info(f"Connecting to MongoDB at: {settings.mongo_db_uri}")
    client = MongoClient(settings.mongo_db_uri)
    return client[settings.mongo_db_name]


def get_collection(db: Database, collection_name: str) -> Collection:
    """
    Returns a MongoDB collection.
    """
    return db[collection_name]


def create_tracks_indexes(db: Database):
    """
    Creates indexes on the 'tracks' collection.
    """
    tracks: Collection = db["tracks"]

    indexes = [
        IndexModel([("path", ASCENDING)], unique=True),
        IndexModel([("tags_lower.artist", TEXT)]),
        IndexModel([("tags_lower.artistsort", TEXT)]),
        IndexModel([("tags_lower.album", TEXT)]),
        IndexModel([("tags_lower.albumartistsort", TEXT)]),
        IndexModel([("tags_lower.title", TEXT)]),
        IndexModel([("tags_lower.genre", TEXT)]),
        IndexModel([("fileprops.format", ASCENDING)]),
        IndexModel([("app_data.play_count", DESCENDING)]),
        IndexModel([("app_data.last_played", DESCENDING)]),
        IndexModel([("app_data.rating", DESCENDING)]),
    ]

    try:
        result = tracks.create_indexes(indexes)
        logger.info(f"Created indexes: {result}")
    except Exception as e:
        logger.error(f"Error creating indexes: {e}", exc_info=True)
