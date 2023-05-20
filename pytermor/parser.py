# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under GNU Lesser General Public License v3.0
# -----------------------------------------------------------------------------
from __future__ import annotations

import re
import typing as t
from functools import lru_cache

from .common import SGR_SEQ_REGEX
from .ansi import make_color_256, ISequence, ColorTarget


RCP_REGEX = re.compile(R"\x1b\[(\d+);(\d+)R")
"""
Regular expression for :abbr:`RCP (Report Cursor Position)` sequence parsing. 
See `decompose_report_cursor_position()`.

:meta hide-value:
"""


@lru_cache
def _compile_contains_sgr_regex(*codes: int) -> re.Pattern:
    return re.compile(Rf'\x1b\[(?:|[\d;]*;)({";".join(map(str, codes))})(?:|;[\d;]*)m')


def contains_sgr(string: str, *codes: int) -> re.Match | None:
    """
    Return the first match of :term:`SGR` sequence in ``string`` with specified
    ``codes`` as params, strictly inside a single sequence in specified order,
    or *None* if nothing was found.

    The match object has one group (or, technically, two):

        - Group #0: the whole matched SGR sequence;
        - Group #1: the requested code bytes only.

    Example regex used for searching: :regex:`\\x1b\\[(?:|[\\d;]*;)(48;5)(?:|;[\\d;]*)m`.

        >>> contains_sgr(make_color_256(128).assemble(), 38)
        <re.Match object; span=(0, 11), match='\x1b[38;5;128m'>
        >>> contains_sgr(make_color_256(84, ColorTarget.BG).assemble(), 48, 5)
        <re.Match object; span=(0, 10), match='\x1b[48;5;84m'>

    :param string: String to search the SGR in.
    :param codes:  Integer SGR codes to find.
    """
    if not string:
        return None
    return _compile_contains_sgr_regex(*codes).search(string)


def parse(string: str) -> list[ISequence]:
    for seq in SGR_SEQ_REGEX.finditer(string):
        groups = seq.groupdict()
        if groups.get("fe_class"):
            pass

def decompose_report_cursor_position(string: str) -> t.Tuple[int, int] | None:
    """
    Parse :abbr:`RCP (Report Cursor Position)` sequence that usually comes from
    a terminal as a response to `QCP <make_query_cursor_position>` sequence and
    contains a cursor's current line and column.

    .. note ::
        As the library in general provides sequence assembling methods, but not
        the disassembling ones, there is no dedicated class for RCP sequences yet.

    >>> decompose_report_cursor_position('\x1b[9;15R')
    (9, 15)

    :param string:  Terminal response with a sequence.
    :return:        Current line and column if the expected sequence exists
                    in ``string``, *None* otherwise.
    """
    if match := RCP_REGEX.match(string):
        return int(match.group(1)), int(match.group(2))
    return None

