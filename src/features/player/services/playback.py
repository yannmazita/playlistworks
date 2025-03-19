# src.features.player.services.playback
# ruff: noqa: E402
import logging
import gi
import random

gi.require_version("Gst", "1.0")
from gi.repository import Gst, GLib  # type: ignore
from PySide6.QtCore import QItemSelectionModel, QObject, Signal, Slot, Property

from src.features.library.models import MusicLibrary

Gst.init(None)

logger = logging.getLogger(__name__)


class PlaybackService(QObject):
    """
    Audio playback service using GStreamer.

    Signals:
        currentTrackChanged(str): Emitted when the currently playing song changes.
            The new song's path is passed as an argument.
        playbackStateChanged(int): Emitted when the playback state changes.
            The new state is passed as an integer (GStreamer state).
        positionChanged(int): Emitted periodically during playback to update the
            current playback position. The position is in milliseconds.
        durationChanged(int): Emitted when the duration of the current song
            is determined or changes. The duration is in milliseconds.
        repeatModeChanged(int): Emitted when the repeat mode changes.
        shuffleModeChanged(bool): Emitted when the shuffle mode changes.
    """

    # Playback repeat modes
    REPEAT_OFF = 0
    REPEAT_ALL = 1
    REPEAT_TRACK = 2
    REPEAT_ONE_SONG = 3

    GST_STATE_VOID_PENDING = (
        Gst.State.VOID_PENDING
    )  # Element in the process of changing state but target state unknown yet
    GST_STATE_NULL = (
        Gst.State.NULL
    )  # Initial state of an element, set when element is created or reset
    GST_STATE_READY = (
        Gst.State.READY
    )  # Element is ready to accept data but not yet processing any. Buffers allocated
    GST_STATE_PAUSED = Gst.State.PAUSED
    GST_STATE_PLAYING = Gst.State.PLAYING

    currentTrackChanged = Signal(str)
    playbackStateChanged = Signal(int)
    positionChanged = Signal(int)  # Position in ms
    durationChanged = Signal(int)  # Duration in ms
    repeatModeChanged = Signal(int)
    shuffleModeChanged = Signal(bool)

    def __init__(self, library: MusicLibrary):
        """
        Initializes the PlaybackService.

        Args:
            library: The music library model.
        """
        super().__init__()
        self._library = library

        self.player = Gst.ElementFactory.make("playbin", "player")
        if not self.player:
            logger.error("Could not create playbin element")

        self.player.set_property("volume", 1.0)

        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self._on_bus_message)

        self._current_song_path = ""
        self._playback_state = Gst.State.NULL

        # Shuffle and repeat mode properties
        self._shuffle_mode = False
        self._repeat_mode = self.REPEAT_OFF
        self._shuffled_indices = []

        # Create a mainloop for message processing
        self._main_loop = GLib.MainLoop()
        self._main_loop_thread = GLib.Thread.new("gst-thread", self._run_main_loop)

        self._position = 0
        self._duration = 0

        # Set up a timer to poll position during playback
        self._position_timer = None
        self._setup_position_timer()

        # Connect to library signals
        self._library.songsChanged.connect(self._on_songs_changed)
        self._library.currentPlaylistSongsChanged.connect(self._on_songs_changed)
        # NEW: Connect to selection model changes
        self._library.songSelectionModelChanged.connect(self._on_selection_changed)

    def get_current_song_path(self):
        return self._current_song_path

    @Slot(str)  # type: ignore
    def set_current_song_path(self, path: str):
        """Sets the current song path and emits the currentTrackChanged signal.

        Args:
            path: The path to the new song.
        """
        if self._current_song_path != path:
            self._current_song_path = path
            self.currentTrackChanged.emit(path)

    currentTrackPath = Property(
        str,
        fget=get_current_song_path,  # type: ignore
        fset=set_current_song_path,
        notify=currentTrackChanged,
    )

    def get_position(self):
        return self._position

    position = Property(int, fget=get_position, notify=positionChanged)  # type: ignore

    def get_playback_state(self):
        return self._playback_state

    playbackState = Property(int, fget=get_playback_state, notify=playbackStateChanged)  # type: ignore

    def get_duration(self):
        return self._duration

    duration = Property(int, fget=get_duration, notify=durationChanged)  # type: ignore

    def get_shuffle_mode(self):
        return self._shuffle_mode

    @Slot(bool)  # type: ignore
    def set_shuffle_mode(self, enabled: bool):
        if self._shuffle_mode != enabled:
            self._shuffle_mode = enabled
            self.shuffleModeChanged.emit(enabled)
            if enabled:
                self._generate_shuffled_indices()
            logger.info(f"Shuffle mode: {'ON' if enabled else 'OFF'}")

    shuffleMode = Property(
        bool,
        fget=get_shuffle_mode,  # type: ignore
        fset=set_shuffle_mode,
        notify=shuffleModeChanged,
    )

    def get_repeat_mode(self):
        return self._repeat_mode

    @Slot(int)  # type: ignore
    def set_repeat_mode(self, mode: int):
        if mode not in (
            self.REPEAT_OFF,
            self.REPEAT_ALL,
            self.REPEAT_TRACK,
            self.REPEAT_ONE_SONG,
        ):
            logger.warning(f"Invalid repeat mode: {mode}")
            return

        if self._repeat_mode != mode:
            self._repeat_mode = mode
            self.repeatModeChanged.emit(mode)
            logger.info(f"Repeat mode set to: {mode}")

    repeatMode = Property(
        int,
        fget=get_repeat_mode,  # type: ignore
        fset=set_repeat_mode,
        notify=repeatModeChanged,
    )

    def _run_main_loop(self):
        """Run the GLib main loop for GStreamer message processing"""
        self._main_loop.run()

    def __del__(self):
        """Clean up resources"""
        if hasattr(self, "_main_loop") and self._main_loop.is_running():
            self._main_loop.quit()
        if hasattr(self, "player"):
            self.player.set_state(Gst.State.NULL)

    def _setup_position_timer(self):
        """Set up timer to update position during playback"""
        from PySide6.QtCore import QTimer

        self._position_timer = QTimer(self)
        self._position_timer.setInterval(500)  # Update every 500ms
        self._position_timer.timeout.connect(self._update_position)

    def _update_position(self):
        """Update current playback position and emit signal"""
        if self._playback_state != Gst.State.PLAYING:
            return

        success, position = self.player.query_position(Gst.Format.TIME)
        if success:
            pos_ms = position // 1000000  # ns to ms
            if pos_ms != self._position:
                self._position = pos_ms
                self.positionChanged.emit(pos_ms)

        success, duration = self.player.query_duration(Gst.Format.TIME)
        if success:
            dur_ms = duration // 1000000  # ns to ms
            if dur_ms != self._duration:
                self._duration = dur_ms
                self.durationChanged.emit(dur_ms)

    def _on_bus_message(self, bus, message):
        """Handle GStreamer bus messages"""
        t = message.type

        if t == Gst.MessageType.EOS:
            # End of stream - handle according to repeat mode
            if self._repeat_mode == self.REPEAT_TRACK:
                # Repeat the current track
                self.seek(0)
                self.player.set_state(Gst.State.PLAYING)
                logger.info("Restarting current track (repeat track mode)")
            elif self._repeat_mode == self.REPEAT_ALL:
                # Play the next song, or go back to the first if at the end
                current_index = (
                    self._library.get_current_selection_model().currentIndex()
                )
                next_index = self._get_next_index(current_index)

                if next_index is not None:
                    self._library.get_current_selection_model().setCurrentIndex(
                        next_index,
                        QItemSelectionModel.NoUpdate,  # type: ignore
                    )
                    song_path = self._library.getCurrentSongPath()
                    self.play(song_path)
                    logger.info(
                        f"Playing next song (repeat all mode): {next_index.row()}"
                    )
                else:
                    # Should not happen with repeat all, but just in case
                    self.player.set_state(Gst.State.NULL)
                    self._update_playback_state(Gst.State.NULL)
                    logger.info("End of playlist reached with no next song")
            elif self._repeat_mode == self.REPEAT_OFF:
                # In REPEAT_OFF mode, continue to next song but don't loop at end
                current_index = (
                    self._library.get_current_selection_model().currentIndex()
                )
                next_index = self._get_next_index(current_index)

                if next_index is not None:
                    self._library.get_current_selection_model().setCurrentIndex(
                        next_index,
                        QItemSelectionModel.NoUpdate,  # type: ignore
                    )
                    song_path = self._library.getCurrentSongPath()
                    self.play(song_path)
                    logger.info(
                        f"Playing next song (repeat off mode): {next_index.row()}"
                    )
                else:
                    # End of playlist reached, stop playback
                    self.player.set_state(Gst.State.NULL)
                    self._update_playback_state(Gst.State.NULL)
                    logger.info("End of playlist reached, stopping playback")
            else:
                # REPEAT_ONE_SONG or any other mode: stop at the end
                self.player.set_state(Gst.State.NULL)
                self._update_playback_state(Gst.State.NULL)
                logger.info("End of stream reached")

        elif t == Gst.MessageType.ERROR:
            self.player.set_state(Gst.State.NULL)
            err, debug = message.parse_error()
            logger.error(f"Error: {err}, {debug}")
            self._update_playback_state(Gst.State.NULL)

        elif t == Gst.MessageType.STATE_CHANGED:
            if message.src == self.player:
                old_state, new_state, pending_state = message.parse_state_changed()
                self._update_playback_state(new_state)
        elif t == Gst.MessageType.STREAM_START:
            logger.info("Stream started")
            # Query and update duration when stream starts
            success, duration = self.player.query_duration(Gst.Format.TIME)
            if success:
                dur_ms = duration // 1000000
                self._duration = dur_ms
                self.durationChanged.emit(dur_ms)

    def _update_playback_state(self, state):
        """Update the playback state and emit signal if changed"""
        if self._playback_state != state:
            self._playback_state = state
            self.playbackStateChanged.emit(state)

            # Start or stop the position timer based on playback state
            if state == Gst.State.PLAYING:
                if self._position_timer and not self._position_timer.isActive():
                    self._position_timer.start()
            else:
                if self._position_timer and self._position_timer.isActive():
                    self._position_timer.stop()

    @Slot()
    def _on_songs_changed(self):
        """Handle the songsChanged signal from MusicLibrary."""
        if self._shuffle_mode:
            self._generate_shuffled_indices()

    @Slot()
    def _on_selection_changed(self):
        """Handle changes in the selection model."""
        if self._shuffle_mode:
            self._generate_shuffled_indices()

    def _generate_shuffled_indices(self):
        """Generate a shuffled list of indices for the current playlist"""
        count = self._library.get_current_song_model().rowCount()
        if count == 0:
            self._shuffled_indices = []
            return

        # Create list of indices and shuffle it
        indices = list(range(count))
        random.shuffle(indices)

        # If a song is currently playing, move its index to the beginning
        current_index = self._library.get_current_selection_model().currentIndex()
        if current_index.isValid() and current_index.row() in indices:
            indices.remove(current_index.row())
            indices.insert(0, current_index.row())

        self._shuffled_indices = indices

    def _get_next_index(self, current_index):
        """Get the next song index based on current settings"""
        count = self._library.get_current_song_model().rowCount()
        if count == 0:
            return None

        if self._repeat_mode == self.REPEAT_TRACK:
            return current_index

        if self._shuffle_mode:
            if not self._shuffled_indices:
                self._generate_shuffled_indices()

            try:
                current_pos = self._shuffled_indices.index(current_index.row())
                if current_pos + 1 < len(self._shuffled_indices):
                    return self._library.get_current_song_model().index(
                        self._shuffled_indices[current_pos + 1], 0
                    )
                elif self._repeat_mode == self.REPEAT_ALL:
                    return self._library.get_current_song_model().index(
                        self._shuffled_indices[0], 0
                    )  # Wrap around
                else:
                    return None  # End of shuffled list
            except ValueError:
                # Current index not in shuffled list, regenerate
                self._generate_shuffled_indices()
                if self._shuffled_indices:
                    return self._library.get_current_song_model().index(
                        self._shuffled_indices[0], 0
                    )
                return None
        else:
            # Sequential playback
            next_row = current_index.row() + 1
            if next_row < count:
                return self._library.get_current_song_model().index(next_row, 0)
            elif self._repeat_mode == self.REPEAT_ALL:
                return self._library.get_current_song_model().index(
                    0, 0
                )  # Wrap around to beginning
            else:
                return None  # End of playlist

    def _get_previous_index(self, current_index):
        """Get the previous song index based on current settings"""
        count = self._library.get_current_song_model().rowCount()
        if count == 0:
            return None

        if self._repeat_mode == self.REPEAT_TRACK:
            return current_index

        if self._shuffle_mode:
            if not self._shuffled_indices:
                self._generate_shuffled_indices()

            try:
                current_pos = self._shuffled_indices.index(current_index.row())
                if current_pos > 0:
                    return self._library.get_current_song_model().index(
                        self._shuffled_indices[current_pos - 1], 0
                    )
                elif self._repeat_mode == self.REPEAT_ALL:
                    return self._library.get_current_song_model().index(
                        self._shuffled_indices[-1], 0
                    )  # Wrap around to end
                else:
                    return None  # Beginning of shuffled list
            except ValueError:
                # Current index not in shuffled list, regenerate
                self._generate_shuffled_indices()
                if self._shuffled_indices:
                    return self._library.get_current_song_model().index(
                        self._shuffled_indices[0], 0
                    )
                return None
        else:
            # Sequential playback
            prev_row = current_index.row() - 1
            if prev_row >= 0:
                return self._library.get_current_song_model().index(prev_row, 0)
            elif self._repeat_mode == self.REPEAT_ALL:
                return self._library.get_current_song_model().index(
                    count - 1, 0
                )  # Wrap around to end
            else:
                return None  # Beginning of playlist

    @Slot(str)  # type: ignore
    def play(self, path: str | None = None):
        """Play or resume playback.
        If a path is provided, load and play the song.
        If no path is provided, resume playback if paused.

        Args:
            path: The path to the audio file. Defaults to None.
        """
        if path:
            try:
                if (
                    path != self._current_song_path
                    or self._playback_state == Gst.State.NULL
                ):
                    self.set_current_song_path(path)
                    # Stop current playback before loading new file
                    self.player.set_state(Gst.State.NULL)
                    # Set the URI
                    if path.startswith(("http://", "https://", "file://")):
                        uri = path
                    else:
                        uri = Gst.filename_to_uri(path)
                    self.player.set_property("uri", uri)
                    logger.info(f"Playing song: {path}")
                self.player.set_state(Gst.State.PLAYING)
            except Exception:
                logger.exception("Error playing song", stack_info=True)
        elif self._playback_state == Gst.State.PAUSED:
            self.player.set_state(Gst.State.PLAYING)
            logger.info("Resuming playback")
        else:
            song_path = self._library.getCurrentSongPath()
            if song_path:
                self.play(song_path)
            else:
                logger.info("No song to play")

    @Slot()
    def pause(self):
        """Pause playback."""
        if self._playback_state == Gst.State.PLAYING:
            logger.info("Pausing playback")
            self.player.set_state(Gst.State.PAUSED)

    @Slot()
    def stop(self):
        """Stop playback."""
        self.player.set_state(Gst.State.NULL)
        logger.info("Stopping playback")

    @Slot(str)  # type: ignore
    def toggle_playback(self, path: str | None = None):
        """Toggle between play and pause.
        If a path is provided, load and
        play/pause the song based on current state.

        Args:
            path: The path to the audio file. Defaults to None.
        """
        current_state = self._playback_state

        if path:
            if path != self._current_song_path or current_state == Gst.State.NULL:
                self.play(path)
            elif current_state == Gst.State.PLAYING:
                self.pause()
            else:
                self.play()
        else:
            if current_state == Gst.State.PLAYING:
                self.pause()
            # MODIFIED: Use selection model
            elif self._library.getCurrentSongPath():
                self.play()

    @Slot(int)  # type: ignore
    def seek(self, position_ms: int):
        """Seek to position in milliseconds

        Args:
            position_ms: The position to seek to in milliseconds.
        """
        if self._playback_state in (Gst.State.PLAYING, Gst.State.PAUSED):
            # Convert to nanoseconds for GStreamer
            position_ns = position_ms * 1000000
            logger.info(f"Seeking to position: {position_ms}ms")
            self.player.seek_simple(
                Gst.Format.TIME,
                Gst.SeekFlags.FLUSH | Gst.SeekFlags.KEY_UNIT,
                position_ns,
            )

    @Slot()  # type: ignore
    def skip_forward(self):
        """Skip to next song based on current playback modes"""
        # MODIFIED: Use selection model
        current_index = self._library.get_current_selection_model().currentIndex()

        # If we're in REPEAT_ONE_SONG mode and already playing, do nothing
        if (
            self._repeat_mode == self.REPEAT_ONE_SONG
            and self._playback_state == Gst.State.PLAYING
        ):
            logger.info("Skip forward ignored in one song mode")
            return

        # If in REPEAT_TRACK mode, just restart the current song
        if (
            self._repeat_mode == self.REPEAT_TRACK
            and self._playback_state == Gst.State.PLAYING
        ):
            self.seek(0)
            logger.info("Restarting current track (repeat track mode)")
            return

        if not current_index.isValid():
            # No song selected, select first song
            if self._library.get_current_song_model().rowCount() > 0:
                # In shuffle mode, use first shuffled index
                if self._shuffle_mode:
                    if not self._shuffled_indices:
                        self._generate_shuffled_indices()
                    if self._shuffled_indices:
                        index_to_play = self._library.get_current_song_model().index(
                            self._shuffled_indices[0], 0
                        )
                        # MODIFIED: Use selection model
                        self._library.get_current_selection_model().setCurrentIndex(
                            index_to_play,
                            QItemSelectionModel.NoUpdate,  # type: ignore
                        )
                        song_path = self._library.getCurrentSongPath()
                        self.play(song_path)
                    return

                # Normal sequential mode
                index_to_play = self._library.get_current_song_model().index(0, 0)
                self._library.get_current_selection_model().setCurrentIndex(
                    index_to_play,
                    QItemSelectionModel.NoUpdate,  # type: ignore
                )
                song_path = self._library.getCurrentSongPath()
                self.play(song_path)
        else:
            # Go to next song based on current mode
            next_index = self._get_next_index(current_index)

            if next_index is not None:
                self._library.get_current_selection_model().setCurrentIndex(
                    next_index,
                    QItemSelectionModel.NoUpdate,  # type: ignore
                )
                song_path = self._library.getCurrentSongPath()
                self.play(song_path)
            else:
                logger.info("End of playlist reached")

    @Slot()  # type: ignore
    def skip_backward(self):
        """Skip to previous song or restart current song based on current playback modes"""
        # MODIFIED: Use selection model
        current_index = self._library.get_current_selection_model().currentIndex()

        # If we're in REPEAT_ONE_SONG mode, do nothing
        if self._repeat_mode == self.REPEAT_ONE_SONG:
            logger.info("Skip backward ignored in one song mode")
            return

        # If we're more than 3 seconds into the song, restart it
        if self._position > 3000:
            self.seek(0)
            return

        # If in REPEAT_TRACK mode, just restart the current song
        if self._repeat_mode == self.REPEAT_TRACK:
            self.seek(0)
            return

        # Otherwise go to previous song
        prev_index = self._get_previous_index(current_index)

        if prev_index is not None:
            self._library.get_current_selection_model().setCurrentIndex(
                prev_index,
                QItemSelectionModel.NoUpdate,  # type: ignore
            )
            song_path = self._library.getCurrentSongPath()
            self.play(song_path)
        else:
            logger.info("Beginning of playlist reached")
            self.seek(0)  # Restart song anyway

    @Slot()  # type: ignore
    def toggle_shuffle(self):
        """Toggle shuffle mode on/off"""
        self.set_shuffle_mode(not self._shuffle_mode)

    @Slot()  # type: ignore
    def cycle_repeat_mode(self):
        """Cycle through repeat modes: Off -> All -> Track -> One Song -> Off"""
        next_mode = (self._repeat_mode + 1) % 4  # Cycle through 0-3
        self.set_repeat_mode(next_mode)
