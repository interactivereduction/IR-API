"""
Provides a generic repository class for performing database operations.
"""
import logging
import os
from typing import Generic, TypeVar, Sequence, Optional

from sqlalchemy import select, func, create_engine, NullPool
from sqlalchemy.exc import NoResultFound, MultipleResultsFound
from sqlalchemy.orm import sessionmaker

from ir_api.core.exceptions import NonUniqueRecordError
from ir_api.core.model import Base
from ir_api.core.specifications.base import Specification

T = TypeVar("T", bound=Base)

logger = logging.getLogger(__name__)

DB_USERNAME = os.environ.get("DB_USERNAME", "postgres")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "password")
DB_IP = os.environ.get("DB_IP", "localhost")

ENGINE = create_engine(
    f"postgresql+psycopg2://{DB_USERNAME}:{DB_PASSWORD}@{DB_IP}:5432/interactive-reduction",
    poolclass=NullPool,
)

SESSION = sessionmaker(ENGINE)


class Repo(Generic[T]):
    """
    A generic repository class for performing database operations on entities of type T.

    This class provides methods to find one or multiple entities based on a specification,
    and to count entities matching a specification. It is designed to work with any entity
    that inherits from the base model class.
    """

    def __init__(self) -> None:
        self._session = SESSION

    def find(self, spec: Specification[T]) -> Sequence[T]:
        """
        Finds entities matching the given specification.

        :param spec: A specification defining the query criteria.
        :return: A sequence of entities of type T that match the specification.
        """
        with self._session() as session:
            query = spec.value
            return session.execute(query).scalars().all()

    def find_one(self, spec: Specification[T]) -> Optional[T]:
        """
        Finds a single entity matching the given specification.

        If no entities are found, None is returned. If multiple entities are found,
        a NonUniqueRecordError is raised.

        :param spec: A specification defining the query criteria.
        :return: An entity of type T that matches the specification, or None if no entities are found.
        :raises NonUniqueRecordError: If more than one entity matches the specification.
        """
        with self._session() as session:
            try:
                return session.execute(spec.value).scalars().one()
            except NoResultFound:
                logger.info("No result found for IMPROVE THIS LOGGING")
                return None
            except MultipleResultsFound as exc:
                logger.error("Non unique record found for IMPROVE THIS LOGGING")
                raise NonUniqueRecordError() from exc

    def count(self, spec: Specification[T]) -> int:
        """
        Counts the number of entities matching the given specification.

        :param spec: A specification defining the query criteria.
        :return: The count of entities of type T that match the specification.
        """
        with self._session() as session:
            result = session.execute(select(func.count()).select_from(spec.value))
            return result.scalar() if result else 0
