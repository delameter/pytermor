# -----------------------------------------------------------------------------
# pytermor [ANSI formatted terminal output toolset]
# (C) 2022 A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
import unittest
import sys
from datetime import timedelta

from pytermor import fmt, fmt_time_delta, fmt_prefixed_unit, PrefixedUnitFmtPreset, fmt_auto_float


def is_verbose_mode() -> bool:
    return any([opt in sys.argv for opt in ['-v', '--verbose']])


def print_verbose(value='', **argv):
    if not is_verbose_mode():
        return
    print(fmt.cyan(value or ""), flush=True, **argv)


class ReplaceSGRTestCase(unittest.TestCase):
    pass  # @TODO


class ReplaceCSITestCase(unittest.TestCase):
    pass  # @TODO


class ReplaceNonAsciiBytesTestCase(unittest.TestCase):
    pass  # @TODO


class FilterApplicationTestCase(unittest.TestCase):
    pass  # @TODO


class FormatAwareLeftAlignmentTestCase(unittest.TestCase):
    pass  # @TODO


class FormatAwareCenterAlignmentTestCase(unittest.TestCase):
    pass  # @TODO


class FormatTimeDeltaMaxLengthTestCase(unittest.TestCase):
    expected_max_len_list = [3, 4, 6, 10, 9, 1000]
    invalid_max_len_list = [-5, 0, 1, 2]
    input_td_list = [
        timedelta(),
        timedelta(microseconds=500), timedelta(milliseconds=200),
        timedelta(seconds=1), timedelta(seconds=4), timedelta(seconds=10),
        timedelta(seconds=20),  timedelta(seconds=50), timedelta(minutes=1), timedelta(minutes=5),
        timedelta(minutes=15), timedelta(minutes=30), timedelta(minutes=45), timedelta(minutes=59),
        timedelta(hours=1, minutes=30), timedelta(hours=4, minutes=15),
        timedelta(hours=8, minutes=59, seconds=59), timedelta(hours=12, minutes=30),
        timedelta(hours=18, minutes=45), timedelta(hours=23, minutes=50), timedelta(days=1),
        timedelta(days=3, hours=4), timedelta(days=5, hours=22, minutes=51),
        timedelta(days=7, minutes=-1), timedelta(days=9), timedelta(days=12, hours=18),
        timedelta(days=16, hours=2), timedelta(days=30), timedelta(days=55), timedelta(days=80),
        timedelta(days=200), timedelta(days=350), timedelta(days=390), timedelta(days=810),
        timedelta(days=10000), timedelta(days=100000), timedelta(days=400000),
        timedelta(days=90000000),
        timedelta(microseconds=-500),  timedelta(milliseconds=-200), timedelta(seconds=-1), timedelta(seconds=-4),
        timedelta(seconds=-10), timedelta(minutes=-5), timedelta(hours=-1, minutes=15),
        timedelta(days=-1, hours=10, minutes=30), timedelta(days=-5), timedelta(days=-9, hours=-23),
        timedelta(days=-100), timedelta(days=-300), timedelta(days=-1000)
    ]

    def test_output_fits_in_required_length(self):
        for expected_max_len in self.expected_max_len_list:
            print_verbose(f'\nLEN={expected_max_len:d}', end=': ')
            print_verbose(f'\nLEN={expected_max_len:d}', end=': ')
            print_verbose(f'\nLEN={expected_max_len:d}', end=': ')
            print_verbose(f'\nLEN={expected_max_len:d}', end=': ')
            for input_td in self.input_td_list:
                with self.subTest(msg=f'Testing "{input_td}" -> max length {expected_max_len}'):
                    actual_output = fmt_time_delta(input_td.total_seconds(), expected_max_len)
                    print_verbose(actual_output, end=', ')
                    self.assertGreaterEqual(expected_max_len, len(actual_output))

    def test_invalid_max_length_fails(self):
        for invalid_max_len in self.invalid_max_len_list:
            with self.subTest(msg=f'Testing invalid max length {invalid_max_len}'):
                self.assertRaises(ValueError, lambda: fmt_time_delta(100, invalid_max_len))


class FormatTimeDeltaExpectedFormatTestCase(unittest.TestCase):
    data_provider = [
        ['0 sec', timedelta()],
        ['0 sec', timedelta(microseconds=500)],
        ['1 sec', timedelta(seconds=1)],
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
        ['2 months', timedelta(days=80)],
        ['6 months', timedelta(days=200)],
        ['11 months', timedelta(days=350)],
        ['1 year', timedelta(days=390)],
        ['2 years', timedelta(days=810)],
        ['27 years', timedelta(days=10000)],
        ['277 years', timedelta(days=100000)],
        ['OVERFLOW', timedelta(days=400000)],
        ['OVERFLOW', timedelta(days=90000000)],
        ['-0 sec', timedelta(microseconds=-500)],
        ['-5 mins', timedelta(minutes=-5)],
        ['-45 mins', timedelta(hours=-1, minutes=15)],
        ['-13h 30min', timedelta(days=-1, hours=10, minutes=30)],
        ['-5d 0h', timedelta(days=-5)],
        ['-9d 23h', timedelta(days=-9, hours=-23)],
        ['-3 months', timedelta(days=-100)],
        ['-10 months', timedelta(days=-300)],
        ['-2 years', timedelta(days=-1000)],
    ]

    def test_output_has_expected_format(self):
        for expected_output, input_td in self.data_provider:
            with self.subTest(msg=f'Testing "{input_td}" -> "{expected_output}"'):
                actual_output = fmt_time_delta(input_td.total_seconds(), 10)
                print_verbose(actual_output, end=', ')
                self.assertEqual(expected_output, actual_output)


class FormatPrefixedUnitMaxLengthTestCase(unittest.TestCase):
    input_num_list = [1.1*pow(11, x) for x in range(1, 20)]
    data_provider = [
        [6, PrefixedUnitFmtPreset(expand_to_max=True, max_value_len=5, unit_separator=None, unit=None)],
        [7, PrefixedUnitFmtPreset(expand_to_max=True, max_value_len=4, unit_separator=' ', unit='m')],
        [7, PrefixedUnitFmtPreset(max_value_len=4, unit_separator=' ', unit='m')],
        [9, PrefixedUnitFmtPreset(max_value_len=6, prefixes=['1', '2', '3'], unit='U')],
        [8, PrefixedUnitFmtPreset(expand_to_max=True, max_value_len=5, prefixes=['1', '2', '3'])],
        [4, PrefixedUnitFmtPreset(max_value_len=3, unit_separator=None, unit=None, prefixes=['p'])],
        [5, PrefixedUnitFmtPreset(max_value_len=3, unit_separator=None, unit='u', prefixes=['P'])],
        [3, PrefixedUnitFmtPreset(max_value_len=1, mcoef=10, unit_separator=None, unit='g', prefixes=['1', '2', '3', '4', '5'])],
    ]

    def test_output_fits_in_required_length(self):
        for expected_max_len, preset in self.data_provider:
            print_verbose(f'\nLEN={expected_max_len:d}', end=': ')
            for input_num in self.input_num_list:
                with self.subTest(msg=f'Testing "{input_num}" -> max length {expected_max_len}'):
                    actual_output = fmt_prefixed_unit(input_num, preset)
                    print_verbose(actual_output, end=', ')
                    self.assertGreaterEqual(expected_max_len, len(actual_output))


class FormatPrefixedUnitExpectedFormatTestCase(unittest.TestCase):
    data_provider = [
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
        for expected_output, input_num in self.data_provider:
            with self.subTest(msg=f'Testing {input_num} -> "{expected_output}"'):
                actual_output = fmt_prefixed_unit(input_num)
                print_verbose(actual_output, end=', ')
                self.assertEqual(expected_output, actual_output)


class FormatAutoFloatExpectedFormatTestCase(unittest.TestCase):
    data_provider = [
        ['1444', [1444, 4, True]],
        [' 144', [144, 4, True]],
        ['  14', [14, 4, True]],
        ['300.0', [300, 5, False]],
        ['30.00', [30, 5, False]],
        [' 3.00', [3, 5, False]],
        [' 0.30', [.3, 5, False]],
        [' 0.03', [.03, 5, False]],
        [' 0.00', [.003, 5, False]],
        ['-5.00', [-5, 5, False]],
        [' -512', [-512, 5, False]],
        ['  1.20', [1.2, 6, False]],
        ['123456', [123456, 6, False]],
        ['  0.00', [0.00012, 6, False]],
        ['  0.01', [0.012, 6, False]],
        ['0.0', [0, 3, False]],
        ['6.0', [6, 3, False]],
        ['146', [145.66, 3, False]],
    ]

    def test_output_has_expected_format(self):
        for expected_output, args in self.data_provider:
                with self.subTest(msg=f'Testing "{args}" -> max length {expected_output}'):
                    actual_output = fmt_auto_float(*args)
                    print_verbose(actual_output, end=', ')
                    self.assertEqual(expected_output, actual_output)
