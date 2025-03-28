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
    TrackNumRole = Qt.UserRole + 6  # type: ignore
    DiscNumRole = Qt.UserRole + 7  # type: ignore
    GenreRole = Qt.UserRole + 8  # type: ignore
    DescriptionRole = Qt.UserRole + 9  # type: ignore
    AlbumArtistRole = Qt.UserRole + 10  # type: ignore
    ComposerRole = Qt.UserRole + 11  # type: ignore
    ReleaseTimeRole = Qt.UserRole + 12  # type: ignore
    BpmRole = Qt.UserRole + 13  # type: ignore
    CommentRole = Qt.UserRole + 14  # type: ignore
    CompilationRole = Qt.UserRole + 15  # type: ignore
    LengthRole = Qt.UserRole + 16  # type: ignore
    BitrateRole = Qt.UserRole + 17  # type: ignore

    NUMTRACK_COLUMN = 0
    TITLE_COLUMN = 1
    ARTIST_COLUMN = 2
    ALBUM_COLUMN = 3
    GENRE_COLUMN = 4
    DESCRIPTION_COLUMN = 5
    ALBUM_ARTIST_COLUMN = 6
    COMPOSER_COLUMN = 7
    RELEASE_TIME_COLUMN = 8
    DISC_NUM_COLUMN = 9
    BPM_COLUMN = 10
    COMMENT_COLUMN = 11
    COMPILATION_COLUMN = 12
    LENGTH_COLUMN = 13
    BITRATE_COLUMN = 14
    PATH_COLUMN = 15

    visibleColumnsChanged = Signal()

    def __init__(self, repository: SongsRepository):
        super().__init__()
        self._repository = repository
        self._songs: list[Song] = []
        # Default visible columns
        self._visible_columns = [
            self.NUMTRACK_COLUMN,
            self.LENGTH_COLUMN,
            self.TITLE_COLUMN,
            self.ARTIST_COLUMN,
            self.ALBUM_COLUMN,
            self.GENRE_COLUMN,
            self.RELEASE_TIME_COLUMN,
        ]
        self._column_headers = {
            self.NUMTRACK_COLUMN: "#",
            self.TITLE_COLUMN: "Title",
            self.ARTIST_COLUMN: "Artist",
            self.ALBUM_COLUMN: "Album",
            self.GENRE_COLUMN: "Genre",
            self.DESCRIPTION_COLUMN: "Description",
            self.ALBUM_ARTIST_COLUMN: "Album Artist",
            self.COMPOSER_COLUMN: "Composer",
            self.RELEASE_TIME_COLUMN: "Date",
            self.DISC_NUM_COLUMN: "Disc",
            self.BPM_COLUMN: "BPM",
            self.COMMENT_COLUMN: "Comment",
            self.COMPILATION_COLUMN: "Compilation",
            self.LENGTH_COLUMN: "Length",
            self.BITRATE_COLUMN: "Bitrate",
            self.PATH_COLUMN: "Path",
        }

    def get_path_role(self):
        return SongModel.PathRole

    pathRole = Property(int, fget=get_path_role)  # type: ignore

    def get_song_id_role(self):
        return SongModel.SongIdRole

    songIdRole = Property(int, fget=get_song_id_role)  # type: ignore

    def get_title_role(self):
        return SongModel.TitleRole

    titleRole = Property(int, fget=get_title_role)  # type: ignore

    def get_artist_role(self):
        return SongModel.ArtistRole

    artistRole = Property(int, fget=get_artist_role)  # type: ignore

    def get_album_role(self):
        return SongModel.AlbumRole

    albumRole = Property(int, fget=get_album_role)  # type: ignore

    # --- Role Properties (New) ---
    def get_track_num_role(self):
        return SongModel.TrackNumRole

    trackNumRole = Property(int, fget=get_track_num_role)  # type: ignore

    def get_disc_num_role(self):
        return SongModel.DiscNumRole

    discNumRole = Property(int, fget=get_disc_num_role)  # type: ignore

    def get_genre_role(self):
        return SongModel.GenreRole

    genreRole = Property(int, fget=get_genre_role)  # type: ignore

    def get_description_role(self):
        return SongModel.DescriptionRole

    descriptionRole = Property(int, fget=get_description_role)  # type: ignore

    def get_album_artist_role(self):
        return SongModel.AlbumArtistRole

    albumArtistRole = Property(int, fget=get_album_artist_role)  # type: ignore

    def get_composer_role(self):
        return SongModel.ComposerRole

    composerRole = Property(int, fget=get_composer_role)  # type: ignore

    def get_release_time_role(self):
        return SongModel.ReleaseTimeRole

    releaseTimeRole = Property(int, fget=get_release_time_role)  # type: ignore

    def get_bpm_role(self):
        return SongModel.BpmRole

    bpmRole = Property(int, fget=get_bpm_role)  # type: ignore

    def get_comment_role(self):
        return SongModel.CommentRole

    commentRole = Property(int, fget=get_comment_role)  # type: ignore

    def get_compilation_role(self):
        return SongModel.CompilationRole

    compilationRole = Property(int, fget=get_compilation_role)  # type: ignore

    def get_length_role(self):
        return SongModel.LengthRole

    lengthRole = Property(int, fget=get_length_role)  # type: ignore

    def get_bitrate_role(self):
        return SongModel.BitrateRole

    bitrateRole = Property(int, fget=get_bitrate_role)  # type: ignore

    def get_visible_columns(self) -> list[int]:
        return self._visible_columns

    def set_visible_columns(self, columns: list[int]):
        try:
            int_columns = [int(c) for c in columns]
        except (ValueError, TypeError):
            logger.warning(f"Invalid data type received for visible columns: {columns}")
            return

        valid_columns = [col for col in int_columns if col in self._column_headers]

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
        sorted_ids = sorted(self._column_headers.keys())
        for column_id in sorted_ids:
            column_name = self._column_headers[column_id]
            columns.append({"id": column_id, "name": column_name})
        return columns

    availableColumns = Property(
        "QVariantList",
        fget=get_available_columns_with_ids,  # type: ignore
        fset=None,
        constant=True,
    )

    @Slot(str, result=bool)  # type: ignore
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

    def _format_length(self, seconds: float) -> str:
        """Helper to format seconds to MM:SS"""
        if seconds is None or not isinstance(seconds, (int, float)) or seconds < 0:
            return ""
        try:
            secs = int(seconds)
            mins, secs = divmod(secs, 60)
            return f"{mins:01d}:{secs:02d}"
        except Exception:
            logger.warning(f"Could not format length: {seconds}", exc_info=True)
            return ""

    def _parse_track_disc_num(self, value_str: str) -> str:
        """Helper to parse 'X/Y' and return 'X'"""
        if not value_str:
            return ""
        return value_str.split("/")[0].strip()

    def data(
        self,
        index: QModelIndex | QPersistentModelIndex,
        role=Qt.DisplayRole,  # type: ignore
    ) -> Any | None:
        if not index.isValid() or index.row() >= len(self._songs):
            return None

        try:
            song = self._songs[index.row()]
            tag_val: str | None = None  # To store intermediate tag lookups

            if role == Qt.DisplayRole:  # type: ignore
                if not (0 <= index.column() < len(self._visible_columns)):
                    logger.warning(
                        f"Invalid column index {index.column()} for visible columns"
                    )
                    return None
                column_id = self._visible_columns[index.column()]

                if column_id == self.NUMTRACK_COLUMN:
                    tag_val = song.get_tag_display("TRACK_NUM")
                    return self._parse_track_disc_num(tag_val)
                elif column_id == self.TITLE_COLUMN:
                    return song.get_tag_display("TITLE")
                elif column_id == self.ARTIST_COLUMN:
                    return song.get_tag_display("ARTIST")
                elif column_id == self.ALBUM_COLUMN:
                    return song.get_tag_display("ALBUM")
                elif column_id == self.GENRE_COLUMN:
                    return song.get_tag_display("GENRE")
                elif column_id == self.DESCRIPTION_COLUMN:
                    return song.get_tag_display("DESCRIPTION")
                elif column_id == self.ALBUM_ARTIST_COLUMN:
                    return song.get_tag_display("ALBUM_ARTIST")
                elif column_id == self.COMPOSER_COLUMN:
                    return song.get_tag_display("COMPOSER")
                elif column_id == self.RELEASE_TIME_COLUMN:
                    return song.get_tag_display("RELEASE_TIME")
                elif column_id == self.DISC_NUM_COLUMN:
                    tag_val = song.get_tag_display("DISC_NUM")
                    return self._parse_track_disc_num(tag_val)
                elif column_id == self.BPM_COLUMN:
                    return song.get_tag_display("BPM")
                elif column_id == self.COMMENT_COLUMN:
                    return song.get_tag_display("COMMENT")
                elif column_id == self.COMPILATION_COLUMN:
                    return song.get_tag_display("COMPILATION")
                elif column_id == self.LENGTH_COLUMN:
                    return self._format_length(song.fileprops.length)
                elif column_id == self.BITRATE_COLUMN:
                    br = song.fileprops.bitrate
                    return f"{br} kbps" if br else ""
                elif column_id == self.PATH_COLUMN:
                    return song.path
                else:
                    # Should not happen
                    logger.warning(f"Unhandled visible column ID: {column_id}")
                    return None

            elif role == self.TitleRole:
                return song.get_tag_display("TITLE")
            elif role == self.ArtistRole:
                return song.get_tag_display("ARTIST")
            elif role == self.AlbumRole:
                return song.get_tag_display("ALBUM")
            elif role == self.PathRole:
                return song.path
            elif role == self.SongIdRole:
                return str(song.id)
            elif role == self.TrackNumRole:
                tag_val = song.get_tag_display("TRACK_NUM")
                return self._parse_track_disc_num(tag_val)
            elif role == self.DiscNumRole:
                tag_val = song.get_tag_display("DISC_NUM")
                return self._parse_track_disc_num(tag_val)
            elif role == self.GenreRole:
                return song.get_tag_display("GENRE")
            elif role == self.DescriptionRole:
                return song.get_tag_display("DESCRIPTION")
            elif role == self.AlbumArtistRole:
                return song.get_tag_display("ALBUM_ARTIST")
            elif role == self.ComposerRole:
                return song.get_tag_display("COMPOSER")
            elif role == self.ReleaseTimeRole:
                return song.get_tag_display("RELEASE_TIME")
            elif role == self.BpmRole:
                tag_val = song.get_tag_display("BPM")
                try:
                    return (
                        str(round(float(tag_val))) if tag_val else ""
                    )  # Return rounded string
                except ValueError:
                    return tag_val  # Return original string if not a number
            elif role == self.CommentRole:
                return song.get_tag_display("COMMENT")
            elif role == self.CompilationRole:
                tag_val = song.get_tag_display("COMPILATION")
                return "Yes" if tag_val == "1" else "No"
            elif role == self.LengthRole:
                return self._format_length(song.fileprops.length)
            elif role == self.BitrateRole:
                br = song.fileprops.bitrate
                return f"{br} kbps" if br else ""
            else:
                # Unknown role
                return None

        except IndexError:
            logger.error(f"Index out of range in data method: row {index.row()}")
            return None
        except Exception as e:
            logger.error(f"Error retrieving data for index {index}: {e}", exc_info=True)
            return None

    def headerData(self, section, orientation, role):
        # Making sure section index is valid for the *visible* columns
        if role == Qt.DisplayRole:  # type: ignore
            if orientation == Qt.Horizontal:  # type: ignore
                if 0 <= section < len(self._visible_columns):
                    column_id = self._visible_columns[section]
                    return self._column_headers.get(column_id, "")
        return None

    def roleNames(self):
        # QT expects bytes
        roles = {
            Qt.DisplayRole: b"display",  # type: ignore
            self.TitleRole: b"title",
            self.ArtistRole: b"artist",
            self.AlbumRole: b"album",
            self.PathRole: b"path",
            self.SongIdRole: b"songId",
            # --- New Roles ---
            self.TrackNumRole: b"trackNum",
            self.DiscNumRole: b"discNum",
            self.GenreRole: b"genre",
            self.DescriptionRole: b"description",
            self.AlbumArtistRole: b"albumArtist",
            self.ComposerRole: b"composer",
            self.ReleaseTimeRole: b"releaseTime",
            self.BpmRole: b"bpm",
            self.CommentRole: b"comment",
            self.CompilationRole: b"compilation",
            self.LengthRole: b"length",
            self.BitrateRole: b"bitrate",
        }
        # Filter out None values if any role constants were somehow None
        return {k: v for k, v in roles.items() if k is not None}

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
