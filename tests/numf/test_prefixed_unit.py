# -----------------------------------------------------------------------------
# pytermor [ANSI formatted terminal output toolset]
# (C) 2022 A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
import unittest

from pytermor import format_prefixed_unit, PRESET_SI_BINARY, PRESET_SI_METRIC, PrefixedUnitPreset
from tests import print_verbose


class TestPrefixedUnit(unittest.TestCase):
    expected_format_high_dataset = [
        ['-142 Tb', -156530231500223], ['-13.5 Gb', -14530231500],
        ['-2.33 Gb', -2501234567], ['-668 Mb', -700500000],
        ['-41.1 Mb', -43106100], ['-1.20 Mb', -1257800],
        ['-130 kb', -133300], ['-44.1 kb', -45200],
        ['-14.6 kb', -15000], ['-6.08 kb', -6230],
        ['-1.05 kb', -1080], ['-1.00 kb', -1024],
        ['-1010 b', -1010], ['-631 b', -631],
        ['-180 b', -180], ['-43 b', -43],
        ['-10 b', -10], ['-1 b', -1],
        ['0 b', 0],
        ['1 b', 1], ['10 b', 10],
        ['43 b', 43], ['180 b', 180],
        ['631 b', 631], ['1010 b', 1010],
        ['1.00 kb', 1024], ['1.05 kb', 1080],
        ['6.08 kb', 6230], ['14.65 kb', 15000],
        ['44.14 kb', 45200], ['130.2 kb', 133300],
        ['1.20 Mb', 1257800], ['41.11 Mb', 43106100],
        ['668.0 Mb', 700500000], ['2.33 Gb', 2501234567],
        ['13.53 Gb', 14530231500], ['142.4 Tb', 156530231500223],
    ]

    def test_output_high_has_expected_format(self):
        for idx, (expected_output, input_num) in enumerate(self.expected_format_high_dataset):
            with self.subTest(msg=f'Testing #{idx} {input_num} -> "{expected_output}"'):
                actual_output = format_prefixed_unit(input_num, PRESET_SI_BINARY)
                print_verbose(actual_output, end=', ')
                self.assertEqual(expected_output, actual_output)

    # @TODO incomplete
    expected_format_low_dataset = [
        ['1.00 m', 1],
        ['0.10 m', 0.1],
        ['0.01 m', 1e-2],  # @FIXME 10.0mm
        ['1.00 mm', 1e-3],
    ]

    def test_output_low_has_expected_format(self):
        for idx, (expected_output, input_num) in enumerate(self.expected_format_low_dataset):
            with self.subTest(msg=f'Testing #{idx} {input_num} -> "{expected_output}"'):
                actual_output = format_prefixed_unit(input_num, PRESET_SI_METRIC)
                print_verbose(actual_output, end=', ')
                self.assertEqual(expected_output, actual_output)

    req_len_dataset = [
        [8, PRESET_SI_METRIC],
        [8, PRESET_SI_BINARY],
        [5, PrefixedUnitPreset(
            max_value_len=3, integer_input=True, mcoef=1000.0,
            prefixes=PRESET_SI_METRIC.prefixes,
            prefix_zero_idx=PRESET_SI_METRIC.prefix_zero_idx,
            unit=None, unit_separator=None,
        )],
        [6, PrefixedUnitPreset(
            max_value_len=4, integer_input=True, mcoef=1000.0,
            prefixes=PRESET_SI_METRIC.prefixes,
            prefix_zero_idx=PRESET_SI_METRIC.prefix_zero_idx,
            unit=None, unit_separator=None,
        )],
    ]
    req_len_input_num_list = [.076 * pow(11, x) * (-1 * (x % 2)) for x in range(-20, 20)]

    def test_output_fits_in_required_length(self):
        for preset_idx, (expected_max_len, preset) in enumerate(self.req_len_dataset):
            print_verbose(f'\nLEN={expected_max_len:d}', end=': ')
            for input_idx, input_num in enumerate(self.req_len_input_num_list):
                with self.subTest(msg=f'Testing P{preset_idx} #{input_idx} "{input_num}" -> max length {expected_max_len}'):
                    actual_output = format_prefixed_unit(input_num, preset)
                    print_verbose(actual_output, end=', ')
                    self.assertGreaterEqual(expected_max_len,
                                            len(actual_output),
                                            f'Actual output ("{actual_output}") exceeds maximum')