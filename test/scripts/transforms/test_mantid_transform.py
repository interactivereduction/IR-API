"""
Test case for mantid transform
"""
import os
from unittest.mock import Mock

from ir_api.scripts.pre_script import PreScript
from ir_api.scripts.transforms.mantid_transform import MantidTransform

ORIGINAL_SCRIPT = """print(1 + 2)
1 + 2
"""

EXPECTED_OUTPUT = """from mantid.kernel import ConfigService
ConfigService.Instance()[\"network.github.api_token\"] = \"special token\"
print(1 + 2)
1 + 2"""


def test_mantid_transform():
    """Test the mantid transform"""
    reduction = Mock()
    reduction.id = 1
    os.environ["GITHUB_API_TOKEN"] = "special token"
    script = PreScript(value=ORIGINAL_SCRIPT)
    MantidTransform().apply(script, reduction)
    assert script.value == EXPECTED_OUTPUT
