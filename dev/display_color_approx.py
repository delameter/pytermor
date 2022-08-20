# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022. A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
"""
USAGE
    display_color_approx <target_color>

ARGUMENTS
    target_color    target color in RGB format, e.g. "a4bd68"

"""
from __future__ import annotations

import sys

from pytermor import ColorIndexed, Span, ansi, ColorRGB


def _main(target_color_hex: int):
    if target_color_hex > 0xffffff:
        _die(f'Invalid color value (should be < 0xffffff): '
             f'0x{target_color_hex:06x}')

    color_target = ColorRGB(target_color_hex)
    colors_indexed = ColorIndexed._approx.approximate(target_color_hex, 5)
    for color_indexed in colors_indexed:
        sgr_indexed = color_indexed.to_sgr(True)
        if sgr_indexed.params[-1] < 16:  # @FIXME костыль
            sgr_indexed = ColorRGB(color_indexed.hex_value).to_sgr(True)
        print(Span(
            color_target.to_sgr(True) + Seqs.BLACK).wrap(f' {color_target} ') +
              Span(sgr_indexed + Seqs.BLACK).wrap(f' {color_indexed} '))


def _die(reason: str|Exception = None):
    if reason:
        print(f'ERROR: {reason!s}')
    _usage()
    exit(1)


def _usage():
    print(__doc__)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        _die()

    try:
        _main(int(sys.argv[1], 16))
    except ValueError as e:
        _die(e)
