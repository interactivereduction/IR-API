"""
Module provides the MariTransform class, an implementation of the Transform abstract base class for MARI instrument
scripts.
"""
import logging

from ir_api.core.model import Reduction
from ir_api.scripts.pre_script import PreScript
from ir_api.scripts.transforms.transform import Transform

logger = logging.getLogger(__name__)


class MariTransform(Transform):
    """
    MariTransform applies modifications to MARI instrument scripts based on reduction input parameters in a Reduction
    entity.
    """

    # pylint: disable = line-too-long
    def apply(self, script: PreScript, reduction: Reduction) -> None:
        logger.info("Beginning Mari transform for reduction %s...", reduction.id)
        lines = script.value.splitlines()
        # MyPY does not believe ColumnElement[JSONB] is indexable, despite JSONB implementing the Indexable mixin
        # If you get here in the future, try removing the type ignore and see if it passes with newer mypy
        for index, line in enumerate(lines):
            if "url_to_mask_file.xml" in line:
                lines[index] = line.replace("url_to_mask_file.xml", reduction.reduction_inputs["mask_file_link"])  # type: ignore
                continue
            if self._replace_input(line, lines, index, "runno", reduction.reduction_inputs["runno"]):  # type: ignore
                continue
            if self._replace_input(line, lines, index, "sum_runs", reduction.reduction_inputs["sum_runs"]):  # type: ignore
                continue
            if self._replace_input(line, lines, index, "ei", reduction.reduction_inputs["ei"]):  # type: ignore
                continue
            if self._replace_input(line, lines, index, "wbvan", reduction.reduction_inputs["wbvan"]):  # type: ignore
                continue
            if self._replace_input(line, lines, index, "monovan", reduction.reduction_inputs["monovan"]):  # type: ignore
                continue
            if self._replace_input(line, lines, index, "sam_mass", reduction.reduction_inputs["sam_mass"]):  # type: ignore
                continue
            if self._replace_input(line, lines, index, "sam_rmm", reduction.reduction_inputs["sam_rmm"]):  # type: ignore
                continue
            if self._replace_input(line, lines, index, "remove_bkg", reduction.reduction_inputs["remove_bkg"]):  # type: ignore
                continue
        script.value = "\n".join(lines)
        logger.info("Transform complete for reduction %s", reduction.id)

    # pylint: enable = line-too-long
