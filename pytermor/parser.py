# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under GNU Lesser General Public License v3.0
# -----------------------------------------------------------------------------
from __future__ import annotations

import re
import typing as t
from functools import lru_cache

from .ansi import make_color_256, ISequence
from .ansi import ColorTarget, seq_from_dict

ESCAPE_SEQ_REGEX = re.compile(
    R"""
	(?P<escape_byte>\x1b)
	(?P<data>
		(?P<nf_class_seq>
			(?P<nf_classifier>[\x20-\x2f])
			(?P<nf_interm>[\x20-\x2f]*)
			(?P<nf_final>[\x30-\x7e])
		)|
		(?P<fp_class_seq>
			(?P<fp_classifier>[\x30-\x3f])
		)|
		(?P<fe_class_seq>
		    (?P<st_classifier>\\)
		    |
		    (?P<osc_classifier>\])
		    (?P<osc_param>[\x30-\x3f]*;;?)
		    |
		    (?P<csi_classifier>\[)
			(?P<csi_interm>[?!]?)
			(?P<csi_param>[\x30-\x3f]*)
			(?P<csi_final>[\x40-\x7e])
		    |
			(?P<fe_classifier>[\x40-\x5a\x5e\x5f])
			(?P<fe_param>[\x30-\x3f]*)
			(?P<fe_interm>[\x20-\x2f]?)
			(?P<fe_final>[\x40-\x7e]?)
		)|
		(?P<fs_class_seq>
			(?P<fs_classifier>[\x60-\x7e])
		)  
	)
	""",
    flags=re.VERBOSE,
)
""" 
Regular expression that matches all classes of escape sequences.

More specifically, it recognizes **nF**, **Fp**, **Fe** and **Fs** [#]_ 
classes. Useful for removing the sequences as well as for granular search 
thanks to named match groups, which include:

    ``escape_byte``
        first byte of every sequence -- ``ESC``, or :hex:`0x1B`.
        
    ``data``
        remaining bytes of the sequence (without escape byte) represented as 
        one of the following groups: ``nf_class_seq``, ``fp_class_seq``, 
        ``fe_class_seq`` or ``fs_class_seq``; each of these splits further to
        even more specific subgroups:
        
        - ``nf_classifier``, ``nf_interm`` and ``nf_final`` as parts of 
          **nF**-class sequences,
        - ``fp_classifier`` for **Fp**-class sequences,
        - ``st_classifier``, ``osc_classifier``, ``osc_param``,  ``csi_classifier``, 
          ``csi_interm``, ``csi_param``, ``csi_final``, ``fe_classifier``, ``fe_param``, 
          ``fe_interm`` and ``fe_final`` for **Fe**-class generic sequences and 
          subtypes (including :term:`SGRs <SGR>`),
        - ``fs_classifier`` for **Fs**-class sequences.

.. [#] `ECMA-35 specification <https://ecma-international.org/publications-and-standards/standards/ecma-35/>`_

:meta hide-value:
"""

SGR_SEQ_REGEX = re.compile(r"(\x1b)(\[)([0-9;:]*)(m)")
"""
Regular expression that matches :term:`SGR` sequences. Group 3 can be used for 
sequence params extraction.

:meta hide-value:
"""

CSI_SEQ_REGEX = re.compile(r"(\x1b)(\[)(([0-9;:<=>?])*)([@A-Za-z])")
"""
Regular expression that matches CSI sequences (a superset which includes 
:term:`SGRs <SGR>`). 

:meta hide-value:
"""

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
        - Group #1: the requested params bytes only.

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


def parse(string: str) -> t.Iterable[ISequence|str]:
    cursor = 0
    for match in ESCAPE_SEQ_REGEX.finditer(string):
        if (mstart := match.start()) > cursor:
            yield string[cursor:mstart]
        cursor = match.end()
        yield seq_from_dict(match.groupdict())
    if last_str := string[cursor:]:
        yield last_str

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

