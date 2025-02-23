# src.common.utils.settings
import logging
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
    log_level: str = "INFO"
    qt_style: str = Field("Basic", alias="application_theme")
    sqlite_db_path: str = Field("", alias="database_path")
    sqlite_echo: bool = Field(False, alias="database_echo")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        logger.debug("#" * 10 + "ENVIRONMENT VARIABLES" + "#" * 10)
        logger.debug(f"Log Level: {self.log_level}")
        logger.debug(f"Application Theme: {self.qt_style}")
        logger.debug(f"Database path: {self.sqlite_db_path}")
        logger.debug("#" * 10)


settings = Settings()
