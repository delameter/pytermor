# -----------------------------------------------------------------------------
# pytermor [ANSI formatted terminal output toolset]
# (C) 2022 A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
from __future__ import annotations

from copy import copy
from typing import Dict, Tuple, List

from . import intcode
from .sequence import build, SequenceSGR


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


# ---------------------------------------------------------------------------

sgr_parity_registry = Registry()

sgr_parity_registry.register_single(intcode.BOLD, intcode.NO_BOLD_DIM)
sgr_parity_registry.register_single(intcode.DIM, intcode.NO_BOLD_DIM)
sgr_parity_registry.register_single(intcode.ITALIC, intcode.ITALIC_OFF)
sgr_parity_registry.register_single(intcode.UNDERLINED, intcode.UNDERLINED_OFF)
sgr_parity_registry.register_single(intcode.DOUBLE_UNDERLINED, intcode.UNDERLINED_OFF)
sgr_parity_registry.register_single(intcode.BLINK_SLOW, intcode.BLINK_OFF)
sgr_parity_registry.register_single(intcode.BLINK_FAST, intcode.BLINK_OFF)
sgr_parity_registry.register_single(intcode.INVERSED, intcode.INVERSED_OFF)
sgr_parity_registry.register_single(intcode.HIDDEN, intcode.HIDDEN_OFF)
sgr_parity_registry.register_single(intcode.CROSSLINED, intcode.CROSSLINED_OFF)
sgr_parity_registry.register_single(intcode.OVERLINED, intcode.OVERLINED_OFF)

for c in [intcode.BLACK, intcode.RED, intcode.GREEN, intcode.YELLOW, intcode.BLUE, intcode.MAGENTA, intcode.CYAN, intcode.WHITE, intcode.GRAY,
          intcode.HI_RED, intcode.HI_GREEN, intcode.HI_YELLOW, intcode.HI_BLUE, intcode.HI_MAGENTA, intcode.HI_CYAN, intcode.HI_WHITE]:
    sgr_parity_registry.register_single(c, intcode.COLOR_OFF)

for c in [intcode.BG_BLACK, intcode.BG_RED, intcode.BG_GREEN, intcode.BG_YELLOW, intcode.BG_BLUE, intcode.BG_MAGENTA, intcode.BG_CYAN,
          intcode.BG_WHITE, intcode.BG_GRAY, intcode.BG_HI_RED, intcode.BG_HI_GREEN, intcode.BG_HI_YELLOW, intcode.BG_HI_BLUE,
          intcode.BG_HI_MAGENTA, intcode.BG_HI_CYAN, intcode.BG_HI_WHITE]:
    sgr_parity_registry.register_single(c, intcode.BG_COLOR_OFF)


sgr_parity_registry.register_complex((intcode.COLOR_EXTENDED, 5), 1, intcode.COLOR_OFF)
sgr_parity_registry.register_complex((intcode.COLOR_EXTENDED, 2), 3, intcode.COLOR_OFF)
sgr_parity_registry.register_complex((intcode.BG_COLOR_EXTENDED, 5), 1, intcode.BG_COLOR_OFF)
sgr_parity_registry.register_complex((intcode.BG_COLOR_EXTENDED, 2), 3, intcode.BG_COLOR_OFF)
