"""
Service Layer for reductions
"""
from typing import Sequence, Literal

from ir_api.core.exceptions import MissingRecordError
from ir_api.core.model import Reduction
from ir_api.core.repositories import Repo
from ir_api.core.specifications.reduction import ReductionSpecification

ORDER_LITERALS = Literal[
    "reduction_start",
    "reduction_end",
    "reduction_state",
    "id",
    "run_start",
    "run_end",
    "output",
    "experiment_number",
    "experiment_title",
]

_REPO: Repo[Reduction] = Repo()


def get_reductions_by_instrument(
    instrument: str,
    limit: int = 0,
    offset: int = 0,
    order_by: ORDER_LITERALS = "reduction_start",
    order_direction: Literal["asc", "desc"] = "desc",
) -> Sequence[Reduction]:
    """
    Given an instrument name return a sequence of reductions for that instrument. Optionally providing a limit and
    offset to be applied to the sequence
    :param instrument: (str) - The instrument to get by
    :param limit: (int) - the maximum number of results to be allowed in the sequence
    :param offset: (int) - the number of reductions to offset the sequence from the entire reduction set
    :param order_direction: (str) Direction to der by "asc" | "desc"
    :param order_by: (str) Field to order by.
    :return: Sequence of Reductions for an instrument
    """
    return _REPO.find(
        ReductionSpecification().by_instrument(
            instrument=instrument, limit=limit, offset=offset, order_by=order_by, order_direction=order_direction
        )
    )


def get_reduction_by_id(reduction_id: int) -> Reduction:
    """
    Given an ID return the reduction with that ID
    :param reduction_id: The id of the reduction to search for
    :return: The reduction
    :raises: MissingRecordError when no reduction for that ID is found
    """
    reduction = _REPO.find_one(ReductionSpecification().by_id(reduction_id))
    if reduction is None:
        raise MissingRecordError(f"No Reduction for id {reduction_id}")
    return reduction


def get_reductions_by_experiment_number(
    experiment_number: int,
    limit: int = 0,
    offset: int = 0,
    order_by: Literal["reduction_start", "reduction_end", "reduction_state", "id"] = "reduction_start",
    order_direction: Literal["asc", "desc"] = "desc",
) -> Sequence[Reduction]:
    """
    Given an experiment number, return all reductions for that experiment
    :param experiment_number: The experiment number
    :param limit: (int) - the maximum number of results to be allowed in the sequence
    :param offset: (int) - the number of reductions to offset the sequence from the entire reduction set
    :param order_direction: (str) Direction to der by "asc" | "desc"
    :param order_by: (str) Field to order by.
    :return: List of reductions
    """
    return _REPO.find(
        ReductionSpecification().by_experiment_number(
            experiment_number=experiment_number,
            limit=limit,
            offset=offset,
            order_direction=order_direction,
            order_by=order_by,
        )
    )


def count_reductions_by_instrument(instrument: str) -> int:
    """
    Given an instrument name, count the reductions for that instrument
    :param instrument: Instrument to count from
    :return: Number of reductions
    """
    return _REPO.count(ReductionSpecification().by_instrument(instrument=instrument))


def count_reductions() -> int:
    """
    Count the total number of reductions
    :return: (int) number of reductions
    """
    return _REPO.count(ReductionSpecification().all())
