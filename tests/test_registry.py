# -----------------------------------------------------------------------------
# pytermor [ANSI formatted terminal output toolset]
# (C) 2022 A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
import unittest

from pytermor import sequence
from pytermor.registry import sgr_parity_registry


class TestRegistry(unittest.TestCase):  # @TODO more
    def test_closing_seq(self):
        self.assertEqual(
            sgr_parity_registry.get_closing_seq(sequence.BOLD + sequence.RED),
            sequence.NO_BOLD_DIM + sequence.COLOR_OFF
        )
