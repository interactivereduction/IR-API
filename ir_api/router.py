"""
Module containing the REST endpoints
"""
from typing import Optional, List

from fastapi import APIRouter
from starlette.background import BackgroundTasks

from ir_api.core.responses import PreScriptResponse, ReductionResponse, ReductionWithRunsResponse
from ir_api.core.services.reduction import (
    get_reductions_by_instrument,
    get_reduction_by_id,
    get_reductions_by_experiment_number,
)
from ir_api.scripts.acquisition import get_script_for_reduction, write_script_locally
from ir_api.scripts.pre_script import PreScript

ROUTER = APIRouter()


@ROUTER.get("/instrument/{instrument}/script")
async def get_pre_script(
    instrument: str, background_tasks: BackgroundTasks, reduction_id: Optional[int] = None
) -> PreScriptResponse:
    """
    Script URI - Not intended for calling
    :param instrument: the instrument
    :param background_tasks: handled by fastapi
    :param run_file: optional query parameter of runfile, used to apply transform
    :return: ScriptResponse
    """
    script = PreScript(value="")
    # This will never be returned from the api, but is necessary for the background task to run
    try:
        script = get_script_for_reduction(instrument, reduction_id)
        return script.to_response()
    finally:
        background_tasks.add_task(write_script_locally, script, instrument)
        # write the script after to not slow down request


@ROUTER.get("/instrument/{instrument}/reductions")
async def get_reductions_for_instrument(instrument: str, limit: int = 0, offset: int = 0) -> List[ReductionResponse]:
    """
    Retrieve a list of reductions for a given instrument.
    :param instrument: the name of the instrument
    :param limit: optional limit for the number of reductions returned (default is 0, which can be interpreted as no limit)
    :param offset: optional offset for the list of reductions (default is 0)
    :return: List of ReductionResponse objects
    """
    instrument = instrument.upper()
    reductions = get_reductions_by_instrument(instrument, limit=limit, offset=offset)
    return [ReductionResponse.from_reduction(r) for r in reductions]


@ROUTER.get("/reduction/{reduction_id}")
async def get_reduction(reduction_id: int) -> ReductionWithRunsResponse:
    """
    Retrieve a reduction with nested run data, by iD.
    :param reduction_id: the unique identifier of the reduction
    :return: ReductionWithRunsResponse object
    """
    reduction = get_reduction_by_id(reduction_id)
    return ReductionWithRunsResponse.from_reduction(reduction)


@ROUTER.get("/experiment/{experiment_number}/reductions")
async def get_reductions_for_experiment(
    experiment_number: int, limit: int = 0, offset: int = 0
) -> List[ReductionResponse]:
    """
    Retrieve a list of reductions associated with a specific experiment number.
    :param experiment_number: the unique experiment number
    :return: List of ReductionResponse objects
    """
    return [
        ReductionResponse.from_reduction(r)
        for r in get_reductions_by_experiment_number(experiment_number, limit=limit, offset=offset)
    ]
