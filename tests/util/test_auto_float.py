# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022. A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
import logging
import unittest
from typing import List

from pytermor.utilnum import format_auto_float


class TestAutoFloat(unittest.TestCase):
    def _test_output_has_expected_format(self, dataset: List[List]):
        format_auto_float(123.456, 4)

        for idx, args in enumerate(dataset):
            (expected_output, value, max_len) = args
            subtest_msg = f'autofloat/match #{idx}: >{max_len}< "{value:.2e}" -> "{expected_output}"'

            with self.subTest(msg=subtest_msg):
                self.assertEqual(
                    len(expected_output), max_len, f"Invalid expectations for {args}"
                )

                actual_output = format_auto_float(value, max_len)
                actual_output = actual_output.replace(" ", "_")
                logging.debug(subtest_msg + f' => "{actual_output}"')

                self.assertEqual(expected_output, actual_output, f"for {args}")


# fmt: off
class TestAutoFloatFixedLength(TestAutoFloat):
    def test_length6_has_expected_format(self):
        self._test_output_has_expected_format([
            ['5.3e10',   5.251505e10, 6],
            ['5.25e7',    5.251505e7, 6],
            ['5.25e6',    5.251505e6, 6],
            ['525150',    5.251505e5, 6],
            ['_52515',    5.251505e4, 6],
            ['5251.5',    5.251505e3, 6],
            ['525.15',    5.251505e2, 6],
            ['52.515',    5.251505e1, 6],
            ['5.2515',    5.251505e0, 6],
            ['0.5252',   5.251505e-1, 6],
            ['0.0525',   5.251505e-2, 6],
            ['5.3e-3',   5.251505e-3, 6],
            ['5.3e-4',   5.251505e-4, 6],
            ['5.3e-5',   5.251505e-5, 6],
            ['5.3e-6',   5.251505e-6, 6],
            ['5.3e-7',   5.251505e-7, 6],

            ['-5e-10', -5.251505e-10, 6],
            ['-_5e10',  -5.251505e10, 6],
            ['-5.3e7',   -5.251505e7, 6],
            ['-5.3e6',   -5.251505e6, 6],
            ['-5.3e5',   -5.251505e5, 6],
            ['-52515',   -5.251505e4, 6],
            ['-_5252',   -5.251505e3, 6],
            ['-525.2',   -5.251505e2, 6],
            ['-52.52',   -5.251505e1, 6],
            ['-5.252',   -5.251505e0, 6],
            ['-0.525',  -5.251505e-1, 6],
            ['-0.053',  -5.251505e-2, 6],
            ['-_5e-3',  -5.251505e-3, 6],
            ['-_5e-4',  -5.251505e-4, 6],
            ['-_5e-5',  -5.251505e-5, 6],
            ['-_5e-6',  -5.251505e-6, 6],
            ['-_5e-7',  -5.251505e-7, 6],
            ['-5e-10', -5.251505e-10, 6],
        ])

    def test_shorter_length_has_expected_format(self):
        # 4-, @TODO
        pass


class TestAutoFloatFixedValue(TestAutoFloat):
    def test_exp_minus_1_has_expected_format(self):
        self._test_output_has_expected_format([
            [          '',  0.12345,  0],
            [         '0',  0.12345,  1],
            [        '_0',  0.12345,  2],
            [       '0.1',  0.12345,  3],
            [      '0.12',  0.12345,  4],
            [     '0.123',  0.12345,  5],
            ['0.12345000',  0.12345, 10],
            [          '', -0.12345,  0],
            [         '!', -0.12345,  1],
            [        '-0', -0.12345,  2],
            [       '-_0', -0.12345,  3],
            [      '-0.1', -0.12345,  4],
            [     '-0.12', -0.12345,  5],
            ['-0.1234500', -0.12345, 10],
        ])

    def test_exp_beetween_0_and_10_has_expected_format(self):
        self._test_output_has_expected_format([
            [          '',  1.23456789e9,  0],
            [         '!',  1.23456789e9,  1],
            [        'e9',  1.23456789e9,  2],
            [       '1e9',  1.23456789e9,  3],
            [      '_1e9',  1.23456789e9,  4],
            [     '1.2e9',  1.23456789e9,  5],
            [    '1.23e9',  1.23456789e9,  6],
            [   '1.235e9',  1.23456789e9,  7],
            [  '1.2346e9',  1.23456789e9,  8],
            [ '1.23457e9',  1.23456789e9,  9],
            ['1234567890',  1.23456789e9, 10],
            [          '', -9.87654321e8,  0],
            [         '!', -9.87654321e8,  1],
            [        '!!', -9.87654321e8,  2],
            [       '-e8', -9.87654321e8,  3],
            [      '-9e8', -9.87654321e8,  4],
            [     '-10e8', -9.87654321e8,  5],
            [    '-9.9e8', -9.87654321e8,  6],
            [   '-9.88e8', -9.87654321e8,  7],
            [  '-9.877e8', -9.87654321e8,  8],
            [ '-9.8765e8', -9.87654321e8,  9],
            ['-987654321', -9.87654321e8, 10],
        ])

    def test_exp_greater_than_10_has_expected_format(self):
        self._test_output_has_expected_format([
            [       '!!',  123456789012345, 2],
            [      'e14',  123456789012345, 3],
            [     '1e14',  123456789012345, 4],
            [    '10e13',   98765432109876, 5],
            [    '_1e14',  123456789012345, 5],  # <-- 12e13 would be better than _1e14
            [   '9.9e13',   98765432109876, 6],  #     (+1 significant digit), but decided that
            [   '1.2e14',  123456789012345, 6],  #     the more normalized notation - the better
            [  '9.88e13',   98765432109876, 7],
            [  '1.23e14',  123456789012345, 7],
            [ '9.877e13',   98765432109876, 8],
            [ '1.235e14',  123456789012345, 8],
            ['9.8765e13',   98765432109876, 9],
            [       '!!',  -98765432109876, 2],
            [      '!!!',  -98765432109876, 3],
            [     '-e13',  -98765432109876, 4],
            [     '-e14', -123456789012345, 4],
            [    '-9e13',  -98765432109876, 5],
            [    '-1e14', -123456789012345, 5],
            [   '-10e13',  -98765432109876, 6],
            [  '-9.9e13',  -98765432109876, 7],
            [ '-9.88e13',  -98765432109876, 8],
            ['-9.877e13',  -98765432109876, 9],
        ])

    def test_int_tight_fit_has_expected_format(self):
        self._test_output_has_expected_format([
            [   '',     0, 0],
            [   '',   0.0, 0],
            [   '',   1.0, 0],
            [   '',  -1.0, 0],
            [  '0',     0, 1],
            [  '0',   0.0, 1],
            [  '2',   2.0, 1],
            [  '!',  -2.0, 1],
            [ '-2',  -2.0, 2],
            [ '_0',     0, 2],
            [ '_0',   0.0, 2],
            [ '_2',   2.0, 2],
            [ '24',  24.0, 2],
            [ '!!', -24.0, 2],
            ['-24', -24.0, 3],
            ['__0',     0, 3],
            ['__0',   0.0, 3],
            ['_24',  24.0, 3],

            # ['9', 9.9, 1],  # @todo
            # ['10', 9.9, 2],
            # ['99', 99.9, 2],
            # ['100', 99.9, 3],
            # [' 100', 99.9, 4],
            # ['-9', -9.9, 2],
            # ['-10', -9.9, 3],
        ])
# fmt: on
