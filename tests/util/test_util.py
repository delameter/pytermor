# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022. A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
import unittest

from pytermor.ansi import Spans
from pytermor.util import format_thousand_sep
from pytermor.util.stdlib_ext import center_sgr
from pytermor.util.string_filter import ReplaceSGR


class TestFormatThousandSep(unittest.TestCase):
    def test_output_has_expected_format(self):
        self.assertEqual(
            format_thousand_sep(1234567890),
            '1 234 567 890'
        )


class TestStringFilter(unittest.TestCase):  # @TODO
    def test_replace_sgr_filter(self):
        self.assertEqual(
            ReplaceSGR().apply(Spans.RED('213')),
            '213'
        )

    pass


class TestStdlibExtensions(unittest.TestCase):  # @TODO
    def test_center_method_works(self):
        self.assertEqual(
            center_sgr(Spans.RED('123'), 7, '.'),
            '..\x1b[31m123\x1b[39m..',
        )

    def test_center_methods_is_equivavlent_to_stdlib(self):
        for width in range(3, 18):
            for len in range(width - 3, width + 3):
                if len <= 0:
                    continue
                raw_string = '123_456_789_0abc_def_'[:len]
                sgr_string = raw_string.replace('123', '1'+Spans.RED('2')+'3')
                self.assertEqual(
                    raw_string.center(width, '.'),
                    ReplaceSGR().apply(center_sgr(sgr_string, width, '.')),
                )
