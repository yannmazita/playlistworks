# src.common.repository
import logging
from typing import Generic, TypeVar
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.exc import (
    IntegrityError,
    MultipleResultsFound,
    NoResultFound,
    SQLAlchemyError,
)
from sqlalchemy.orm import Session

from src.common.models import Base
from src.common.schemas import Base as BaseSchema

logger = logging.getLogger(__name__)
Model = TypeVar("Model", bound=Base)
Schema = TypeVar("Schema", bound=BaseSchema)


class DatabaseRepository(Generic[Model, Schema]):
    """
    Repository for performing database queries.

    Attributes:
        model: The model to be used for queries.
    """

    def __init__(self, model: type[Model]) -> None:
        self.model: type[Model] = model

    def create(self, session: Session, data: Schema) -> Model:
        """
        Create a new instance of the model in the database.
        """
        try:
            logger.debug(f"Creating {self.model.__name__}")
            instance = self.model(**data.model_dump())  # type: ignore
            session.add(instance)
            session.commit()
            session.refresh(instance)
            logger.info(
                f"Created {self.model.__name__} with ID {getattr(instance, 'id', 'unknown')}"
            )
            return instance
        except (IntegrityError, SQLAlchemyError, Exception) as e:
            logger.error(f"Error occurred: {e}", exc_info=False)
            session.rollback()
            raise e

    def get_by_attribute(
        self,
        session: Session,
        value: UUID | str,
        column: str = "id",
        with_for_update: bool = False,
    ) -> Model:
        """
        Get an instance of the model from the database.
        """
        try:
            logger.debug(f"Getting {self.model.__name__} with {column} {value}")
            query = select(self.model).where(getattr(self.model, column) == value)

            if with_for_update:
                query = query.with_for_update()

            response = session.execute(query)
            instance = response.scalar_one()
            return instance
        except (MultipleResultsFound, NoResultFound, SQLAlchemyError, Exception) as e:
            logger.error(f"Error occurred: {e}", exc_info=False)
            raise e

    def update_by_attribute(
        self,
        session: Session,
        data: Schema,
        value: UUID | str,
        column: str = "id",
        none_replace: bool = False,
    ) -> Model:
        """
        Update an instance of the model in the database.
        """
        try:
            logger.debug(f"Updating {self.model.__name__} with {column} {value}")
            instance = self.get_by_attribute(
                session, value, column, with_for_update=True
            )

            items = data.model_dump(exclude_unset=True).items()
            for key, val in items:
                if val is None and not none_replace:
                    continue
                setattr(instance, key, val)

            session.add(instance)
            session.commit()
            session.refresh(instance)
            return instance
        except (
            MultipleResultsFound,
            NoResultFound,
            IntegrityError,
            SQLAlchemyError,
            Exception,
        ) as e:
            logger.error(f"Error occurred: {e}", exc_info=False)
            session.rollback()
            raise e

    def delete(self, session: Session, value: UUID | str, column: str = "id") -> Model:
        """
        Delete an instance of the model from the database.
        """
        try:
            logger.debug(f"Deleting {self.model.__name__} with {column} {value}")
            instance = self.get_by_attribute(session, value, column)
            session.delete(instance)
            session.commit()
            return instance
        except (
            MultipleResultsFound,
            NoResultFound,
            IntegrityError,
            SQLAlchemyError,
            Exception,
        ) as e:
            logger.error(f"Error occurred: {e}", exc_info=False)
            session.rollback()
            raise e

    def get_all(self, session: Session, offset: int = 0, limit: int = 100):
        """
        Get all instances of the model from the database.
        """
        try:
            logger.debug(
                f"Fetching {limit} {self.model.__name__} instances from {offset}"
            )
            total_count_query = select(func.count()).select_from(self.model)
            total_count_response = session.execute(total_count_query)
            total_count: int = total_count_response.scalar_one()

            query = select(self.model).offset(offset).limit(limit)
            response = session.execute(query)
            instances = response.scalars().all()
            return instances, total_count
        except (NoResultFound, SQLAlchemyError, Exception) as e:
            logger.error(f"Error occurred: {e}", exc_info=False)
            raise e
