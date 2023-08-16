"""
Service Layer for reductions
"""
from typing import Optional, Sequence

from ir_api.core.model import Reduction, Run, Instrument
from ir_api.core.repositories import ReductionRepo

_REDUCTION_REPO = ReductionRepo()


def get_reductions_by_instrument(
    instrument: str, limit: Optional[int] = None, offset: Optional[int] = None
) -> Sequence[Reduction]:
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
