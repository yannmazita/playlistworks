# src.features.player.services.playback
import logging
from PySide6.QtCore import QObject, Signal, Slot, QUrl, Property
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput

from src.features.tracks.models import TrackTableModel


logger = logging.getLogger(__name__)


class PlaybackService(QObject):
    """
    Audio playback class.
    """

    currentTrackChanged = Signal(str)
    playbackStateChanged = Signal(QMediaPlayer.PlaybackState)

    def __init__(self, track_model: TrackTableModel):
        super().__init__()
        self._track_model = track_model

        self.audio_output = QAudioOutput()
        self.player = QMediaPlayer()
        self.player.setAudioOutput(self.audio_output)

        self._current_track_path: str = ""
        self._playback_state = QMediaPlayer.PlaybackState.StoppedState

        self.player.playbackStateChanged.connect(self._on_playback_state_changed)

    @property
    @Property(str, notify=currentTrackChanged, final=False)  # type: ignore
    def currentTrackPath(self):
        """Get the current track path"""
        return self._current_track_path

    @currentTrackPath.setter
    def currentTrackPath(self, path):
        if self._current_track_path != path:
            self._current_track_path = path
            self.currentTrackChanged.emit(path)

    @property
    @Property(QMediaPlayer.PlaybackState, notify=playbackStateChanged)  # type: ignore
    def playbackState(self):
        """Get the playback state"""
        return self._playback_state

    @Slot(QMediaPlayer.PlaybackState)  # type: ignore
    def _on_playback_state_changed(self, state):
        """Handle playback state changes"""
        self._playback_state = state
        self.playbackStateChanged.emit(state)

    @Slot(str)  # type: ignore
    def play(self, path: str | None = None):
        """Play or resume playback."""
        if path:
            try:
                if (
                    path != self._current_track_path
                    or self.player.playbackState()
                    == QMediaPlayer.PlaybackState.StoppedState
                ):
                    self.currentTrackPath = path
                    file_url = QUrl.fromLocalFile(path)
                    self.player.setSource(file_url)
                    logger.info(f"Playing track: {path}")
                self.player.play()
            except Exception:
                logger.exception("Error playing track", stack_info=True)
        elif self.player.playbackState() == QMediaPlayer.PlaybackState.PausedState:
            self.player.play()
            logger.info("Resuming playback")
        else:
            logger.info("No track to play")

    @Slot()
    def pause(self):
        """Pause playback."""
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            logger.info("Pausing playback")
            self.player.pause()

    @Slot()
    def stop(self):
        """Stop playback."""
        self.player.stop()
        logger.info("Stopping playback")

    @Slot(str)  # type: ignore
    def toggle_playback(self, path: str | None = None):
        """Toggle between play and pause."""
        current_state = self.player.playbackState()

        if path:
            if (
                path != self._current_track_path
                or current_state == QMediaPlayer.PlaybackState.StoppedState
            ):
                self.play(path)
            elif current_state == QMediaPlayer.PlaybackState.PlayingState:
                self.pause()
            else:
                self.play()
        else:
            if current_state == QMediaPlayer.PlaybackState.PlayingState:
                self.pause()
            elif self._current_track_path:
                self.play()

    @Slot(int)  # type: ignore
    def handleRowClick(self, row):
        """Handle when a row is clicked"""
        if 0 <= row < self._track_model.rowCount():
            self._track_model.set_selected_track_index(row)
            logging.debug(f"Row {row} clicked")
