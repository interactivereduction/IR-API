"""
Tests for run service
"""
from typing import Callable
from unittest.mock import patch

from ir_api.core.services.run import get_runs_by_instrument, get_run_count_by_instrument, get_total_run_count


@patch("ir_api.core.services.run._RUN_REPO")
def test_get_runs_by_instrument(mock_run_repo):
    """
    Test that get_runs by instrument makes correct repo call
    :param mock_run_repo: Mock repo
    :return: None
    """
    get_runs_by_instrument("test", limit=5, offset=6)
    assert mock_run_repo.find.call_count == 1
    assert mock_run_repo.find.call_args[1]["limit"] == 5
    assert mock_run_repo.find.call_args[1]["offset"] == 6


@patch("ir_api.core.services.run._RUN_REPO")
def test_get_run_count_by_instrument(mock_repo):
    """
    Test correct repo calls for count by instrument
    :return: None
    """
    get_run_count_by_instrument("test")
    assert mock_repo.count.call_count == 1
    args, _ = mock_repo.count.call_args
    assert isinstance(args[0], Callable)


@patch("ir_api.core.services.run._RUN_REPO")
def test_get_total_run_count(mock_repo):
    """
    Test correct repo calls for counting all runs
    :return: None
    """
    get_total_run_count()
    mock_repo.count.assert_called_once()
