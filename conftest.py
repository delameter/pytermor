# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under GNU Lesser General Public License v3.0
# -----------------------------------------------------------------------------
# file responsible for doctest running and custom shared fixtures
import warnings
from doctest import ELLIPSIS

from sybil import Sybil
from sybil.parsers.codeblock import PythonCodeBlockParser
from sybil.parsers.doctest import DocTestParser

import pytermor as pt

def pytest_assertrepr_compare(op, left, right):
    if isinstance(left, pt.Style) and isinstance(right, pt.Style) and op == "==":
        return [repr(left) + " != " + repr(right)]
    return []


pytest_plugins = ["tests.fixtures"]

pytest_collect_file = Sybil(
    parsers=[DocTestParser(optionflags=ELLIPSIS), PythonCodeBlockParser()],
    patterns=["*.rst", "*.py"],
).pytest()
