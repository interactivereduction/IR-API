"""
Service Layer for reductions
"""
from typing import Sequence

from ir_api.core.exceptions import MissingRecordError
from ir_api.core.model import Reduction, Run, Instrument
from ir_api.core.repositories import ReductionRepo

_REDUCTION_REPO = ReductionRepo()


def get_reductions_by_instrument(instrument: str, limit: int = 0, offset: int = 0) -> Sequence[Reduction]:
    """
    Given an instrument name return a sequence of reductions for that instrument. Optionally providing a limit and
    offset to be applied to the sequence
    :param instrument: (str) - The instrument to get by
    :param limit: (int) - the maximum number of results to be allowed in the sequence
    :param offset: (int) - the number of reductions to offset the sequence from the entire reduction set
    :return: Sequence of Reductions for an instrument
    """
    return _REDUCTION_REPO.find(
        lambda reduction: reduction.runs.any(Run.instrument.has(Instrument.instrument_name == instrument)),
        limit=limit,
        offset=offset,
    )


def get_reduction_by_id(id: int) -> Reduction:
    """
    Given an ID return the reduction with that ID
    :param id: The id of the reduction to search for
    :return: The reduction
    :raises: MissingRecordError when no reduction for that ID is found
    """
    reduction = _REDUCTION_REPO.find_one(lambda reduction: reduction.id == id)
    if reduction is None:
        raise MissingRecordError(f"No Reduction for id {id}")
    return reduction


def get_reductions_by_experiment_number(experiment_number: int, limit: int = 0, offset: int = 0) -> Sequence[Reduction]:
    """
    Given an experiment number, return all reductions for that experiment
    :param experiment_number: The experiment number
    :return: List of reductions
    """
    return _REDUCTION_REPO.find(
        lambda reduction: reduction.runs.any(Run.experiment_number == experiment_number), limit=limit, offset=offset
    )
