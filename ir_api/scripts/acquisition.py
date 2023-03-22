"""
Acquisition module contains all the functionality for obtaining the script locally and from the remote repository
"""
import logging
from typing import Optional

import requests

from ir_api.scripts.script import Script


logger = logging.getLogger(__name__)

# INSTRUMENTS = ["foo", "bar", "baz"]
#
#
# def get_all_scripts() -> None:
#     """
#     Get each script from the remote repository and write them locally
#     :return: None
#     """
#     for instrument in INSTRUMENTS:
#         script = get_by_instrument_name(instrument)
#         write_script_locally(script)


def _get_script_from_remote(instrument: str) -> Script:
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
        return Script(request.text, is_latest=True)

    except ConnectionError:
        # log exception
        logger.warning("Could not get %s script from remote", instrument)
        raise


def _get_script_locally(instrument: str) -> Script:
    """
    Get the local copy of the script for the given instrument
    :param instrument: str - instrument name
    :return: None
    """
    try:
        logger.info("Attempting to get %s script locally...", instrument)
        with open(f"ir_api/local_scripts/{instrument}.py", "r", encoding="utf-8") as fle:
            return Script(value="".join(line for line in fle))
    except FileNotFoundError as exc:
        logger.exception("Could not retrieve %s script locally", instrument)
        raise RuntimeError(f"Unable to load any script for instrument: {instrument}") from exc


def write_script_locally(script: Script, instrument: str) -> None:
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
        with open(f"ir_api/local_scripts/{instrument}.py", "w+", encoding="utf-8") as fle:
            fle.writelines(script.original_value)


def get_by_instrument_name(instrument: str) -> Script:
    """
    Get the script object for the given instrument
    :param instrument: str - the instrument
    :return: Script - The script object
    """
    try:
        return _get_script_from_remote(instrument)
    except RuntimeError:
        return _get_script_locally(instrument)


def get_script_for_run(instrument: str, run_file: Optional[str] = None) -> Script:
    """
    Get the script object for the given run, and optional run file
    :param instrument: str -  The instrument
    :param run_file: Optional[str] - the run file name. If provided will apply necessary transforms to the script
    :return: Script -  The script
    """
    logger.info("Getting script for instrument: %s...", instrument)
    script = get_by_instrument_name(instrument)
    if run_file:
        # TODO
        # transform = get_transform_for_run(instrument, run_file)
        # transform.apply(script, run_file)
        pass
    return script
