"""
Module defining specifications for querying Run entities in the IR API.

It includes the RunSpecification class which allows for building complex queries
for Run entities based on various criteria such as instrument, limit, offset,
order by, and order direction.
"""

# pylint: disable=unused-argument
# The limit and offsets in specifications will incorrectly flag as unused. They are used when they are intercepted by
# the paginate decorator
from __future__ import annotations

from typing import Type, Literal

from ir_api.core.model import Run, Instrument
from ir_api.core.specifications.base import Specification, paginate, apply_ordering


class RunSpecification(Specification[Run]):
    """
    A specification class for building queries to fetch Run entities.

    Allows for filtering and ordering runs based on different attributes such as
    instrument name, experiment number, run start/end times, and more.
    """

    @property
    def model(self) -> Type[Run]:
        return Run

    @paginate
    def by_instrument(
        self,
        instrument: str,
        limit: int = 0,
        offset: int = 0,
        order_by: Literal[
            "experiment_number", "run_end", "run_start", "good_frames", "raw_frames", "id", "filename"
        ] = "run_start",
        order_direction: Literal["asc", "desc"] = "desc",
    ) -> RunSpecification:
        """
        Filters runs by the specified instrument and applies ordering, limit, and offset to the query.

        :param instrument: The name of the instrument to filter runs by.
        :param limit: The maximum number of runs to return.
        :param offset: The number of runs to skip before starting to return the results.
        :param order_by: The attribute to order the runs by.
        :param order_direction: The direction to order the runs, either 'asc' for ascending or 'desc' for descending.
        :return: An instance of RunSpecification with the applied filters and ordering.
        """
        self.value = self.value.join(Instrument).where(Instrument.instrument_name == instrument)
        apply_ordering(self.value, self.model, order_by, order_direction)
        return self
