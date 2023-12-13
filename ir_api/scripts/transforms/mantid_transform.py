"""Common transform for mantid scripts"""
import logging
import os

from ir_api.core.model import Reduction
from ir_api.scripts.pre_script import PreScript
from ir_api.scripts.transforms.transform import Transform

logger = logging.getLogger(__name__)


class MantidTransform(Transform):
    """Applies mantid common transform. Currently adding a github token"""

    def apply(self, script: PreScript, reduction: Reduction) -> None:
        logger.info("Applying mantid transform for reduction %s", reduction.id)
        lines = script.value.splitlines()
        new_lines = [
            "from __future__ import print_function",
            "from mantid.kernel import ConfigService",
            f"ConfigService.Instance()[\"network.github.api_token\"] = \"{os.getenv('GITHUB_API_TOKEN', '')}\"",
        ]
        new_lines.extend(lines)
        script.value = "\n".join(new_lines)
        logger.info("Transform complete for %s", reduction.id)
