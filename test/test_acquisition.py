"""
Tests for script acquisition
"""
from unittest.mock import Mock, patch, mock_open

import pytest

from ir_api.scripts.acquisition import (
    _get_script_from_remote,
    _get_script_locally,
    write_script_locally,
    get_by_instrument_name,
)
from ir_api.scripts.script import Script

INSTRUMENT = "instrument_1"


@pytest.fixture
def mock_response():
    """
    Response pytest fixture
    :return:
    """
    response = Mock()
    response.status_code = 200
    response.text = "test script content"
    return response


@patch("requests.get")
def test__get_script_from_remote(mock_get, mock_response):
    """
    Test script is created from remote request
    :param mock_get: mock - request.get mock
    :param mock_response: mock - the mocked response object
    :return: None
    """
    mock_get.return_value = mock_response

    result = _get_script_from_remote(INSTRUMENT)
    assert result.value == "test script content"
    assert result.is_latest


@patch("requests.get")
def test__get_script_from_remote_failure(mock_get, mock_response):
    """Test Runtime Error is raised when remote acquisition fails"""
    mock_response.status_code = 404
    mock_get.return_value = mock_response

    with pytest.raises(RuntimeError):
        _get_script_from_remote(INSTRUMENT)


@patch("requests.get")
def test__get_script_from_remote_connection_error(mock_get, caplog):
    """
    Test exception is logged, then reraised when remote is not reachable
    :param mock_get: mock - the mock request.get
    :param caplog: the pytest log capture object
    :return: None
    """
    mock_get.side_effect = ConnectionError

    with pytest.raises(ConnectionError):
        _get_script_from_remote(INSTRUMENT)
        assert "Could not get instrument_1 script from remote" in caplog.text


@patch("builtins.open", new_callable=mock_open, read_data="test script content")
def test__get_script_locally(mock_file):
    """
    Test script is read locally
    :param mock_file: Mock - mocked file context manager
    :return: None
    """
    result = _get_script_locally(INSTRUMENT)
    assert result.value == "test script content"
    assert result.is_latest is False
    mock_file.assert_called_once_with("ir_api/local_scripts/instrument_1.py", "r", encoding="utf-8")


@patch("builtins.open", side_effect=FileNotFoundError)
def test__get_script_locally_not_found(_):
    """
    Test RunTimeError is raised when script not obtainable locally
    :param _: Discarded mock
    :return: None
    """
    with pytest.raises(RuntimeError):
        _get_script_locally(INSTRUMENT)


@patch("builtins.open", new_callable=mock_open)
def test_write_script_locally(mock_file):
    """
    Test script is written locally
    :param mock_file: Mock - mocked file context manager
    :return: None
    """
    script = Script("test script content", is_latest=True)
    write_script_locally(script, INSTRUMENT)
    mock_file.assert_called_once_with("ir_api/local_scripts/instrument_1.py", "w+", encoding="utf-8")
    mock_file().writelines.assert_called_once_with("test script content")


@patch("ir_api.scripts.acquisition._get_script_from_remote")
@patch("ir_api.scripts.acquisition._get_script_locally")
def test_get_by_instrument_name_remote_(mock_get_local, mock_get_remote):
    """
    test will not get locally when script retrieved from remote
    :param mock_get_local: mock - mocked get local
    :param mock_get_remote: mock - mocked get remote
    :return: None
    """
    get_by_instrument_name(INSTRUMENT)
    mock_get_remote.assert_called_once()
    mock_get_local.assert_not_called()


@patch("ir_api.scripts.acquisition._get_script_from_remote", side_effect=RuntimeError)
@patch("ir_api.scripts.acquisition._get_script_locally")
def test_get_by_instrument_name_local(mock_local, mock_remote):
    """
    Test will attempt to get script locally when remote fails
    :param mock_local: mock - mock get local
    :param mock_remote: mock - mock get remote
    :return: None
    """
    get_by_instrument_name(INSTRUMENT)
    mock_remote.assert_called_once()
    mock_local.assert_called_once()
