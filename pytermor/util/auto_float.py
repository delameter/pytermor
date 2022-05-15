# -----------------------------------------------------------------------------
# pytermor [ANSI formatted terminal output toolset]
# (C) 2022 A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
from math import trunc


def fmt_auto_float(value: float, max_len: int, output_int: bool) -> str:
    """
    Dynamically adjust decimal digits amount to fill up output string
    with significant digits as much as possible.

    Examples:
      - auto_float(1234.56, 4, False)   ->   1235
      - auto_float(123.56, 4, False)   ->    124
      - auto_float(12.56, 4, False)   ->   12.6
      - auto_float(1.56, 4, False)   ->   1.56
      - auto_float(1234.56, 4, True)  ->   1235
      - auto_float(12.56, 4, True)  ->   13

    :param value: value to format
    :param max_len: maximum output string length (total)
    :param output_int: omit decimal point and everything to the right of it
    :return: formatted value
    """
    if not output_int:
        max_decimals_len = 2
        integer_len = len(str(trunc(value)))
        decimals_and_point_len = min(max_decimals_len + 1, max_len - integer_len)

        decimals_len = 0
        if decimals_and_point_len >= 2:  # dot without decimals makes no sense
            decimals_len = decimals_and_point_len - 1
        dot_str = f'.{decimals_len!s}'
    else:
        dot_str = '.0'

    return f'{value:{max_len}{dot_str}f}'
