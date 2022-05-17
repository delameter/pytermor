# -----------------------------------------------------------------------------
# pytermor [ANSI formatted terminal output toolset]
# (C) 2022 A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
import unittest

from pytermor import format_auto_float
from tests import print_verbose


class TestAutoFloat(unittest.TestCase):
    expected_format_dataset = [
        ['300.0', [300, 5]],
        ['30.00', [30, 5]],
        [' 3.00', [3, 5]],
        [' 0.30', [.3, 5]],
        [' 0.03', [.03, 5]],
        [' 0.00', [.003, 5]],
        ['-5.00', [-5, 5]],
        [' -512', [-512, 5]],
        ['  1.20', [1.2, 6]],
        ['123456', [123456, 6]],
        ['  0.00', [0.00012, 6]],
        ['  0.01', [0.012, 6]],
        ['0.0', [0, 3]],
        ['6.0', [6, 3]],
        ['146', [145.66, 3]],
    ]

    def test_output_has_expected_format(self):
        for idx, (expected_output, args) in enumerate(self.expected_format_dataset):
            with self.subTest(msg=f'Testing #{idx} "{args}" -> max length {expected_output}'):
                actual_output = format_auto_float(*args)
                print_verbose(actual_output, end=', ')
                self.assertEqual(expected_output, actual_output)