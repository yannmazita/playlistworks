# src.features.library.schemas
from typing import Any
from pydantic import BaseModel, Field, field_validator
from pathlib import Path


class FileProperties(BaseModel):
    """File properties (not from tags)"""

    size: int = Field(description="File size in bytes")
    bitrate: int = Field(description="Bitrate in kbps")
    sample_rate: int = Field(description="Sample rate in Hz")
    channels: int = Field(description="Number of audio channels")
    length: float = Field(description="Song length in seconds")
    mtime: float = Field(description="Last modification time of the file (UNIX time)")


class AppData(BaseModel):
    """Application-specific data"""

    play_count: int = Field(default=0)
    skip_count: int = Field(default=0)
    last_played: float | None = Field(
        default=None, description="Last played time (UNIX time)"
    )
    rating: float | None = Field(default=None, ge=0, le=5)
    added_date: float = Field(description="Date added (UNIX time)")


class Song(BaseModel):
    id: int | None = Field(default=None)
    path: str = Field(description="Path to the audio file")
    fileprops: FileProperties = Field(description="File properties")
    tags: dict[str, list[Any]] = Field(
        default_factory=dict, description="All tags from the file as key-value pairs"
    )
    app_data: AppData = Field(description="Application data")

    @field_validator("path")
    @classmethod
    def normalize_path(cls, v: str) -> str:
        """Ensure path is an absolute path and normalized"""
        return str(Path(v).absolute())

    # Helper methods for access
    def get_tag(self, name: str, default: list[str] | None = None) -> list[str] | None:
        """Get a tag value, case-insensitive"""
        if name in self.tags:
            if isinstance(self.tags, dict):
                return self.tags[name]
            else:
                return None

        return default

    def get_tag_display(self, name: str, default: str = "") -> str:
        """Get a tag as a display string (first value or joined)"""
        values = self.get_tag(name)
        if not values:
            return default

        if len(values) == 1:
            return values[0]

        return ", ".join(values)
