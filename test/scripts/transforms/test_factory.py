import pytest

from ir_api.scripts.transforms.factory import get_transform_for_run
from ir_api.scripts.transforms.mari_transforms import MariTransform
from ir_api.scripts.transforms.transform import MissingTransformError


def test_get_transform_for_run_mari():
    instrument = "mari"
    transform = get_transform_for_run(instrument)
    assert isinstance(transform, MariTransform)


def test_get_transform_for_run_unknown_instrument():
    instrument = "unknown"
    with pytest.raises(MissingTransformError) as excinfo:
        get_transform_for_run(instrument)
    assert str(excinfo.value) == f"No transform for instrument {instrument}"
