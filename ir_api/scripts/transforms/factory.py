"""
This module provides a factory function to get the appropriate transform for a given instrument.
"""
from ir_api.scripts.transforms.mari_transforms import MariTransform
from ir_api.scripts.transforms.transform import Transform, MissingTransformError


def get_transform_for_run(instrument) -> Transform:
    """
    Get the appropriate transform for the given instrument and run file
    :param instrument: str - the instrument
    :return: - Transform
    """
    match instrument.lower():
        case "mari":
            return MariTransform()
        case _:
            raise MissingTransformError(f"No transform for instrument {instrument}")
