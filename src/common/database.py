# src.common.database
from contextlib import contextmanager
from typing import Any, Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from src.common.models import Base
from src.common.utils.settings import settings

SQLITE_DB_URL = f"sqlite:///{settings.sqlite_db_path}"


class DatabaseSessionManager:
    def __init__(self, db_url: str, engine_kwargs: dict[str, Any] = {}):
        self._engine = create_engine(db_url, **engine_kwargs)
        self._sessionmaker = sessionmaker(
            autocommit=False, bind=self._engine, expire_on_commit=False
        )

    def close(self):
        if self._engine is None:
            raise Exception("DatabaseSessionManager is not initialized")

        self._engine.dispose()
        self._engine = None
        self._sessionmaker = None

    @contextmanager
    def connect(self):
        if self._engine is None:
            raise Exception("DatabaseSessionManager is not initialized")

        connection = self._engine.connect()
        try:
            yield connection
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    @contextmanager
    def session(self) -> Iterator[Session]:
        if self._sessionmaker is None:
            raise Exception("DatabaseSessionManager is not initialized")

        session = self._sessionmaker()
        try:
            yield session
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()


sessionmanager = DatabaseSessionManager(SQLITE_DB_URL, {"echo": settings.sqlite_echo})


def get_session() -> Iterator[Session]:
    with sessionmanager.session() as session:
        yield session


def create_db_and_tables():
    with sessionmanager._engine.begin() as conn:
        Base.metadata.create_all(bind=conn)
