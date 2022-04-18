import unittest

from pytermor import seq
from pytermor.registry import sgr_parity_registry


class RegistryTestCase(unittest.TestCase):  # @TODO more
    def test_closing_seq(self):
        self.assertEqual(sgr_parity_registry.get_closing_seq(seq.BOLD + seq.RED), seq.BOLD_DIM_OFF + seq.COLOR_OFF)

