# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022. A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
import logging
import unittest
from datetime import timedelta

from pytermor.util import format_time_delta, TimeDeltaFormatter, TimeUnit
from pytermor.util.time_delta import _TimeDeltaFormatterRegistry


class TestTimeDeltaFormatter(unittest.TestCase):
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
            subtest_msg = f'tdelta/match #{idx}: "{input_arg}" -> "{expected_output}"'

            with self.subTest(msg=subtest_msg):
                actual_output = format_time_delta(input_arg.total_seconds(), self.expected_format_max_len)
                logging.debug(subtest_msg + f' => "{actual_output}"')

                self.assertEqual(expected_output, actual_output)

    # ---------------------------------------------------------------------------

    req_len_expected_len_list = [3, 4, 6, 10, 9, 1000]
    req_len_input_delta_list = [el[1] for el in expected_format_dataset]

    def test_output_fits_in_required_length(self):
        for idx, expected_max_len in enumerate(self.req_len_expected_len_list):
            logging.debug(f'expected_max_len={expected_max_len:d}:')

            for input_idx, input_td in enumerate(self.req_len_input_delta_list):
                subtest_msg = f'tdelta/len #{input_idx}: "{input_td}" -> (len {expected_max_len})'

                with self.subTest(msg=subtest_msg):
                    actual_output = format_time_delta(input_td.total_seconds(), expected_max_len)
                    logging.debug(subtest_msg + f' => (len {len(actual_output)}) "{actual_output}"')

                    self.assertGreaterEqual(expected_max_len,
                                            len(actual_output),
                                            f'Actual output ("{actual_output}") exceeds maximum')

    # ---------------------------------------------------------------------------

    invalid_len_list = [-5, 0, 1, 2]

    def test_invalid_max_length_fails(self):
        for invalid_max_len in self.invalid_len_list:
            with self.subTest(msg=f'invalid max length {invalid_max_len}'):
                self.assertRaises(ValueError, lambda: format_time_delta(100, invalid_max_len))


class TestTimeDeltaFormatterRegistry(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._registry = _TimeDeltaFormatterRegistry()

    @classmethod
    def tearDownClass(cls) -> None:
        cls._registry = None

    def test_formatter_registration(self):  # @TODO more
        formatter = TimeDeltaFormatter(
            units=[
                TimeUnit('s', 60),
                TimeUnit('m', 60),
                TimeUnit('h', 24),
            ],
            allow_negative=False,
        )
        self._registry.register(formatter)

        self.assertIn(formatter.max_len, self._registry._formatters)
        self.assertEquals(formatter, self._registry.get_by_max_len(formatter.max_len))
