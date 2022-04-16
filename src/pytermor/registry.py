# -----------------------------------------------------------------------------
# pytermor [ANSI formatted terminal output toolset]
# (C) 2022 A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
from __future__ import annotations

from copy import copy
from typing import Dict, Tuple, List

from pytermor import build

from . import code
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

sgr_parity_registry.register_single(code.BOLD, code.BOLD_DIM_OFF)
sgr_parity_registry.register_single(code.DIM, code.BOLD_DIM_OFF)
sgr_parity_registry.register_single(code.ITALIC, code.ITALIC_OFF)
sgr_parity_registry.register_single(code.UNDERLINED, code.UNDERLINED_OFF)
sgr_parity_registry.register_single(code.DOUBLE_UNDERLINED, code.UNDERLINED_OFF)
sgr_parity_registry.register_single(code.BLINK_SLOW, code.BLINK_OFF)
sgr_parity_registry.register_single(code.BLINK_FAST, code.BLINK_OFF)
sgr_parity_registry.register_single(code.INVERSED, code.INVERSED_OFF)
sgr_parity_registry.register_single(code.HIDDEN, code.HIDDEN_OFF)
sgr_parity_registry.register_single(code.CROSSLINED, code.CROSSLINED_OFF)
sgr_parity_registry.register_single(code.OVERLINED, code.OVERLINED_OFF)

for c in [code.BLACK, code.RED, code.GREEN, code.YELLOW, code.BLUE, code.MAGENTA, code.CYAN, code.WHITE, code.GRAY,
          code.HI_RED, code.HI_GREEN, code.HI_YELLOW, code.HI_BLUE, code.HI_MAGENTA, code.HI_CYAN, code.HI_WHITE]:
    sgr_parity_registry.register_single(c, code.COLOR_OFF)

for c in [code.BG_BLACK, code.BG_RED, code.BG_GREEN, code.BG_YELLOW, code.BG_BLUE, code.BG_MAGENTA, code.BG_CYAN,
          code.BG_WHITE, code.BG_GRAY, code.BG_HI_RED, code.BG_HI_GREEN, code.BG_HI_YELLOW, code.BG_HI_BLUE,
          code.BG_HI_MAGENTA, code.BG_HI_CYAN, code.BG_HI_WHITE]:
    sgr_parity_registry.register_single(c, code.BG_COLOR_OFF)


sgr_parity_registry.register_complex((code.COLOR_EXTENDED, 5), 1, code.COLOR_OFF)
sgr_parity_registry.register_complex((code.COLOR_EXTENDED, 2), 3, code.COLOR_OFF)
sgr_parity_registry.register_complex((code.BG_COLOR_EXTENDED, 5), 1, code.BG_COLOR_OFF)
sgr_parity_registry.register_complex((code.BG_COLOR_EXTENDED, 2), 3, code.BG_COLOR_OFF)
