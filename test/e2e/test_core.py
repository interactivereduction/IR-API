"""
end-to-end tests
"""
# pylint: disable=line-too-long, wrong-import-order
from unittest.mock import patch

from starlette.testclient import TestClient

from ir_api.ir_api import app
from test.utils import IR_FAKER_PROVIDER

client = TestClient(app)


faker = IR_FAKER_PROVIDER


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
    response = client.get("/reduction/5001")
    assert response.status_code == 200
    assert response.json() == {
        "id": 5001,
        "reduction_end": None,
        "reduction_inputs": {
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
        "reduction_outputs": None,
        "reduction_start": None,
        "reduction_state": "NOT_STARTED",
        "reduction_status_message": None,
        "runs": [
            {
                "experiment_number": 1820497,
                "filename": "MAR25581.nxs",
                "good_frames": 6452,
                "instrument_name": "TEST",
                "raw_frames": 8067,
                "run_end": "2019-03-22T10:18:26",
                "run_start": "2019-03-22T10:15:44",
                "title": "Whitebeam - vanadium - detector tests - vacuum bad - HT on not on all LAB",
                "users": "Wood,Guidi,Benedek,Mansson,Juranyi,Nocerino,Forslund,Matsubara",
            }
        ],
        "script": None,
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


@patch("ir_api.scripts.acquisition._get_script_from_remote", side_effect=RuntimeError)
def test_unsafe_path_request_returns_400_status(_):
    """
    Test that a 400 is returned for unsafe characters in script request
    :return:
    """
    response = client.get("/instrument/mari./script")  # %2F is encoded /
    assert response.status_code == 400
    assert response.json() == {"message": "The given request contains bad characters"}


@patch("ir_api.scripts.acquisition.LOCAL_SCRIPT_DIR", "ir_api/local_scripts")
def test_get_test_prescript_for_reduction():
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
        == """from __future__ import print_function
# This line is inserted via test


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
    response = client.get("/experiment/1820497/reductions")
    assert response.status_code == 200
    assert response.json() == [
        {
            "id": 5001,
            "reduction_end": None,
            "reduction_inputs": {
                "ei": "'auto'",
                "mask_file_link": "https://raw.githubusercontent.com/pace-neutrons/InstrumentFiles/"
                "964733aec28b00b13f32fb61afa363a74dd62130/mari/mari_mask2023_1.xml",
                "monovan": 0,
                "remove_bkg": True,
                "runno": 25581,
                "sam_mass": 0.0,
                "sam_rmm": 0.0,
                "sum_runs": False,
                "wbvan": 12345,
            },
            "reduction_outputs": None,
            "reduction_start": None,
            "reduction_state": "NOT_STARTED",
            "reduction_status_message": None,
            "script": None,
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
    """
    Test array of reductions returned for given instrument when the instrument and reductions exist
    :return: None
    """
    response = client.get("/instrument/test/reductions")
    assert response.status_code == 200
    assert response.json() == [
        {
            "id": 5001,
            "reduction_end": None,
            "reduction_inputs": {
                "ei": "'auto'",
                "mask_file_link": "https://raw.githubusercontent.com/pace-neutrons/InstrumentFiles/"
                "964733aec28b00b13f32fb61afa363a74dd62130/mari/mari_mask2023_1.xml",
                "monovan": 0,
                "remove_bkg": True,
                "runno": 25581,
                "sam_mass": 0.0,
                "sam_rmm": 0.0,
                "sum_runs": False,
                "wbvan": 12345,
            },
            "reduction_outputs": None,
            "reduction_start": None,
            "reduction_state": "NOT_STARTED",
            "reduction_status_message": None,
            "script": None,
        }
    ]


def test_reductions_by_instrument_no_reductions():
    """
    Test empty array returned when no reductions for instrument
    :return:
    """
    response = client.get("/instrument/foo/reductions")
    assert response.status_code == 200
    assert response.json() == []


def test_reductions_count():
    """
    Test count endpoint for all reductions
    :return:
    """
    response = client.get("/reductions/count")
    assert response.status_code == 200
    assert response.json()["count"] == 5001


def test_limit_reductions():
    """Test reductions can be limited"""
    response = client.get("/instrument/mari/reductions?limit=4")
    assert len(response.json()) == 4


def test_offset_reductions():
    """
    Test results are offset
    """
    response_one = client.get("/instrument/mari/reductions")
    response_two = client.get("/instrument/mari/reductions?offset=10")
    assert response_one.json()[0] != response_two.json()[0]


def test_limit_offset_reductions():
    """
    Test offset with limit
    """
    response_one = client.get("/instrument/mari/reductions?limit=4")
    response_two = client.get("/instrument/mari/reductions?limit=4&offset=10")

    assert len(response_two.json()) == 4
    assert response_one.json() != response_two.json()


def test_instrument_reductions_count():
    """
    Test instrument reductions count
    """
    response = client.get("/instrument/TEST/reductions/count")
    assert response.json()["count"] == 1


def test_readiness_and_liveness_probes():
    """
    Test endpoint for probes
    :return: None
    """
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.text == '"ok"'
