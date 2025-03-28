# src.features.library.models
import logging
from typing import Any
from PySide6.QtCore import (
    QAbstractTableModel,
    QItemSelectionModel,
    QModelIndex,
    QObject,
    QPersistentModelIndex,
    Qt,
    Signal,
    Property,
    Slot,
)

from src.features.library.repository import Song, SongsRepository
from src.features.library.schemas import Playlist, PlaylistSong
from src.features.playlists.repository import (
    PlaylistSongRepository,
    PlaylistsRepository,
)

logger = logging.getLogger(__name__)


class SongModel(QAbstractTableModel):
    TitleRole = Qt.UserRole + 1  # type: ignore
    ArtistRole = Qt.UserRole + 2  # type: ignore
    AlbumRole = Qt.UserRole + 3  # type: ignore
    PathRole = Qt.UserRole + 4  # type: ignore
    SongIdRole = Qt.UserRole + 5  # type: ignore

    TITLE_COLUMN = 0
    ARTIST_COLUMN = 1
    ALBUM_COLUMN = 2

    visibleColumnsChanged = Signal()

    def __init__(self, repository: SongsRepository):
        super().__init__()
        self._repository = repository
        self._songs: list[Song] = []
        self._visible_columns = [
            self.TITLE_COLUMN,
            self.ARTIST_COLUMN,
            self.ALBUM_COLUMN,
        ]
        self._column_headers = {
            self.TITLE_COLUMN: "Title",
            self.ARTIST_COLUMN: "Artist",
            self.ALBUM_COLUMN: "Album",
        }

    def get_path_role(self):
        return SongModel.PathRole

    pathRole = Property(
        int,
        fget=get_path_role,  # type: ignore
    )

    def get_song_id_role(self):
        return SongModel.SongIdRole

    songIdRole = Property(
        int,
        fget=get_song_id_role,  # type: ignore
    )

    def get_title_role(self):
        return SongModel.TitleRole

    titleRole = Property(
        int,
        fget=get_title_role,  # type: ignore
    )

    def get_artist_role(self):
        return SongModel.ArtistRole

    artistRole = Property(
        int,
        fget=get_artist_role,  # type: ignore
    )

    def get_album_role(self):
        return SongModel.AlbumRole

    albumRole = Property(
        int,
        fget=get_album_role,  # type: ignore
    )

    def get_visible_columns(self) -> list[int]:
        return self._visible_columns

    def set_visible_columns(self, columns: list[int]):
        valid_columns = [col for col in columns if col in self._column_headers]

        if valid_columns != self._visible_columns:
            self.beginResetModel()
            self._visible_columns = valid_columns
            self.endResetModel()
            self.visibleColumnsChanged.emit()

    visibleColumns = Property(
        "QVariantList",
        fget=get_visible_columns,  # type: ignore
        fset=set_visible_columns,
        notify=visibleColumnsChanged,
    )

    def get_available_columns_with_ids(self):
        columns = []
        for column_id, column_name in self._column_headers.items():
            columns.append({"id": column_id, "name": column_name})
        return columns

    availableColumns = Property(
        "QVariantList",
        fget=get_available_columns_with_ids,  # type: ignore
        fset=None,
        notify=None,
    )

    @Slot(str)  # type: ignore
    def isColumnVisible(self, column_name: str) -> bool:
        column_id = next(
            (
                key
                for key, value in self._column_headers.items()
                if value == column_name
            ),
            None,
        )
        return column_id is not None and column_id in self._visible_columns

    def rowCount(
        self, parent: QModelIndex | QPersistentModelIndex = QModelIndex()
    ) -> int:
        return len(self._songs)

    def columnCount(
        self, parent: QModelIndex | QPersistentModelIndex = QModelIndex()
    ) -> int:
        return len(self._visible_columns)

    def data(
        self,
        index: QModelIndex | QPersistentModelIndex,
        role=Qt.DisplayRole,  # type: ignore
    ) -> Any | None:
        if not index.isValid():
            logger.warning("Invalid index in data method")
            return None
        song = self._songs[index.row()]

        if role == Qt.DisplayRole:  # type: ignore
            column_id = self._visible_columns[index.column()]

            if column_id == self.TITLE_COLUMN:
                return song.get_tag_display("TITLE")
            elif column_id == self.ARTIST_COLUMN:
                return song.get_tag_display("ARTIST")
            elif column_id == self.ALBUM_COLUMN:
                return song.get_tag_display("ALBUM")
        elif role == self.TitleRole:
            value = song.get_tag_display("TITLE")
            return value
        elif role == self.ArtistRole:
            value = song.get_tag_display("ARTIST")
            return value
        elif role == self.AlbumRole:
            value = song.get_tag_display("ALBUM")
            return value
        elif role == self.PathRole:
            return song.path
        elif role == self.SongIdRole:
            return str(song.id)
        else:
            return None

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:  # type: ignore
            if orientation == Qt.Horizontal:  # type: ignore
                if 0 <= section < len(self._visible_columns):
                    column_id = self._visible_columns[section]
                    return self._column_headers.get(column_id, "")
        return None

    def roleNames(self):
        roles = {
            Qt.DisplayRole: b"display",  # type: ignore
            # Qt.EditRole: b"edit",  # type: ignore
            self.TitleRole: b"title",
            self.ArtistRole: b"artist",
            self.PathRole: b"path",
            self.SongIdRole: b"songId",
        }
        return roles

    def setSongs(self, songs: list[Song]):
        self.beginResetModel()
        self._songs = songs
        self.endResetModel()


class PlaylistModel(QAbstractTableModel):
    NameRole = Qt.UserRole + 1  # type: ignore
    IdRole = Qt.UserRole + 2  # type: ignore
    IsDynamicRole = Qt.UserRole + 3  # type: ignore
    QueryRole = Qt.UserRole + 4  # type: ignore

    def __init__(self, playlists_repository: PlaylistsRepository):
        super().__init__()
        self._playlists_repository = playlists_repository
        self._playlists: list[Playlist] = []

    def get_name_role(self):
        return PlaylistModel.NameRole

    nameRole = Property(
        int,
        fget=get_name_role,  # type: ignore
    )

    def get_id_role(self):
        return PlaylistModel.IdRole

    idRole = Property(
        int,
        fget=get_id_role,  # type: ignore
    )

    def get_is_dynamic_role(self):
        return PlaylistModel.IsDynamicRole

    isDynamicRole = Property(
        int,
        fget=get_is_dynamic_role,  # type: ignore
    )

    def get_query_role(self):
        return PlaylistModel.QueryRole

    queryRole = Property(
        int,
        fget=get_query_role,  # type: ignore
    )

    def rowCount(self, parent: QModelIndex | QPersistentModelIndex = QModelIndex()):
        return len(self._playlists)

    def columnCount(
        self, parent: QModelIndex | QPersistentModelIndex = QModelIndex()
    ) -> int:
        return 1

    def data(
        self,
        index: QModelIndex | QPersistentModelIndex,
        role=Qt.DisplayRole,  # type: ignore
    ) -> Any:
        if not index.isValid() or index.row() >= len(self._playlists):
            return None

        playlist = self._playlists[index.row()]

        if role == self.NameRole:
            return playlist.name
        elif role == self.IdRole:
            return playlist.id
        elif role == self.IsDynamicRole:
            return playlist.is_dynamic
        elif role == self.QueryRole:
            return playlist.query

        return None

    def roleNames(self):
        return {
            self.NameRole: b"name",
            self.IdRole: b"playlistId",
            self.IsDynamicRole: b"isDynamic",
            self.QueryRole: b"query",
        }

    def setPlaylists(self, playlists):
        self.beginResetModel()
        self._playlists = playlists
        self.endResetModel()


class MusicLibrary(QObject):
    songsChanged = Signal()
    playlistsChanged = Signal()
    currentPlaylistSongsChanged = Signal()
    songModelChanged = Signal()
    playlistModeChanged = Signal()

    songSelectionModelChanged = Signal()
    playlistSelectionModelChanged = Signal()

    def __init__(
        self,
        songs_repository: SongsRepository,
        playlists_repository: PlaylistsRepository,
        playlist_song_repository: PlaylistSongRepository,
    ):
        super().__init__()
        self._song_repository = songs_repository
        self._playlists_repository = playlists_repository
        self._playlist_song_repository = playlist_song_repository

        # Initialize models
        self._playlist_model = PlaylistModel(playlists_repository)
        self._song_model = SongModel(songs_repository)
        self._current_playlist_songs = SongModel(songs_repository)
        self._current_song_model = self._song_model

        self._song_selection_model = QItemSelectionModel(self._song_model)
        self._playlist_selection_model = QItemSelectionModel(self._playlist_model)
        self._current_playlist_songs_selection_model = QItemSelectionModel(
            self._current_playlist_songs
        )
        self._current_selection_model = self._song_selection_model

        self._playlist_mode = False

        self.loadAllSongs()
        self.loadAllPlaylists()

    def get_playlist_model(self):
        return self._playlist_model

    playlistModel = Property(
        QObject,
        fget=get_playlist_model,  # type: ignore
        fset=None,
        notify=playlistsChanged,
    )

    def get_song_model(self):
        return self._song_model

    songModel = Property(
        QObject,
        fget=get_song_model,  # type: ignore
        fset=None,
        notify=songsChanged,
    )

    def get_current_playlist_songs(self):
        return self._current_playlist_songs

    currentPlaylistSongs = Property(
        QObject,
        fget=get_current_playlist_songs,  # type: ignore
        fset=None,
        notify=currentPlaylistSongsChanged,
    )

    def get_current_song_model(self):
        return self._current_song_model

    currentSongModel = Property(
        QObject,
        fget=get_current_song_model,  # type: ignore
        fset=None,
        notify=songModelChanged,
    )

    def get_song_selection_model(self):
        return self._song_selection_model

    songSelectionModel = Property(
        QObject,
        fget=get_song_selection_model,  # type: ignore
        notify=songSelectionModelChanged,
    )

    def get_playlist_selection_model(self):
        return self._playlist_selection_model

    playlistSelectionModel = Property(
        QObject,  # type: ignore
        fget=get_playlist_selection_model,  # type: ignore
        notify=playlistSelectionModelChanged,
    )

    def get_current_playlist_songs_selection_model(self):
        return self._current_playlist_songs_selection_model

    currentPlaylistSongsSelectionModel = Property(
        QObject,  # type: ignore
        fget=get_current_playlist_songs_selection_model,  # type: ignore
        notify=songSelectionModelChanged,
    )

    def get_current_selection_model(self):
        return self._current_selection_model

    currentSelectionModel = Property(
        QObject,  # type: ignore
        fget=get_current_selection_model,  # type: ignore
        notify=songSelectionModelChanged,
    )

    def get_playlist_mode(self):
        return self._playlist_mode

    def set_playlist_mode(self, boolean: bool):
        self._playlist_mode = boolean
        if boolean:
            self._current_song_model = self._current_playlist_songs
            self._current_selection_model = self._current_playlist_songs_selection_model
            self.songModelChanged.emit()
            self.songSelectionModelChanged.emit()
        else:
            self._current_song_model = self._song_model
            self._current_selection_model = self._song_selection_model
            self.songModelChanged.emit()
            self.songSelectionModelChanged.emit()

    playlistMode = Property(
        bool,
        fget=get_playlist_mode,  # type: ignore
        fset=set_playlist_mode,
        notify=playlistModeChanged,
    )

    def loadAllSongs(self):
        songs = self._song_repository.find_many()
        self._song_model.setSongs(songs)
        self.songsChanged.emit()

    def loadAllPlaylists(self):
        playlists = self._playlists_repository.find_many()
        self._playlist_model.setPlaylists(playlists)
        self.playlistsChanged.emit()

    def loadPlaylistSongs(self, playlist_id: int):
        songs = self._playlist_song_repository.get_playlist_songs(playlist_id)
        self._current_playlist_songs.setSongs(songs)
        self.currentPlaylistSongsChanged.emit()

    @Slot(str, int)  # type: ignore
    def searchSongs(self, query: str, playlist_id: int):
        # QT doesn't allow union types so we'll be using -1 for library-wide searches
        if playlist_id == -1:
            if not query:
                self.loadAllSongs()
            else:
                songs = self._song_repository.search_songs(query)
                self._song_model.setSongs(songs)
                self.songsChanged.emit()
        else:
            if not query:
                self.loadPlaylistSongs(playlist_id)
            else:
                songs = self._playlist_song_repository.search_songs(query, playlist_id)
                self._current_playlist_songs.setSongs(songs)
                self.currentPlaylistSongsChanged.emit()

    @Slot(str, str, bool)  # type: ignore
    def createPlaylist(self, name: str, query: str = "", is_dynamic: bool = False):
        model = Playlist(name=name, query=query, is_dynamic=is_dynamic)
        playlist_id = self._playlists_repository.insert(model)
        self.loadAllPlaylists()
        return playlist_id

    @Slot(int, str, str, bool)  # type: ignore
    def updatePlaylist(self, playlist_id: int, name: str, query: str, is_dynamic: bool):
        model = Playlist(name=name, query=query, is_dynamic=is_dynamic)
        self._playlists_repository.update(playlist_id, model)
        self.loadAllPlaylists()

    @Slot(int)  # type: ignore
    def deletePlaylist(self, playlist_id: int):
        self._playlists_repository.delete(playlist_id)
        self.loadAllPlaylists()

    @Slot(int, int)  # type: ignore
    def addSongToPlaylist(
        self, playlist_id: int, song_id: int, position: int | None = None
    ):
        model = PlaylistSong(
            playlist_id=playlist_id, song_id=song_id, position=position
        )
        self._playlist_song_repository.insert(model)
        self.loadPlaylistSongs(playlist_id)

    @Slot(int, int)  # type: ignore
    def removeSongFromPlaylist(self, playlist_id: int, song_id: int):
        self._playlist_song_repository.remove_song_from_playlist(playlist_id, song_id)
        self.loadPlaylistSongs(playlist_id)

    @Slot(int)  # type: ignore
    def setCurrentPlaylist(self, playlist_id: int):
        self.loadPlaylistSongs(playlist_id)

    @Slot(int)  # type: ignore
    def incrementPlayCount(self, song_id: int):
        self._song_repository.update_song_playcount(song_id)

    @Slot(QModelIndex)  # type: ignore
    def clearSelection(self, index: QModelIndex):
        self._current_selection_model.clearSelection()

    @Slot(QModelIndex)  # type: ignore
    def select(self, index: QModelIndex):
        self._current_selection_model.select(index, QItemSelectionModel.Select)  # type: ignore

    @Slot(QModelIndex)  # type: ignore
    def setCurrentIndex(self, index: QModelIndex):
        self._current_selection_model.setCurrentIndex(
            index,
            # QItemSelectionModel.NoUpdate,  # type: ignore
            QItemSelectionModel.ClearAndSelect | QItemSelectionModel.Current,  # type: ignore
        )

    def getCurrentSongPath(self):
        index = self._current_selection_model.currentIndex()
        if index.isValid():
            return self._current_song_model.data(index, Qt.UserRole + 4)  # type: ignore
        return None
