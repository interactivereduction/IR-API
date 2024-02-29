"""
Tests for run service
"""

from unittest.mock import patch

from ir_api.core.services.run import get_runs_by_instrument, get_run_count_by_instrument, get_total_run_count


@patch("ir_api.core.services.run._REPO")
@patch("ir_api.core.services.run.RunSpecification")
def test_get_runs_by_instrument(mock_spec_class, mock_run_repo):
    """
    Test that get_runs by instrument makes correct repo call
    :param mock_run_repo: Mock repo
    :return: None
    """
    spec = mock_spec_class.return_value
    get_runs_by_instrument("test", limit=5, offset=6)
    mock_run_repo.find.assert_called_once_with(spec.by_instrument(instrument="test", limit=5, offset=6))


@patch("ir_api.core.services.run._REPO")
@patch("ir_api.core.services.run.RunSpecification")
def test_get_run_count_by_instrument(mock_spec_class, mock_repo):
    """
    Test correct repo calls for count by instrument
    :return: None
    """
    spec = mock_spec_class.return_value
    get_run_count_by_instrument("test")
    mock_repo.count.assert_called_once_with(spec.by_instrument(instrument="test", limit=5, offset=6))


@patch("ir_api.core.services.run._REPO")
@patch("ir_api.core.services.run.RunSpecification")
def test_get_total_run_count(mock_spec_class, mock_repo):
    """
    Test correct repo calls for counting all runs
    :return: None
    """
    spec = mock_spec_class.return_value
    get_total_run_count()
    mock_repo.count.assert_called_once_with(spec.all())
