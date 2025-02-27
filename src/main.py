# src.main
import logging
import sys
from pathlib import Path

from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle

from src.common.database import get_db_connection, initialize_database
from src.common.utils.headless import Headless
from src.common.utils.path import get_component_paths
from src.common.utils.settings import settings


logger = logging.getLogger()
logger.setLevel(settings.log_level)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


def main():
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()
    QQuickStyle.setStyle(settings.qt_style)
    # for path in get_component_paths():
    #    logger.debug(f"Added component path path {path}")
    #    engine.addImportPath(path)

    engine.load(Path(__file__).parent / "Main.qml")

    if not engine.rootObjects():
        sys.exit(-1)

    exit_code = app.exec()
    del engine
    sys.exit(exit_code)


if __name__ == "__main__":
    # main()
    connection = get_db_connection()
    initialize_database(connection)
    # headless = Headless("", connection)
    # headless.run()
