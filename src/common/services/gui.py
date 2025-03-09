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
    def __init__(self, backend: BackendServices):
        self.app = QGuiApplication(sys.argv)
        self.engine = QQmlApplicationEngine()
        self.backend = backend
        self.directory_handler = DirectoryHandler(self.backend)

        self.backend.scanFinished.connect(self._on_scan_finished)
        self.backend.scanError.connect(self._on_scan_error)

        QQuickStyle.setStyle(settings.qt_style)
        self._setup_context_properties()

    def _setup_context_properties(self):
        self.engine.rootContext().setContextProperty(
            "directoryHandler", self.directory_handler
        )
        self.engine.rootContext().setContextProperty("backend", self.backend)
        self.engine.rootContext().setContextProperty(
            "trackTableModel", self.backend.track_model
        )
        if self.backend.playback_service:
            self.engine.rootContext().setContextProperty(
                "playbackService", self.backend.playback_service
            )

    def _on_scan_finished(self, error_paths: list[tuple[Path, Exception]]):
        """Handle scan finished event."""
        logger.info("Library scan finished, refreshing track table model")
        self.backend.track_model.refresh()
        for path, error in error_paths:
            logger.error(f"Failed to scan: {path} - {error}")

    def _on_scan_error(self):
        """Handle scan error event."""
        logger.info("Library scan suspended, refreshing track table model")
        self.backend.track_model.refresh()

    def run(self):
        self.engine.load(Path(SRC_PATH) / "Main.qml")
        if not self.engine.rootObjects():
            sys.exit(-1)
        exit_code = self.app.exec()
        del self.engine
        sys.exit(exit_code)
