# src.features.player.services.playback
# ruff: noqa: E402
import logging
import gi

gi.require_version("Gst", "1.0")
from gi.repository import Gst, GLib  # type: ignore
from PySide6.QtCore import Qt, QObject, Signal, Slot, Property

from src.features.library.models import SongModel

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

    Properties:
        position (int): The current playback position in milliseconds.
        duration (int): The total duration of the current song in milliseconds.
        currentTrackPath (str): The file path of the currently playing song.
        playbackState (int): The current GStreamer playback state.
    """

    currentTrackChanged = Signal(str)
    playbackStateChanged = Signal(int)
    positionChanged = Signal(int)  # Position in ms
    durationChanged = Signal(int)  # Duration in ms

    GST_STATE_VOID_PENDING = Gst.State.VOID_PENDING
    """Represents an element that is in the process of changing state, but the
    target state is not yet known."""
    GST_STATE_NULL = Gst.State.NULL
    """The NULL state is the initial state of an element.  It is typically set
    when an element is created or when it is reset."""
    GST_STATE_READY = Gst.State.READY
    """The READY state is the state where an element is prepared to accept data,
    but it is not yet processing data. Buffers are allocated, and the element
    is ready to transition to the PAUSED state."""
    GST_STATE_PAUSED = Gst.State.PAUSED
    """In the PAUSED state, an element is ready to accept and process data, but
    it is not actively doing so. The element is typically waiting for a preroll
    to complete or for the application to explicitly start playback."""
    GST_STATE_PLAYING = Gst.State.PLAYING
    """The PLAYING state is the state where the element is actively processing
    data and time is progressing."""

    def __init__(self, song_model: SongModel):
        """
        Initializes the PlaybackService.

        Args:
            song_model: The model providing song data.
        """
        super().__init__()
        self._song_model = song_model

        self.player = Gst.ElementFactory.make("playbin", "player")
        if not self.player:
            logger.error("Could not create playbin element")

        self.player.set_property("volume", 1.0)

        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self._on_bus_message)

        self._current_song_path = ""
        self._playback_state = Gst.State.NULL

        # Create a mainloop for message processing
        self._main_loop = GLib.MainLoop()
        self._main_loop_thread = GLib.Thread.new("gst-thread", self._run_main_loop)

        self._position = 0
        self._duration = 0

        # Set up a timer to poll position during playback
        self._position_timer = None
        self._setup_position_timer()

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
            # End of stream
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
                if self._position_timer and not self._position_timer.isActive():
                    self._position_timer.stop()

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
            elif self._current_song_path:
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
        """Skip to next song"""
        current_index = self._song_model.get_selected_song_index()
        if current_index == -1:
            # No song selected, select first song
            if self._song_model.rowCount() > 0:
                self._song_model.set_selected_song_index(0)
                song_path = self._song_model.data(
                    self._song_model.index(0, 0),
                    Qt.UserRole + 4,  # type: ignore
                )
                self.play(song_path)
        else:
            # Go to next song if available
            next_index = current_index + 1
            if next_index < self._song_model.rowCount():
                self._song_model.set_selected_song_index(next_index)
                song_path = self._song_model.data(
                    self._song_model.index(next_index, 0),
                    Qt.UserRole + 4,  # type: ignore
                )
                self.play(song_path)
            else:
                logger.info("Already at last song")

    @Slot()  # type: ignore
    def skip_backward(self):
        """Skip to previous song or restart current song"""
        current_index = self._song_model.get_selected_song_index()

        # If we're more than 3 seconds into the song, restart it
        if self._position > 3000:
            self.seek(0)
            return

        # Otherwise go to previous song
        if current_index > 0:
            prev_index = current_index - 1
            self._song_model.set_selected_song_index(prev_index)
            song_path = self._song_model.data(
                self._song_model.index(prev_index, 0),
                Qt.UserRole + 4,  # type: ignore
            )
            self.play(song_path)
        else:
            logger.info("Already at first song")
            self.seek(0)  # Restart song anyway

    @Slot(int)  # type: ignore
    def handleRowClick(self, row: int):
        """Handle when a row is clicked

        Args:
            row: The row index that was clicked.
        """
        if 0 <= row < self._song_model.rowCount():
            self._song_model.set_selected_song_index(row)
            logging.debug(f"Row {row} clicked")
