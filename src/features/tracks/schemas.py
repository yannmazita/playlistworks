# src.features.tracks.schemas
from pydantic import BaseModel
from src.common.schemas import Base, UuidMixin
from src.core.types import ID3Keys


class TrackBase(Base):
    title: list[str]
    artist: list[str]
    album: list[str] | None = None
    genre: list[str] | None = None
    track_number: str | None = None
    duration: int | None = None
    path: str
    id3_metadata: dict[ID3Keys, list[str]] | None = None


class TrackCreate(TrackBase):
    pass


class TrackRead(TrackBase, UuidMixin):
    pass


class TrackUpdate(Base):
    title: list[str] | None = None
    artist: list[str] | None = None
    album: list[str] | None = None
    genre: list[str] | None = None
    track_number: str | None = None
    duration: int | None = None
    id3_metadata: dict[ID3Keys, list[str]] | None = None


class Tracks(BaseModel):
    tracks: list[TrackRead]
    total: int
