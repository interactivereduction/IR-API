"""
Tests for script acquisition
"""

import os
from unittest.mock import Mock, patch, mock_open, MagicMock

import pytest

from ir_api.core.exceptions import (
    MissingRecordError,
    MissingScriptError,
    UnsafePathError,
)
from ir_api.scripts.acquisition import (
    _get_script_from_remote,
    _get_script_locally,
    write_script_locally,
    get_by_instrument_name,
    get_script_for_reduction,
    _get_latest_commit_sha,
)
from ir_api.scripts.pre_script import PreScript

# pylint: disable = redefined-outer-name
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
@patch("ir_api.scripts.acquisition._get_latest_commit_sha")
def test_sha_env_set_when_sha_present(mock_sha, mock_get, mock_response):
    """Test that environment variable is set when sha is not None."""
    mock_sha.return_value = "valid_sha"
    mock_get.return_value = mock_response

    _get_script_from_remote(INSTRUMENT)

    assert os.environ["sha"] == "valid_sha"


@patch("requests.get")
@patch("ir_api.scripts.acquisition.os.environ.__setitem__")
@patch("ir_api.scripts.acquisition._get_latest_commit_sha")
def test_sha_env_not_set_when_sha_none(mock_sha, mock_setitem, mock_get, mock_response):
    """Test that environment variable is not set when sha is None."""
    mock_sha.return_value = None
    mock_get.return_value = mock_response

    _get_script_from_remote(INSTRUMENT)

    mock_setitem.assert_not_called()


@patch("requests.get")
@patch("ir_api.scripts.acquisition._get_latest_commit_sha")
def test_prescript_sha_assigned_correctly(mock_sha, mock_get, mock_response):
    """Test that the sha attribute of the PreScript object is assigned the correct value."""
    mock_sha.return_value = "valid_sha"
    mock_get.return_value = mock_response

    result = _get_script_from_remote(INSTRUMENT)
    assert result.sha == "valid_sha"


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
    with pytest.raises(MissingScriptError):
        _get_script_locally(INSTRUMENT)


@patch("builtins.open", new_callable=mock_open)
def test_write_script_locally(mock_file):
    """
    Test script is written locally
    :param mock_file: Mock - mocked file context manager
    :return: None
    """
    script = PreScript("test script content", is_latest=True)
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


@patch("ir_api.scripts.acquisition.get_by_instrument_name")
def test_get_script_for_reduction_no_reduction_id(mock_get_by_name):
    """
    Test base script returned when no id provided
    :param mock_get_by_name: Mock
    :return: None
    """
    expected_script = PreScript(value="some script")
    mock_get_by_name.return_value = expected_script
    result = get_script_for_reduction("some instrument")

    assert result == expected_script


@patch("ir_api.scripts.acquisition.get_transform_for_instrument")
@patch("ir_api.scripts.acquisition.ReductionRepo")
@patch("ir_api.scripts.acquisition.get_by_instrument_name")
def test_get_script_for_reduction_with_valid_reduction_id(mock_get_by_name, mock_repo, mock_get_transform):
    """
    Test transform applied to obtained script when reduction id provided
    :param mock_get_by_name: Mock
    :param mock_repo: Mock
    :param mock_get_transform: Mock
    :return: None
    """
    mock_reduction = MagicMock()
    mock_transform = Mock()
    mock_get_transform.return_value = mock_transform
    mock_repo.return_value.find_one.return_value = mock_reduction
    expected_script = PreScript("some script")
    mock_get_by_name.return_value = expected_script
    result = get_script_for_reduction("some instrument", 1)
    mock_get_by_name.assert_called_once_with("some instrument")
    mock_get_transform.assert_called_once_with("some instrument")
    mock_transform.apply.assert_called_once_with(expected_script, mock_reduction)

    assert result == expected_script


@patch("ir_api.scripts.acquisition.ReductionRepo")
@patch("ir_api.scripts.acquisition.get_by_instrument_name", return_value="some instrument")
def test_get_script_for_reduction_with_invalid_reduction_id(_, mock_repo):
    """
    Test exception raised when reduction id is given but no reduction exists
    :param _: Mock
    :param mock_repo: Mock
    :return: None
    """
    mock_repo.return_value.find_one.return_value = None
    instrument = "some_instrument"
    reduction_id = -1

    with pytest.raises(MissingRecordError) as excinfo:
        get_script_for_reduction(instrument, reduction_id)

    assert f"No reduction found with id: {reduction_id}" in str(excinfo.value)


@patch("ir_api.scripts.acquisition.requests.get")
def test_get_latest_commit_sha_ok(mock_get):
    """
    Test sha is returned when ok
    :param mock_get: mocked get request
    :return: None
    """
    mock_response = Mock()
    mock_response.json.return_value = {"sha": "abcd1234"}
    mock_get.return_value = mock_response

    assert _get_latest_commit_sha() == "abcd1234"


@patch("ir_api.scripts.acquisition.requests.get")
def test_get_latest_commit_sha_not_ok(mock_get):
    """
    Test None is returned for non-ok get
    :param mock_get: mocked get request
    :return: None
    """
    mock_response = Mock()
    mock_response.ok = False
    mock_get.return_value = mock_response

    assert _get_latest_commit_sha() is None


@patch("ir_api.scripts.acquisition.requests.get")
def test_get_latest_commit_sha_returns_none_on_exception(mock_get):
    """
    Test None is still returned if the request results in an exception
    :param mock_get: Mock get
    :return: None
    """
    mock_get.side_effect = Exception
    assert _get_latest_commit_sha() is None


def test_get_by_instrument_path_character_raises_exception():
    """
    Test that an exception is raised when a path character is in the instrument name
    :return: None
    """
    with pytest.raises(UnsafePathError):
        get_by_instrument_name("mari/..")
