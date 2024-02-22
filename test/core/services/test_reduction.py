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
    count_reductions,
    count_reductions_by_instrument,
)


@patch("ir_api.core.services.reduction._REPO")
@patch("ir_api.core.services.reduction.ReductionSpecification")
def test_get_reductions_by_instrument(mock_spec_class, mock_repo):
    """
    Test that get_reductions by instrument makes correct repo call
    :param mock_repo: Mocked Repo class
    :return: None
    """
    spec = mock_spec_class.return_value
    get_reductions_by_instrument("test", limit=5, offset=6)

    mock_repo.find.assert_called_once_with(spec.by_instrument("test", limit=5, offset=6))


@patch("ir_api.core.services.reduction._REPO")
def test_get_reduction_by_id_reduction_exists(mock_repo):
    """
    Test that correct repo call and return is made
    :param mock_repo: Mocked Repo
    :return:
    """
    expected_reduction = Mock()
    mock_repo.find_one.return_value = expected_reduction
    reduction = get_reduction_by_id(1)
    assert reduction == expected_reduction


@patch("ir_api.core.services.reduction._REPO")
def test_get_reduction_by_id_not_found_raises(mock_repo):
    """
    Test MissingRecordError raised when repo returns None
    :param mock_repo: Mocked Repo
    :return: None
    """
    mock_repo.find_one.return_value = None
    with pytest.raises(MissingRecordError):
        get_reduction_by_id(1)


@patch("ir_api.core.services.reduction._REPO")
@patch("ir_api.core.services.reduction.ReductionSpecification")
def test_get_reductions_by_experiment_number(mock_spec_class, mock_repo):
    """
    Test correct Repo calls are made for by experiment number
    :param mock_repo: The Mocked Repo
    :return: None
    """
    spec = mock_spec_class.return_value
    get_reductions_by_experiment_number(123456, limit=6, offset=7)

    mock_repo.find.assert_called_once_with(spec.by_experiment_number(experiment_number=123456, limit=6, offset=7))


@patch("ir_api.core.services.reduction._REPO")
def test_count_reductions(mock_repo):
    """
    Test count is called
    :return: None
    """
    count_reductions()
    mock_repo.count.assert_called_once()


@patch("ir_api.core.services.reduction._REPO")
@patch("ir_api.core.services.reduction.ReductionSpecification")
def test_count_reductions_by_instrument(mock_spec_class, mock_repo):
    """
    Test count by instrument
    :param mock_repo: mock repo fixture
    :return: None
    """
    spec = mock_spec_class.return_value
    count_reductions_by_instrument("TEST")
    mock_repo.count.assert_called_once_with(spec.by_instrument("TEST"))
