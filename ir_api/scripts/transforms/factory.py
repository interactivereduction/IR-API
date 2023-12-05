"""
This module provides a factory function to get the appropriate transform for a given instrument.
"""
import logging

from ir_api.scripts.transforms.mari_transforms import MariTransform
from ir_api.scripts.transforms.osiris_transform import OsirisTransform
from ir_api.scripts.transforms.test_transforms import TestTransform
from ir_api.scripts.transforms.tosca_transform import ToscaTransform
from ir_api.scripts.transforms.transform import Transform, MissingTransformError

logger = logging.getLogger(__name__)


def get_transform_for_instrument(instrument: str) -> Transform:
    """
    Get the appropriate transform for the given instrument and run file
    :param instrument: str - the instrument
    :return: - Transform
    """
    logger.info("Getting transform for instrument: %s", instrument)
    match instrument.lower():
        case "mari":
            return MariTransform()
        case "tosca":
            return ToscaTransform()
        case "osiris":
            return OsirisTransform()
        case "test":
            return TestTransform()
        case _:
            raise MissingTransformError(f"No transform for instrument {instrument}")
