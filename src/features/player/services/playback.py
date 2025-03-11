# src.features.player.services.playback
# ruff: noqa: E402
import logging
import gi

gi.require_version("Gst", "1.0")
from gi.repository import Gst, GLib  # type: ignore
from PySide6.QtCore import QObject, Signal, Slot, Property

from src.features.tracks.models import TrackTableModel

Gst.init(None)

logger = logging.getLogger(__name__)


class PlaybackService(QObject):
    """
    Audio playback class using GStreamer.
    """

    currentTrackChanged = Signal(str)
    playbackStateChanged = Signal(int)

    GST_STATE_VOID_PENDING = Gst.State.VOID_PENDING
    GST_STATE_NULL = Gst.State.NULL
    GST_STATE_READY = Gst.State.READY
    GST_STATE_PAUSED = Gst.State.PAUSED
    GST_STATE_PLAYING = Gst.State.PLAYING

    def __init__(self, track_model: TrackTableModel):
        super().__init__()
        self._track_model = track_model

        self.player = Gst.ElementFactory.make("playbin", "player")
        if not self.player:
            logger.error("Could not create playbin element")

        self.player.set_property("volume", 1.0)

        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self._on_bus_message)

        self._current_track_path = ""
        self._playback_state = Gst.State.NULL

        # Create a mainloop for message processing
        self._main_loop = GLib.MainLoop()
        self._main_loop_thread = GLib.Thread.new("gst-thread", self._run_main_loop)

    def _run_main_loop(self):
        """Run the GLib main loop for GStreamer message processing"""
        self._main_loop.run()

    def __del__(self):
        """Clean up resources"""
        if hasattr(self, "_main_loop") and self._main_loop.is_running():
            self._main_loop.quit()
        if hasattr(self, "player"):
            self.player.set_state(Gst.State.NULL)

    @Property(str, notify=currentTrackChanged)  # type: ignore
    def currentTrackPath(self):
        """Get the current track path"""
        return self._current_track_path

    @Slot(str)  # type: ignore
    def set_current_track_path(self, path: str):
        if self._current_track_path != path:
            self._current_track_path = path
            self.currentTrackChanged.emit(path)

    @Property(int, notify=playbackStateChanged)  # type: ignore
    def playbackState(self):
        """Get the playback state"""
        return self._playback_state

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

    def _update_playback_state(self, state):
        """Update the playback state and emit signal if changed"""
        if self._playback_state != state:
            self._playback_state = state
            self.playbackStateChanged.emit(state)

    @Slot(str)  # type: ignore
    def play(self, path: str | None = None):
        """Play or resume playback."""
        if path:
            try:
                if (
                    path != self._current_track_path
                    or self._playback_state == Gst.State.NULL
                ):
                    self.set_current_track_path(path)
                    # Stop current playback before loading new file
                    self.player.set_state(Gst.State.NULL)
                    # Set the URI
                    if path.startswith(("http://", "https://", "file://")):
                        uri = path
                    else:
                        uri = Gst.filename_to_uri(path)
                    self.player.set_property("uri", uri)
                    logger.info(f"Playing track: {path}")
                self.player.set_state(Gst.State.PLAYING)
            except Exception:
                logger.exception("Error playing track", stack_info=True)
        elif self._playback_state == Gst.State.PAUSED:
            self.player.set_state(Gst.State.PLAYING)
            logger.info("Resuming playback")
        else:
            logger.info("No track to play")

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
        """Toggle between play and pause."""
        current_state = self._playback_state

        if path:
            if path != self._current_track_path or current_state == Gst.State.NULL:
                self.play(path)
            elif current_state == Gst.State.PLAYING:
                self.pause()
            else:
                self.play()
        else:
            if current_state == Gst.State.PLAYING:
                self.pause()
            elif self._current_track_path:
                self.play()

    @Slot(int)  # type: ignore
    def handleRowClick(self, row):
        """Handle when a row is clicked"""
        if 0 <= row < self._track_model.rowCount():
            self._track_model.set_selected_track_index(row)
            logging.debug(f"Row {row} clicked")
