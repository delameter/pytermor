# -----------------------------------------------------------------------------
# pytermor [ANSI formatted terminal output toolset]
# (C) 2022 A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
from math import trunc


def format_auto_float(value: float, max_len: int) -> str:
    """
    Dynamically adjust decimal digit amount to fill the output string
    up with significant digits as much as possible.

    Examples:
      - format_auto_float(1234.56, 4) -> 1235
      - format_auto_float( 123.56, 4) ->  124
      - format_auto_float(  12.56, 4) -> 12.6
      - format_auto_float(   1.56, 4) -> 1.56

    :param value: value to format
    :param max_len: maximum output string length (total)
    :return: formatted value
    """
    max_decimals_len = 2
    integer_len = len(str(trunc(value)))
    decimals_and_point_len = min(max_decimals_len + 1, max_len - integer_len)

    decimals_len = 0
    if decimals_and_point_len >= 2:  # dot without decimals makes no sense
        decimals_len = decimals_and_point_len - 1
    dot_str = f'.{decimals_len!s}'

    return f'{value:{max_len}{dot_str}f}'
