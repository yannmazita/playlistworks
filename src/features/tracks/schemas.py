# src.features.tracks.schemas
from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field, field_validator, model_validator
from pathlib import Path


class FileProperties(BaseModel):
    """File properties (not from tags)"""

    size: int = Field(description="File size in bytes")
    format: str = Field(description="File format (mp3, flac, ogg, etc.)")
    bitrate: int = Field(description="Bitrate in kbps")
    sample_rate: int = Field(description="Sample rate in Hz")
    channels: int = Field(description="Number of audio channels")
    length: float = Field(description="Track length in seconds")
    mtime: datetime = Field(description="Last modification time of the file")


class AppData(BaseModel):
    """Application-specific data"""

    play_count: int = Field(default=0)
    skip_count: int = Field(default=0)
    last_played: datetime | None = Field(default=None)
    rating: float | None = Field(default=None, ge=0, le=5)
    added_date: datetime = Field(default_factory=datetime.now)


class Track(BaseModel):
    path: str = Field(description="Path to the audio file")
    fileprops: FileProperties = Field(description="File properties")
    tags: dict[str, list[str]] = Field(
        default_factory=dict, description="All tags from the file as key-value pairs"
    )
    tags_lower: dict[str, list[str]] = Field(
        default_factory=dict,
        description="Lowercase versions of all tags for case-insensitive search",
    )
    app_data: AppData = Field(default_factory=AppData, description="Application data")

    # Original raw metadata (for debugging/reference)
    raw_metadata: dict[str, Any] | None = Field(
        default=None, description="Original raw metadata from the file"
    )

    @model_validator(mode="after")
    def normalize_tags(self) -> "Track":
        """Make sure tags_lower has lowercase versions of all tags"""
        if not self.tags_lower and self.tags:
            self.tags_lower = {
                k: [v.lower() if isinstance(v, str) else v for v in vals]
                for k, vals in self.tags.items()
            }
        return self

    @field_validator("path")
    @classmethod
    def normalize_path(cls, v: str) -> str:
        """Ensure path is an absolute path and normalized"""
        return str(Path(v).absolute())

    # Helper methods for access
    def get_tag(self, name: str, default: list[str] | None = None) -> list[str] | None:
        """Get a tag value, case-insensitive"""
        # Try exact match first for speed
        if name in self.tags:
            return self.tags[name]

        # Try case-insensitive match
        name_lower = name.lower()
        for k in self.tags:
            if k.lower() == name_lower:
                return self.tags[k]

        return default

    def get_tag_display(self, name: str, default: str = "") -> str:
        """Get a tag as a display string (first value or joined)"""
        values = self.get_tag(name)
        if not values:
            return default

        if len(values) == 1:
            return values[0]

        return ", ".join(values)
