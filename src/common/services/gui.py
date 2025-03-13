# src.common.services.gui
import logging
import sys
from pathlib import Path

from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle

from src.common.handlers import DirectoryHandler
from src.common.services.backend import BackendServices
from src.common.utils.path import SRC_PATH
from src.common.utils.settings import settings

logger = logging.getLogger(__name__)


class GuiServices:
    """Manages the GUI, connects to backend services, and handles events.

    Attributes:
        app: The Qt application instance.
        engine: The QML engine.
        backend: The backend services instance.
        directory_handler: Handler for directory operations.
    """

    def __init__(self, backend: BackendServices):
        """Initializes the GuiServices.

        Args:
            backend: The backend services instance.
        """
        self.app = QGuiApplication(sys.argv)
        self.engine = QQmlApplicationEngine()
        self.backend = backend
        self.directory_handler = DirectoryHandler(self.backend)

        self.backend.scanFinished.connect(self._on_scan_finished)
        self.backend.scanError.connect(self._on_scan_error)

        QQuickStyle.setStyle(settings.qt_style)
        self._setup_context_properties()

    def _setup_context_properties(self):
        """Sets up context properties for QML.

        This makes Python objects accessible to the QML frontend.
        """
        self.engine.rootContext().setContextProperty(
            "directoryHandler", self.directory_handler
        )
        self.engine.rootContext().setContextProperty("backend", self.backend)
        self.engine.rootContext().setContextProperty(
            "songModel", self.backend.song_model
        )
        if self.backend.playback_service:
            self.engine.rootContext().setContextProperty(
                "playbackService", self.backend.playback_service
            )

    def _on_scan_finished(self, error_paths: list[tuple[Path, Exception]]):
        """Handles the scanFinished signal from the backend.

        Refreshes the song table model and logs any errors.

        Args:
            error_paths: A list of tuples, where each tuple contains
                the path of a file that failed to scan and
                the corresponding exception.
        """
        logger.info("Library scan finished, refreshing song table model")
        self.backend.song_model.refresh()
        for path, error in error_paths:
            logger.error(f"Failed to scan: {path} - {error}")

    def _on_scan_error(self):
        """Handles the scanError signal from the backend.

        Refreshes the song table model.
        """
        logger.info("Library scan suspended, refreshing song table model")
        self.backend.song_model.refresh()

    def run(self):
        """Loads the QML file, starts the event loop, and handles exit."""
        self.engine.load(Path(SRC_PATH) / "Main.qml")
        if not self.engine.rootObjects():
            sys.exit(-1)
        exit_code = self.app.exec()
        del self.engine
        sys.exit(exit_code)
