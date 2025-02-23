# src.features.tracks.models
from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, mapped_column

from src.common.models import Base, UuidMixin


class Track(Base, UuidMixin):
    __tablename__ = "tracks"
    title: Mapped[list[str]] = mapped_column(nullable=False)
    artist: Mapped[list[str]] = mapped_column(nullable=False)
    album: Mapped[list[str]] = mapped_column(nullable=True)
    genre: Mapped[list[str]] = mapped_column(nullable=True)
    duration: Mapped[int] = mapped_column(nullable=True)
    path: Mapped[str] = mapped_column(nullable=False, unique=True)
    id3_metadata: Mapped[dict] = mapped_column(JSON, nullable=True)
