"""
Main module contains the uvicorn entrypoint
"""
import logging
import sys
from typing import Optional

from fastapi import FastAPI, Request
from starlette.background import BackgroundTasks
from starlette.responses import JSONResponse

from ir_api.core.exceptions import MissingRecordError, MissingScriptError
from ir_api.core.responses import PreScriptResponse
from ir_api.scripts.acquisition import write_script_locally, get_script_for_reduction
from ir_api.scripts.pre_script import PreScript

stdout_handler = logging.StreamHandler(stream=sys.stdout)
logging.basicConfig(
    handlers=[stdout_handler],
    format="[%(asctime)s]-%(name)s-%(levelname)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


app = FastAPI()


@app.exception_handler(MissingRecordError)
async def missing_record_handler(_: Request, __: MissingRecordError) -> JSONResponse:
    """
    Automatically return a 404 when a MissingRecordError is raised
    :param _:
    :param __:
    :return: JSONResponse with 404
    """
    return JSONResponse(
        status_code=404,
        content={"message": "Resource not found"},
    )


@app.exception_handler(MissingScriptError)
async def missing_script_error(_: Request, __: MissingScriptError):
    """
    Automatically return a 404 when the script could not be found locally or remote
    :param _:
    :param __:
    :return:  JSONResponse with 404
    """
    return JSONResponse(
        status_code=404,
        content={
            "message": "The script could not be found locally or on remote, it is likely the script does not exist"
        },
    )


@app.get("/instrument/{instrument}/script")
async def get(instrument: str, background_tasks: BackgroundTasks, run_file: Optional[str] = None) -> ScriptResponse:
    """
    Script URI - Not intended for calling
    :param instrument: the instrument
    :param background_tasks: handled by fastapi
    :param run_file: optional query parameter of runfile, used to apply transform
    :return: ScriptResponse
    """
    script = Script(value="")
    # This will never be returned from the api, but is necessary for the background task to run
    try:
        script = get_script_for_run(instrument, run_file)
        return script.to_response()
    finally:
        background_tasks.add_task(write_script_locally, script, instrument)
        # write the script after to not slow down request
