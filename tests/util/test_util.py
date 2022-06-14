# -----------------------------------------------------------------------------
# pytermor [ANSI formatted terminal output toolset]
# (C) 2022 A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
import unittest

from pytermor import span
from pytermor.util import center_sgr, ReplaceSGR
from pytermor.sequence import SequenceSGR


class TestStringFilter(unittest.TestCase):  # @TODO
    def test_replace_sgr_filter(self):
        self.assertEqual(
            ReplaceSGR().apply(span.RED('213')),
            '213'
        )
    pass


class TestStdlibExtensions(unittest.TestCase):  # @TODO
    def test_center_method(self):
        self.assertRegexpMatches(
            center_sgr(span.RED('123'), 7),
            f'  {SequenceSGR.regexp()}123{SequenceSGR.regexp()}  '
        )
