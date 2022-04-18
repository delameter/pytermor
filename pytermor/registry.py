# -----------------------------------------------------------------------------
# pytermor [ANSI formatted terminal output toolset]
# (C) 2022 A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
from __future__ import annotations

from copy import copy
from typing import Dict, Tuple, List

from pytermor import build

from . import sgr
from .seq import SequenceSGR


class Registry:
    def __init__(self):
        self._code_to_breaker_map: Dict[int|Tuple[int, ...], SequenceSGR] = dict()
        self._complex_code_def: Dict[int|Tuple[int, ...], int] = dict()
        self._complex_code_max_len: int = 0

    def register_single(self, starter_code: int | Tuple[int, ...], breaker_code: int):
        if starter_code in self._code_to_breaker_map:
            raise RuntimeError(f'Conflict: SGR code {starter_code} already has a registered breaker')
        self._code_to_breaker_map[starter_code] = SequenceSGR(breaker_code)

    def register_complex(self, starter_codes: Tuple[int, ...], param_len: int, breaker_code: int):
        self.register_single(starter_codes, breaker_code)

        if starter_codes in self._complex_code_def:
            raise RuntimeError(f'Conflict: SGR complex {starter_codes} already has a registered breaker')
        self._complex_code_def[starter_codes] = param_len
        self._complex_code_max_len = max(self._complex_code_max_len, len(starter_codes) + param_len)

    def get_closing_seq(self, opening_seq: SequenceSGR) -> SequenceSGR:
        closing_seq_params: List[int] = []
        opening_params = copy(opening_seq.params)
        while len(opening_params):
            key_params: int|Tuple[int, ...]|None = None
            for complex_len in range(1, min(len(opening_params), self._complex_code_max_len + 1)):
                opening_complex_suggestion = tuple(opening_params[:complex_len])
                if opening_complex_suggestion in self._complex_code_def:
                    key_params = opening_complex_suggestion
                    complex_total_len = complex_len + self._complex_code_def[opening_complex_suggestion]
                    opening_params = opening_params[complex_total_len:]
                    break
            if key_params is None:
                key_params = opening_params.pop(0)
            if key_params not in self._code_to_breaker_map:
                continue
            closing_seq_params.extend(self._code_to_breaker_map[key_params].params)

        return build(*closing_seq_params)


sgr_parity_registry = Registry()

sgr_parity_registry.register_single(sgr.BOLD, sgr.BOLD_DIM_OFF)
sgr_parity_registry.register_single(sgr.DIM, sgr.BOLD_DIM_OFF)
sgr_parity_registry.register_single(sgr.ITALIC, sgr.ITALIC_OFF)
sgr_parity_registry.register_single(sgr.UNDERLINED, sgr.UNDERLINED_OFF)
sgr_parity_registry.register_single(sgr.DOUBLE_UNDERLINED, sgr.UNDERLINED_OFF)
sgr_parity_registry.register_single(sgr.BLINK_SLOW, sgr.BLINK_OFF)
sgr_parity_registry.register_single(sgr.BLINK_FAST, sgr.BLINK_OFF)
sgr_parity_registry.register_single(sgr.INVERSED, sgr.INVERSED_OFF)
sgr_parity_registry.register_single(sgr.HIDDEN, sgr.HIDDEN_OFF)
sgr_parity_registry.register_single(sgr.CROSSLINED, sgr.CROSSLINED_OFF)
sgr_parity_registry.register_single(sgr.OVERLINED, sgr.OVERLINED_OFF)

for c in [sgr.BLACK, sgr.RED, sgr.GREEN, sgr.YELLOW, sgr.BLUE, sgr.MAGENTA, sgr.CYAN, sgr.WHITE, sgr.GRAY,
          sgr.HI_RED, sgr.HI_GREEN, sgr.HI_YELLOW, sgr.HI_BLUE, sgr.HI_MAGENTA, sgr.HI_CYAN, sgr.HI_WHITE]:
    sgr_parity_registry.register_single(c, sgr.COLOR_OFF)

for c in [sgr.BG_BLACK, sgr.BG_RED, sgr.BG_GREEN, sgr.BG_YELLOW, sgr.BG_BLUE, sgr.BG_MAGENTA, sgr.BG_CYAN,
          sgr.BG_WHITE, sgr.BG_GRAY, sgr.BG_HI_RED, sgr.BG_HI_GREEN, sgr.BG_HI_YELLOW, sgr.BG_HI_BLUE,
          sgr.BG_HI_MAGENTA, sgr.BG_HI_CYAN, sgr.BG_HI_WHITE]:
    sgr_parity_registry.register_single(c, sgr.BG_COLOR_OFF)


sgr_parity_registry.register_complex((sgr.COLOR_EXTENDED, 5), 1, sgr.COLOR_OFF)
sgr_parity_registry.register_complex((sgr.COLOR_EXTENDED, 2), 3, sgr.COLOR_OFF)
sgr_parity_registry.register_complex((sgr.BG_COLOR_EXTENDED, 5), 1, sgr.BG_COLOR_OFF)
sgr_parity_registry.register_complex((sgr.BG_COLOR_EXTENDED, 2), 3, sgr.BG_COLOR_OFF)
