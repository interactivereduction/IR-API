"""
Tests for reduction service
"""
from unittest.mock import patch, Mock

import pytest

from ir_api.core.exceptions import MissingRecordError
from ir_api.core.services.reduction import (
    get_reductions_by_instrument,
    get_reduction_by_id,
    get_reductions_by_experiment_number,
)


@patch("ir_api.core.services.reduction._REDUCTION_REPO")
def test_get_reductions_by_instrument(mock_repo):
    get_reductions_by_instrument("test", limit=5, offset=6)

    assert mock_repo.find.call_count == 1
    assert mock_repo.find.call_args[1]["limit"] == 5
    assert mock_repo.find.call_args[1]["offset"] == 6


@patch("ir_api.core.services.reduction._REDUCTION_REPO")
def test_get_reduction_by_id_reduction_exists(mock_repo):
    expected_reduction = Mock()
    mock_repo.find_one.return_value = expected_reduction
    reduction = get_reduction_by_id(1)
    assert reduction == expected_reduction


@patch("ir_api.core.services.reduction._REDUCTION_REPO")
def test_get_reduction_by_id_not_found_raises(mock_repo):
    mock_repo.find_one.return_value = None
    with pytest.raises(MissingRecordError):
        get_reduction_by_id(1)


@patch("ir_api.core.services.reduction._REDUCTION_REPO")
def test_get_reductions_by_experiment_number(mock_repo):
    get_reductions_by_experiment_number(123456, limit=6, offset=7)

    assert mock_repo.find.call_count == 1
    assert mock_repo.find.call_args[1]["limit"] == 6
    assert mock_repo.find.call_args[1]["offset"] == 7
