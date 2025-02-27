# src.features.playlists.schemas
from typing import Literal
from pydantic import BaseModel, Field


class Playlist(BaseModel):
    id: int | None = Field(default=None, description="Playlist ID")
    name: str = Field(description="Name of the playlist")
    description: str = Field(default="", description="Description of the playlist")
    query: str = Field(default="", description="Query for dynamic playlists")
    playlist_type: Literal["static", "dynamic"] = Field(
        default="static", description="Type of playlist"
    )
