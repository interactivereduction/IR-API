"""
Module containing the REST endpoints
"""
from typing import Optional

from fastapi import APIRouter
from starlette.background import BackgroundTasks

from ir_api.core.responses import PreScriptResponse
from ir_api.scripts.acquisition import (
    get_script_for_reduction,
    write_script_locally,
    get_script_by_sha,
)
from ir_api.scripts.pre_script import PreScript

ROUTER = APIRouter()


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


@ROUTER.get("/instrument/{instrument}/script/sha/{sha}")
async def get_pre_script_by_sha(
    instrument: str, sha: str, reduction_id: Optional[int] = None
) -> PreScriptResponse:
    """

    :param instrument:
    :param sha:
    :param reduction_id:
    :return:
    """
    return get_script_by_sha(instrument, sha, reduction_id).to_response()
