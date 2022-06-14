# -----------------------------------------------------------------------------
# pytermor [ANSI formatted terminal output toolset]
# (C) 2022 A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
import logging
import unittest

from pytermor.util import PrefixedUnitFormatter, PREFIXES_SI, PREFIX_ZERO_SI, format_si_binary, format_si_metric


class TestPrefixedUnit(unittest.TestCase):
    expected_format_dataset = [
        [format_si_binary, [
            ['-2054 ?b', -2.54324345e30], ['- 205 ?b', -2.54324345e29],
            ['-20.5 ?b', -2.54324345e28], ['- 192 Yb', -0.2315142e27],
            ['-1.59 Yb', -1.9218723e24], ['-1.58 Zb', -1.871231e21],
            ['-1.42 Eb', -1.6414761e18], ['-1.42 Pb', -1.60292e15],
            ['- 142 Tb', -156.530231e12], ['-13.5 Gb', -14.5301e9],
            ['-2.33 Gb', -2501234567], ['- 668 Mb', -700500000],
            ['-41.1 Mb', -43106100], ['-1.20 Mb', -1257800],
            ['- 130 kb', -133300], ['-44.1 kb', -45200],
            ['-14.6 kb', -15000], ['-6.08 kb', -6230],
            ['-1.05 kb', -1080], ['-1.00 kb', -1024],
            ['-1010 b', -1010], ['-631 b', -631],
            ['-180 b', -180], ['-43 b', -43],
            ['-10 b', -10], ['-1 b', -1],
            ['0 b', 0],
            ['1 b', 1], ['10 b', 10],
            ['43 b', 43], ['180 b', 180],
            ['631 b', 631], ['1010 b', 1010],
            ['1.000 kb', 1024], ['1.055 kb', 1080],
            ['6.084 kb', 6230], ['14.65 kb', 15000],
            ['44.14 kb', 45200], ['130.2 kb', 133300],
            ['1.200 Mb', 1257800], ['41.11 Mb', 43106100],
            ['668.0 Mb', 700500000], ['2.329 Gb', 2501234567],
            ['13.53 Gb', 14.53041e9], ['142.4 Tb', 156.530231e12],
            ['1.424 Pb', 1.602989e15], ['1.424 Eb', 1.641669584e18],
            ['1.586 Zb', 1.8719334e21], ['1.589 Yb', 1.921267334e24],
            ['191.5 Yb', 2.31487598e26], ['20.54 ?b', 2.543258343e28],
        ]], [format_si_metric, [
            ['12.3 ?', 1.23456789e28],
            ['12.3 Y', 1.23456789e25], ['12.3 Z', 1.23456789e22], ['12.3 E', 1.23456789e19],
            ['1.23 E', 1.23456789e18], ['123 P', 1.23456789e17], ['12.3 P', 1.23456789e16],
            ['1.23 P', 1.23456789e15], ['123 T', 1.23456789e14], ['12.3 T', 1.23456789e13],
            ['1.23 T', 1.23456789e12], ['123 G', 1.23456789e11], ['12.3 G', 1.23456789e10],
            ['1.23 G', 1.23456789e9], ['123 M', 1.23456789e8], ['12.3 M', 1.23456789e7],
            ['1.23 M', 1.23456789e6], ['123 k', 1.23456789e5], ['12.3 k', 1.23456789e4],
            ['1.23 k', 1.23456789e3], ['123', 1.23456789e2], ['12.3', 1.23456789e1],
            ['1.23', 1.23456789],
            ['0.12', 0.123456789], ['0.01', 1.23456789e-2], ['0.00', 1.23456789e-3],
            ['0.12 m', 1.23456789e-4], ['0.01 m', 1.23456789e-5], ['0.00 m', 1.23456789e-6],
            ['0.12 μ', 1.23456789e-7], ['0.01 μ', 1.23456789e-8], ['0.00 μ', 1.23456789e-9],
            ['0.12 n', 1.23456789e-10], ['0.01 n', 1.23456789e-11], ['0.00 n', 1.23456789e-12],
            ['0.12 p', 1.23456789e-13], ['0.01 p', 1.23456789e-14], ['0.00 p', 1.23456789e-15],
            ['0.12 f', 1.23456789e-16], ['0.01 f', 1.23456789e-17], ['0.00 f', 1.23456789e-18],
            ['0.12 a', 1.23456789e-19], ['0.12 z', 1.23456789e-22], ['0.12 y', 1.23456789e-25],
            ['0.12 ?', 1.23456789e-28],
        ]]
    ]

    def test_output_has_expected_format(self):
        for formatter_idx, (formatter_fn, formatter_input) in enumerate(self.expected_format_dataset):
            for input_idx, (expected_output, input_num) in enumerate(formatter_input):
                subtest_msg = f'prefixed/match F{formatter_idx} #{input_idx}: "{input_num:.2e}" -> "{expected_output}"'

                with self.subTest(msg=subtest_msg):
                    actual_output = formatter_fn(input_num)
                    logging.debug(subtest_msg + f' => "{actual_output}"')

                    self.assertEqual(expected_output, actual_output)

    """ ----------------------------------------------------------------------------------------------------------- """

    req_len_dataset = [
        [6, format_si_metric],
        [8, format_si_binary],
        [6, PrefixedUnitFormatter(
            max_value_len=4, integer_input=False, mcoef=1000.0,
            prefixes=PREFIXES_SI,
            prefix_zero_idx=PREFIX_ZERO_SI,
            unit='m', unit_separator=None,
        ).format],
        [10, PrefixedUnitFormatter(
            max_value_len=9, integer_input=False, mcoef=1000.0,
            prefixes=PREFIXES_SI,
            prefix_zero_idx=PREFIX_ZERO_SI,
            unit=None, unit_separator=None,
        ).format],
    ]
    req_len_input_num_list = [.076 * pow(11, x) * (1 - 2 * (x % 2)) for x in range(-20, 20)]

    def test_output_fits_in_required_length(self):
        for formatter_idx, (expected_max_len, formatter_fn) in enumerate(self.req_len_dataset):
            logging.debug(f'expected_max_len={expected_max_len}: ')

            for input_idx, input_num in enumerate(self.req_len_input_num_list):
                subtest_msg = f'prefixed/len P{formatter_idx} #{input_idx} "{input_num:.2e}" -> (len {expected_max_len})'

                with self.subTest(msg=subtest_msg):
                    actual_output = formatter_fn(input_num)
                    logging.debug(subtest_msg + f' => (len {len(actual_output)}) "{actual_output}"')

                    self.assertGreaterEqual(expected_max_len,
                                            len(actual_output),
                                            f'Actual output ("{actual_output}") exceeds maximum')
