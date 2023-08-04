"""
Acquisition module contains all the functionality for obtaining the script locally and from the remote repository
"""
import logging
from typing import Optional

import requests

from ir_api.core.exceptions import MissingRecordError, MissingScriptError
from ir_api.core.repositories import ReductionRepo
from ir_api.scripts.pre_script import PreScript
from ir_api.scripts.transforms.factory import get_transform_for_instrument

logger = logging.getLogger(__name__)

LOCAL_SCRIPT_DIR = "ir_api/local_scripts"


def _get_latest_commit_sha() -> Optional[str]:
    """
    Get the latest commit sha of the autoreduction-script repository
    :return: (str) - the commit sha
    """
    try:
        logger.info("Getting latest commit sha for autoreduction-script repo")
        response = requests.get(
            "https://api.github.com/repos/interactivereduction/autoreduction-scripts/commits/HEAD", timeout=30
        )

        return response.json()["sha"] if response.ok else None

    except Exception as exc:  # pylint:disable=broad-exception-caught
        logger.exception(exc)
        logger.warning("Could not get latest commit sha ")
        return None


def _get_script_from_remote(instrument: str) -> PreScript:
    """
    Get the remote script for given instrument
    :param instrument: str - instrument name
    :return: Script - Returned script
    """

    try:
        logger.info("Attempting to get latest %s script...", instrument)
        request = requests.get(
            f"https://raw.githubusercontent.com/interactivereduction/autoreduction-scripts/main/"
            f"{instrument.upper()}/reduce.py",
            timeout=30,
        )
        if request.status_code != 200:
            logger.warning("Could not get %s script from remote", instrument)
            raise RuntimeError(f"Could not get {instrument} script from remote")
        logger.info("Obtained %s script", instrument)
        sha = _get_latest_commit_sha()
        return PreScript(request.text, is_latest=True, sha=sha)

    except ConnectionError:
        # log exception
        logger.warning("Could not get %s script from remote", instrument)
        raise


def _get_script_locally(instrument: str) -> PreScript:
    """
    Get the local copy of the script for the given instrument
    :param instrument: str - instrument name
    :return: None
    """
    try:
        logger.info("Attempting to get %s script locally...", instrument)
        with open(f"{LOCAL_SCRIPT_DIR}/{instrument}.py", "r", encoding="utf-8") as fle:
            return PreScript(value="".join(line for line in fle))
    except FileNotFoundError as exc:
        logger.exception("Could not retrieve %s script locally", instrument)
        raise MissingScriptError(f"Unable to load any script for instrument: {instrument}") from exc


def write_script_locally(script: PreScript, instrument: str) -> None:
    """
    Write the given script locally
    :param script: Script - the script to write
    :param instrument: str - the instrument
    :return: None
    """
    if script.original_value == "":
        logger.warning("Unable to acquire any script for instrument %s", instrument)
        raise RuntimeError(f"Failed to acquire script for instrument {instrument} from remote and locally")
    if script.is_latest:
        logger.info("Updating local %s script", instrument)
        with open(f"{LOCAL_SCRIPT_DIR}/{instrument}.py", "w+", encoding="utf-8") as fle:
            fle.writelines(script.original_value)


def get_by_instrument_name(instrument: str) -> PreScript:
    """
    Get the script object for the given instrument
    :param instrument: str - the instrument
    :return: Script - The script object
    """
    try:
        return _get_script_from_remote(instrument)
    except RuntimeError:
        return _get_script_locally(instrument)


def get_script_for_reduction(instrument: str, reduction_id: Optional[int] = None) -> PreScript:
    """
    Get the script object for the given instrument, and optional reduction id
    :param instrument: str -  The instrument
    :param reduction_id: Optional[id] - the reduction id. If provided will apply necessary transforms to the script
    :return: PreScript -  The script
    """
    logger.info("Getting script for instrument: %s...", instrument)
    script = get_by_instrument_name(instrument)
    if reduction_id:
        reduction_repo = ReductionRepo()
        logger.info("Querying for reduction: %s", reduction_id)
        reduction = reduction_repo.find_one(lambda r: r.id == reduction_id)
        if not reduction:
            logger.info("Reduction not found")
            raise MissingRecordError(f"No reduction found with id: {reduction_id}")
        logger.info("Reduction %s found", reduction_id)
        transform = get_transform_for_instrument(instrument)
        transform.apply(script, reduction)

    return script
