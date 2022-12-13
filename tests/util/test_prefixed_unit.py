# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022. A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
import logging
import unittest

from pytermor.utilnum import (
    format_si_metric,
    format_si_binary,
    PrefixedUnitFormatter,
    PREFIXES_SI,
    PREFIX_ZERO_SI,
)


class TestPrefixedUnit(unittest.TestCase):
    # fmt: off
    expected_format_dataset = [
        [format_si_binary, [
            # ['-20.5 ?b', -2.54324345e28], ['- 192 Yb', -0.2315142e27],
            # ['-1.59 Yb', -1.9218723e24], ['-1.58 Zb', -1.871231e21],
            # ['-1.42 Eb', -1.6414761e18], ['-1.42 Pb', -1.60292e15],
            # ['- 142 Tb', -156.530231e12], ['-13.5 Gb', -14.5301e9],
            # ['-2.33 Gb', -2501234567], ['- 668 Mb', -700500000],
            # ['-41.1 Mb', -43106100], ['-1.20 Mb', -1257800],
            ['-130 kb', -133300], ['-44 kb', -45200],
            ['-14 kb', -15000], ['-6 kb', -6230],
            ['-1 kb', -1080], ['-1 kb', -1024],
            ['-1010 b', -1010], ['-631 b', -631],
            ['-180 b', -180], ['-43 b', -43],
            ['-10 b', -10], ['-1 b', -1],
            ['0 b', -0.1], ['0 b', -0.01],
            ['0 b', -0], ['0 b', -0.0],
            ['0 b', 0], ['0 b', 0.0],
            ['0 b', 0.1], ['0 b', 0.01],
            ['1 b', 1], ['10 b', 10],
            ['43 b', 43], ['180 b', 180],
            ['631 b', 631], ['1010 b', 1010],
            ['1 kb', 1024], ['1 kb', 1080],
            ['6 kb', 6230], ['14 kb', 15000],
            ['44 kb', 45200], ['130 kb', 133300],
            ['1 Mb', 1257800], ['41 Mb', 43106100],
            ['668 Mb', 700500000], ['2 Gb', 2501234567],
            ['13 Gb', 14.53041e9], ['142 Tb', 156.530231e12],
            ['1 Pb', 1.602989e15], ['1 Eb', 1.641669584e18],
            ['1 Zb', 1.8719334e21], ['1 Yb', 1.921267334e24],
            ['191 Yb', 2.31487598e26], ['20 ?b', 2.543258343e28],
        ]], [lambda val: format_si_metric(val, unit=''), [
            ['12.3 ?', 1.23456789e28],
            ['12.3 Y', 1.23456789e25], ['12.3 Z', 1.23456789e22], ['12.3 E', 1.23456789e19],
            ['1.23 E', 1.23456789e18], ['123 P', 1.23456789e17], ['12.3 P', 1.23456789e16],
            ['1.23 P', 1.23456789e15], ['123 T', 1.23456789e14], ['12.3 T', 1.23456789e13],
            ['1.23 T', 1.23456789e12], ['123 G', 1.23456789e11], ['12.3 G', 1.23456789e10],
            ['1.23 G', 1.23456789e9], ['123 M', 1.23456789e8], ['12.3 M', 1.23456789e7],
            ['1.23 M', 1.23456789e6], ['123 k', 1.23456789e5], ['12.3 k', 1.23456789e4],
            ['1.23 k', 1.23456789e3], ['123', 1.23456789e2], ['12.3', 1.23456789e1],
            ['1.23', 1.23456789],
            ['0.12', 0.123456789], ['12.3 m', 1.23456789e-2], ['1.23 m', 1.23456789e-3],
            ['0.12 m', 1.23456789e-4], ['12.3 μ', 1.23456789e-5], ['1.23 μ', 1.23456789e-6],
            ['0.12 μ', 1.23456789e-7], ['12.3 n', 1.23456789e-8], ['1.23 n', 1.23456789e-9],
            ['0.12 n', 1.23456789e-10], ['12.3 p', 1.23456789e-11], ['1.23 p', 1.23456789e-12],
            ['0.12 p', 1.23456789e-13], ['12.3 f', 1.23456789e-14], ['1.23 f', 1.23456789e-15],
            ['0.12 f', 1.23456789e-16], ['12.3 a', 1.23456789e-17], ['1.23 a', 1.23456789e-18],
            ['0.12 a', 1.23456789e-19], ['0.12 z', 1.23456789e-22], ['0.12 y', 1.23456789e-25],
            ['0.12 ?', 1.23456789e-28],
        ]], [lambda val: format_si_metric(val, unit='m'), [
            ['100.0 am', 1e-16], ['10.00 am', 1e-17], ['1.00 am', 1e-18],
            ['100.0 fm', 1e-13], ['10.00 fm', 1e-14], ['1.00 fm', 1e-15],
            ['100.0 pm', 1e-10], ['10.00 pm', 1e-11], ['1.00 pm', 1e-12],
            ['100.0 nm', 1e-07], ['10.00 nm', 1e-08], ['1.00 nm', 1e-09],
            ['10.00 μm', 1e-05],  ['5.00 μm', 5e-06], ['1.00 μm', 1e-06],
            ['-0.5 mm', -5e-04], ['-0.1 mm', -1e-04], ['- 50 μm',-5e-05],  # <-- isn't 100 μm better than 0.1 mm ?
            ['0.50 mm',  5e-04], ['0.10 mm',  1e-04], ['50.0 μm', 5e-05],
            ['10.00 mm', 1e-02], ['5.00 mm',  5e-03], ['1.00 mm', 1e-03],
            ['0.50 m',   5e-01],  ['0.10 m',  1e-01], ['50.0 mm', 5e-02],
            ['1.00 m',  1],
            ['0 m',    -0], ['0 m', -0.0],
            ['0 m',     0], ['0 m',  0.0],
        ]], [lambda val: format_si_metric(val, unit='V'), [
            ['5.00 V',      5], ['10.0 V',   1e01], ['50.0 V',   5e01],
            ['100 V',    1e02], ['500 V',    5e02], ['1.00 kV',  1e03],
            ['5.00 kV',  5e03], ['10.0 kV',  1e04], ['50.0 kV',  5e04],
            ['100 kV',   1e05], ['500 kV',   5e05], ['1.00 MV',  1e06],
            ['-100 kV', -1e05], ['-500 kV', -5e05], ['-1.0 MV', -1e06],
            ['10.0 MV',  1e07], ['100 MV',   1e08], ['1.00 GV',  1e09],
            ['10.0 GV',  1e10], ['100 GV',   1e11], ['1.00 TV',  1e12],
            ['10.0 TV',  1e13], ['100 TV',   1e14], ['1.00 PV',  1e15],
            ['10.0 PV',  1e16], ['100 PV',   1e17], ['1.00 EV',  1e18],
        ]]
    ]
    # fmt: on

    def test_output_has_expected_format(self):
        for formatter_idx, (formatter_fn, formatter_input) in enumerate(
            self.expected_format_dataset
        ):
            for input_idx, (expected_output, input_num) in enumerate(formatter_input):
                subtest_msg = f'prefixed/match F{formatter_idx} #{input_idx}: "{input_num:.2e}" -> "{expected_output}"'

                with self.subTest(msg=subtest_msg):
                    actual_output = formatter_fn(input_num)
                    logging.debug(subtest_msg + f' => "{actual_output}"')

                    self.assertEqual(expected_output, actual_output)

    """ ----------------------------------------------------------------------------------------------------------- """

    req_len_dataset = [
        [6, lambda val: format_si_metric(val, unit="")],
        [8, format_si_binary],
        [
            6,
            PrefixedUnitFormatter(
                max_value_len=4,
                truncate_frac=False,
                mcoef=1000.0,
                prefixes=PREFIXES_SI,
                prefix_zero_idx=PREFIX_ZERO_SI,
                unit="m",
                unit_separator=None,
            ).format,
        ],
        [
            10,
            PrefixedUnitFormatter(
                max_value_len=9,
                truncate_frac=False,
                mcoef=1000.0,
                prefixes=PREFIXES_SI,
                prefix_zero_idx=PREFIX_ZERO_SI,
                unit=None,
                unit_separator=None,
            ).format,
        ],
    ]
    req_len_input_num_list = [
        0.076 * pow(11, x) * (1 - 2 * (x % 2)) for x in range(-20, 20)
    ]

    def test_output_fits_in_required_length(self):
        for formatter_idx, (expected_max_len, formatter_fn) in enumerate(
            self.req_len_dataset
        ):
            logging.debug(f"expected_max_len={expected_max_len}: ")

            for input_idx, input_num in enumerate(self.req_len_input_num_list):
                subtest_msg = (
                    f'prefixed/len P{formatter_idx} #{input_idx} "{input_num:.2e}"'
                    f" -> (len {expected_max_len})"
                )

                with self.subTest(msg=subtest_msg):
                    actual_output = formatter_fn(input_num)
                    logging.debug(
                        subtest_msg + f' => (len {len(actual_output)}) "{actual_output}"'
                    )

                    self.assertGreaterEqual(
                        expected_max_len,
                        len(actual_output),
                        f'Actual output ("{actual_output}") exceeds maximum',
                    )
