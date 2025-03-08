# src.features.tracks.models
import logging
from PySide6.QtCore import (
    QAbstractTableModel,
    QModelIndex,
    QPersistentModelIndex,
    Qt,
    Signal,
    Slot,
)

from src.features.tracks.repository import Track, TracksRepository

logger = logging.getLogger(__name__)


class TrackTableModel(QAbstractTableModel):
    selectedTrackChanged = Signal(int)

    def __init__(self, repository: TracksRepository):
        QAbstractTableModel.__init__(self)
        self.repository = repository
        self.tracks: list[Track] = []
        self.load_data()
        self._selected_track_index = -1

    def load_data(self):
        self.beginResetModel()
        self.tracks = self.repository.find_many()
        self.endResetModel()
        logger.debug(f"Loaded {len(self.tracks)} tracks")

    def rowCount(
        self, parent: QModelIndex | QPersistentModelIndex = QModelIndex()
    ) -> int:
        return len(self.tracks)

    def columnCount(
        self, parent: QModelIndex | QPersistentModelIndex = QModelIndex()
    ) -> int:
        return 3

    def data(
        self,
        index: QModelIndex | QPersistentModelIndex,
        role=Qt.DisplayRole,  # type: ignore
    ) -> str | None:
        if not index.isValid():
            logger.warning("Invalid index in data method")
            return None
        track = self.tracks[index.row()]

        if role == Qt.DisplayRole:  # type: ignore
            if index.column() == 0:
                value = track.get_tag_display("TITLE")
                return value
            elif index.column() == 1:
                value = track.get_tag_display("ARTIST")
                return value
            elif index.column() == 2:
                value = track.get_tag_display("ALBUM")
                return value
        elif role == Qt.UserRole + 1:  # type: ignore
            value = track.get_tag_display("TITLE")
            return value
        elif role == Qt.UserRole + 2:  # type: ignore
            value = track.get_tag_display("ARTIST")
            return value
        elif role == Qt.UserRole + 3:  # type: ignore
            value = track.get_tag_display("ALBUM")
            return value
        elif role == Qt.UserRole + 4:  # type: ignore
            return track.path
        else:
            return None

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:  # type: ignore
            if orientation == Qt.Horizontal:  # type: ignore
                if section == 0:
                    return "Title"
                elif section == 1:
                    return "Artist"
                elif section == 2:
                    return "Album"
        return None

    def roleNames(self):
        roles = {
            Qt.DisplayRole: b"display",  # type: ignore
            # Qt.EditRole: b"edit",  # type: ignore
            Qt.UserRole + 1: b"title",  # type: ignore
            Qt.UserRole + 2: b"artist",  # type: ignore
            Qt.UserRole + 3: b"album",  # type: ignore
            Qt.UserRole + 4: b"trackPath",  # type: ignore
        }
        logger.debug(f"Role names: {roles}")
        return roles

    def refresh(self):
        """Reload data from the repository"""
        logger.debug("Refreshing track table model")
        self.load_data()

    @property
    def selectedTrackIndex(self) -> int:
        return self._selected_track_index

    @selectedTrackIndex.setter
    def selectedTrackIndex(self, index: int):
        if self._selected_track_index != index:
            self._selected_track_index = index
            self.selectedTrackChanged.emit(index)
            logger.debug(f"Selected track index changed: {index}")

    @Slot(int)  # type: ignore
    def setSelectedTrack(self, row: int):
        self.selectedTrackIndex = row
