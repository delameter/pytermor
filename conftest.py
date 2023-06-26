# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under GNU Lesser General Public License v3.0
# -----------------------------------------------------------------------------
# file responsible for doctest running and custom shared fixtures
import re
from doctest import ELLIPSIS

from sybil import Sybil
from sybil.parsers.codeblock import PythonCodeBlockParser
from sybil.parsers.doctest import DocTestParser

import pytermor as pt
import typing as t


class TestSgrVisualizer(pt.SgrStringReplacer):
    """
    May incorrectly handle complex SGRs like 38;5;22 --
    will detect color 22, misidentify it as BOLD_DIM_OFF
    with the same code 22 and insert an closing bracket
    where it does not belong. SO: TESTING PURPOSES ONLY.
    """

    def __init__(self):
        super().__init__(self._visualize)
        self._resetters: t.Set[str] = {str(rc.value) for rc in pt.get_resetter_codes()}

    def _visualize(self, m: re.Match[str]) -> str:
        params = {*m.groupdict().get("param", "").split(pt.SequenceSGR.PARAM_SEPARATOR)}
        resetters = {p for p in params if p in self._resetters}
        regulars = params - resetters
        prefix, suffix = "", ""
        if len(regulars):
            prefix += "⬚"
            suffix += "⎛"
        if len(resetters):
            prefix += "⎠"
            suffix += ""
        return prefix + m.group(0) + suffix


_sgr_visualizer = TestSgrVisualizer()


def pytest_assertrepr_compare(op, left, right):
    if isinstance(left, str) and isinstance(right, str) and op == "==":
        if "\x1b" in (left + right):
            print()
            print("  Actual: ", _sgr_visualizer.apply(left))
            print("Expected: ", _sgr_visualizer.apply(right))
        return None
    if isinstance(left, pt.Style) and isinstance(right, pt.Style) and op == "==":
        return [repr(left) + " != " + repr(right)]
    return None


pytest_plugins = ["tests.fixtures"]

pytest_collect_file = Sybil(
    parsers=[DocTestParser(optionflags=ELLIPSIS), PythonCodeBlockParser()],
    patterns=["*.rst", "*.py"],
).pytest()
