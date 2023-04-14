from ir_api.core.entities import Script, Reduction
from ir_api.scripts.transforms.transform import Transform


class MariTransform(Transform):
    def apply(self, script: Script, reduction: Reduction) -> None:
        lines = script.value.splitlines()
        for index, line in enumerate(lines):
            if self._replace_line(line, lines, index, "runno", reduction.reduction_inputs["runno"]):
                continue
            if self._replace_line(line, lines, index, "sum_runs", reduction.reduction_inputs["sum_runs"]):
                continue
            if self._replace_line(line, lines, index, "ei", reduction.reduction_inputs["ei"]):
                continue
            if self._replace_line(line, lines, index, "monovan", reduction.reduction_inputs["monovan"]):
                continue
            if self._replace_line(line, lines, index, "sam_mass", reduction.reduction_inputs["sam_mass"]):
                continue
            if self._replace_line(line, lines, index, "sam_rmm", reduction.reduction_inputs["sam_rmm"]):
                continue
            if self._replace_line(line, lines, index, "remove_bkg", reduction.reduction_inputs["remove_bkg"]):
                continue
        script.value = "\n".join(lines)

    def _replace_line(self, line, lines, index, line_start, replacement):
        if line.startswith(line_start):
            lines[index] = f"{line_start} = {replacement}"
            return True
        return False
