from unittest.mock import Mock, patch, mock_open

import pytest

from ir_api.scripts.acquisition import (
    _get_script_from_remote,
    _get_script_locally,
    write_script_locally,
    get_by_instrument_name,
)
from ir_api.scripts.script import Script


@pytest.fixture
def mock_response():
    response = Mock()
    response.status_code = 200
    response.text = "test script content"
    return response


@patch("requests.get")
def test__get_script_from_remote(mock_get, mock_response):
    mock_get.return_value = mock_response

    instrument = "instrument_1"
    result = _get_script_from_remote(instrument)
    assert result.value == "test script content"
    assert result.is_latest


@patch("requests.get")
def test__get_script_from_remote_failure(mock_get):
    mock_response = Mock()
    mock_response.status_code = 404
    mock_get.return_value = mock_response

    instrument = "instrument_1"
    with pytest.raises(Exception):
        _get_script_from_remote(instrument)


@patch("requests.get")
def test__get_script_from_remote_connection_error(mock_get):
    mock_get.side_effect = ConnectionError

    instrument = "instrument_1"
    with pytest.raises(ConnectionError):
        _get_script_from_remote(instrument)


@patch("builtins.open", new_callable=mock_open, read_data="test script content")
def test__get_script_locally(mock_file):
    instrument = "instrument_1"
    result = _get_script_locally(instrument)
    assert result.value == "test script content"
    assert result.is_latest is False
    mock_file.assert_called_once_with("ir_api/local_scripts/instrument_1.py", "r", encoding="utf-8")


@patch("builtins.open", side_effect=FileNotFoundError)
def test__get_script_locally_not_found(mock_file):
    instrument = "instrument_1"
    with pytest.raises(RuntimeError):
        _get_script_locally(instrument)


@patch("builtins.open", new_callable=mock_open)
def test_write_script_locally(mock_file):
    script = Script("test script content", is_latest=True)
    instrument = "instrument_1"
    write_script_locally(script, instrument)
    mock_file.assert_called_once_with("ir_api/local_scripts/instrument_1.py", "w+", encoding="utf-8")
    mock_file().writelines.assert_called_once_with("test script content")


def test_write_script_locally_no_content():
    script = Script("", is_latest=True)
    instrument = "instrument_1"
    with pytest.raises(RuntimeError):
        write_script_locally(script, instrument)


@patch("ir_api.scripts.acquisition._get_script_from_remote")
@patch("ir_api.scripts.acquisition._get_script_locally")
def test_get_by_instrument_name_remote_(mock_get_local, mock_get_remote):
    instrument = "instrument_1"
    get_by_instrument_name(instrument)
    mock_get_remote.assert_called_once()
    mock_get_local.assert_not_called()


@patch("ir_api.scripts.acquisition._get_script_from_remote", side_effect=RuntimeError)
@patch("ir_api.scripts.acquisition._get_script_locally")
def test_get_by_instrument_name_local(mock_local, mock_remote):
    instrument = "instrument_1"
    get_by_instrument_name(instrument)
    mock_remote.assert_called_once()
    mock_local.assert_called_once()
