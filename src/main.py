# src.main
import logging
import sys

from src.common.database import get_db_connection, initialize_database
from src.common.services.backend import BackendServices
from src.common.services.gui import GuiServices
from src.common.utils.settings import settings

logger = logging.getLogger()
logger.setLevel(settings.log_level)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


def main():
    try:
        connection = get_db_connection()
        initialize_database(connection)
        backend = BackendServices(connection)
        gui = GuiServices(backend)

        gui.run()

    except Exception as e:
        logger.exception(f"An error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
