"""
This module defines repository classes for handling data access operations on
database tables mapped to SQLAlchemy ORM models for the `Script`, `Reduction`, `Run`,
and `Instrument` entities.
"""
import logging
import os
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Type, Optional, Callable, Sequence, Union

from sqlalchemy import create_engine, select, LambdaElement, ColumnElement, QueuePool
from sqlalchemy.exc import MultipleResultsFound, NoResultFound
from sqlalchemy.orm import sessionmaker

from ir_api.core.exceptions import NonUniqueRecordError
from ir_api.core.model import Script, Reduction, Run, Instrument, Base

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=Base)

DB_USERNAME = os.environ.get("DB_USERNAME", "postgres")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "password")
DB_IP = os.environ.get("DB_IP", "localhost")
ENGINE = create_engine(
    f"postgresql+psycopg2://{DB_USERNAME}:{DB_PASSWORD}@{DB_IP}:5432/interactive-reduction",
    poolclass=QueuePool,
    pool_size=20,
)
SESSION = sessionmaker(ENGINE)


class ReadOnlyRepo(ABC, Generic[T]):
    """
    A generic read-only repository class for handling data access operations on
    database tables mapped to SQLAlchemy ORM models.

    This class should be subclassed and the `_model_type` property should be implemented
    to provide the specific ORM model for the corresponding repository.
    """

    def __init__(self) -> None:
        self._session = SESSION

    @property
    @abstractmethod
    def _model_type(self) -> Type[T]:
        pass

    def find_one(
        self, filter_expression: Callable[[Type[T]], Union[LambdaElement, ColumnElement["bool"]]]
    ) -> Optional[T]:
        """
        Find the single entity, if more than one is returned, a NonUniqueRecordError will be raised

        :param filter_expression: (Callable[[Type[T]], ColumnElement["bool"]]) The filter expression to be applied.
        :return: (Optional[T]) The found entity, or None if not found.
        """
        logger.info(
            "Finding one: %s",
            self._model_type,
        )
        with self._session() as session:
            query = select(self._model_type)
            query = query.filter(filter_expression(self._model_type))
            try:
                return session.execute(query).scalars().one()
            except NoResultFound:
                return None
            except MultipleResultsFound as exc:
                logger.error("Non unique record found for filter: %s", filter_expression)
                raise NonUniqueRecordError() from exc

    def find(self, filter_expression: Callable[[Type[T]], Union[LambdaElement, ColumnElement["bool"]]]) -> Sequence[T]:
        """
        Find entities that match a specified filter expression.

        :param filter_expression: (Callable[[Type[T]], ColumnElement["bool"]]) The filter expression to be applied.
        :return: (Sequence[T]) A sequence of found entities.
        """
        logger.info("Finding %s", self._model_type)
        with self._session() as session:
            query = select(self._model_type)
            query = query.filter(filter_expression(self._model_type))
            return session.execute(query).scalars().all()


class CRUDRepo(ReadOnlyRepo[T], ABC):
    """
    A generic repository class for handling CRUD operations (Create, Read, Update, Delete) on
    database tables mapped to SQLAlchemy ORM models. Inherits from `ReadOnlyRepo`.

    This class should be subclassed and the `_model_type`, `_entity_type`, and `_transformer`
    properties should be implemented to provide the specific ORM model, domain entity, and
    transformer for the corresponding repository.
    """

    def insert(self, entity: T) -> None:
        """
        Insert a new entity into the database.

        :param entity: (U) The entity to be inserted.
        """
        # TODO: Phase 2

    def update(self, model: T) -> None:
        """
        Update an existing entity in the database.

        :param model: (U) The entity with updated values.
        """
        # TODO: Phase 2

    def delete(self, entity: T) -> None:
        """
        Delete an existing entity from the database.

        :param entity: (U) The entity to be deleted.
        """
        # TODO: Phase 2


class ScriptRepo(ReadOnlyRepo[Script]):
    """
    A specific repository class for handling data access operations for the `Script` entity.
    Inherits from `ReadOnlyRepo`.
    """

    @property
    def _model_type(self) -> Type[Script]:
        return Script


class ReductionRepo(ReadOnlyRepo[Reduction]):
    """
    A specific repository class for handling data access operations for the `Reduction` entity.
    Inherits from `ReadOnlyRepo`.
    """

    @property
    def _model_type(self) -> Type[Reduction]:
        return Reduction


class RunRepo(ReadOnlyRepo[Run]):
    """
    A specific repository class for handling data access operations for the `Run` entity.
    Inherits from `ReadOnlyRepo`.
    """

    @property
    def _model_type(self) -> Type[Run]:
        return Run


class InstrumentRepo(ReadOnlyRepo[Instrument]):
    """
    A specific repository class for handling data access operations for the `Instrument` entity.
    Inherits from `ReadOnlyRepo`.
    """

    @property
    def _model_type(self) -> Type[Instrument]:
        return Instrument
