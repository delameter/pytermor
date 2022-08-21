# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022. A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
import unittest

from pytermor.util import format_thousand_sep
from pytermor.util.string_filter import ReplaceSGR
from pytermor.util.stdlib_ext import center_sgr
from pytermor.ansi import Spans, SequenceSGR


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
    def test_center_method(self):
        self.assertRegexpMatches(
            center_sgr(Spans.RED('123'), 7),
            f'  {SequenceSGR.regexp()}123{SequenceSGR.regexp()}  '
        )
