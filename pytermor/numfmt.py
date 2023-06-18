# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under GNU Lesser General Public License v3.0
# -----------------------------------------------------------------------------
"""
utilnum
"""
from __future__ import annotations

from collections.abc import Iterable

from .log import logger
import math
import re
import typing as t
from abc import abstractmethod
from dataclasses import dataclass
from math import floor, isclose, log, log10, trunc

from .cval import cv
from .exception import ConflictError
from .filter import Align
from .style import Style, Styles, merge_styles
from .text import Fragment, IRenderable, RT, Text

_OVERFLOW_CHAR = "!"

# fmt: off
PREFIXES_SI_DEC = [  #: :meta hide-value:
    'q', 'r', 'y', 'z', 'a', 'f', 'p', 'n', 'µ', 'm',
    None,
    'k', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y', 'R', 'Q',
]
"""
Prefix preset used by `format_si()` and `format_bytes_human()`. Covers values 
from :math:`10^{-30}` to :math:`10^{32}`. Note lower-cased 'k' prefix.
"""
# fmt: on


# noinspection NonAsciiCharacters
class Highlighter:
    """
    S
    """

    def __init__(self, dim_units: bool = True) -> None:
        self._dim_units = dim_units

    # fmt: off
    _PREFIX_UNIT_REGEX = re.compile(
        r"""
        (?: ^ | (?<!\x1b\[)(?<=[]()\s\[-])\b )
        (?P<intp>\d+)
        (?P<frac>[.,]\d+)?
        (?P<sep>\s?)
        (?P<pfx>[kmgtpuμµn%])?
        (?P<unit>
            i?b[/ip]?t?s?|
            v|a|s(?:econd|ec|)s?|
            m(?:inute|in|onth|on|o|)s?|
            h(?:our|r|)s?|
            d(?:ay|)s?|
            w(?:eek|k|)s?|
            y(?:ear|r|)s?|
            hz
        )?
        (?= []\s\b()[] | $ )
        """,
        flags=re.IGNORECASE | re.VERBOSE,
    )                                           # | OOM | (+) GENERICS (-) |(+) TIME (-)|
                                                # |-----|------------------|------------|
    STYLE_DEFAULT = Style(bold=False)           # |     | misc.            | sec.       |
    STYLE_NUL = Style(fg=cv.GRAY, bold=False)   # |   0 | zero             |            |
    STYLE_PRC = Style(fg=cv.MAGENTA)            # |   2 |            perc. |            |
    STYLE_KIL = Style(fg=cv.BLUE)               # |   3 | Kilo-     milli- | min.    ms |
    STYLE_MEG = Style(fg=cv.CYAN)               # |   6 | Mega-     micro- | hour    μs |
    STYLE_GIG = Style(fg=cv.GREEN)              # |   9 | Giga-      nano- | day     ns |
    STYLE_TER = Style(fg=cv.YELLOW)             # |  12 | Tera-      pico- | week    ps |
    STYLE_MON = Style(fg=cv.HI_YELLOW)          # |     |                  | month      |
    STYLE_PET = Style(fg=cv.RED)                # |  15 | Peta-            | year       |

    _PREFIX_MAP = {
        '%': STYLE_PRC,
        'K': STYLE_KIL, 'k': STYLE_KIL, 'm': STYLE_KIL,
        'M': STYLE_MEG,                 'μ': STYLE_MEG, 'µ': STYLE_MEG,
        'G': STYLE_GIG, 'g': STYLE_GIG, 'n': STYLE_GIG,
        'T': STYLE_TER,                 'p': STYLE_TER,
        'P': STYLE_PET,
    }
    _TIME_UNIT_MAP = {
        '%': STYLE_PRC,
        's': STYLE_PRC, 'sec': STYLE_PRC, 'second': STYLE_PRC,
        'm': STYLE_KIL, 'min': STYLE_KIL, 'minute': STYLE_KIL,
        'h': STYLE_MEG,  'hr': STYLE_MEG,   'hour': STYLE_MEG,
        'd': STYLE_GIG,                      'day': STYLE_GIG,
        'w': STYLE_TER,  'wk': STYLE_TER,   'week': STYLE_TER,
        'M': STYLE_MON,  'mo': STYLE_MON,    'mon': STYLE_MON, 'month': STYLE_MON,
        'y': STYLE_PET,  'yr': STYLE_PET,   'year': STYLE_PET,
    }
    _OOM_MAP = {
        0: STYLE_DEFAULT,  3: STYLE_KIL,   6: STYLE_MEG,
        9: STYLE_GIG,     12: STYLE_TER,  15: STYLE_PET,
    }

    _UNITLESS_LENGTH_THRESHOLD = 6
    # fmt: on

    def colorize(self, string: str) -> Text:
        """
        parse and highlight

        :param string:
        :return:
        """
        cursor = 0
        result = Text()
        for m in self._PREFIX_UNIT_REGEX.finditer(string):
            result += string[cursor : m.start()]
            result.append(*self.apply(**m.groupdict("")))
            cursor = m.end()
        result += string[cursor:]
        return result

    def apply(
        self, intp: str, frac: str, sep: str, pfx: str, unit: str
    ) -> t.List[Fragment]:
        """
        highlight already parsed

        :param intp:
        :param frac:
        :param sep:
        :param pfx:
        :param unit:
        :return:
        """
        digits = intp + frac[1:]
        unit_norm = re.sub(r"^\s*(.)+s?\s*$", r"\1", unit)  # @TODO test this

        st = self.STYLE_DEFAULT
        if set(digits) == {"0"}:
            st = self.STYLE_NUL
        elif pfx:
            st = self._PREFIX_MAP.get(pfx, self.STYLE_DEFAULT)
        elif unit_norm:
            st = self._TIME_UNIT_MAP.get(unit_norm, self.STYLE_DEFAULT)
        elif len(digits) > self._UNITLESS_LENGTH_THRESHOLD:
            return [
                *self._multiapply(intp),
                *self._multiapply(frac, reverse=True),
                Fragment(sep),
                # Fragment(pfx),   # both should be empty
                # Fragment(unit),  # in this branch
            ]

        int_st = merge_styles(st, fallbacks=[Style(bold=True)])
        # bold unless style prohibits (STYLE_NUL)
        frac_st = merge_styles(st, fallbacks=[Style(bold=True, dim=True)])
        # dim bold unless style prohibits
        unit_st = pfx_st = merge_styles(st, fallbacks=[Style(dim=self._dim_units)])
        # dim unless style or instance settings prohibit
        return [
            Fragment(intp, int_st),
            Fragment(frac, frac_st),
            Fragment(sep),
            Fragment(pfx, pfx_st),
            Fragment(unit, unit_st),
        ]

    def _multiapply(self, num: str, *, reverse: bool = False) -> Iterable[Fragment]:
        def _get_style(oom: int, fade: int) -> Style:
            base = self._OOM_MAP.get(abs(oom), self.STYLE_DEFAULT)
            if 1 <= fade <= 3:
                return Style(base, bold=True)
            return Style(self.STYLE_DEFAULT, dim=(fade % 6 < 3))

        def _iter(numpart: str, oom=0, maxfade=0) -> Fragment:
            st = _get_style(oom, maxfade - oom)
            if len(numpart) > 3:
                if reverse:
                    yield Fragment(numpart[:3], st)
                    yield from _iter(numpart[3:], oom - 3, maxfade)
                else:
                    yield from _iter(numpart[:-3], oom + 3, maxfade)
                    yield Fragment(numpart[-3:], st)
            else:
                yield Fragment(numpart, st)

        yield from _iter(num, 0, len(num))


class SupportsFallback:
    _DEFAULTS: t.Dict = None

    @classmethod
    def _set_defaults(cls, defaults: SupportsFallback):
        type(defaults)._DEFAULTS = defaults.__dict__

    def _apply_defaults(self, fallback: SupportsFallback = None):
        for attr_name, default in self._DEFAULTS.items():
            if getattr(self, attr_name) is None:
                if (fallback_attr := getattr(fallback, attr_name, None)) is not None:
                    setattr(self, attr_name, fallback_attr)
                    continue
                setattr(self, attr_name, default)


class NumFormatter(SupportsFallback):
    def __init__(self, auto_color: bool, highlighter: t.Type[Highlighter] | Highlighter):
        self._auto_color: bool = auto_color

        if isinstance(highlighter, type):
            highlighter = highlighter()
        self._highlighter: Highlighter = highlighter

    @abstractmethod
    def format(self, val: float, auto_color: bool) -> RT:
        raise NotImplementedError

    def _colorize(self, auto_color: bool, val: str, sep: str, pfx: str, unit: str) -> RT:
        unit_full = (pfx + unit).strip()
        if not unit_full or unit_full.isspace():
            sep = ""

        if not self._get_color_effective(auto_color):
            return "".join((val.strip(), sep, unit_full))

        int_part, point, frac_part = val.strip().partition(".")
        args = dict(intp=int_part, frac=point + frac_part, sep=sep, pfx=pfx, unit=unit)
        result = self._highlighter.apply(**args)
        return Text(*result, align=Align.RIGHT)

    def _get_color_effective(self, auto_color: bool) -> bool:
        if auto_color is not None:
            return auto_color
        return self._auto_color


class StaticFormatter(NumFormatter):
    """
    Format ``value`` using settings passed to constructor. The purpose of this class
    is to fit into specified string length as much significant digits as it's
    theoretically possible by using multipliers and unit prefixes. Designed
    for metric systems with bases 1000 or 1024.

    The key property of this formatter is maximum length -- the output will not
    excess specified amount of characters no matter what (that's what is "static" for).

    You can create your own formatters if you need fine tuning of the
    output and customization. If that's not the case, there are facade
    methods `format_si()`, `format_si_binary()` and `format_bytes_human()`,
    which will invoke predefined formatters and doesn't require setting up.
    """

    def __init__(
        self,
        fallback: StaticFormatter = None,
        *,
        max_value_len: int = None,
        auto_color: bool = None,
        allow_negative: bool = None,
        allow_fractional: bool = None,
        discrete_input: bool = None,
        unit: str = None,
        unit_separator: str = None,
        mcoef: float = None,
        pad: bool = None,
        legacy_rounding: bool = None,
        prefixes: t.List[str | None] = None,
        prefix_refpoint_shift: int = None,
        value_mapping: t.Dict[float, RT] | t.Callable[[float], RT] = None,  # @TODO
        highlighter: t.Type[Highlighter] | Highlighter = None,
    ):
        """
        .. note ::

            All arguments except ``fallback`` are *kwonly*-type arguments.

        .. default-role:: math

        :param fallback:
            For any (constructing) instance attribute without a value (=\\ *None*):
            look up for this attribute in ``fallback`` instance, and if the value is
            specified, take it and save as yours own; if the attribute is undefined in
            ``fallback`` as well, use the default class value for this attribute instead.

        :param int max_value_len:
            [default: 4] Target string length. Must be at least **3**, because it's a
            minimum requirement for formatting values from 0 to 999.
            Next number to 999 is 1000, which will be formatted as "1k".

            Setting ``allow_negative`` to *True* increases lower bound to **4** because
            the values now can be less than 0, and minus sign also occupies one char in
            the output.

            Setting ``mcoef`` to anything other than 1000.0 also increases the minimum
            by 1, to **5**. The reason is that non-decimal coefficients like 1024 require
            additional char to render as switching to the next prefix happens later:
            "999 b", "1000 b", "1001 b", ..."1023 b", "1 Kb".

        :param bool auto_color:
            [default: *False*] Enable automatic colorizing of the result. Color depends
            on order of magnitude of the value, and always the same, e.g.: blue color for
            numbers in `[1000; 10^6)` and `[10^{-3}; 1)` ranges (prefixes
            nearest to 1, kilo- and milli-); cyan for values in `[10^6; 10^9)` and
            `[10^{-6}; 10^{-3})` ranges (next ones, mega-/micro-), etc. The values
            from `[1; 999]` are colored in neutral gray. See :any:`Highlighter`.

        :param bool allow_negative:
            [default: *True*] Allow negative numbers handling, or (if set to *False*)
            ignore the sign and round all of them to 0.0. This option effectively
            increases lower limit of ``max_value_len`` by 1 (when enabled).

        :param bool allow_fractional:
            [default: *True*] Allows the usage of fractional values in the output. If
            set to *False*, the results will be rounded. Does not affect lower
            limit of ``max_value_len``.

        :param bool discrete_input:
            [default: *False*] If set to *True*, truncate the fractional part off the
            input and do not use floating-point format for *base output*, i.e., without
            prefix and multiplying coefficient. Useful when the values are originally
            discrete (e.g., bytes). Note that the same effect could be achieved by
            setting ``allow_fractional`` to *False*, except that it will influence
            prefixed output as well ("1.08 kB" -> "1kB").

        :param str unit:
            [default: empty *str*] Unit to apply prefix to (e.g., "m", 'B").
            Can be empty.

        :param str unit_separator:
            [default: a space] String to place in between the value and the
            (prefixed) unit. Can be empty.

        :param float mcoef:
            [default: 1000.0] Multiplying coefficient applied to the value:

            .. math ::

                V_{out} = V_{in} * b^{(-m/3)},

            where: `V_{in}` is an input value, `V_{out}` is a numeric part
            of the output, `b` is ``mcoef`` (base), and `m` is the order of
            magnitude corresponding to a selected unit prefix. For example, in case
            of default (decimal) formatter and input value equal to 17345989 the selected
            prefix will be "M" with the order of magnitude = 6:

            .. math ::

                V_{out} = 17345989*1000^{(-6/3)} = 17345989*10^{-6} = 17.346 .

        :param bool pad:
            [default: *False*]

        :param bool legacy_rounding:
            [default: *False*]

        :param list[str|None] prefixes:
            [default: :any:`PREFIXES_SI_DEC`] Prefix list from min power to max.
            Reference point (with zero-power multiplier, or 1.0) is determined by
            searching for *None* in the list provided, therefore it's a requirement
            for the argument to have at least one *None* value. Prefix list for a
            formatter without fractional values support could look like this::

                [None, "k", "M", "G", "T"]

            Prefix step is fixed to `log_{10} 1000 = 3`, as specified for
            metric prefixes.

        :param int prefix_refpoint_shift:
            [default: 0] Should be set to a non-zero number if input represents
            already prefixed value; e.g. to correctly format a variable,
            which stores the frequency in MHz, set prefix shift to 2;
            the formatter then will render 2333 as "2.33 GHz" instead of
            incorrect "2.33 kHz".

        :param value_mapping: @TODO
        :param highlighter: ...

        .. default-role:: any
        """
        super().__init__(auto_color, highlighter)

        self._max_value_len: int = max_value_len
        self._allow_negative: bool = allow_negative
        self._allow_fractional: bool = allow_fractional
        self._discrete_input: bool = discrete_input
        self._unit: str = unit
        self._unit_separator: str = unit_separator
        self._mcoef: float = mcoef
        self._pad: bool = pad
        self._legacy_rounding: bool = legacy_rounding
        self._prefixes: t.List[str | None] = prefixes
        self._prefix_refpoint_shift: int = prefix_refpoint_shift
        self._value_mapping: t.Dict[float, RT] | t.Callable[[float], RT] = value_mapping

        if self._DEFAULTS is None:
            return
        self._apply_defaults(fallback)

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
                "the reference point with multiplying coefficient 1.00."
            )
        self._prefix_refpoint_idx += self._prefix_refpoint_shift
        if not (0 <= self._prefix_refpoint_idx < len(self._prefixes)):
            raise ValueError("Shifted prefix reference point is out of bounds")

    def get_max_len(self, unit: str = None) -> int:
        """
        :param unit: Unit override. Set to *None* to use formatter default.
        :return:     Maximum length of the result. Note that constructor argument
                     is `max_value_len`, which is a different parameter.
        """
        result = self._max_value_len
        result += len(self._unit_separator)
        result += len(self._get_unit_effective(unit))
        result += self._get_max_prefix_len()
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

    def format(self, val: float, unit: str = None, auto_color: bool = None) -> RT:
        """
        :param val:   Input value.
        :param unit:  Unit override. Set to *None* to use formatter default.
        :param auto_color:  Color mode, *bool* to enable/disable auto-colorizing,
                            *None* to use formatter default value.
        :return: Formatted value, *Text* if colorizing is on, *str* otherwise.
        """
        origin_val = val
        unit_eff = self._get_unit_effective(unit)
        if not self._allow_negative:
            val = max(0.0, val)
        if self._discrete_input and self._prefix_refpoint_shift == 0:
            val = trunc(val)

        abs_value = abs(val)
        power_base = self._mcoef ** (1 / 3)  # =10 for metric, ~10.079 for binary
        if abs_value == 0.0:
            prefix_shift = 0
        else:
            # order of magnitude:
            oom = floor(round(log(abs_value, power_base), 6))
            # rounding is required because cumulative floating point error can lead to:
            # 1024^9 = 1099511600000.0 -> "1024 GiB" (expected "1.00 TiB")
            #                     1023 -> "1.00 KiB" (expected "1023 B")

            oom_shift = 0 if self._legacy_rounding else -1  # Legacy OFF: "180ms"
            prefix_shift = round((oom + oom_shift) / 3)  # Legacy ON : "0.18s"

        base_output = prefix_shift == 0
        val /= power_base ** (prefix_shift * 3)
        unit_idx = self._prefix_refpoint_idx + prefix_shift
        if 0 <= unit_idx < len(self._prefixes):
            prefix = self._prefixes[unit_idx] or ""
        else:
            prefix = "?" * self._get_max_prefix_len()

        sep = self._unit_separator
        fractional_output = self._allow_fractional and not (
            base_output and self._discrete_input
        )

        # drop excessive digits first, or get excessive zeros for the values near float
        # precision limit for 64-bit systems, e.g. for 10 - e-15 (=9.999999999999998) and
        # max_value_len=3 the result would be "10.0" instead of "10".
        eff_val = round(val, self._max_value_len - 1)

        # @TODO here i started to feel that there should be an easier way to do all the
        #       math (more specifically, to avoid one or two redundant transformations),
        #       but it's impossible to prove or reject it without an investigation. the
        #       reason for this is existence of three (wut?) round operations in a row.
        if fractional_output:
            val_str = format_auto_float(eff_val, self._max_value_len, False)
        else:
            val_str = f"{trunc(eff_val):d}"

        if len(val_str) > self._max_value_len:
            logger.warning(
                "Inconsistent result -- max val length %d exceeded (%d): '%s' <- %f"
                % (self._max_value_len, len(val_str), val_str, origin_val)
            )

        result = self._colorize(auto_color, val_str, sep, prefix, unit_eff)
        if self._pad:
            max_len = self.get_max_len(unit)
            pad_len = max(0, max_len - len(result))
            result = (" " * pad_len) + result
            if isinstance(result, IRenderable):
                result.set_width(max_len)
        return result

    def _get_unit_effective(self, unit: str) -> str:
        if unit is not None:
            return unit
        return self._unit

    def _get_max_prefix_len(self) -> int:
        return max([len(p) for p in self._prefixes if p is not None])

    def __repr__(self) -> str:
        return self.__class__.__qualname__


# noinspection PyProtectedMember
StaticFormatter._set_defaults(
    StaticFormatter(
        max_value_len=4,
        auto_color=False,
        allow_negative=True,
        allow_fractional=True,
        discrete_input=False,
        unit="",
        unit_separator=" ",
        mcoef=1000.0,
        pad=False,
        legacy_rounding=False,
        prefixes=PREFIXES_SI_DEC,
        prefix_refpoint_shift=0,
        value_mapping=dict(),
        highlighter=Highlighter,
    )
)


class DynamicFormatter(NumFormatter):
    """
    A simplified version of static formatter for cases, when length of the result
    string doesn't matter too much (e.g., for log output), and you don't have
    intention to customize the output (too much).
    """

    def __init__(
        self,
        fallback: DynamicFormatter = None,
        units: list[BaseUnit] = None,
        *,
        auto_color: bool = None,
        allow_fractional: bool = None,
        unit_separator: str = None,
        oom_shift: int = None,
        highlighter: t.Type[Highlighter] = None,
    ):
        """
        .. note ::

            All arguments except ``fallback`` and ``units`` are
            *kwonly*-type arguments.

        """
        super().__init__(auto_color, highlighter)

        self._allow_fractional: bool = allow_fractional
        self._unit_separator: str = unit_separator
        self._units: list[BaseUnit] = units
        self._oom_shift: int = oom_shift
        self._base: int = 10

        if self._DEFAULTS is None:
            return
        self._apply_defaults(fallback)

        if len(self._units) < 2:
            raise ValueError("At least two base units are required")

    def format(self, val: float, auto_color: bool = False, oom_shift: int = None) -> RT:
        """
        ,,,
        :param val:
        :param oom_shift:
        :param auto_color:
        :return:
        """
        if self._get_color_effective(auto_color):
            return self._colorize(auto_color, *self._format_raw(val, oom_shift, True))
        return self._format_raw(val, oom_shift, False)

    def _format_raw(
        self, val: float, oom_shift: int = None, as_tuple: bool = False
    ) -> str | t.Tuple[str, ...]:
        eff_oom_shift = self._oom_shift if oom_shift is None else oom_shift
        min_unit = self._units[-1]
        min_val = math.pow(self._base, min_unit.oom)
        if abs(val) > min_val:
            val_oom = math.log(abs(val), self._base) + eff_oom_shift
        else:
            val_oom = min_unit.oom - 1

        val_mp = None
        unit = base_unit = min_unit
        for _unit in self._units:
            if _unit.oom == eff_oom_shift:
                base_unit = _unit
            if val_oom >= _unit.oom:
                coef = math.pow(self._base, _unit.oom - eff_oom_shift)
                val_mp = val / coef
                unit = _unit
                break

        if val_mp is None:
            val_mp = 0
            unit = base_unit

        if unit.integer or not self._allow_fractional:
            val_str = "{:>d}".format(math.trunc(val_mp))
        else:
            val_str = "{:>.1f}".format(val_mp)

        result = (val_str, self._unit_separator, unit.prefix, unit.unit)
        if as_tuple:
            return result
        return "".join(result)


# noinspection PyProtectedMember
DynamicFormatter._set_defaults(
    DynamicFormatter(
        auto_color=False,
        allow_fractional=True,
        unit_separator=" ",
        oom_shift=0,
        highlighter=Highlighter,
    )
)


@dataclass(frozen=True)
class BaseUnit:
    oom: float
    unit: str = ""
    prefix: str = ""
    _integer: bool = None

    @property
    def integer(self) -> bool:
        if self._integer is None:
            return not isinstance(self.oom, int)
        return self._integer


class DualFormatter(NumFormatter):
    """
    Formatter designed for time intervals. Key feature of this formatter is
    ability to combine two units and display them simultaneously,
    e.g. return "3h 48min" instead of "228 mins" or "3 hours", etc.

    It is possible to create custom formatters if fine tuning of the output and
    customization is necessary; otherwise use a facade method `format_time_delta()`,
    which selects appropriate formatter by specified max length from a preset list.

    Example output::

        "10 secs", "5 mins", "4h 15min", "5d 22h"

    :param fallback:
    :param units:
    :param auto_color: If *True*, the result will be colorized depending on unit type.
    :param allow_negative:
    :param allow_fractional:
    :param unit_separator:
    :param pad:   Set to *True* to pad the value with spaces on the left side
                  and ensure it's length is equal to `max_len`, or to *False*
                  to allow shorter result strings.
    :param plural_suffix:
    :param overflow_msg:
    :param highlighter:
    """

    def __init__(
        self,
        fallback: DualFormatter = None,
        units: t.List[DualBaseUnit] = None,
        *,
        auto_color: bool = None,
        allow_negative: bool = None,
        allow_fractional: bool = None,
        unit_separator: str = None,
        pad: bool = None,
        plural_suffix: str = None,
        overflow_msg: str = None,
        highlighter: t.Type[Highlighter] = None,
    ):
        super().__init__(auto_color, highlighter)

        self._units = units
        self._allow_negative = allow_negative
        self._allow_fractional = allow_fractional
        self._unit_separator = unit_separator
        self._pad = pad
        self._plural_suffix = plural_suffix
        self._overflow_msg = overflow_msg

        if self._DEFAULTS is None:
            return
        self._apply_defaults(fallback)

        self._fractional_formatter = StaticFormatter(
            max_value_len=4,
            unit="s",
            unit_separator="",
            allow_negative=self._allow_negative,
            allow_fractional=self._allow_fractional,
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

    def format(self, val_sec: float, auto_color: bool = None) -> RT:
        """
        Pretty-print difference between two moments in time. If input
        value is too big for the current formatter to handle, return "OVERFLOW"
        string (or a part of it, depending on ``max_len``).

        :param val_sec:     Input value in seconds.
        :param auto_color:  Color mode, *bool* to enable/disable colorizing,
                            *None* to use formatter default value.
        :return: Formatted time delta, *Text* if colorizing is on, *str* otherwise.
        """
        result = self.format_base(val_sec, auto_color)
        if result is None:
            result = self._overflow_msg[: self.max_len]
            if self._get_color_effective(auto_color):
                result = Text(result, Styles.ERROR_LABEL)

        if self._pad:
            pad_len = max(0, self._max_len - len(result))
            result = (" " * pad_len) + result
            if isinstance(result, IRenderable):
                result.set_width(self._max_len)

        return result

    # @TODO naming?
    def format_base(self, val_sec: float, auto_color: bool = None) -> RT | None:
        """
        Pretty-print difference between two moments in time. If input
        value is too big for the current formatter to handle, return *None*.

        :param val_sec:     Input value in seconds.
        :param auto_color:  Color mode, *bool* to enable/disable colorizing,
                            *None* to use formatter default value.
        :return: Formatted value as *Text* if colorizing is on; as *str*
                 otherwise. Returns *None* on overflow.
        """
        num = abs(val_sec)
        unit_idx = 0
        result_sub = ""

        negative = self._allow_negative and val_sec < 0
        sign = "-" if negative else ""
        result = None

        if self._allow_fractional and num < self._units[0].in_next:
            if self._max_len is not None:
                result = self._fractional_formatter.format(
                    val_sec, auto_color=auto_color
                )
                if len(result) > self._max_len:
                    # for example, 500ms doesn't fit in the shortest possible
                    # delta string (which is 3 chars), so "<1s" will be returned
                    result = None

        while result is None and unit_idx < len(self._units):
            unit = self._units[unit_idx]
            if unit.overflow_after and num > unit.overflow_after:
                if not self._max_len:  # max len is being computed now
                    raise RecursionError()
                return None

            unit_name = unit.name
            unit_name_suffixed = unit_name
            if self._plural_suffix and trunc(num) != 1:
                unit_name_suffixed += self._plural_suffix

            unit_short = unit_name[0]
            if unit.custom_short:
                unit_short = unit.custom_short

            next_unit_ratio = unit.in_next
            sep = self._unit_separator or ""

            if abs(num) < 1:
                if negative:
                    result = self._colorize(
                        auto_color, "~", "0", sep, unit_name_suffixed
                    )
                elif isclose(num, 0, abs_tol=1e-03):
                    result = self._colorize(auto_color, "", "0", sep, unit_name_suffixed)
                else:
                    result = self._colorize(auto_color, "<", "1", sep, unit_name)

            elif unit.collapsible_after is not None and num < unit.collapsible_after:
                val_sec = str(floor(num))
                result = (
                    self._colorize(auto_color, sign, val_sec, "", unit_short)
                    + result_sub
                )

            elif not next_unit_ratio or num < next_unit_ratio:
                val_sec = str(floor(num))
                result = self._colorize(
                    auto_color, sign, val_sec, sep, unit_name_suffixed
                )

            else:
                next_num = floor(num / next_unit_ratio)
                prev_val = str(floor(num - (next_num * next_unit_ratio)))
                result_sub = self._colorize(auto_color, sep, prev_val, "", unit_short)
                num = next_num
                unit_idx += 1
                continue

        return result or ""

    def _colorize(
        self, auto_color: bool, extra: str, val: str, sep: str, unit: str
    ) -> RT:
        if not self._get_color_effective(auto_color):
            return "".join((extra, val, sep, unit))

        args = dict(intp=val, frac="", sep=sep, pfx="", unit=unit)
        return Text(Fragment(extra), *self._highlighter.apply(**args), align=Align.RIGHT)

    def _compute_max_len(self):
        max_len = 0
        coef = 1.00

        for unit in self._units:
            test_val = unit.in_next
            if not test_val:
                test_val = unit.overflow_after
            if not test_val:
                continue
            test_val_sec = coef * (test_val - 1) * (-1 if self._allow_negative else 1)

            try:
                max_len_unit = self.format_base(test_val_sec, auto_color=False)
            except RecursionError:
                continue

            max_len = max(max_len, len(max_len_unit))
            coef *= unit.in_next or unit.overflow_after

        self._max_len = max_len


# noinspection PyProtectedMember
DualFormatter._set_defaults(
    DualFormatter(
        units=[],
        auto_color=False,
        allow_negative=False,
        allow_fractional=True,
        unit_separator=None,
        pad=False,
        plural_suffix=None,
        overflow_msg="OVERFLOW",
        highlighter=Highlighter,
    )
)


@dataclass(frozen=True)
class DualBaseUnit:
    """
    TU

    .. important ::

        ``in_next`` and `overflow_after` are mutually exclusive, and either of
        them is required.

    :param name: A unit name to display.
    :param in_next:
        The base -- how many current units the next (single) unit contains,
        e.g., for an hour in context of days::

            CustomBaseUnit("hour", 24)

    :param overflow_after:     Value upper limit.
    :param custom_short:       Use specified short form instead of first letter
                               of ``name`` when operating in double-value mode.
    :param collapsible_after:  Min threshold for double output to become a regular one.
    """

    name: str
    in_next: int = None
    overflow_after: int = None
    custom_short: str = None
    collapsible_after: int = None

    def __post_init__(self):
        if not self.in_next and not self.overflow_after:
            raise ValueError("Either in_next or overflow_after is required.")
        if self.in_next and self.overflow_after:
            raise ValueError("Mutually exclusive attributes: in_next, overflow_after.")


class DualFormatterRegistry:
    """
    Simple DualFormatter registry for storing formatters and selecting
    the suitable one by max output length.
    """

    def __init__(self):
        self._formatters: t.Dict[int, DualFormatter] = dict()
        self._min_len: int | None = None
        self._max_len: int | None = None

    def register(self, *formatters: DualFormatter):
        """..."""
        for formatter in formatters:
            key = formatter.max_len
            if key in self._formatters:
                raise ConflictError(f"Formatter with max len {key} already exists")
            self._formatters[key] = formatter

    def find_matching(self, max_len: int) -> DualFormatter | None:
        """..."""
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

    def get_by_max_len(self, max_len: int) -> DualFormatter | None:
        """..."""
        return self._formatters.get(max_len, None)

    def get_shortest(self) -> DualFormatter | None:
        """..."""
        return self._formatters.get(min(self._formatters.keys()))

    def get_longest(self) -> DualFormatter | None:
        """..."""
        return self._formatters.get(max(self._formatters.keys()))


# -----------------------------------------------------------------------------


formatter_si = StaticFormatter()

formatter_si_binary = StaticFormatter(
    allow_negative=False,
    discrete_input=True,
    unit="B",
    unit_separator=" ",
    mcoef=1024.0,
    prefixes=[None, "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi", "Yi", "Ri", "Qi"],
)

formatter_bytes_human = StaticFormatter(
    allow_negative=False,
    discrete_input=True,
    unit_separator="",
    highlighter=Highlighter(dim_units=False),
)

formatter_time = DynamicFormatter(
    units=[
        BaseUnit(math.log10(60 * 60 * 24 * 365), "y"),
        BaseUnit(math.log10(60 * 60 * 24 * 30), "M"),
        BaseUnit(math.log10(60 * 60 * 24 * 7), "w"),
        BaseUnit(math.log10(60 * 60 * 24), "d"),
        BaseUnit(math.log10(60 * 60), "h"),
        BaseUnit(math.log10(60), "m"),
        BaseUnit(0, "s"),
        BaseUnit(-3, "s", prefix="m"),
        BaseUnit(-6, "s", prefix="µ"),
        BaseUnit(-9, "s", prefix="n"),
        BaseUnit(-12, "s", prefix="p"),
        BaseUnit(-15, "s", prefix="f"),
        BaseUnit(-18, "s", prefix="a"),
    ]
)

formatter_time_ms = DynamicFormatter(
    formatter_time, oom_shift=-3, unit_separator="", allow_fractional=False
)

dual_registry = DualFormatterRegistry()
dual_registry.register(
    DualFormatter(
        units=[
            DualBaseUnit("s", 60),
            DualBaseUnit("m", 60),
            DualBaseUnit("h", 24),
            DualBaseUnit("d", 30),
            DualBaseUnit("M", overflow_after=9),
        ],
        allow_negative=False,
        allow_fractional=True,
        unit_separator=None,
        plural_suffix=None,
        overflow_msg="ERR",
    ),
    DualFormatter(
        units=[
            DualBaseUnit("s", 60),
            DualBaseUnit("m", 60),
            DualBaseUnit("h", 24),
            DualBaseUnit("d", 30),
            DualBaseUnit("M", 12),
            DualBaseUnit("y", overflow_after=99),
        ],
        allow_negative=False,
        allow_fractional=True,
        unit_separator=" ",
        plural_suffix=None,
        overflow_msg="ERRO",
    ),
    DualFormatter(
        units=[
            DualBaseUnit("s", 60),
            DualBaseUnit("m", 60),
            DualBaseUnit("h", 24),
            DualBaseUnit("d", 30),
            DualBaseUnit("M", 12),
            DualBaseUnit("y", overflow_after=99),
        ],
        allow_negative=True,
        allow_fractional=True,
        unit_separator=" ",
        plural_suffix=None,
        overflow_msg="ERROR",
    ),
    DualFormatter(
        units=[
            DualBaseUnit("sec", 60),
            DualBaseUnit("min", 60),
            DualBaseUnit("hr", 24, collapsible_after=10),
            DualBaseUnit("day", 30, collapsible_after=10),
            DualBaseUnit("mon", 12),
            DualBaseUnit("yr", overflow_after=99),
        ],
        allow_negative=False,
        allow_fractional=True,
        unit_separator=" ",
        plural_suffix=None,
    ),
    DualFormatter(
        units=[
            DualBaseUnit("sec", 60),
            DualBaseUnit("min", 60, custom_short="min"),
            DualBaseUnit("hour", 24, collapsible_after=24),
            DualBaseUnit("day", 30, collapsible_after=10),
            DualBaseUnit("month", 12),
            DualBaseUnit("year", overflow_after=999),
        ],
        allow_negative=True,
        allow_fractional=True,
        unit_separator=" ",
        plural_suffix="s",
    ),
)


# -----------------------------------------------------------------------------


def format_thousand_sep(val: int | float, separator: str = " ") -> str:
    """
    Returns input ``val`` with integer part split into groups of three digits,
    joined then with ``separator`` string.

    >>> format_thousand_sep(260341)
    '260 341'
    >>> format_thousand_sep(-9123123123.55, ',')
    '-9,123,123,123.55'

    :max output len:  :math:`(L + max(0, floor(M/3)))`,

                       where *L* is ``val`` length, and *M* is
                       order of magnitude of ``val``
    :param val:       value to format
    :param separator: character(s) to use as thousand separators
    """
    return f"{val:_}".replace("_", separator)


def format_auto_float(val: float, req_len: int, allow_exp_form: bool = True) -> str:
    """
    Dynamically adjust decimal digit amount and format to fill up the output string
    with as many significant digits as possible, and keep the output length strictly
    equal to `req_len` at the same time.

    For values impossible to fit into a string of required length and when rounding
    doesn't help (e.g. 12 500 000 and 5 chars) algorithm switches to scientific notation,
    and the result looks like '1.2e7'. If this feature is explicitly disabled
    with ``allow_exp_form`` = *False*, then:

        1) if absolute value is less than 1, zeros will be returned ('0.0000');
        2) if value is a big number (like :math:`10^9`), `ValueError` will be
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

    :max output len:        *adjustable*
    :param val:             Value to format.
    :param req_len:         Required output string length.
    :param allow_exp_form:  Allow scientific notation usage when that's the only way
                            of fitting the value into a string of required length.
    :raises ValueError:     When value is too long and ``allow_exp_form`` is *False*.
    """
    if req_len < 0:
        raise ValueError(f"Required length should be >= 0 (got {req_len})")

    sign = ""
    if val < 0:
        sign = "-"
        req_len -= 1

    if req_len == 0:
        return _OVERFLOW_CHAR * (len(sign))

    abs_value = abs(val)
    if abs_value < 1 and req_len == 1:
        # '0' is better than '-'
        return f"{sign}0"

    if val == 0.0:
        return f"{sign}{0:{req_len}.0f}"

    oom = floor(log10(abs_value))  # order of magnitude
    exp_threshold_left = -2
    exp_threshold_right = req_len - 1

    # oom threshold depends on req
    # length on the right, and is
    # fixed to -2 on the left:

    #   req |    3     4     5     6 |
    #  thld | -2,2  -2,3  -2,4  -2,5 |

    # it determines oom values to
    # enable scientific notation for:

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

    if not allow_exp_form:
        # if exponent mode is disabled, the formatter will try as best
        # as he can to display at least something meaningful; although
        # this can work for the values with the order of magnitude < 0
        # (and result in something like '0.001'), the method will fail
        # on the large input values.
        exp_threshold_left = None

    # fmt: off
    oom_lt_left_thr = (exp_threshold_left is not None and oom < exp_threshold_left)
    oom_gt_right_thr = (oom > exp_threshold_right)
    require_exp_form = oom_lt_left_thr or oom_gt_right_thr
    # fmt: on

    if require_exp_form and not allow_exp_form:  # oh well...
        msg = f"Failed to fit {val:.2f} into {req_len} chars without exp notation"
        raise ValueError(msg)

    if require_exp_form:
        exponent_len = len(str(oom)) + 1  # 'e'
        if req_len < exponent_len:
            # there is no place even for exponent
            return _OVERFLOW_CHAR * (len(sign) + req_len)

        significand = abs_value / pow(10, oom)
        max_significand_len = req_len - exponent_len

        # max_significand_len can be 0, in that case significand_str will be empty;
        # that means we cannot fit it the significand, but still can display approximate
        # number power using the 'eN'/'-eN' output format:  -52515050000 -> '-e10'
        significand_str = format_auto_float(
            significand, max_significand_len, allow_exp_form=False
        )
        return f"{sign}{significand_str}e{oom}"

    integer_len = max(1, oom + 1)
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


def format_si(val: float, unit: str = None, auto_color: bool = None) -> RT:
    """
    Invoke fixed-length decimal SI formatter; format ``value`` as a unitless value with
    SI-prefixes; a unit can be provided as an argument of `format()` method.
    Suitable for formatting any SI unit with values from :math:`10^{-30}` to
    :math:`10^{32}`.

    Total maximum length is ``max_value_len + 2``, which is **6**
    by default (4 from value + 1 from separator and + 1 from prefix).
    If the unit is defined and is a non-empty string, the maximum output
    length increases by length of that unit.

    .. code-block:: python
        :caption: Extending the formatter

        my_formatter = StaticFormatter(formatter_si)

    >>> format_si(1010, 'm²')
    '1.01 km²'
    >>> format_si(0.223, 'g')
    '223 mg'
    >>> format_si(1213531546, 'W')  # great scott
    '1.21 GW'
    >>> format_si(1.22e28, 'eV')  # the Planck energy
    '12.2 ReV'

    :max output len:    6
    :param val:         Input value (unitless).
    :param unit:        A unit override [default unit is an empty string].
    :param auto_color:  Color mode override, *bool* to enable/disable colorizing
                        depending on unit type, *None* to use formatters' setting
                        value [*False* by default].
    :return: Formatted value, *Text* if colorizing is on, *str* otherwise.
    """
    return formatter_si.format(val, unit, auto_color)


def format_si_binary(val: float, unit: str = None, auto_color: bool = False) -> RT:
    """
    Invoke fixed-length binary SI formatter which formats ``value`` as binary
    size ("KiB", "MiB") with base 1024. Unit can be customized. Covers values
    from :math:`0` to :math:`10^{32}`.

    While being similar to `formatter_si`, this formatter
    differs in one aspect. Given a variable with default value = 995,
    formatting it results in "995 B". After increasing it
    by 20 it equals to 1015, which is still not enough to become
    a kilobyte -- so returned value will be "1015 B". Only after one
    more increase (at 1024 and more) the value will morph into "1.00 KiB"
    form.

    That's why the initial ``max_value_len`` should be at least 5 -- because it
    is a minimum requirement for formatting values from 1023 to -1023. However,
    The negative values for this formatter are disabled by default and rendered
    as 0, which decreases the ``max_value_len`` minimum value back to 4.

    Total maximum length of the result is ``max_value_len + 4`` = **8**
    (base + 1 from separator + 1 from unit + 2 from prefix, assuming all of
    them have default values defined in `formatter_si_binary`).

    .. code-block:: python
        :caption: Extending the formatter

        my_formatter = StaticFormatter(formatter_si_binary)

    >>> format_si_binary(1010)  # 1010 b < 1 kb
    '1010 B'
    >>> format_si_binary(1080)
    '1.05 KiB'
    >>> format_si_binary(45200)
    '44.1 KiB'
    >>> format_si_binary(1.258 * pow(10, 6), 'b')
    '1.20 Mib'

    :max output len:    8
    :param val:         Input value in bytes.
    :param unit:        A unit override [default unit is "B"].
    :param auto_color:  Color mode override, *bool* to enable/disable colorizing
                        depending on unit type, *None* to use formatters' setting
                        value [*False* by default].
    :return: Formatted value, *Text* if colorizing is on, *str* otherwise.
    """
    return formatter_si_binary.format(val, unit, auto_color)


def format_bytes_human(val: int, auto_color: bool = False) -> RT:
    """
    Invoke special case of fixed-length SI formatter optimized for processing
    byte-based values. Inspired by default stats formatting used in
    `htop <https://htop.dev/>`__. Comprises traits of both preset SI formatters,
    the key ones being:

        - expecting integer inputs;
        - prohibiting negative inputs;
        - operating in decimal mode with the base of 1000 (not 1024);
        - the absence of units and value-unit separators in the output, while
          prefixes are still present;
        - (if colors allowed) utilizing `Highlighter` with a bit customized setup,
          as detailed below.

    Total maximum length is ``max_value_len + 1``, which is **5**
    by default (4 from value + 1 from prefix).

    .. admonition :: Highlighting options

        Default highlighter for this formatter does not render units (as well as
        prefixes) dimmed. The main reason for that is the absence of actual unit in
        the output of this formatter, while prefixes are still there; this allows
        to format the fractional output this way: [1].57[k], where brackets []
        indicate brighter colors.

        This format is acceptable because only essential info gets highlighted; however,
        in case of other formatters with actual units in the output this approach leads
        to complex and mixed-up formatting; furthermore, it doesn't matter if the
        highlighting affects the prefix part only or both prefix and unit parts -- in
        either case it's just too much formatting on a unit of surface:
        [1].53 [Ki]B (looks patchworky).

    .. table:: Default formatters comparison

        ============== ============== =========== =============
        Value          `SI(unit='B')` `SI_BINARY` `BYTES_HUMAN`
        ============== ============== =========== =============
        1568           '1.57 kB'      '1.53 KiB'  '1.57k'
        218371331      '218 MB'       '208 MiB'   '218M'
        0.25           '250 mB' [#]_  '0 B'       '0'
        -1218371331232 '-1.2 TB'      '0 B'       '0'
        ============== ============== =========== =============

    .. [#] 250 millibytes is not something you would see every day

    .. code-block:: python
        :caption: Extending the formatter

        my_formatter = StaticFormatter(formatter_bytes_human, unit_separator=" ")

    >>> format_bytes_human(990)
    '990'
    >>> format_bytes_human(1010)
    '1.01k'
    >>> format_bytes_human(45200)
    '45.2k'
    >>> format_bytes_human(1.258 * pow(10, 6))
    '1.26M'

    :max output len:   5
    :param val:        Input value in bytes.
    :param auto_color:  Color mode override, *bool* to enable/disable colorizing
                        depending on unit type, *None* to use formatters' setting
                        value [*False* by default].
    :return: Formatted value, *Text* if colorizing is on, *str* otherwise.
    """
    return formatter_bytes_human.format(val, auto_color=auto_color)


def format_time(val_sec: float, auto_color: bool = None) -> RT:
    """
    Invoke dynamic-length general-purpose time formatter, which supports a
    wide range of output units, including seconds, minutes, hours, days, weeks,
    months, years, milliseconds, microseconds, nanoseconds etc.

    .. code-block:: python
        :caption: Extending the formatter

        my_formatter = DynamicFormatter(formatter_time, unit_separator=" ")

    >>> format_time(12)
    '12.0 s'
    >>> format_time(65536)
    '18 h'
    >>> format_time(0.00324)
    '3.2 ms'

    :max output len:    *varying*
    :param val_sec:     Input value in seconds.
    :param auto_color:  Color mode override, *bool* to enable/disable colorizing
                        depending on unit type, *None* to use formatters' setting
                        value [*False* by default].
    """
    return formatter_time.format(val_sec, auto_color)


def format_time_ms(value_ms: float, auto_color: bool = None) -> RT:
    """
    Invoke a variation of `formatter_time` specifically configured to
    format small time intervals.

    .. code-block:: python
        :caption: Extending the formatter

        my_formatter = DynamicFormatter(formatter_time_ms, unit_separator=" ")

    >>> format_time_ms(1)
    '1ms'
    >>> format_time_ms(344)
    '344ms'
    >>> format_time_ms(0.967)
    '967µs'

    :param value_ms:    Input value in milliseconds.
    :param auto_color:  Color mode override, *bool* to enable/disable colorizing
                        depending on unit type, *None* to use formatters' setting
                        value [*False* by default].
    :return:
    """
    return formatter_time_ms.format(value_ms, auto_color)


def format_time_ns(value_ns: float, auto_color: bool = None) -> RT:
    """
    Wrapper for `format_time_ms()` expecting input value as nanoseconds.

    >>> format_time_ns(1003000)
    '1ms'
    >>> format_time_ns(3232332224)
    '3s'
    >>> format_time_ns(9932248284343.32)
    '2h'

    :param value_ns:    Input value in nanoseconds.
    :param auto_color:  Color mode override, *bool* to enable/disable colorizing
                        depending on unit type, *None* to use formatters' setting
                        value [*False* by default].
    :return:
    """
    return formatter_time_ms.format(value_ns, auto_color, oom_shift=-9)


def format_time_delta(
    val_sec: float, max_len: int = None, auto_color: bool = None
) -> RT:
    """
    Format time interval using the most suitable format with one or
    two time units, depending on ``max_len`` argument. Key feature
    of this formatter is an ability to combine two units and display
    them simultaneously, e.g. return "3h 48min" instead of "228 mins"
    or "3 hours", and on top of that -- fixed-length output.

    There are predefined formatters with output lengths of **3, 4, 5,
    6** and **10** characters. Therefore, you can pass in any value
    from 3 inclusive and it's guarenteed that result's length
    will be less or equal to required length. If `max_len` is
    omitted, longest registred formatter will be used.

    .. note ::

        Negative values are supported by formatters 5 and 10 only.

    >>> format_time_delta(10, 3)
    '10s'
    >>> format_time_delta(10, 6)
    '10.0s'
    >>> format_time_delta(15350, 4)
    '4 h'
    >>> format_time_delta(15350)
    '4h 15min'

    :max output len:    3, 4, 5, 6, 10
    :param val_sec:     Input value in seconds.
    :param max_len:     Maximum output string length (total).
    :param auto_color:  Color mode override, *bool* to enable/disable colorizing
                        depending on unit type, *None* to use formatters' setting
                        value [*False* by default].
    """
    if max_len is None:
        formatter = dual_registry.get_longest()
    else:
        formatter = dual_registry.find_matching(max_len)

    if formatter is None:
        raise ValueError(f"No settings defined for max length = {max_len} (or less)")

    return formatter.format(val_sec, auto_color)


def format_time_delta_shortest(val_sec: float, auto_color: bool = None) -> RT:
    """
    Wrapper around `format_time_delta()` with pre-set shortest formatter.

    :max output len:    3
    :param val_sec:     Input value in seconds.
    :param auto_color:  Color mode override, *bool* to enable/disable colorizing
                        depending on unit type, *None* to use formatters' setting
                        value [*False* by default].
    """
    return dual_registry.get_shortest().format(val_sec, auto_color)


def format_time_delta_longest(val_sec: float, auto_color: bool = None) -> RT:
    """
    Wrapper around `format_time_delta()` with pre-set longest formatter.

    :max output len:    10
    :param val_sec:     Input value in seconds.
    :param auto_color:  Color mode override, *bool* to enable/disable colorizing
                        depending on unit type, *None* to use formatters' setting
                        value [*False* by default].
    """
    return dual_registry.get_longest().format(val_sec, auto_color)


_highlighter = Highlighter()


def highlight(string: str) -> RT:
    """
    .. todo ::

        @TODO

    :max output len:    *same as input*
    :param string:      input text
    """
    return _highlighter.colorize(string)
