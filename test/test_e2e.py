"""
end-to-end tests
"""
import re
# pylint: disable=line-too-long
from unittest.mock import patch

import pytest
from starlette.testclient import TestClient

from ir_api.core.model import Base, Instrument, Run, Reduction, ReductionState
from ir_api.core.repositories import ENGINE, SESSION
from ir_api.ir_api import app

client = TestClient(app)

TEST_INSTRUMENT = Instrument(instrument_name="test")
TEST_REDUCTION = Reduction(
    reduction_inputs={
        "ei": "'auto'",
        "sam_mass": 0.0,
        "sam_rmm": 0.0,
        "monovan": 0,
        "remove_bkg": True,
        "sum_runs": False,
        "runno": 25581,
        "mask_file_link": "https://raw.githubusercontent.com/pace-neutrons/InstrumentFiles/"
        "964733aec28b00b13f32fb61afa363a74dd62130/mari/mari_mask2023_1.xml",
        "wbvan": 12345,
    },
    reduction_state=ReductionState.NOT_STARTED,
)
TEST_RUN = Run(
    instrument=TEST_INSTRUMENT,
    title="Whitebeam - vanadium - detector tests - vacuum bad - HT on not on all LAB",
    experiment_number=1820497,
    filename="MAR25581.nxs",
    run_start="2019-03-22T10:15:44",
    run_end="2019-03-22T10:18:26",
    raw_frames=8067,
    good_frames=6452,
    users="Wood,Guidi,Benedek,Mansson,Juranyi,Nocerino,Forslund,Matsubara",
    reductions=[TEST_REDUCTION],
)


@pytest.fixture(scope="module", autouse=True)
def setup():
    """
    Setup database pre-testing
    :return:
    """
    Base.metadata.drop_all(ENGINE)
    Base.metadata.create_all(ENGINE)
    with SESSION() as session:
        session.add(TEST_REDUCTION)
        session.commit()
        session.refresh(TEST_REDUCTION)


def assert_is_commit_sha(string: str) -> None:
    """
    assert given string is a commit sha
    :param string: the string to check
    :return: None
    """
    assert re.match("^[a-f0-9]{7,40}$", string) is not None


@patch("ir_api.scripts.acquisition.LOCAL_SCRIPT_DIR", "ir_api/local_scripts")
def test_get_default_test_prescript():
    """
    Test obtaining of untransformed mari pre script
    :return: None
    """
    response = client.get("/instrument/test/script")

    assert response.status_code == 200
    response_object = response.json()
    assert response_object["is_latest"]
    assert (
        response_object["value"]
        == """from __future__ import print_function

print("Doing some science")

x = 4
y = 2

for i in range(20):
    x *= y

def something() -> None:
    return

something()
"""
    )
    assert_is_commit_sha(response_object["sha"])


def test_get_script_by_sha_no_reduction_id_instrument_exists_hash_exists():
    response = client.get("/instrument/test/script/sha/64c6121")
    assert response.json() == {
        "is_latest": False,
        "sha": "64c6121",
        "value": "from __future__ import print_function\n"
        "\n"
        'print("Doing some science")\n'
        "\n"
        "x = 4\n"
        "y = 2\n"
        "\n"
        "for i in range(20):\n"
        "    x *= y\n"
        "\n"
        "def something() -> None:\n"
        "    return\n"
        "\n"
        "something()\n",
    }


def test_get_script_by_sha_instrument_doesnt_exist_returns_404():
    response = client.get("/instrument/foo/script/sha/64c6121")
    assert response.status_code == 404
    assert response.json() == {"message": "Resource not found"}


def test_get_script_by_sha_instrument_exists_sha_doesnt_exist_returns_404():
    response = client.get("/instrument/test/script/sha/12345")
    assert response.status_code == 404
    assert response.json() == {"message": "Resource not found"}


def test_get_script_by_sha_instrument_and_sha_doesnt_exist_returns_404():
    response = client.get("/instrument/foo/script/sha/12345")
    assert response.status_code == 404
    assert response.json() == {"message": "Resource not found"}


def test_get_script_by_sha_with_reduction_id():
    response = client.get("/instrument/test/script/sha/64c6121?reduction_id=1")
    assert response.status_code == 200
    response = response.json()
    assert response["is_latest"] is False
    assert response["sha"] == "64c6121"
    assert (
        response["value"]
        == """# This line is inserted via test
from __future__ import print_function


x = 22
y = 2

for i in range(20):
    x *= y

def something() -> None:
    return

something()"""
    )


def test_get_default_prescript_instrument_does_not_exist():
    """
    Test 404 for requesting script from unknown instrument
    :return:
    """
    response = client.get("/instrument/foo/script")
    assert response.status_code == 404
    assert response.json() == {
        "message": "The script could not be found locally or on remote, it is likely the script does not exist"
    }


@patch("ir_api.scripts.acquisition.LOCAL_SCRIPT_DIR", "ir_api/local_scripts")
def test_get_prescript_when_reduction_does_not_exist():
    """
    Test return 404 when requesting pre script from non existant reduction
    :return:
    """
    response = client.get("/instrument/mari/script?reduction_id=4324234")
    assert response.status_code == 404
    assert response.json() == {"message": "Resource not found"}


@patch("ir_api.scripts.acquisition.LOCAL_SCRIPT_DIR", "ir_api/local_scripts")
def test_get_mari_prescript_for_reduction():
    """
    Test the return of transformed test script
    :return: None
    """
    response = client.get("/instrument/test/script?reduction_id=1")
    assert response.status_code == 200
    response_object = response.json()

    assert response_object["is_latest"]
    assert (
        response_object["value"]
        == """# This line is inserted via test
from __future__ import print_function


x = 22
y = 2

for i in range(20):
    x *= y

def something() -> None:
    return

something()"""
    )
