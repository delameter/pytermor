# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under GNU Lesser General Public License v3.0
# -----------------------------------------------------------------------------
import pytest

from pytermor import Align, render, Fragment
from pytermor.ansi import SeqIndex
from pytermor.utilstr import center_sgr, SgrStringReplacer, StringAligner


class TestStringFilter:  # @TODO
    def test_replace_sgr_filter(self):
        actual = SgrStringReplacer().apply(f"{SeqIndex.RED}213{SeqIndex.RESET}")
        expected = "213"
        assert actual == expected


@pytest.mark.setup(output_mode='TRUE_COLOR')
class TestStringAligner:
    @pytest.mark.parametrize('expected,align,width', [
        ("\x1b[31m" "123" "\x1b[39m\x1b[34m" "456" "\x1b[39m" "   ", Align.LEFT, 9),
        ("  \x1b[31m" "123" "\x1b[39m\x1b[34m" "456" "\x1b[39m ", Align.CENTER, 9),
        ("   \x1b[31m" "123" "\x1b[39m\x1b[34m" "456" "\x1b[39m", Align.RIGHT, 9),
    ])
    def test_sgr_aware_mode(self, expected: str, align: Align, width: int):
        inp = render(Fragment("123", "red")+Fragment("456", "blue"))
        actual = StringAligner(align, width, sgr_aware=True).apply(inp)
        assert actual == expected

class TestStdlibExtensions:  # @TODO
    def test_center_method_works(self):
        actual = center_sgr(f"{SeqIndex.RED}123{SeqIndex.COLOR_OFF}", 7, ".")
        expected = "..\x1b[31m123\x1b[39m.."
        assert actual == expected

    @pytest.mark.parametrize("len_shift", range(-3, 3))
    @pytest.mark.parametrize("width", range(4, 18))
    def test_center_methods_is_equivalent_to_stdlib(self, width: int, len_shift: int):
        len = width + len_shift
        assert len > 0

        raw_string = "123_456_789_0abc_def_"[:len]
        sgr_string = raw_string.replace("123", f"1{SeqIndex.RED}2{SeqIndex.COLOR_OFF}3")
        actual = raw_string.center(width, ".")
        expected = SgrStringReplacer().apply(center_sgr(sgr_string, width, "."))
        assert actual == expected
