"""
API Level Exception Handlers.
"""
from starlette.requests import Request
from starlette.responses import JSONResponse

from ir_api.core.exceptions import MissingRecordError, MissingScriptError


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


async def missing_script_handler(_: Request, __: MissingScriptError) -> JSONResponse:
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
