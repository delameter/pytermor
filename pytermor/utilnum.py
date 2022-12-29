# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022. A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
"""

.. testsetup:: *

    from pytermor.utilnum import *

"""
from __future__ import annotations

from dataclasses import dataclass
from math import floor, log10, trunc, log, isclose, ceil
from typing import List, Dict, Tuple

from .common import LogicError
from .utilstr import rjust_sgr

_OVERFLOW_CHAR = "!"


def format_thousand_sep(value: int | float, separator: str = " ") -> str:
    """
    Returns input ``value`` with integer part split into groups of three digits,
    joined then with ``separator`` string.

    >>> format_thousand_sep(260341)
    '260 341'
    >>> format_thousand_sep(-9123123123.55, ',')
    '-9,123,123,123.55'

    :param value:
    :param separator:
    """
    return f"{value:_}".replace("_", separator)


# -----------------------------------------------------------------------------


def format_auto_float(
    value: float, req_len: int, allow_exponent_notation: bool = True
) -> str:
    """
    Dynamically adjust decimal digit amount and format
    to fill up the output string with as many significant
    digits as possible, and keep the output length
    strictly equal to `req_len`  at the same time.

    For values impossible to fit into a string of required length and rounding doesn't
    help (e.g. 12 500 000 and 5 chars) algorithm switches to scientific notation
    and the result looks like '1.2e7', unless this feature is explicitly disabled
    with ``allow_exponent_notation`` = False. Then there are two options:

        1) if absolute value is less than 1, zeros will be displayed ('0.0000');
        2) in case of big numbers (like 10\ :sup:`9`) *ValueError* will be
           raised instead.

    >>> format_auto_float(0.012345678, 5)
    '0.012'
    >>> format_auto_float(0.123456789, 5)
    '0.123'
    >>> format_auto_float(1.234567891, 5)
    '1.235'
    >>> format_auto_float(12.34567891, 5)
    '12.35'
    >>> format_auto_float(123.4567891, 5)
    '123.5'
    >>> format_auto_float(1234.567891, 5)
    ' 1235'
    >>> format_auto_float(12345.67891, 5)
    '12346'

    :param value:   Value to format
    :param req_len: Required output string length
    :param allow_exponent_notation:
                    Enable/disable the possibility to use an exponent form, when
                    there is no other way of fitting the value into string of
                    requested length.
    :raises ValueError:
                    If value is too big to fit into ``req_len`` digits and
                    ``allow_exponent_notation`` is set to False.
    """
    if req_len < -1:
        raise ValueError(f"Required length should be >= 0 (got {req_len})")

    sign = ""
    if value < 0:
        sign = "-"
        req_len -= 1

    if req_len == 0:
        return _OVERFLOW_CHAR * (len(sign))

    abs_value = abs(value)
    if abs_value < 1 and req_len == 1:
        # '0' is better than '-'
        return f"{sign}0"

    if value == 0.0:
        return f"{sign}{0:{req_len}.0f}"

    exponent = floor(log10(abs_value))
    exp_threshold_left = -2
    exp_threshold_right = req_len - 1

    # exponential mode threshold depends
    # on req length on the right, and is
    # fixed to -2 on the left:

    #   req |    3     4     5     6 |
    #  thld | -2,2  -2,3  -2,4  -2,5 |

    # it determines exponent values to
    # enable exponent notation for:

    #  value exp req thld cnd result |
    # ------ --- --- ---- --- ------ |
    # 0.0001  -4   4 -2,3   t   1e-4 |
    #  0.001  -3   4 -2,3   f   1e-3 | - less than threshold
    #   0.01  -2   4 -2,3   f   0.01 | ---- N -
    #    0.1  -1   4 -2,3   f   0.10 |      O M
    #      1   0   4 -2,3   f   1.00 |      R O
    #     10   1   4 -2,3   f   10.0 |      M D
    #    100   2   4 -2,3   f  100.0 |      A E
    #   1000   3   4 -2,3   f   1000 | ---- L -
    #  10000   4   4 -2,3   t    1e4 | - greater than threshold

    if not allow_exponent_notation:
        # if exponent mode is disabled, we will try as best
        # as we can to display at least something significant;
        # this can work for some of the values around the zero
        # (and result in like '0.00001'), but not for very big ones.
        exp_threshold_left = None

    required_exponent = (
        exp_threshold_left is not None and exponent < exp_threshold_left
    ) or exponent > exp_threshold_right

    if required_exponent:
        if not allow_exponent_notation:  # oh well...
            raise ValueError(
                f"Failed to fit {value:.2f} into {req_len} chars without scientific notation"
            )

        exponent_len = len(str(exponent)) + 1  # 'e'
        if req_len < exponent_len:
            # there is no place even for exponent
            return _OVERFLOW_CHAR * (len(sign) + req_len)

        significand = abs_value / pow(10, exponent)
        max_significand_len = req_len - exponent_len
        try:
            # max_significand_len can be 0, in that case significand_str will be empty; that
            # means we cannot fit it the significand, but still can display approximate number power
            # using the 'eN'/'-eN' notation
            significand_str = format_auto_float(
                significand, max_significand_len, allow_exponent_notation=False
            )

        except ValueError:
            return f"{sign}e{exponent}".rjust(req_len)

        return f"{sign}{significand_str}e{exponent}"

    integer_len = max(1, exponent + 1)
    if integer_len == req_len:
        # special case when rounding
        # can change the result length
        integer_str = f"{abs_value:{req_len}.0f}"

        if len(integer_str) > integer_len:
            # e.g. req_len = 1, abs_value = 9.9
            #      => should be displayed as 9, not 10
            integer_str = f"{trunc(abs_value):{req_len}d}"

        return f"{sign}{integer_str}"

    decimals_with_point_len = req_len - integer_len
    decimals_len = decimals_with_point_len - 1

    # dot without decimals makes no sense, but
    # python's standard library handles
    # this by itself: f'{12.3:.0f}' => '12'
    dot_str = f".{decimals_len!s}"

    return f"{sign}{abs_value:{req_len}{dot_str}f}"


# -----------------------------------------------------------------------------


class PrefixedUnitFormatter:
    """
    Formats ``value`` using settings passed to constructor. The main idea of this class
    is to fit into specified string length as much significant digits as it's
    theoretically possible by using multipliers and unit prefixes to
    indicate them.

    You can create your own formatters if you need fine tuning of the
    output and customization. If that's not the case, there are facade
    methods :meth:`format_si_metric()` and :meth:`format_si_binary()`,
    which will invoke predefined formatters and doesn't require setting up.

    ``max_value_len`` must be at least **3**, because it's a
    minimum requirement for formatting values from 0 to 999.
    Next number to 999 is 1000, which will be formatted as "1k".

    Setting ``allow_negative`` to *True* increases lower bound of ``max_value_len``
    to **4** because the values now can be less than 0, and minus sign also occupies
    one char of the output.

    Setting ``mcoef`` to anything other than 1000.0 also increases the minimum
    of ``max_value_len`` argument by 1, to **5**. The reason is that non-decimal
    coefficients like 1024 require additional char to render as switching
    to the next prefix happens later: 999 b, 1000 b, 1001 b ... 1023 b, 1 Kb.

    All arguments except ``parent`` are *kwonly*\ -type arguments.

    :param parent:
    :param max_value_len:  Target string length. As mentioned above, must be at
                           least 3-5, depending on other options.
    :param allow_negative:
    :param truncate_frac:
    :param unit:
    :param unit_separator:
    :param mcoef:
    :param legacy_rounding:
    :param pad:
    :param prefixes:
    """

    # fmt: off
    PREFIXES_SI = [
        'y', 'z', 'a', 'f', 'p', 'n', 'μ', 'm',
        None,
        'k', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y',
    ]
    """
    Prefix presets used by default module formatters. Can be
    useful if you are building your own formatter.
    """
    # fmt: on

    _attribute_defaults = {
        "_max_value_len": 5,
        "_truncate_frac": False,
        "_allow_negative": False,
        "_unit": "",
        "_unit_separator": "",
        "_mcoef": 1000,
        "_legacy_rounding": False,
        "_pad": False,
        "_prefixes": PREFIXES_SI,
        "_prefix_refpoint_shift": 0,
    }

    def __init__(
        self,
        parent: PrefixedUnitFormatter = None,
        *,
        max_value_len: int = None,
        truncate_frac: bool = None,
        allow_negative: bool = None,
        unit: str = None,
        unit_separator: str = None,
        mcoef: float = None,
        legacy_rounding: bool = None,
        pad: bool = None,
        prefixes: List[str | None] = None,
        prefix_refpoint_shift: int = None,
    ):
        self._max_value_len: int = max_value_len
        self._truncate_frac: bool = truncate_frac
        self._allow_negative: bool = allow_negative
        self._unit: str = unit
        self._unit_separator: str = unit_separator
        self._mcoef: float = mcoef
        self._legacy_rounding: bool = legacy_rounding
        self._pad: bool = pad
        self._prefixes: List[str | None] = prefixes
        self._prefix_refpoint_shift: int = prefix_refpoint_shift

        for attr_name, default in self._attribute_defaults.items():
            if getattr(self, attr_name) is None:
                if (parent_attr := getattr(parent, attr_name, None)) is not None:
                    setattr(self, attr_name, parent_attr)
                    continue
                setattr(self, attr_name, default)

        if self._max_value_len < self.max_len_lower_bound:
            raise ValueError(
                f"Impossible to display all decimal numbers as "
                f"{self._max_value_len}-char length."
            )

        try:
            self._prefix_refpoint_idx: int = self._prefixes.index(None)
        except ValueError:
            raise ValueError(
                "At least one of the prefixes should be None, as it indicates "
                "the reference point with multiplying coefficient is 1.00."
            )
        self._prefix_refpoint_idx += self._prefix_refpoint_shift
        if not (0 <= self._prefix_refpoint_idx < len(self._prefixes)):
            raise ValueError("Shifted prefix reference point is out of bounds")

    @property
    def max_len(self) -> int:
        """
        :return: Maximum length of the result. Note that constructor argument
                 is `max_value_len`, which is a different parameter.
        """
        result = self._max_value_len
        result += len(self._unit_separator)
        result += len(self._unit)
        result += max([len(p) for p in self._prefixes if p])
        return result

    @property
    def max_len_lower_bound(self) -> int:
        result = 3
        if self._allow_negative:
            result += 1
        if not self.is_decimal:
            result += 1
        return result

    @property
    def is_decimal(self) -> bool:
        return self._mcoef == 1000.0

    def format(
        self, value: float, unit: str = None, join: bool = True
    ) -> str | Tuple[str, str, str]:
        """
        :param value:  Input value.
        :param unit:   Unit override.
        :param join:   Return the result as a string if set to *True*,
                       or as a (num, sep, unit) tuple otherwise.
        """
        is_decimal = self._mcoef == 1000.0
        min_value_len = (
            3 + (1 if self._allow_negative else 0) + (1 if not is_decimal else 0)
        )
        if self._max_value_len < min_value_len:
            raise ValueError(
                f"Impossible to display all decimal numbers as {self._max_value_len}-char length."
            )

        if not self._allow_negative:
            value = max(0.0, value)
        if self._truncate_frac:
            value = trunc(value)
        if unit is None:
            unit = self._unit

        abs_value = abs(value)
        power_base = self._mcoef ** (1 / 3)  # =10 for metric, ~10.079 for binary
        if abs_value == 0.0:
            prefix_shift = 0
        else:
            exponent = floor(round(log(abs_value, power_base), 3))
            exp_shift = 0 if self._legacy_rounding else -1  # "0.18s" --> "180ms"
            prefix_shift = round((exponent + exp_shift) / 3)

        value /= power_base ** (prefix_shift * 3)
        unit_idx = self._prefix_refpoint_idx + prefix_shift
        if 0 <= unit_idx < len(self._prefixes):
            unit_full = (self._prefixes[unit_idx] or "") + unit
        else:
            unit_full = ("?" * max([len(p) for p in self._prefixes if p])) + unit

        unit_separator = self._unit_separator
        if not unit_full or unit_full.isspace():
            unit_separator = ""

        if self._truncate_frac:
            num_str = f"{trunc(value)!s:.{self._max_value_len}s}"
        else:
            # drop excessive digits first, or get weird results for values near float
            # precision limit for 64-bit systems, e.g. for 10 - e-15 (=9.999999999999998)
            eff_value = round(value, self._max_value_len - 2)
            num_str = format_auto_float(eff_value, self._max_value_len, False)

        result_num, result_sep, result_unit = (
            num_str.strip(),
            unit_separator,
            unit_full.strip(),
        )
        result_joined = "".join((result_num, result_sep, result_unit))
        pad = ""

        if self._pad:
            pad_len = max(0, self.max_len - len(result_joined))
            pad = "".ljust(pad_len)

        if join:
            return pad + result_joined
        return pad + result_num, result_sep, result_unit

    def __repr__(self) -> str:
        return self.__class__.__qualname__


formatter_si_metric = PrefixedUnitFormatter(
    max_value_len=4, allow_negative=True, unit_separator=" ", unit="m"
)
"""
Format ``value`` as meters with SI-prefixes. Base is 1000. 
Unit can be changed at `format()` invocation. Suitable for formatting 
any SI unit with values from approximately 10^-27 to 10^27.

:usage:

    .. code-block :: 
        
        # either of: 
        formatter_si_metric.format(<value>, ...)
        format_si_metric(<value>, ...)
    
:max len: 
  
    Total maximum length is ``max_value_len + 3``, which is **7**
    (+3 is from separator, unit and prefix, assuming all of them
    have 1-char width).

:see: `format_si_metric()`

"""

formatter_si_binary = PrefixedUnitFormatter(
    max_value_len=4,
    truncate_frac=True,
    allow_negative=False,
    unit="b",
    unit_separator=" ",
    mcoef=1024.0,
)
"""
Format ``value`` as binary size (bytes, kbytes, Mbytes) with base 
= 1024. Unit can be customized.

While being similar to `formatter_si_metric`, this formatter 
differs in one aspect.  Given a variable with default value = 995,
formatting it's value results in "995 b". After increasing it
by 20 we'll have 1015, but it's still not enough to become
a kilobyte -- so returned value will be "1015 b". Only after one
more increase (at 1024 and more) the value will be in a form
of "1.00 kb".

:usage:

    .. code-block :: 
        
        # either of: 
        formatter_si_binary.format(<value>, ...)
        format_si_binary(<value>, ...)
    
:max len: 
  
    So, in this case ``max_value_len`` must be at least 5 (not 4),
    because it's a minimum requirement for formatting values from 1023
    to -1023.
    
    The negative values for this formatter are disabled by default and thus 
    will be rounded as 0, which decreases the ``max_value_len`` minimum value 
    by 1 (to 4).
    
    Total maximum length is ``max_value_len + 3`` = 7 (+3 is from separator,
    unit and prefix, assuming all of them have 1-char width).

:see: `format_si_binary()`

"""


def format_si_metric(
    value: float, unit: str = None, join: bool = True
) -> str | Tuple[str, str, str]:
    """
    Wrapper for `formatter_si_metric.format()<formatter_si_metric>`.

    >>> format_si_metric(1010, 'm²')
    '1.01 km²'
    >>> format_si_metric(0.0319, 'g')
    '31.9 mg'
    >>> format_si_metric(1213531546, 'W')  # great scott
    '1.21 GW'
    >>> format_si_metric(1.26e-9, 'eV')
    '1.26 neV'

    :param value: Input value (unitless).
    :param unit:  Value unit, printed right after the prefix.
    :param join:  Return the result as a string if set to *True*,
                  or as a (num, sep, unit) tuple otherwise.
    """
    return formatter_si_metric.format(value, unit, join)


def format_si_binary(
    value: float, unit: str = None, join: bool = True
) -> str | Tuple[str, str, str]:
    """
    Wrapper for `formatter_si_binary.format()<formatter_si_binary>`.

    >>> format_si_binary(1010)  # 1010 b < 1 kb
    '1010 b'
    >>> format_si_binary(1080)
    '1 kb'
    >>> format_si_binary(45200)
    '44 kb'
    >>> format_si_binary(1.258 * pow(10, 6), 'bps')
    '1 Mbps'

    :param value: Input value in bytes.
    :param unit:  Value unit, printed right after the prefix.
    :param join:  Return the result as a string if set to *True*,
                      or as a (num, sep, unit) tuple otherwise.
    """
    return formatter_si_binary.format(value, unit, join)


# -----------------------------------------------------------------------------


def format_time_delta(seconds: float, max_len: int = None) -> str:
    """
    Format time delta using suitable format (which depends on
    ``max_len`` argument). Key feature of this formatter is
    ability to combine two units and display them simultaneously,
    e.g. return "3h 48min" instead of "228 mins" or "3 hours",

    There are predefined formatters with output length of 3, 4,
    6 and 10 characters. Therefore, you can pass in any value
    from 3 inclusive and it's guarenteed that result's length
    will be less or equal to required length. If `max_len` is
    omitted, longest registred formatter will be used.

    >>> format_time_delta(10, 3)
    '10s'
    >>> format_time_delta(10, 6)
    '10.0s'
    >>> format_time_delta(15350, 4)
    '4 h'
    >>> format_time_delta(15350)
    '4h 15min'

    :param seconds: Value to format
    :param max_len: Maximum output string length (total)
    """
    if max_len is None:
        formatter = tdf_registry.get_longest()
    else:
        formatter = tdf_registry.find_matching(max_len)

    if formatter is None:
        raise ValueError(f"No settings defined for max length = {max_len} (or less)")

    return formatter.format(seconds)


class TimeDeltaFormatter:
    """
    Formatter for time intervals. Key feature of this formatter is
    ability to combine two units and display them simultaneously,
    e.g. return "3h 48min" instead of "228 mins" or "3 hours", etc.

    You can create your own formatters if you need fine tuning of the
    output and customization. If that's not the case, there is a
    facade method :meth:`format_time_delta()` which will select appropriate
    formatter automatically.

    Example output::

        "10 secs", "5 mins", "4h 15min", "5d 22h"

    :param units:
    :param allow_negative:
    :param allow_subsecond:
    :param unit_separator:
    :param plural_suffix:
    :param overflow_msg:
    """

    def __init__(
        self,
        units: List[TimeUnit],
        allow_negative: bool = False,
        allow_subsecond: bool = True,
        unit_separator: str = None,
        plural_suffix: str = None,
        overflow_msg: str = "OVERFLOW",
    ):
        self._units = units
        self._allow_negative = allow_negative
        self._allow_subsecond = allow_subsecond
        self._unit_separator = unit_separator
        self._plural_suffix = plural_suffix
        self._overflow_msg = overflow_msg

        self._subsecond_formatter = PrefixedUnitFormatter(
            max_value_len=4, allow_negative=True, unit="s", unit_separator="", pad=False
        )
        self._max_len = None
        self._compute_max_len()

    @property
    def max_len(self) -> int:
        """
        This property cannot be set manually, it is
        computed on initialization automatically.

        :return: Maximum possible output string length.
        """
        return self._max_len

    def format(self, seconds: float, pad: bool = False) -> str:
        """
        Pretty-print difference between two moments in time. If input
        value is too big for the current formatter to handle, return "OVERFLOW"
        string (or a part of it, depending on ``max_len``).

        :param seconds: Input value.
        :param pad:  Set to *True* to pad the value with spaces on the left side
                     and ensure it's length is equal to `max_len`, or to *False*
                     to allow shorter result strings.
        """
        result = self.format_raw(seconds)
        if result is None:
            result = self._overflow_msg[: self.max_len]

        if pad:
            result = rjust_sgr(result, self._max_len)

        return result

    def format_raw(self, seconds: float) -> str | None:
        """
        Pretty-print difference between two moments in time. If input
        value is too big for the current formatter to handle, return *None*.

        :param seconds: Input value.
        """
        num = abs(seconds)
        unit_idx = 0
        prev_frac = ""

        negative = self._allow_negative and seconds < 0
        sign = "-" if negative else ""
        result = None

        if self._allow_subsecond and num < 60:
            if self._max_len is not None:
                if (
                    len(result := self._subsecond_formatter.format(seconds))
                    > self._max_len
                ):
                    # for example, 500ms doesn't fit in the shortest possible
                    # delta string (which is 3 chars), so "<1s" will be returned
                    result = None

        while result is None and unit_idx < len(self._units):
            unit = self._units[unit_idx]
            if unit.overflow_afer and num > unit.overflow_afer:
                if not self._max_len:  # max len is being computed now
                    raise RecursionError()
                return None

            unit_name = unit.name
            unit_name_suffixed = unit_name
            if self._plural_suffix and trunc(num) != 1:
                unit_name_suffixed += self._plural_suffix

            short_unit_name = unit_name[0]
            if unit.custom_short:
                short_unit_name = unit.custom_short

            next_unit_ratio = unit.in_next
            unit_separator = self._unit_separator or ""

            if abs(num) < 1:
                if negative:
                    result = f"~0{unit_separator}{unit_name_suffixed:s}"
                elif isclose(num, 0, abs_tol=1e-03):
                    result = f"0{unit_separator}{unit_name_suffixed:s}"
                else:
                    result = f"<1{unit_separator}{unit_name:s}"

            elif unit.collapsible_after is not None and num < unit.collapsible_after:
                result = f"{sign}{floor(num):d}{short_unit_name:s}{unit_separator}{prev_frac:<s}"

            elif not next_unit_ratio or num < next_unit_ratio:
                result = f"{sign}{floor(num):d}{unit_separator}{unit_name_suffixed:s}"

            else:
                next_num = floor(num / next_unit_ratio)
                prev_frac = "{:d}{:s}".format(
                    floor(num - (next_num * next_unit_ratio)), short_unit_name
                )
                num = next_num
                unit_idx += 1
                continue

        return result or ""

    def _compute_max_len(self):
        max_len = 0
        coef = 1.00

        for unit in self._units:
            test_val = unit.in_next
            if not test_val:
                test_val = unit.overflow_afer
            if not test_val:
                continue
            test_val_seconds = (
                coef * (test_val - 1) * (-1 if self._allow_negative else 1)
            )

            try:
                max_len_unit = self.format_raw(test_val_seconds)
            except RecursionError:
                continue

            max_len = max(max_len, len(max_len_unit))
            coef *= unit.in_next or unit.overflow_afer

        self._max_len = max_len


@dataclass(frozen=True)
class TimeUnit:
    name: str
    in_next: int = None  # how many current units equal to the (one) next unit
    custom_short: str = None
    collapsible_after: int = None  # min threshold for double-delta to become regular
    overflow_afer: int = None  # max threshold


class _TimeDeltaFormatterRegistry:
    """
    Simple tdf_registry for storing formatters and selecting
    the suitable one by max output length.
    """

    def __init__(self):
        self._formatters: Dict[int, TimeDeltaFormatter] = dict()

    def register(self, *formatters: TimeDeltaFormatter):
        for formatter in formatters:
            self._formatters[formatter.max_len] = formatter

    def find_matching(self, max_len: int) -> TimeDeltaFormatter | None:
        exact_match = self.get_by_max_len(max_len)
        if exact_match is not None:
            return exact_match

        suitable_max_len_list = sorted(
            [key for key in self._formatters.keys() if key <= max_len],
            key=lambda k: k,
            reverse=True,
        )
        if len(suitable_max_len_list) == 0:
            return None
        return self.get_by_max_len(suitable_max_len_list[0])

    def get_by_max_len(self, max_len: int) -> TimeDeltaFormatter | None:
        return self._formatters.get(max_len, None)

    def get_shortest(self) -> _TimeDeltaFormatterRegistry | None:
        return self._formatters.get(min(self._formatters.keys() or [None]))

    def get_longest(self) -> _TimeDeltaFormatterRegistry | None:
        return self._formatters.get(max(self._formatters.keys() or [None]))


tdf_registry = _TimeDeltaFormatterRegistry()


tdf_registry.register(
    TimeDeltaFormatter(
        [
            TimeUnit("s", 60),
            TimeUnit("m", 60),
            TimeUnit("h", 24),
            TimeUnit("d", overflow_afer=99),
        ],
        allow_negative=False,
        allow_subsecond=True,
        unit_separator=None,
        plural_suffix=None,
        overflow_msg="ERR",
    ),
    TimeDeltaFormatter(
        [
            TimeUnit("s", 60),
            TimeUnit("m", 60),
            TimeUnit("h", 24),
            TimeUnit("d", 30),
            TimeUnit("M", 12),
            TimeUnit("y", overflow_afer=99),
        ],
        allow_negative=False,
        allow_subsecond=True,
        unit_separator=" ",
        plural_suffix=None,
        overflow_msg="ERRO",
    ),
    TimeDeltaFormatter(
        [
            TimeUnit("sec", 60),
            TimeUnit("min", 60),
            TimeUnit("hr", 24, collapsible_after=10),
            TimeUnit("day", 30, collapsible_after=10),
            TimeUnit("mon", 12),
            TimeUnit("yr", overflow_afer=99),
        ],
        allow_negative=False,
        allow_subsecond=True,
        unit_separator=" ",
        plural_suffix=None,
    ),
    TimeDeltaFormatter(
        [
            TimeUnit("sec", 60),
            TimeUnit("min", 60, custom_short="min"),
            TimeUnit("hour", 24, collapsible_after=24),
            TimeUnit("day", 30, collapsible_after=10),
            TimeUnit("month", 12),
            TimeUnit("year", overflow_afer=999),
        ],
        allow_negative=True,
        allow_subsecond=True,
        unit_separator=" ",
        plural_suffix="s",
    ),
)
