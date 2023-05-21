# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under GNU Lesser General Public License v3.0
# -----------------------------------------------------------------------------
# file responsible for doctest running and custom shared fixtures

from doctest import ELLIPSIS

from sybil import Sybil
from sybil.parsers.codeblock import PythonCodeBlockParser
from sybil.parsers.doctest import DocTestParser


pytest_plugins = ["tests.fixtures"]

pytest_collect_file = Sybil(
    parsers=[DocTestParser(optionflags=ELLIPSIS), PythonCodeBlockParser()],
    patterns=["*.rst", "*.py"],
).pytest()


# def pytest_assertrepr_compare(op, left, right):
#     a = 4
#     if isinstance(left, int) and isinstance(right, int):
#         return [f"{left} (0x{left:06x}) != {right} (0x{right:06x})"]
#     return None
