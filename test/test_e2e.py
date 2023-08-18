"""
end-to-end tests
"""
import re

# pylint: disable=line-too-long
from unittest.mock import patch

import pytest
from starlette.testclient import TestClient

from ir_api.core.model import Instrument, Run, Reduction, ReductionState
from ir_api.core.repositories import SESSION
from ir_api.ir_api import app
from utils.db_generator import main as generate_db

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
    Setup database pre testing
    :return:
    """
    generate_db()
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


def test_get_reduction_by_id_reduction_doesnt_exist():
    """
    Test 404 for reduction not existing
    :return:
    """
    response = client.get("/reduction/123144324234234234")
    assert response.status_code == 404
    assert response.json() == {"message": "Resource not found"}


def test_get_reduction_by_id_reduction_exists():
    """
    Test reduction returned for id that exists
    :return:
    """
    response = client.get("/reduction/1")
    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "reduction_end": "2021-02-09T03:59:48",
        "reduction_inputs": {"age": "WtlvblwzmmlxpbRCHjZS", "agree": "MUYAYAVjoYzWuSyMvItT", "rate": True},
        "reduction_outputs": "What should this be?",
        "reduction_start": "2021-02-09T03:31:48",
        "reduction_state": "UNSUCCESSFUL",
        "reduction_status_message": "Prepare small behind agreement structure item several able knowledge return director war.",
        "runs": [
            {
                "experiment_number": 61544,
                "filename": "/archive/NDXHET/Instrument/data/cycle_17_03/HET61544.nxs",
                "good_frames": 4011,
                "instrument_name": "HET",
                "raw_frames": 7070,
                "run_end": "2020-11-17T04:22:10",
                "run_start": "2020-11-17T03:49:10",
                "title": "Light final summer pass official positive.",
                "users": "Jeremy Smith, James Mora",
            }
        ],
        "script": {"value": "import os\nprint('foo')\n"},
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
    Test the return of transformed mari script
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


def test_get_reductions_for_experiment_number():
    """
    Test reduction returned for experiment
    :return:
    """
    response = client.get("/experiment/36803/reductions")
    assert response.status_code == 200
    assert response.json() == [
        {
            "id": 2133,
            "reduction_end": "2020-10-04T07:45:05",
            "reduction_inputs": {"figure": "YinqTBddoeJWMVahyATY", "focus": -73552971014.5794},
            "reduction_outputs": "What should this be?",
            "reduction_start": "2020-10-04T07:20:05",
            "reduction_state": "SUCCESSFUL",
            "reduction_status_message": "Open for add face receive force fly always nature.",
            "script": {"value": "import os\nprint('foo')\n"},
        }
    ]


def test_get_reductions_for_experiment_number_does_not_exist():
    """
    Test empty array returned when no reduction for an experiment number
    :return:
    """
    response = client.get("/experiment/12345678/reductions")
    assert response.status_code == 200
    assert response.json() == []


def test_get_reductions_for_instrument_reductions_exist():
    response = client.get("/instrument/MARI/reductions?limit=3")
    assert response.status_code == 200
    assert response.json() == [
        {
            "id": 7107,
            "reduction_end": None,
            "reduction_inputs": {
                "candidate": "RopSkhiHRdTOkfKlDTxS",
                "data": 1068,
                "foot": "xlypwBpsPGhzvRYMjclo",
                "improve": False,
                "in": "kxrFULFuYAGlwjjLwEXK",
                "official": 2194,
                "per": "DBXYUThgatRmqOwzOhge",
                "sound": 19863726282.8752,
                "up": True,
                "whatever": "afXkrONWBczHRtfkSHBy",
            },
            "reduction_outputs": None,
            "reduction_start": None,
            "reduction_state": "NOT_STARTED",
            "reduction_status_message": None,
            "script": {"value": "import os\nprint('foo')\n"},
        },
        {
            "id": 9882,
            "reduction_end": "2019-02-27T07:17:09",
            "reduction_inputs": {"growth": 4986, "make": -94539028.1069814},
            "reduction_outputs": "What should this be?",
            "reduction_start": "2019-02-27T07:02:09",
            "reduction_state": "ERROR",
            "reduction_status_message": "Speech clear education onto stay throughout face huge class.",
            "script": {"value": "import os\nprint('foo')\n"},
        },
        {
            "id": 7272,
            "reduction_end": "2019-11-28T23:58:47",
            "reduction_inputs": {
                "her": 3159459467009.81,
                "level": 7122,
                "loss": "eHKbuJDBTlKMMYyYomdw",
                "natural": -49.4505509648397,
                "trade": 6447883.13642678,
                "white": "KUtEOLGYqqAEJLRXSWWi",
            },
            "reduction_outputs": "What should this be?",
            "reduction_start": "2019-11-28T23:14:47",
            "reduction_state": "SUCCESSFUL",
            "reduction_status_message": "Or not option history rate manager cover time own artist various ask.",
            "script": {"value": "import os\nprint('foo')\n"},
        },
    ]


def test_reductions_by_instrument_no_reductions():
    """
    Test empty array returned when no reductions for instrument
    :return:
    """
    response = client.get("/instrument/test/reductions?limit=3")
    assert response.status_code == 200
    assert response.json() == []
