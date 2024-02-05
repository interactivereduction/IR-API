"""
Service Layer for runs
"""
from typing import Sequence, Literal

from ir_api.core.model import Instrument, Run
from ir_api.core.repositories import RunRepo

_RUN_REPO = RunRepo()


def get_total_run_count() -> int:
    """
    Get the total number of runs
    :return: The number of runs
    """
    return _RUN_REPO.count()


def get_run_count_by_instrument(instrument: str) -> int:
    """
    Get the total number of runs for the given instrument
    :param instrument: The instrument
    :return: The number of runs
    """
    return _RUN_REPO.count(lambda run: run.instrument.has(Instrument.instrument_name == instrument))


def get_runs_by_instrument(
    instrument: str,
    limit: int = 0,
    offset: int = 0,
    order_by: Literal[
        "experiment_number", "run_end", "run_start", "good_frames", "raw_frames", "id", "filename"
    ] = "run_start",
    order_direction: Literal["asc", "desc"] = "desc",
) -> Sequence[Run]:
    """
    Get the runs for the given instrument
    :param instrument: Instrument name
    :param limit: optional limit to be applied
    :param offset: optional offset to be applied
    :param order_by: optional field to order by
    :param order_direction: optional direction to order by in
    :return: The sequence of runs
    """
    return _RUN_REPO.find(
        lambda run: run.instrument.has(Instrument.instrument_name == instrument),
        limit=limit,
        offset=offset,
        order_by=order_by,
        order_direction=order_direction,
    )
