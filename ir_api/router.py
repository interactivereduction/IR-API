"""
Module containing the REST endpoints
"""
from typing import Optional, List, Literal

from fastapi import APIRouter
from starlette.background import BackgroundTasks

from ir_api.core.responses import (
    PreScriptResponse,
    ReductionResponse,
    ReductionWithRunsResponse,
    CountResponse,
)
from ir_api.core.services.reduction import (
    get_reductions_by_instrument,
    get_reduction_by_id,
    get_reductions_by_experiment_number,
    count_reductions,
    count_reductions_by_instrument,
)
from ir_api.scripts.acquisition import (
    get_script_for_reduction,
    write_script_locally,
    get_script_by_sha,
)
from ir_api.scripts.pre_script import PreScript

ROUTER = APIRouter()


@ROUTER.get("/healthz")
async def get() -> Literal["ok"]:
    return "ok"


@ROUTER.get("/instrument/{instrument}/script")
async def get_pre_script(
    instrument: str,
    background_tasks: BackgroundTasks,
    reduction_id: Optional[int] = None,
) -> PreScriptResponse:
    """
    Script URI - Not intended for calling
    :param instrument: the instrument
    :param background_tasks: handled by fastapi
    :param reduction_id: optional query parameter of runfile, used to apply transform
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


@ROUTER.get("/instrument/{instrument}/script/sha/{sha}")
async def get_pre_script_by_sha(instrument: str, sha: str, reduction_id: Optional[int] = None) -> PreScriptResponse:
    """

    :param instrument:
    :param sha:
    :param reduction_id:
    :return:
    """
    return get_script_by_sha(instrument, sha, reduction_id).to_response()


@ROUTER.get("/instrument/{instrument}/reductions")
async def get_reductions_for_instrument(
    instrument: str,
    limit: int = 0,
    offset: int = 0,
    order_by: Literal["reduction_start", "reduction_end", "reduction_state", "id"] = "reduction_start",
    order_direction: Literal["asc", "desc"] = "desc",
) -> List[ReductionResponse]:
    """
    Retrieve a list of reductions for a given instrument.
    :param instrument: the name of the instrument
    :param limit: optional limit for the number of reductions returned (default is 0, which can be interpreted as
    no limit)
    :param offset: optional offset for the list of reductions (default is 0)
    :param order_by: Literal["reduction_start", "reduction_end", "reduction_state", "id"]
    :param order_direction: Literal["asc", "desc"]
    :return: List of ReductionResponse objects
    """
    instrument = instrument.upper()
    reductions = get_reductions_by_instrument(
        instrument, limit=limit, offset=offset, order_by=order_by, order_direction=order_direction
    )
    return [ReductionResponse.from_reduction(r) for r in reductions]


@ROUTER.get("/instrument/{instrument}/reductions/count")
async def count_reductions_for_instrument(
    instrument: str,
) -> CountResponse:
    """
    Count reductions for a given instrument.
    :param instrument: the name of the instrument
    :return: List of ReductionResponse objects
    """
    instrument = instrument.upper()
    return CountResponse(count=count_reductions_by_instrument(instrument))


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
    experiment_number: int,
    limit: int = 0,
    offset: int = 0,
    order_by: Literal["reduction_start", "reduction_end", "reduction_state", "id"] = "reduction_start",
    order_direction: Literal["desc", "asc"] = "desc",
) -> List[ReductionResponse]:
    """
    Retrieve a list of reductions associated with a specific experiment number.
    :param experiment_number: the unique experiment number:
    :param limit: Number of results to limit to
    :param offset: Number of results to offset by
    :param order_by: Literal["reduction_start", "reduction_end", "reduction_state", "id"]
    :param order_direction: Literal["asc", "desc"]
    :return: List of ReductionResponse objects
    """
    return [
        ReductionResponse.from_reduction(r)
        for r in get_reductions_by_experiment_number(
            experiment_number, limit=limit, offset=offset, order_by=order_by, order_direction=order_direction
        )
    ]


@ROUTER.get("/reductions/count")
async def count_all_reductions() -> CountResponse:
    """
    Count all reductions
    :return: CountResponse containing the count
    """
    return CountResponse(count=count_reductions())
