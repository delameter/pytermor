# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
import unittest

import pytermor as pt
from pytermor.ansi import SeqIndex
from pytermor.utilstr import center_sgr, SgrStringReplacer
from pytermor import format_thousand_sep


class TestFormatThousandSep(unittest.TestCase):
    def test_output_has_expected_format(self):
        self.assertEqual(format_thousand_sep(1234567890), "1 234 567 890")


class TestStringFilter(unittest.TestCase):  # @TODO
    def test_replace_sgr_filter(self):
        self.assertEqual(
            SgrStringReplacer().apply(f"{SeqIndex.RED}213{SeqIndex.RESET}"), "213"
        )


class TestStdlibExtensions(unittest.TestCase):  # @TODO
    def test_center_method_works(self):
        self.assertEqual(
            center_sgr(f"{SeqIndex.RED}123{SeqIndex.COLOR_OFF}", 7, "."),
            "..\x1b[31m123\x1b[39m..",
        )

    def test_center_methods_is_equivavlent_to_stdlib(self):
        for width in range(3, 18):
            for len in range(width - 3, width + 3):
                if len <= 0:
                    continue
                raw_string = "123_456_789_0abc_def_"[:len]
                sgr_string = raw_string.replace(
                    "123", f"1{SeqIndex.RED}2{SeqIndex.COLOR_OFF}3"
                )
                self.assertEqual(
                    raw_string.center(width, "."),
                    SgrStringReplacer().apply(center_sgr(sgr_string, width, ".")),
                )
