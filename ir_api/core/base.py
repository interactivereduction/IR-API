"""
base module contains common base classes and the reduction state enum
"""
from __future__ import annotations

import enum
from abc import ABC

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Entity(ABC):
    """
    An abstract base class for domain entities. This class serves as a base for all domain entities in the application.
    Acting as a pseudo marker interface.

    Subclasses should implement their specific attributes and behavior.
    """


class Base(DeclarativeBase):
    """
    Base class for SQLAlchemy ORM models. It includes a primary key `id` attribute.

    Attributes:
        id (Mapped[int]): The primary key column for the ORM model.
    """

    id: Mapped[int] = mapped_column(primary_key=True)


class ReductionState(enum.Enum):
    """
    Enum for reduction status
    """

    SUCCESSFUL = "Successful"
    UNSUCCESSFUL = "Unsuccessful"
    ERROR = "Error"
    NOT_STARTED = "NotStarted"
