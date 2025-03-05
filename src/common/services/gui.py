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
from src.features.tracks.models import TrackTableModel

logger = logging.getLogger(__name__)


class GuiServices:
    def __init__(self, backend: BackendServices):
        self.app = QGuiApplication(sys.argv)
        self.engine = QQmlApplicationEngine()
        self.backend = backend

        self.directory_handler = DirectoryHandler(self.backend)
        self.track_table_model = TrackTableModel(self.backend.tracks_repository)

        self.backend.scanFinished.connect(self._on_scan_finished)
        self.backend.scanError.connect(self._on_scan_error)

        QQuickStyle.setStyle(settings.qt_style)
        self._setup_context_properties()

    def _setup_context_properties(self):
        self.engine.rootContext().setContextProperty(
            "trackTableModel", self.track_table_model
        )
        self.engine.rootContext().setContextProperty(
            "directoryHandler", self.directory_handler
        )
        self.engine.rootContext().setContextProperty("backend", self.backend)

    def _on_scan_finished(self):
        """Handle scan finished event."""
        logger.info("Library scan finished, refreshing track table model")
        self.track_table_model.refresh()

    def _on_scan_error(self):
        """Handle scan error event."""
        logger.info("Library scan suspended, refreshing track table model")
        self.track_table_model.refresh()

    def run(self):
        self.engine.load(Path(SRC_PATH) / "Main.qml")
        if not self.engine.rootObjects():
            sys.exit(-1)
        exit_code = self.app.exec()
        del self.engine
        sys.exit(exit_code)
