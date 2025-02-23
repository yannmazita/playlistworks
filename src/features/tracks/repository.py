# src.features.tracks.repository
from src.features.tracks.models import Track
from src.common.repository import DatabaseRepository


class TracksRepository(DatabaseRepository):
    """
    Repository for performing database queries on tracks.
    """

    def __init__(self):
        super().__init__(Track)
