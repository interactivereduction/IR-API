"""
end-to-end tests
"""


from unittest.mock import patch

import pytest
from starlette.testclient import TestClient

from ir_api.core.model import Base, Instrument, Run, Reduction, ReductionState
from ir_api.core.repositories import ENGINE, SESSION
from ir_api.ir_api import app

client = TestClient(app)

TEST_INSTRUMENT = Instrument(instrument_name="mari")
TEST_REDUCTION = Reduction(
    reduction_inputs={
        "ei": "auto",
        "sam_mass": 0.0,
        "sam_rmm": 0.0,
        "monovan": 0,
        "remove_bkg": True,
        "sum_runs": False,
        "runno": 25581,
    },
    reduction_state=ReductionState.NOT_STARTED,
)
TEST_RUN = Run(
    instrument=TEST_INSTRUMENT,
    experiment_title="Whitebeam - vanadium - detector tests - vacuum bad - HT on not on all LAB",
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
    Base.metadata.drop_all(ENGINE)
    Base.metadata.create_all(ENGINE)
    with SESSION() as session:
        session.add(TEST_REDUCTION)
        session.commit()
        session.refresh(TEST_REDUCTION)


@patch("ir_api.scripts.acquisition.LOCAL_SCRIPT_DIR", "ir_api/local_scripts")
def test_get_default_mari_prescript():
    response = client.get("/instrument/mari/script")

    assert response.status_code == 200
    assert response.json() == {
        "is_latest": True,
        "value": "from __future__ import print_function\n"
        "from mantid import config\n"
        "from MARIReduction_Sample import *\n"
        "import time\n"
        "import os\n"
        "import datetime\n"
        "import sys\n"
        "if sys.version_info > (3,):\n"
        "    if sys.version_info < (3,4):\n"
        "        from imp import reload\n"
        "    else:\n"
        "        from importlib import reload\n"
        "try:\n"
        "    #Note: due to the mantid-python implementation, one needs to "
        "run this \n"
        "    #script in Mantid  script window  TWICE!!!  to deploy the the "
        "changes made to MARIReduction_Sample.py file.\n"
        "    sys.path.insert(0,'/instrument/MARI/RBNumber/USER_RB_FOLDER/')\n"
        "    reload(sys.modules['MARIReduction_Sample'])\n"
        "except:\n"
        '    print("*** WARNING can not reload MARIReduction_Sample file")\n'
        "    pass\n"
        "\n"
        "# Run number and Ei\n"
        "runno=26644\n"
        "sum_runs=False\n"
        "ei=[30, 11.8]\n"
        "\n"
        "# White vanadium run number\n"
        "wbvan=28041\n"
        "# Default save directory\n"
        "config['defaultsave.directory'] = "
        "'/instrument/MARI/RBNumber/USER_RB_FOLDER' #data_dir \n"
        "\n"
        "# Absolute normalisation parameters\n"
        "#monovan=21803\n"
        "#sam_mass=41.104\n"
        "#sam_rmm=398.9439\n"
        "monovan=0\n"
        "sam_mass=0\n"
        "sam_rmm=0\n"
        "\n"
        "# Set to true to remove the constant ToF background from the data.\n"
        "remove_bkg = True\n"
        "\n"
        "# If necessary, add any sequence of reduction paramerters defined "
        "in MARIParameters.xml file \n"
        "# to the end ot the illiad string using the form: property=value \n"
        "# (e.g.:  "
        "iliad_mari(runno,ei,wbvan,monovan,sam_mass,sam_rmm,sum_runs,check_background=False)\n"
        "iliad_mari(runno, ei, wbvan, monovan, sam_mass, sam_rmm, sum_runs, "
        "check_background=remove_bkg,\n"
        "    hard_mask_file='MASK_FILE_XML')\n"
        "\n"
        "# To run reduction _and_ compute density of states together "
        "uncomment this and comment iliad_mari above\n"
        "# bkgruns and runno can be lists, which means those runs will be "
        "summed, and the sum is reduced\n"
        "#bkgruns = 20941\n"
        "#iliad_dos(runno, wbvan, ei, monovan, sam_mass, sam_rmm, sum_runs, "
        "background=bkgrun, temperature=5)\n"
        "\n",
    }


def test_get_default_prescript_instrument_does_not_exist():
    response = client.get("/instrument/foo/script")
    assert response.status_code == 404
    assert response.json() == {
        "message": "The script could not be found locally or on remote, it is likely the script does not exist"
    }


@patch("ir_api.scripts.acquisition.LOCAL_SCRIPT_DIR", "ir_api/local_scripts")
def test_get_prescript_when_reduction_does_not_exist():
    response = client.get("/instrument/mari/script?reduction_id=4324234")
    assert response.status_code == 404
    assert response.json() == {"message": "Resource not found"}


@patch("ir_api.scripts.acquisition.LOCAL_SCRIPT_DIR", "ir_api/local_scripts")
def test_get_mari_prescript_for_reduction():
    response = client.get("/instrument/mari/script?reduction_id=1")
    assert response.status_code == 200
    assert response.json() == {
        "is_latest": True,
        "value": "from __future__ import print_function\n"
        "from mantid import config\n"
        "from MARIReduction_Sample import *\n"
        "import time\n"
        "import os\n"
        "import datetime\n"
        "import sys\n"
        "if sys.version_info > (3,):\n"
        "    if sys.version_info < (3,4):\n"
        "        from imp import reload\n"
        "    else:\n"
        "        from importlib import reload\n"
        "try:\n"
        "    #Note: due to the mantid-python implementation, one needs to "
        "run this \n"
        "    #script in Mantid  script window  TWICE!!!  to deploy the the "
        "changes made to MARIReduction_Sample.py file.\n"
        "    sys.path.insert(0,'/instrument/MARI/RBNumber/USER_RB_FOLDER/')\n"
        "    reload(sys.modules['MARIReduction_Sample'])\n"
        "except:\n"
        '    print("*** WARNING can not reload MARIReduction_Sample file")\n'
        "    pass\n"
        "\n"
        "# Run number and Ei\n"
        "runno = 25581\n"
        "sum_runs = False\n"
        "ei = auto\n"
        "\n"
        "# White vanadium run number\n"
        "wbvan=28041\n"
        "# Default save directory\n"
        "config['defaultsave.directory'] = "
        "'/instrument/MARI/RBNumber/USER_RB_FOLDER' #data_dir \n"
        "\n"
        "# Absolute normalisation parameters\n"
        "#monovan=21803\n"
        "#sam_mass=41.104\n"
        "#sam_rmm=398.9439\n"
        "monovan = 0\n"
        "sam_mass = 0.0\n"
        "sam_rmm = 0.0\n"
        "\n"
        "# Set to true to remove the constant ToF background from the data.\n"
        "remove_bkg = True\n"
        "\n"
        "# If necessary, add any sequence of reduction paramerters defined "
        "in MARIParameters.xml file \n"
        "# to the end ot the illiad string using the form: property=value \n"
        "# (e.g.:  "
        "iliad_mari(runno,ei,wbvan,monovan,sam_mass,sam_rmm,sum_runs,check_background=False)\n"
        "iliad_mari(runno, ei, wbvan, monovan, sam_mass, sam_rmm, sum_runs, "
        "check_background=remove_bkg,\n"
        "    hard_mask_file='MASK_FILE_XML')\n"
        "\n"
        "# To run reduction _and_ compute density of states together "
        "uncomment this and comment iliad_mari above\n"
        "# bkgruns and runno can be lists, which means those runs will be "
        "summed, and the sum is reduced\n"
        "#bkgruns = 20941\n"
        "#iliad_dos(runno, wbvan, ei, monovan, sam_mass, sam_rmm, sum_runs, "
        "background=bkgrun, temperature=5)\n",
    }
