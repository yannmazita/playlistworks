# src.features.playlists.services.playlists
from PySide6.QtCore import QObject, Slot

from src.features.library.models import MusicLibrary


class PlaylistService(QObject):
    def __init__(self, library: MusicLibrary):
        super().__init__()
        self._library = library
        self._current_playlist_id = None

    @Slot(int)  # type: ignore
    def setCurrentPlaylist(self, playlist_id):
        """Set the current playlist and load its songs."""
        self._current_playlist_id = playlist_id
        self._library.loadPlaylistSongs(playlist_id)
