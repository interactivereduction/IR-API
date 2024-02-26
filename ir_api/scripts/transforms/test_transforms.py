"""
Test transform used in e2e
"""

from ir_api.core.model import Reduction
from ir_api.scripts.pre_script import PreScript
from ir_api.scripts.transforms.transform import Transform


class TestTransform(Transform):
    """
    Test transform used for the test instrument in e2e tests
    """

    def apply(self, script: PreScript, reduction: Reduction) -> None:
        lines = script.value.splitlines()
        for index, line in enumerate(lines):
            if line.startswith("print"):
                lines.pop(index)
                continue
            if line.startswith("x ="):
                lines[index] = "x = 22"
                continue
        lines.insert(0, "# This line is inserted via test")
        script.value = "\n".join(lines)
