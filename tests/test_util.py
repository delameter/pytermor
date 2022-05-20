# -----------------------------------------------------------------------------
# pytermor [ANSI formatted terminal output toolset]
# (C) 2022 A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
import unittest

from pytermor import SequenceSGR, span
from pytermor.util import center_aware, ReplaceSGR


class TestStringFilter(unittest.TestCase):  # @TODO
    def test_replace_sgr_filter(self):
        self.assertEqual(
            ReplaceSGR().apply(span.red('213')),
            '213'
        )
    pass


class TestStdlibExtensions(unittest.TestCase):  # @TODO
    def test_center_method(self):
        self.assertRegexpMatches(
            center_aware(span.red('123'), 7),
            f'  {SequenceSGR.regexp()}123{SequenceSGR.regexp()}  '
        )
