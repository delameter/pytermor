# -----------------------------------------------------------------------------
# pytermor [ANSI formatted terminal output toolset]
# (C) 2022 A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
import unittest

from pytermor import format_auto_float
from tests import verb_print_info, verb_print_subtests


class TestAutoFloat(unittest.TestCase):
    expected_format_dataset = [
        ['0.0', [0, 3]],
        ['6.0', [6, 3]],
        ['146', [145.66, 3]],
        ['300.0', [300, 5]],
        ['30.00', [30, 5]],
        ['3.000', [3, 5]],
        ['0.300', [.3, 5]],
        ['0.030', [.03, 5]],
        ['0.003', [.003, 5]],
        ['-5.00', [-5, 5]],
        [' -512', [-512, 5]],
        ['1.2000', [1.2, 6]],
        ['123456', [123456, 6]],
        ['0.0001', [0.00012, 6]],
        ['0.0120', [0.012, 6]],
    ]

    def test_output_has_expected_format(self):
        verb_print_info()

        for idx, (expected_output, args) in enumerate(self.expected_format_dataset):
            subtest_msg = f'autofloat/match #{idx}: >{args[1]}< "{args[0]:.2e}" -> "{expected_output}"'

            with self.subTest(msg=subtest_msg):
                actual_output = format_auto_float(*args)
                verb_print_info(subtest_msg + f' => "{actual_output}"')
                self.assertEqual(expected_output, actual_output)
        verb_print_subtests(len(self.expected_format_dataset))
