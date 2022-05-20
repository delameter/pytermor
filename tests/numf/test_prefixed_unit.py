# -----------------------------------------------------------------------------
# pytermor [ANSI formatted terminal output toolset]
# (C) 2022 A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
import unittest

from pytermor import format_prefixed_unit, PRESET_SI_BINARY, PRESET_SI_METRIC, PrefixedUnitPreset
from tests import verb_print_info, verb_print_header, verb_print_subtests


class TestPrefixedUnit(unittest.TestCase):
    expected_format_dataset = [
        [PRESET_SI_BINARY, [
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
            ['1.000 kb', 1024], ['1.055 kb', 1080],
            ['6.084 kb', 6230], ['14.65 kb', 15000],
            ['44.14 kb', 45200], ['130.2 kb', 133300],
            ['1.200 Mb', 1257800], ['41.11 Mb', 43106100],
            ['668.0 Mb', 700500000], ['2.329 Gb', 2501234567],
            ['13.53 Gb', 14530231500], ['142.4 Tb', 156530231500223],
        ]], [PRESET_SI_METRIC, [
            ['1.23 m', 1.23456789],
            ['0.12 m', 0.123456789], ['0.01 m', 1.23456789e-2], ['0.00 m', 1.23456789e-3],
            ['0.12 mm', 1.23456789e-4], ['0.01 mm', 1.23456789e-5], ['0.00 mm', 1.23456789e-6],
            ['0.12 μm', 1.23456789e-7], ['0.01 μm', 1.23456789e-8], ['0.00 μm', 1.23456789e-9],
            ['0.12 nm', 1.23456789e-10], ['0.01 nm', 1.23456789e-11], ['0.00 nm', 1.23456789e-12],
            ['0.12 pm', 1.23456789e-13], ['0.01 pm', 1.23456789e-14], ['0.00 pm', 1.23456789e-15],
            ['0.12 fm', 1.23456789e-16], ['0.01 fm', 1.23456789e-17], ['0.00 fm', 1.23456789e-18],
        ]]
    ]

    def test_output_has_expected_format(self):
        verb_print_info()
        subtest_count = 0

        for preset_idx, (preset, preset_input) in enumerate(self.expected_format_dataset):
            for input_idx, (expected_output, input_num) in enumerate(preset_input):
                subtest_msg = f'prefixed/match P{preset_idx} #{input_idx}: "{input_num:.2e}" -> "{expected_output}"'

                with self.subTest(msg=subtest_msg):
                    actual_output = format_prefixed_unit(input_num, preset)
                    verb_print_info(subtest_msg + f' => "{actual_output}"')
                    subtest_count += 1
                    self.assertEqual(expected_output, actual_output)
        verb_print_subtests(subtest_count)

    """ ----------------------------------------------------------------------------------------------------------- """

    req_len_dataset = [
        [7, PRESET_SI_METRIC],
        [8, PRESET_SI_BINARY],
        [5, PrefixedUnitPreset(
            max_value_len=4, integer_input=False, mcoef=1000.0,
            prefixes=PRESET_SI_METRIC.prefixes,
            prefix_zero_idx=PRESET_SI_METRIC.prefix_zero_idx,
            unit=None, unit_separator=None,
        )],
        [10, PrefixedUnitPreset(
            max_value_len=9, integer_input=False, mcoef=1000.0,
            prefixes=PRESET_SI_METRIC.prefixes,
            prefix_zero_idx=PRESET_SI_METRIC.prefix_zero_idx,
            unit=None, unit_separator=None,
        )],
    ]
    req_len_input_num_list = [.076 * pow(11, x) * (1 - 2 * (x % 2)) for x in range(-20, 20)]

    def test_output_fits_in_required_length(self):
        verb_print_info()
        subtest_count = 0

        for preset_idx, (expected_max_len, preset) in enumerate(self.req_len_dataset):
            verb_print_header(f'expected_max_len={expected_max_len}: ')
            self.assertEqual(expected_max_len,
                             preset.max_len,
                             f'Expected max len {expected_max_len} doesn\'t correspond to preset property ({preset.max_len})'
                             )

            for input_idx, input_num in enumerate(self.req_len_input_num_list):
                subtest_msg = f'prefixed/len P{preset_idx} #{input_idx} "{input_num:.2e}" -> (len {expected_max_len})'

                with self.subTest(msg=subtest_msg):
                    actual_output = format_prefixed_unit(input_num, preset)
                    verb_print_info(subtest_msg + f' => (len {len(actual_output)}) "{actual_output}"')
                    subtest_count += 1
                    self.assertGreaterEqual(expected_max_len,
                                            len(actual_output),
                                            f'Actual output ("{actual_output}") exceeds maximum')
        verb_print_subtests(subtest_count)
