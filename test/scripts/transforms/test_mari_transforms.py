"""
Test cases for MariTransform
"""
from unittest.mock import Mock

import pytest

from ir_api.scripts.pre_script import PreScript
from ir_api.scripts.transforms.mari_transforms import MariTransform


# pylint: disable = redefined-outer-name


@pytest.fixture
def script():
    """
    MariTransform  PreScript fixture
    :return:
    """
    return PreScript(
        value="""from __future__ import print_function
from mantid import config
from MARIReduction_Sample import *
import time
import os
import datetime
import sys
if sys.version_info > (3,):
    if sys.version_info < (3,4):
        from imp import reload
    else:
        from importlib import reload
try:
    #Note: due to the mantid-python implementation, one needs to run this 
    #script in Mantid  script window  TWICE!!!  to deploy the the changes made to MARIReduction_Sample.py file.
    sys.path.insert(0,'/instrument/MARI/RBNumber/USER_RB_FOLDER/')
    reload(sys.modules['MARIReduction_Sample'])
except:
    print("*** WARNING can not reload MARIReduction_Sample file")
    pass

# Run number and Ei
runno=26644
sum_runs=False
ei=[30, 11.8]

# White vanadium run number
wbvan=28041
# Default save directory
config['defaultsave.directory'] = '/instrument/MARI/RBNumber/USER_RB_FOLDER' #data_dir 

# Absolute normalisation parameters
#monovan=21803
#sam_mass=41.104
#sam_rmm=398.9439
monovan=0
sam_mass=0
sam_rmm=0

# Set to true to remove the constant ToF background from the data.
remove_bkg = True

# If necessary, add any sequence of reduction paramerters defined in MARIParameters.xml file 
# to the end ot the illiad string using the form: property=value 
# (e.g.:  iliad_mari(runno,ei,wbvan,monovan,sam_mass,sam_rmm,sum_runs,check_background=False)
iliad_mari(runno, ei, wbvan, monovan, sam_mass, sam_rmm, sum_runs, check_background=remove_bkg,
    hard_mask_file='MASK_FILE_XML')"""
    )


@pytest.fixture
def reduction():
    """
    Reduction fixture
    :return:
    """
    mock = Mock()
    mock.reduction_inputs = {
        "runno": 12345,
        "sum_runs": True,
        "ei": [50, 20],
        "monovan": 54321,
        "sam_mass": 30,
        "sam_rmm": 400,
        "remove_bkg": False,
    }
    return mock


def test_mari_transform_apply(script, reduction):
    """
    Test mari transform applies correct updates to script
    :param script: The script fixture
    :param reduction: The reduciton fixture
    :return: None
    """
    transform = MariTransform()

    original_lines = script.value.splitlines()
    transform.apply(script, reduction)
    updated_lines = script.value.splitlines()

    assert len(original_lines) == len(updated_lines)

    for index, line in enumerate(updated_lines):
        if line.startswith("runno"):
            assert line == "runno = 12345"
        elif line.startswith("sum_runs"):
            assert line == "sum_runs = True"
        elif line.startswith("ei"):
            assert line == "ei = [50, 20]"
        elif line.startswith("monovan"):
            assert line == "monovan = 54321"
        elif line.startswith("sam_mass"):
            assert line == "sam_mass = 30"
        elif line.startswith("sam_rmm"):
            assert line == "sam_rmm = 400"
        elif line.startswith("remove_bkg"):
            assert line == "remove_bkg = False"
        else:
            assert line == original_lines[index]
