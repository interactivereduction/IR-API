"""
Main module contains the uvicorn entrypoint
"""
import logging
import sys
from typing import Optional

from fastapi import FastAPI
from starlette.background import BackgroundTasks

from ir_api.scripts.acquisition import write_script_locally, get_script_for_run
from ir_api.scripts.script import Script, ScriptResponse

stdout_handler = logging.StreamHandler(stream=sys.stdout)
logging.basicConfig(
    handlers=[stdout_handler],
    format="[%(asctime)s]-%(name)s-%(levelname)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


app = FastAPI()


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
