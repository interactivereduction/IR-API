"""
Tests for the transform factory function
"""
import pytest

from ir_api.scripts.transforms.factory import get_transform_for_instrument
from ir_api.scripts.transforms.mari_transforms import MariTransform
from ir_api.scripts.transforms.osiris_transform import OsirisTransform
from ir_api.scripts.transforms.test_transforms import TestTransform
from ir_api.scripts.transforms.tosca_transform import ToscaTransform
from ir_api.scripts.transforms.transform import MissingTransformError


def test_get_transform_for_run_mari():
    """
    Test mari transform returned for mari
    :return: None
    """
    instrument = "mari"
    transform = get_transform_for_instrument(instrument)
    assert isinstance(transform, MariTransform)


def test_get_transform_for_tosca():
    """
    Test Tosca transform returned for tosca
    :return: None
    """
    transform = get_transform_for_instrument("tosca")
    assert isinstance(transform, ToscaTransform)


def test_get_transform_for__osiris():
    """
    Test that OsirisTransform is returned for Osiris
    :return: None
    """
    instrument = "osiris"
    transform = get_transform_for_instrument(instrument)
    assert isinstance(transform, OsirisTransform)


def test_get_transform_for_run_test():
    """
    Test that TestTransform returned for TestInstrument
    :return: None
    """
    instrument = "test"
    transform = get_transform_for_instrument(instrument)
    assert isinstance(transform, TestTransform)


def test_get_transform_for_run_unknown_instrument():
    """
    Test that missing transform error raised for unknown instrument
    :return: None
    """
    instrument = "unknown"
    with pytest.raises(MissingTransformError) as excinfo:
        get_transform_for_instrument(instrument)
    assert str(excinfo.value) == f"No transform for instrument {instrument}"
