# src.features.playlists.playlist
from PySide6.QtCore import QObject, Signal


class PlaylistService(QObject):
    nameChanged = Signal()
    queryChanged = Signal()
    songsChanged = Signal()
