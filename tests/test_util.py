# -----------------------------------------------------------------------------
# pytermor [ANSI formatted terminal output toolset]
# (C) 2022 A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
import sys
import unittest
from datetime import timedelta

from pytermor import fmt, fmt_time_delta, fmt_prefixed_unit, fmt_auto_float, PrefixedUnitPreset, \
    FMT_PRESET_SI_METRIC, FMT_PRESET_SI_BINARY


def is_verbose_mode() -> bool:
    return any([opt in sys.argv for opt in ['-v', '--verbose']])


def print_verbose(value='', **argv):
    if not is_verbose_mode():
        return
    print(fmt.cyan(value or ""), flush=True, **argv)


class TestStringFilter(unittest.TestCase):
    pass  # @TODO


class TestFormatAwareAlignment(unittest.TestCase):
    pass  # @TODO


class TestPrefixedUnit(unittest.TestCase):
    expected_format_dataset = [
        ['-142 Tb', -156530231500223],
        ['-13.5 Gb', -14530231500],
        ['-2.33 Gb', -2501234567],
        ['-668 Mb', -700500000],
        ['-41.1 Mb', -43106100],
        ['-1.20 Mb', -1257800],
        ['-130 kb', -133300],
        ['-44.1 kb', -45200],
        ['-14.6 kb', -15000],
        ['-6.08 kb', -6230],
        ['-1.05 kb', -1080],
        ['-1.00 kb', -1024],
        ['-1010 b', -1010],
        ['-631 b', -631],
        ['-180 b', -180],
        ['-43 b', -43],
        ['-10 b', -10],
        ['-1 b', -1],
        ['0 b', 0],
        ['1 b', 1],
        ['10 b', 10],
        ['43 b', 43],
        ['180 b', 180],
        ['631 b', 631],
        ['1010 b', 1010],
        ['1.00 kb', 1024],
        ['1.05 kb', 1080],
        ['6.08 kb', 6230],
        ['14.65 kb', 15000],
        ['44.14 kb', 45200],
        ['130.2 kb', 133300],
        ['1.20 Mb', 1257800],
        ['41.11 Mb', 43106100],
        ['668.0 Mb', 700500000],
        ['2.33 Gb', 2501234567],
        ['13.53 Gb', 14530231500],
        ['142.4 Tb', 156530231500223],
    ]

    def test_output_has_expected_format(self):
        for idx, (expected_output, input_num) in enumerate(self.expected_format_dataset):
            with self.subTest(msg=f'Testing #{idx} {input_num} -> "{expected_output}"'):
                actual_output = fmt_prefixed_unit(input_num)
                print_verbose(actual_output, end=', ')
                self.assertEqual(expected_output, actual_output)

    req_len_dataset = [
        [8, FMT_PRESET_SI_METRIC],
        [8, FMT_PRESET_SI_BINARY],
        [5, PrefixedUnitPreset(
            max_value_len=3, integer_input=True, mcoef=1000.0,
            prefixes=FMT_PRESET_SI_METRIC.prefixes,
            prefix_zero_idx=FMT_PRESET_SI_METRIC.prefix_zero_idx,
            unit=None, unit_separator=None,
        )],
        [6, PrefixedUnitPreset(
            max_value_len=4, integer_input=True, mcoef=1000.0,
            prefixes=FMT_PRESET_SI_METRIC.prefixes,
            prefix_zero_idx=FMT_PRESET_SI_METRIC.prefix_zero_idx,
            unit=None, unit_separator=None,
        )],
    ]
    req_len_input_num_list = [.076 * pow(11, x) * (-1 * (x % 2)) for x in range(-20, 20)]

    def test_output_fits_in_required_length(self):
        for preset_idx, (expected_max_len, preset) in enumerate(self.req_len_dataset):
            print_verbose(f'\nLEN={expected_max_len:d}', end=': ')
            for input_idx, input_num in enumerate(self.req_len_input_num_list):
                with self.subTest(msg=f'Testing P{preset_idx} #{input_idx} "{input_num}" -> max length {expected_max_len}'):
                    actual_output = fmt_prefixed_unit(input_num, preset)
                    print_verbose(actual_output, end=', ')
                    self.assertGreaterEqual(expected_max_len,
                                            len(actual_output),
                                            f'Actual output ("{actual_output}") exceeds maximum')


class TestTimeDelta(unittest.TestCase):
    expected_format_max_len = 10
    expected_format_dataset = [
        ['OVERFLOW', timedelta(days=-700000)],
        ['-2 years', timedelta(days=-1000)],
        ['-10 months', timedelta(days=-300)],
        ['-3 months', timedelta(days=-100)],
        ['-9d 23h', timedelta(days=-9, hours=-23)],
        ['-5d 0h', timedelta(days=-5)],
        ['-13h 30min', timedelta(days=-1, hours=10, minutes=30)],
        ['-45 mins', timedelta(hours=-1, minutes=15)],
        ['-5 mins', timedelta(minutes=-5)],
        ['-2 secs', timedelta(seconds=-2.01)],
        ['-2 secs', timedelta(seconds=-2)],
        ['-1 sec', timedelta(seconds=-2, microseconds=1)],
        ['-1 sec', timedelta(seconds=-1.9)],
        ['-1 sec', timedelta(seconds=-1.1)],
        ['-1 sec', timedelta(seconds=-1.0)],
        ['~0 secs', timedelta(seconds=-0.5)],
        ['~0 secs', timedelta(milliseconds=-50)],
        ['~0 secs', timedelta(microseconds=-100)],
        ['~0 secs', timedelta(microseconds=-1)],
        ['0 secs', timedelta()],
        ['0 secs', timedelta(microseconds=500)],
        ['<1 sec', timedelta(milliseconds=25)],
        ['<1 sec', timedelta(seconds=0.1)],
        ['<1 sec', timedelta(seconds=0.9)],
        ['1 sec', timedelta(seconds=1)],
        ['1 sec', timedelta(seconds=1.0)],
        ['1 sec', timedelta(seconds=1.1)],
        ['1 sec', timedelta(seconds=1.9)],
        ['1 sec', timedelta(seconds=2, microseconds=-1)],
        ['2 secs', timedelta(seconds=2)],
        ['2 secs', timedelta(seconds=2.0)],
        ['2 secs', timedelta(seconds=2.5)],
        ['10 secs', timedelta(seconds=10)],
        ['1 min', timedelta(minutes=1)],
        ['5 mins', timedelta(minutes=5)],
        ['15 mins', timedelta(minutes=15)],
        ['45 mins', timedelta(minutes=45)],
        ['1h 30min', timedelta(hours=1, minutes=30)],
        ['4h 15min', timedelta(hours=4, minutes=15)],
        ['8h 59min', timedelta(hours=8, minutes=59, seconds=59)],
        ['12h 30min', timedelta(hours=12, minutes=30)],
        ['18h 45min', timedelta(hours=18, minutes=45)],
        ['23h 50min', timedelta(hours=23, minutes=50)],
        ['1d 0h', timedelta(days=1)],
        ['3d 4h', timedelta(days=3, hours=4)],
        ['5d 22h', timedelta(days=5, hours=22, minutes=51)],
        ['6d 23h', timedelta(days=7, minutes=-1)],
        ['9d 0h', timedelta(days=9)],
        ['12 days', timedelta(days=12, hours=18)],
        ['16 days', timedelta(days=16, hours=2)],
        ['1 month', timedelta(days=30)],
        ['1 month', timedelta(days=55)],
        ['2 months', timedelta(days=70)],
        ['2 months', timedelta(days=80)],
        ['6 months', timedelta(days=200)],
        ['11 months', timedelta(days=350)],
        ['1 year', timedelta(days=390)],
        ['2 years', timedelta(days=810)],
        ['27 years', timedelta(days=10000)],
        ['277 years', timedelta(days=100000)],
        ['OVERFLOW', timedelta(days=400000)],
    ]

    def test_output_has_expected_format(self):
        for idx, (expected_output, input_arg) in enumerate(self.expected_format_dataset):
            with self.subTest(msg=f'Test #{idx}: "{input_arg}" -> "{expected_output}"'):
                if type(input_arg) is not timedelta:
                    input_arg = timedelta(days=input_arg)

                actual_output = fmt_time_delta(input_arg.total_seconds(), self.expected_format_max_len)
                print_verbose(actual_output, end=', ')
                self.assertEqual(expected_output, actual_output)

    req_len_expected_len_list = [3, 4, 6, 10, 9, 1000]
    req_len_input_delta_list = [el[1] for el in expected_format_dataset]

    def test_output_fits_in_required_length(self):
        for idx, expected_max_len in enumerate(self.req_len_expected_len_list):
            print_verbose(f'\nLEN={expected_max_len:d}', end=': ')
            for input_td in self.req_len_input_delta_list:
                with self.subTest(msg=f'Testing #{idx} "{input_td}" -> max length {expected_max_len}'):
                    actual_output = fmt_time_delta(input_td.total_seconds(), expected_max_len)
                    print_verbose(actual_output, end=', ')
                    self.assertGreaterEqual(expected_max_len, len(actual_output))

    invalid_len_list = [-5, 0, 1, 2]

    def test_invalid_max_length_fails(self):
        for invalid_max_len in self.invalid_len_list:
            with self.subTest(msg=f'Testing invalid max length {invalid_max_len}'):
                self.assertRaises(ValueError, lambda: fmt_time_delta(100, invalid_max_len))


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
                actual_output = fmt_auto_float(*args)
                print_verbose(actual_output, end=', ')
                self.assertEqual(expected_output, actual_output)
