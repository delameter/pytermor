# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022. A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
"""
Module with output formatters. By default :class:`SGRRenderer` is used. It
also contains compatibility settings, see `SGRRenderer.set_up()`.

Working with non-default renderer can be achieved in two ways:

a. Method `RendererManager.set_up()` sets the default renderer globally.
b. Alternatively, you can use renderer's own class method `Renderer.render()`
   directly and avoid calling `Style.render()` method whatsoever.

.. testsetup:: *

    from pytermor.color import Colors
    from pytermor.render import *

    SGRRenderer.set_up(force_styles = True)

"""
from __future__ import annotations

import abc
import sys
import traceback
from abc import abstractmethod
from dataclasses import dataclass, field
from typing import List, Sized, Any
from typing import TextIO
from typing import Type, Dict, Set

from .ansi import SequenceSGR, Span, NOOP_SEQ, Seqs
from .color import Color, ColorRGB, ColorIndexed, ColorDefault, NOOP_COLOR, Colors
from .common import Registry
from .util.string_filter import ReplaceSGR


class Text:
    """
    Text
    """

    def __init__(self, text: Any = None, style: Style|str = None):
        self._runs: List[_TextRun] = [_TextRun(text, style)]

    def render(self) -> str:
        return ''.join(r.render() for r in self._runs)

    def append(self, text: str|Text):
        if isinstance(text, str):
            self._runs.append(_TextRun(text))
        elif isinstance(text, Text):
            self._runs += text._runs
        else:
            raise TypeError('Can add Text to another Text instance or str only')

    def prepend(self, text: str|Text):
        if isinstance(text, str):
            self._runs.insert(0, _TextRun(text))
        elif isinstance(text, Text):
            self._runs = text._runs + self._runs
        else:
            raise TypeError('Can add Text to another Text instance or str only')

    def __str__(self) -> str:
        return self.render()

    def __len__(self) -> int:
        return sum(len(r) for r in self._runs)

    def __format__(self, *args, **kwargs) -> str:
        runs_amount = len(self._runs)
        if runs_amount == 0:
            return ''.__format__(*args, **kwargs)
        if runs_amount > 1:
            raise RuntimeError(
                f'Can only __format__ Texts consisting of 0 or 1 TextRuns, '
                f'got {runs_amount}. Consider applying the styles and creating'
                f' the Text instance after value formatting.')
        return self._runs[0].__format__(*args, **kwargs)

    def __add__(self, other: str|Text) -> Text:
        self.append(other)
        return self

    def __iadd__(self, other: str|Text) -> Text:
        self.append(other)
        return self

    def __radd__(self, other: str|Text) -> Text:
        self.prepend(other)
        return self


class _TextRun(Sized):
    def __init__(self, string: Any = None, style: Style|str = None):
        self._string: str = str(string)
        if isinstance(style, str):
            style = Style(fg=style)
        self._style: Style|None = style

    def render(self) -> str:
        if not self._style:
            return self._string
        return self._style.render(self._string)

    def __len__(self) -> int:
        return len(self._string)

    def __format__(self, *args, **kwargs) -> str:
        self._string = self._string.__format__(*args, **kwargs)
        return self.render()


@dataclass
class Style:
    """Create a new ``Style()``.

    Key difference between ``Styles`` and ``Spans`` or ``SGRs`` is that
    ``Styles`` describe colors in RGB format and therefore support output
    rendering in several different formats (see :mod:`.render`).

    Both ``fg`` and ``bg`` can be specified as:

    1. :class:`.Color` instance or library preset;
    2. key code -- name of any of aforementioned presets, case-insensitive;
    3. integer color value in hexademical RGB format.
    4. None -- the color will be unset.

    :param fg:          Foreground (i.e., text) color.
    :param bg:          Background color.
    :param inherit:     Parent instance to copy unset properties from.
    :param blink:       Blinking effect; *supported by limited amount of Renderers*.
    :param bold:        Bold or increased intensity.
    :param crosslined:  Strikethrough.
    :param dim:         Faint, decreased intensity.
    :param double_underlined:
        Faint, decreased intensity.
    :param inversed:    Swap foreground and background colors.
    :param italic:      Italic.
    :param overlined:   Overline.
    :param underlined:  Underline.
    :param class_name:  Arbitary string used by some renderers, e.g. by ``HtmlRenderer``.

    >>> Style(fg='green', bold=True)
    Style[fg=008000, no bg, bold]
    >>> Style(bg=0x0000ff)
    Style[no fg, bg=0000ff]
    >>> Style(fg=Colors.XTERM_DEEP_SKY_BLUE_1, bg=Colors.XTERM_GREY_93)
    Style[fg=00afff, bg=eeeeee]
    """
    _fg: Color = field(default=None, init=False)
    _bg: Color = field(default=None, init=False)

    def __init__(self, inherit: Style = None, fg: Color|int|str = None,
                 bg: Color|int|str = None, blink: bool = None, bold: bool = None,
                 crosslined: bool = None, dim: bool = None,
                 double_underlined: bool = None, inversed: bool = None,
                 italic: bool = None, overlined: bool = None, underlined: bool = None,
                 class_name: str = None):
        if fg is not None:
            self._fg = self._resolve_color(fg, True)
        if bg is not None:
            self._bg = self._resolve_color(bg, True)

        self.blink = blink
        self.bold = bold
        self.crosslined = crosslined
        self.dim = dim
        self.double_underlined = double_underlined
        self.inversed = inversed
        self.italic = italic
        self.overlined = overlined
        self.underlined = underlined
        self.class_name = class_name

        if inherit is not None:
            self._clone_from(inherit)

        if self._fg is None:
            self._fg = NOOP_COLOR
        if self._bg is None:
            self._bg = NOOP_COLOR

    def render(self, text: Any = None) -> str:
        """
        Returns ``text`` with all attributes and colors applied.

        By default uses `SequenceSGR` renderer, that means that output will contain
        ANSI escape sequences.
        """
        return RendererManager.get_default().render(text, self)

    def autopick_fg(self) -> Color|None:
        """
        Pick ``fg_color`` depending on ``bg_color``. Set ``fg_color`` to
        either 4% gray (almost black) if background is bright, or to 96% gray
        (almost white) if it is dark, and after that return the applied ``fg_color``.
        If ``bg_color`` is undefined, do nothing and return None.

        :return: Suitable foreground color or None.
        """
        if self._bg is None or self._bg.hex_value is None:
            return

        h, s, v = Color.hex_value_to_hsv_channels(self._bg.hex_value)
        if v >= .45:
            self._fg = Colors.RGB_GRAY_04
        else:
            self._fg = Colors.RGB_GRAY_96
        # @TODO check if there is a better algorithm,
        #       because current thinks text on #000080 should be black
        return self._fg

    # noinspection PyMethodMayBeStatic
    def _resolve_color(self, arg: str|int|Color, nullable: bool) -> Color|None:
        if isinstance(arg, Color):
            return arg

        if isinstance(arg, int):
            return ColorRGB(arg)

        if isinstance(arg, str):
            resolved_color = Colors.resolve(arg)
            if not isinstance(resolved_color, Color):
                raise ValueError(f'Attribute is not valid Color: {resolved_color}')
            return resolved_color

        return None if nullable else Colors.NOOP

    def _clone_from(self, inherit: Style):
        for attr in list(self.__dict__.keys()) + ['_fg', '_bg']:
            inherit_val = getattr(inherit, attr)
            if getattr(self, attr) is None and inherit_val is not None:
                setattr(self, attr, inherit_val)

    def __repr__(self):
        if self._fg is None or self._bg is None:
            return self.__class__.__name__ + '[uninitialized]'
        props_set = [self.fg.format_value('fg=', 'no fg'),
                     self.bg.format_value('bg=', 'no bg'), ]
        for attr_name in dir(self):
            if not attr_name.startswith('_'):
                attr = getattr(self, attr_name)
                if isinstance(attr, bool) and attr is True:
                    props_set.append(attr_name)

        return self.__class__.__name__ + '[{:s}]'.format(', '.join(props_set))

    @property
    def fg(self) -> Color:
        return self._fg

    @property
    def bg(self) -> Color:
        return self._bg

    @fg.setter
    def fg(self, val: str|int|Color):
        self._fg: Color = self._resolve_color(val, nullable=False)

    @bg.setter
    def bg(self, val: str|int|Color):
        self._bg: Color = self._resolve_color(val, nullable=False)


NOOP_STYLE = Style()
"""
Special style which passes the text 
furthrer without any modifications.
"""

class Stylesheet:
    """
    @wat when how выпилить к черту
    """

    def __init__(self, default: Style = None):
        self.default: Style = self._opt_arg(default)

    def _opt_arg(self, arg: Style|None):
        return arg or NOOP_STYLE

    def __repr__(self):
        styles_set = sum(map(lambda a: int(isinstance(a, Style)),
                             [getattr(self, attr_name) for attr_name in dir(self) if
                              not attr_name.startswith('_')]))
        return self.__class__.__name__ + '[{:d} props]'.format(styles_set)


class RendererManager:
    _default: Type[Renderer] = None

    @classmethod
    def set_up(cls, default_renderer: Type[Renderer]|None = None):
        """
        Set up renderer preferences. Affects all renderer types.

        :param default_renderer:
            Default renderer to use globally. Passing None will result in library
            default setting restored (`SGRRenderer`).

        >>> RendererManager.set_up(DebugRenderer)
        >>> Style(fg='red').render('text')
        '|ǝ31|text|ǝ39|'

        >>> NoOpRenderer.render('text',Style(fg='red'))
        'text'
        """
        cls._default = default_renderer or SGRRenderer

    @classmethod
    def get_default(cls) -> Type[Renderer]:
        """ Get global default renderer type. """
        return cls._default


class Renderer(metaclass=abc.ABCMeta):
    """ Abstract ancestor of all renderers. """

    @classmethod
    @abstractmethod
    def render(cls, text: Any, style: Style) -> str:
        """
        Apply colors and attributes described in ``style`` argument to
        ``text`` and return the result. Output format depends on renderer's
        class (which defines the implementation).
        """
        raise NotImplementedError


class SGRRenderer(Renderer):
    """
    Default renderer that `Style.render() <Style.render>` invokes. Transforms
    `Color` instances defined in ``style`` argument into ANSI control sequence
    characters and merges them with input string.
    """
    _force_styles: bool|None = False
    _compatibility_indexed: bool = False
    _compatibility_default: bool = False

    @classmethod
    def set_up(cls, force_styles: bool|None = False,
               compatibility_indexed: bool = False,
               compatibility_default: bool = False):
        """
        Set up renderer preferences. Affects all renderer types.

        :param force_styles:

            * If set to *None*, all renderers will pass input text through themselves
              without any changes (i.e. no colors and attributes will be applied).
            * If set to *True*, renderers will always apply the formatting regardless
              of other internal rules and algorithms.
            * If set to *False* [default], the final decision will be made
              by every renderer independently, based on their own algorithms.

        :param compatibility_indexed:

            Disable *RGB* (or True Color) output mode. 256-color (*indexed*) sequences
            will be printed out instead of disabled ones. Useful when combined with
            ``curses`` -- that way you can check the terminal capabilities from the
            inside of that terminal and switch to different output mode at once.

        :param compatibility_default:

            Disable *indexed* output mode and use *default* 16-color sequences instead.
            If this setting is set to *True*, the value of ``compatibility_indexed``
            will be ignored completely. Useful when combined with ``curses`` -- that
            way you can check the terminal capabilities from the inside of that
            terminal and switch to different output mode at once.

        """
        cls._force_styles = force_styles
        cls._compatibility_indexed = compatibility_indexed
        cls._compatibility_default = compatibility_default

    @classmethod
    def render(cls, text: Any, style: Style):
        """
        Render ``text`` with ``style`` applied as ANSI control sequences.

        Respects compatibility preferences (see `RendererManager.set_up()`) and
        maps RGB colors to closest *indexed* colors if terminal doesn't support
        RGB output. In case terminal doesn't support even 256 colors, falls back
        to *default* colors, searching for closest counterparts in 16-color table.

        Type of output ``SequenceSGR`` depends on type of `Color` variables in
        ``style`` argument. Keeping all that
        in mind, let's summarize:

        1. `ColorRGB` can be rendered as True Color sequence, indexed sequence
           or default (16-color) sequence depending on terminal capabilities.
        2. `ColorIndexed` can be rendered as indexed sequence or default sequence.
        3. `ColorDefault` will be rendered as default-color sequence.

        >>> SGRRenderer.render('text', Style(fg='red', bold=True))
        '\\x1b[1;31mtext\\x1b[22;39m'

        :param style: Style to apply.
        :param text: Input string.
        :return: Input string enclosed in SGR sequences.
        """
        opening_seq = cls._render_attributes(style) + \
                      cls._render_color(style.fg, False) + \
                      cls._render_color(style.bg, True)

        # in case there are line breaks -- split text to lines and apply
        # SGRs for each line separately. it increases the chances that style
        # will be correctly displayed regardless of implementation details of
        # user's pager, multiplexer, terminal emulator etc.
        rendered_text = ''
        for line in str(text).splitlines(keepends=True):
            rendered_text += Span(opening_seq).wrap(line)
        return rendered_text

    @classmethod
    def _render_attributes(cls, style: Style) -> SequenceSGR:
        result = NOOP_SEQ
        if not cls._is_sgr_usage_allowed():
            return result

        if style.blink:             result += Seqs.BLINK_SLOW
        if style.bold:              result += Seqs.BOLD
        if style.crosslined:        result += Seqs.CROSSLINED
        if style.dim:               result += Seqs.DIM
        if style.double_underlined: result += Seqs.DOUBLE_UNDERLINED
        if style.inversed:          result += Seqs.INVERSED
        if style.italic:            result += Seqs.ITALIC
        if style.overlined:         result += Seqs.OVERLINED
        if style.underlined:        result += Seqs.UNDERLINED

        return result

    @classmethod
    def _render_color(cls, color: Color, bg: bool) -> SequenceSGR:
        if not cls._is_sgr_usage_allowed():
            return NOOP_SEQ

        hex_value = color.hex_value

        if isinstance(color, ColorRGB):
            if cls._compatibility_default:
                return ColorDefault.find_closest(hex_value).to_sgr(bg=bg)
            if cls._compatibility_indexed:
                return ColorIndexed.find_closest(hex_value).to_sgr(bg=bg)
            return color.to_sgr(bg=bg)

        elif isinstance(color, ColorIndexed):
            if cls._compatibility_default:
                return ColorDefault.find_closest(hex_value).to_sgr(bg=bg)
            return color.to_sgr(bg=bg)

        elif isinstance(color, ColorDefault):
            return color.to_sgr(bg=bg)

        raise NotImplementedError(f'Unknown Color inhertior {color!s}')

    @classmethod
    def _is_sgr_usage_allowed(cls) -> bool:
        if cls._force_styles is True:
            return True
        if cls._force_styles is None:
            return False
        return sys.stdout.isatty()


class TmuxRenderer(Renderer):
    pass


class NoOpRenderer(Renderer):
    @classmethod
    def render(cls, text: Any, style: Style) -> str:
        """
        Special renderer type that does nothing with the input string and just
        returns it as is. That's true only when it _is_ a str beforehand;
        otherwise argument will be casted to str and then returned.

        >>> NoOpRenderer.render('text',Style(fg='red', bold=True))
        'text'

        :param style: Style to ignore.
        :param text: Input string.
        :return: Input string without changes.
        """
        return str(text)


class HtmlRenderer(Renderer):
    DEFAULT_ATTRS = ['color', 'background-color', 'font-weight', 'font-style',
                     'text-decoration', 'border', 'filter', ]

    @classmethod
    def render(cls, text: Any, style: Style) -> str:
        """
        >>> HtmlRenderer.render('text',Style(fg='red', bold=True))
        '<span style="color: #800000; font-weight: 700">text</span>'
        """

        span_styles: Dict[str, Set[str]] = dict()
        for attr in cls._get_default_attrs():
            span_styles[attr] = set()

        if style.fg.hex_value is not None:
            span_styles['color'].add(style.fg.format_value("#"))
        if style.bg.hex_value is not None:
            span_styles['background-color'].add(style.bg.format_value("#"))

        if style.blink:  # modern browsers doesn't support it without shit piled up
            span_styles['border'].update(('1px', 'dotted'))
        if style.bold:
            span_styles['font-weight'].add('700')
        if style.crosslined:
            span_styles['text-decoration'].add('line-through')
        if style.dim:
            span_styles['filter'].update(('saturate(0.5)', 'brightness(0.75)'))
        if style.double_underlined:
            span_styles['text-decoration'].update(('underline', 'double'))
        if style.inversed:
            span_styles['color'], span_styles['background-color'] = \
                span_styles['background-color'], span_styles['color']
        if style.italic:
            span_styles['font-style'].add('italic')
        if style.overlined:
            span_styles['text-decoration'].add('overline')
        if style.underlined:
            span_styles['text-decoration'].add('underline')

        span_class_str = f'' if style.class_name is None else f' class="{style.class_name}"'
        span_style_str = '; '.join(f"{k}: {' '.join(v)}"
                                   for k, v in span_styles.items()
                                   if len(v) > 0)
        return f'<span{span_class_str} style="{span_style_str}">{text}</span>'  # @TODO  # attribues

    @classmethod
    def _get_default_attrs(cls) -> List[str]:
        return cls.DEFAULT_ATTRS


class DebugRenderer(Renderer):
    @classmethod
    def render(cls, text: Any, style: Style) -> str:
        """
        >>> DebugRenderer.render('text',Style(fg='red', bold=True))
        '|ǝ1;31|text|ǝ22;39|'
        """
        return ReplaceSGR(r'|ǝ\3|').apply(SGRRenderer.render(str(text), style))


RendererManager.set_up()


class Styles(Registry[Style]):
    """
    Some ready-to-use styles. Can be used as examples.

    This registry has unique keys in comparsion with other ones (`Seqs` / `Spans` /
    `IntCodes`),
    Therefore there is no risk of key/value duplication and all presets can be listed
    in the initial place -- at API docs page directly.
    """

    ERROR = Style(fg=Colors.RED)
    ERROR_LABEL = Style(ERROR, bold=True)
    ERROR_ACCENT = Style(fg=Colors.HI_RED)


def print_exception(e: Exception, file: TextIO = sys.stderr, with_trace: bool = True):
    """
    print_exception

    :param e:
    :param file:
    :param with_trace:
    :return:
    """
    tb_lines = [line.rstrip('\n') for line in
                traceback.format_exception(e.__class__, e, e.__traceback__)]

    error_text = Text()
    if with_trace:
        error_text += Text('\n'.join(tb_lines), Styles.ERROR) + '\n\n'

    error_text += (
        Text('ERROR:', Styles.ERROR_LABEL) + Text(f' {e}', Styles.ERROR_ACCENT))

    print(error_text.render(), file=file)


def distribute_padded(values: List[str|Text], max_len: int, pad_before: bool = False,
                      pad_after: bool = False, ) -> str:
    if pad_before:
        values.insert(0, '')
    if pad_after:
        values.append('')

    values_amount = len(values)
    gapes_amount = values_amount - 1
    values_len = sum(len(v) for v in values)
    spaces_amount = max_len - values_len
    if spaces_amount < gapes_amount:
        raise ValueError(f'There is not enough space for all values with padding')

    result = ''
    for value_idx, value in enumerate(values):
        gape_len = spaces_amount // (gapes_amount or 1)  # for last value
        result += value + ' ' * gape_len
        gapes_amount -= 1
        spaces_amount -= gape_len

    return result
