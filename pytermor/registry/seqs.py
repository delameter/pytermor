# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022. A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
from __future__ import annotations

from copy import copy
from typing import Dict, Tuple, List

from .int_codes import IntCodes
from ..common import Registry
from ..ansi import SequenceSGR


class Seqs(Registry[SequenceSGR]):
    """
    Registry of sequence presets.

    .. attention::
       Registry constants are omitted from API doc pages to improve readability
       and avoid duplication. Summary list of all presets can be found in
       `guide.presets` section of the guide.
    """

    RESET = SequenceSGR(IntCodes.RESET)
    """
    Hard reset sequence.
    """

    # attributes
    BOLD = SequenceSGR(IntCodes.BOLD)
    DIM = SequenceSGR(IntCodes.DIM)
    ITALIC = SequenceSGR(IntCodes.ITALIC)
    UNDERLINED = SequenceSGR(IntCodes.UNDERLINED)
    BLINK_SLOW = SequenceSGR(IntCodes.BLINK_SLOW)
    BLINK_FAST = SequenceSGR(IntCodes.BLINK_FAST)
    BLINK_DEFAULT = BLINK_SLOW
    INVERSED = SequenceSGR(IntCodes.INVERSED)
    HIDDEN = SequenceSGR(IntCodes.HIDDEN)
    CROSSLINED = SequenceSGR(IntCodes.CROSSLINED)
    DOUBLE_UNDERLINED = SequenceSGR(IntCodes.DOUBLE_UNDERLINED)
    OVERLINED = SequenceSGR(IntCodes.OVERLINED)

    BOLD_DIM_OFF = SequenceSGR(IntCodes.BOLD_DIM_OFF)       # there is no separate sequence for
    ITALIC_OFF = SequenceSGR(IntCodes.ITALIC_OFF)           # disabling either of BOLD or DIM
    UNDERLINED_OFF = SequenceSGR(IntCodes.UNDERLINED_OFF)   # while keeping the other
    BLINK_OFF = SequenceSGR(IntCodes.BLINK_OFF)
    INVERSED_OFF = SequenceSGR(IntCodes.INVERSED_OFF)
    HIDDEN_OFF = SequenceSGR(IntCodes.HIDDEN_OFF)
    CROSSLINED_OFF = SequenceSGR(IntCodes.CROSSLINED_OFF)
    OVERLINED_OFF = SequenceSGR(IntCodes.OVERLINED_OFF)

    # text colors
    BLACK = SequenceSGR(IntCodes.BLACK)
    RED = SequenceSGR(IntCodes.RED)
    GREEN = SequenceSGR(IntCodes.GREEN)
    YELLOW = SequenceSGR(IntCodes.YELLOW)
    BLUE = SequenceSGR(IntCodes.BLUE)
    MAGENTA = SequenceSGR(IntCodes.MAGENTA)
    CYAN = SequenceSGR(IntCodes.CYAN)
    WHITE = SequenceSGR(IntCodes.WHITE)
    # code.COLOR_EXTENDED is handled by color_indexed()
    COLOR_OFF = SequenceSGR(IntCodes.COLOR_OFF)

    # background colors
    BG_BLACK = SequenceSGR(IntCodes.BG_BLACK)
    BG_RED = SequenceSGR(IntCodes.BG_RED)
    BG_GREEN = SequenceSGR(IntCodes.BG_GREEN)
    BG_YELLOW = SequenceSGR(IntCodes.BG_YELLOW)
    BG_BLUE = SequenceSGR(IntCodes.BG_BLUE)
    BG_MAGENTA = SequenceSGR(IntCodes.BG_MAGENTA)
    BG_CYAN = SequenceSGR(IntCodes.BG_CYAN)
    BG_WHITE = SequenceSGR(IntCodes.BG_WHITE)
    # code.BG_COLOR_EXTENDED is handled by color_indexed()
    BG_COLOR_OFF = SequenceSGR(IntCodes.BG_COLOR_OFF)

    # high intensity text colors
    GRAY = SequenceSGR(IntCodes.GRAY)
    HI_RED = SequenceSGR(IntCodes.HI_RED)
    HI_GREEN = SequenceSGR(IntCodes.HI_GREEN)
    HI_YELLOW = SequenceSGR(IntCodes.HI_YELLOW)
    HI_BLUE = SequenceSGR(IntCodes.HI_BLUE)
    HI_MAGENTA = SequenceSGR(IntCodes.HI_MAGENTA)
    HI_CYAN = SequenceSGR(IntCodes.HI_CYAN)
    HI_WHITE = SequenceSGR(IntCodes.HI_WHITE)

    # high intensity background colors
    BG_GRAY = SequenceSGR(IntCodes.BG_GRAY)
    BG_HI_RED = SequenceSGR(IntCodes.BG_HI_RED)
    BG_HI_GREEN = SequenceSGR(IntCodes.BG_HI_GREEN)
    BG_HI_YELLOW = SequenceSGR(IntCodes.BG_HI_YELLOW)
    BG_HI_BLUE = SequenceSGR(IntCodes.BG_HI_BLUE)
    BG_HI_MAGENTA = SequenceSGR(IntCodes.BG_HI_MAGENTA)
    BG_HI_CYAN = SequenceSGR(IntCodes.BG_HI_CYAN)
    BG_HI_WHITE = SequenceSGR(IntCodes.BG_HI_WHITE)


class _SgrPairityRegistry:
    """
    Internal class responsible for correct SGRs termination.
    """
    _code_to_breaker_map: Dict[int|Tuple[int, ...], SequenceSGR] = dict()
    _complex_code_def: Dict[int|Tuple[int, ...], int] = dict()
    _complex_code_max_len: int = 0

    @classmethod
    def __new__(cls, *args, **kwargs):

        _regulars = [(IntCodes.BOLD, IntCodes.BOLD_DIM_OFF),
                     (IntCodes.DIM, IntCodes.BOLD_DIM_OFF),
                     (IntCodes.ITALIC, IntCodes.ITALIC_OFF),
                     (IntCodes.UNDERLINED, IntCodes.UNDERLINED_OFF),
                     (IntCodes.DOUBLE_UNDERLINED, IntCodes.UNDERLINED_OFF),
                     (IntCodes.BLINK_SLOW, IntCodes.BLINK_OFF),
                     (IntCodes.BLINK_FAST, IntCodes.BLINK_OFF),
                     (IntCodes.INVERSED, IntCodes.INVERSED_OFF),
                     (IntCodes.HIDDEN, IntCodes.HIDDEN_OFF),
                     (IntCodes.CROSSLINED, IntCodes.CROSSLINED_OFF),
                     (IntCodes.OVERLINED, IntCodes.OVERLINED_OFF), ]

        for c in _regulars:
            cls.bind_regular(*c)

        for c in [*IntCodes.LIST_COLORS, *IntCodes.LIST_HI_COLORS]:
            cls.bind_regular(c, IntCodes.COLOR_OFF)

        for c in [*IntCodes.LIST_BG_COLORS, *IntCodes.LIST_BG_HI_COLORS]:
            cls.bind_regular(c, IntCodes.BG_COLOR_OFF)

        cls.bind_complex((IntCodes.COLOR_EXTENDED, 5), 1, IntCodes.COLOR_OFF)
        cls.bind_complex((IntCodes.COLOR_EXTENDED, 2), 3, IntCodes.COLOR_OFF)
        cls.bind_complex((IntCodes.BG_COLOR_EXTENDED, 5), 1, IntCodes.BG_COLOR_OFF)
        cls.bind_complex((IntCodes.BG_COLOR_EXTENDED, 2), 3, IntCodes.BG_COLOR_OFF)

    @classmethod
    def bind_regular(cls, starter_code: int|Tuple[int, ...], breaker_code: int):
        if starter_code in cls._code_to_breaker_map:
            raise RuntimeError(f'Conflict: SGR code {starter_code} already '
                               f'has a registered breaker')

        cls._code_to_breaker_map[starter_code] = SequenceSGR(breaker_code)

    @classmethod
    def bind_complex(cls, starter_codes: Tuple[int, ...], param_len: int,
                     breaker_code: int):
        cls.bind_regular(starter_codes, breaker_code)

        if starter_codes in cls._complex_code_def:
            raise RuntimeError(f'Conflict: SGR complex {starter_codes} already '
                               f'has a registered breaker')

        cls._complex_code_def[starter_codes] = param_len
        cls._complex_code_max_len = max(cls._complex_code_max_len,
                                         len(starter_codes) + param_len)

    @classmethod
    def get_closing_seq(cls, opening_seq: SequenceSGR) -> SequenceSGR:
        closing_seq_params: List[int] = []
        opening_params = copy(opening_seq.params)

        while len(opening_params):
            key_params: int|Tuple[int, ...]|None = None

            for complex_len in range(1, min(len(opening_params),
                                            cls._complex_code_max_len + 1)):
                opening_complex_suggestion = tuple(opening_params[:complex_len])

                if opening_complex_suggestion in cls._complex_code_def:
                    key_params = opening_complex_suggestion
                    complex_total_len = (
                        complex_len + cls._complex_code_def[opening_complex_suggestion])
                    opening_params = opening_params[complex_total_len:]
                    break

            if key_params is None:
                key_params = opening_params.pop(0)
            if key_params not in cls._code_to_breaker_map:
                continue

            closing_seq_params.extend(cls._code_to_breaker_map[key_params].params)

        return SequenceSGR(*closing_seq_params)

_SgrPairityRegistry()
