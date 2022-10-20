# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022. A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
"""
Module with output formatters. By default :class:`SgrRenderer` is used. It
also contains compatibility settings, see `SgrRenderer.setup()`.

Working with non-default renderer can be achieved in two ways:

    a. Method `RendererManager.set_default()` sets the default renderer globally.
       After that calling ``Renderable.render()`` will automatically invoke said renderer
       and all formatting will be applied.
    b. Alternatively, you can use renderer's own instance method `AbstractRenderer.render()`
       directly and avoid messing up with the manager:
       ``HtmlRenderer().render(<Renderable>)``

.. rubric:: TL;DR

To unconditionally print formatted message to output terminal, do something like
this:

>>> from pytermor import SgrRenderer, Styles, Text
>>> renderer = RendererManager.set_forced_sgr_as_default()
>>> Text('Warning: AAAA', Styles.WARNING).render()
'\\x1b[33mWarning: AAAA\\x1b[39m'


.. testsetup:: *

    from pytermor.color import Colors
    from pytermor.render import *

    RendererManager.set_forced_sgr_as_default()

-----

.. todo ::

    Scheme can be simplified, too many unnecessary abstractions for now.

    Renderable
          (implemented by Text) should include algorithms for creating intermediate
          styles for text pieces that lie in beetween first opening sequence (or tag)
          and second, for example -- this happens when one Text instance is included
          into another.
    Style's
          responsibility is to preserve the state of text piece and thats it.
    Renderer
          should transform style into corresponding output format and thats it.

    API 2:
        Text(string, style, leave_open = True)  # no style means all open styles will
        be closed at the end
        Text().append(string, style, leave_open = True)
        Text().prepend(string, style, leave_open = False)
        Text().raw
        Text().apply(style)
        Text().render(with=AbstractRenderer())
        Text() + Text() = Text().append(Text().raw, Text().style)
        Text() + str = Text().append(str)
        str + Text() = Text().prepend(str)

        Style(style, fg, bg...)
        # no Style().render()!
        AbstractRenderer().setup()
        AbstractRenderer().render(text)
        SgrRenderer().is_sgr_usage_allowed()

    renderers should have instance methods only!
"""
from __future__ import annotations

import re
import sys
from abc import abstractmethod, ABCMeta
from dataclasses import dataclass, field
from functools import reduce
from typing import List, Sized, Any, FrozenSet, Tuple
from typing import Type, Dict, Set

from .ansi import SequenceSGR, Span, NOOP_SEQ, Seqs, IntCodes
from .color import Color, ColorRGB, ColorIndexed16, ColorIndexed256, NOOP_COLOR, Colors
from .common import LogicError, Registry, Renderable
from .util import ljust_sgr, rjust_sgr, center_sgr, ReplaceSGR


@dataclass
class Style:
    """Create a new ``Style()``.

    Key difference between ``Styles`` and ``Spans`` or ``SGRs`` is that
    ``Styles`` describe colors in RGB format and therefore support output
    rendering in several different formats (see :mod:`._render`).

    Both ``fg`` and ``bg`` can be specified as:

    1. :class:`.Color` instance or library preset;
    2. key code -- name of any of aforementioned presets, case-insensitive;
    3. integer color value in hexademical RGB format.
    4. None -- the color will be unset.

    Inheritance ``parent`` -> ``child`` works this way:

    1. If an argument in child's constructor is empty (=None), take value from
       ``parent``'s corresponding attribute.
    2. If an argument in child's constructor is *not* empty (=True|False|Color etc.),
       use it as child's attribute.

    .. note ::
        There will be no empty (=None) attributes of type `Color` after initialization
        -- they are replaced with special constant `NOOP_COLOR`, that works as if
        there was no color defined and allows to avoid writing of boilerplate code
        to check if a color is None here and there.

    :param parent:      Style to copy attributes without value from.
    :param fg:          Foreground (i.e., text) color.
    :param bg:          Background color.
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
    :param class_name:  Arbitary string used by some renderers, e.g. by
                        ``HtmlRenderer``.

    >>> Style(fg='green', bold=True)
    Style[fg=008000, no bg, bold]
    >>> Style(bg=0x0000ff)
    Style[no fg, bg=0000ff]
    >>> Style(fg=Colors.DEEP_SKY_BLUE_1, bg=Colors.GREY_93)
    Style[fg=00afff, bg=eeeeee]
    """
    _fg: Color = field(default=None, init=False)
    _bg: Color = field(default=None, init=False)

    renderable_attributes = frozenset([
        'fg',
        'bg',
        'blink',
        'bold',
        'crosslined',
        'dim',
        'double_underlined',
        'inversed',
        'italic',
        'overlined',
        'underlined',
    ])

    def __init__(self, parent: Style = None, fg: Color|int|str = None,
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

        if parent is not None:
            self._clone_from(parent)

        if self._fg is None:
            self._fg = NOOP_COLOR
        if self._bg is None:
            self._bg = NOOP_COLOR

    def autopick_fg(self) -> Style:
        """
        Pick ``fg_color`` depending on ``bg_color``. Set ``fg_color`` to
        either 4% gray (almost black) if background is bright, or to 80% gray
        (bright gray) if it is dark. If background is None, do nothing.

        .. todo ::

            check if there is a better algorithm,
            because current thinks text on #000080 should be black

        :return: self
        """
        if self._bg is None or self._bg.hex_value is None:
            return self

        h, s, v = Color.hex_value_to_hsv_channels(self._bg.hex_value)
        if v >= .45:
            self._fg = Colors.RGB_GREY_4
        else:
            self._fg = Colors.RGB_GREY_80
        return self

    def flip(self) -> Style:
        """
        Swap foreground color and background color.
        :return: self
        """
        self._fg, self._bg = self._bg, self._fg
        return self

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

        return None if nullable else NOOP_COLOR

    @property
    def attributes(self) -> FrozenSet:
        return frozenset(list(self.__dict__.keys()) + ['fg', 'bg'])

    @property
    def _attributes(self) -> FrozenSet:
        return frozenset(list(self.__dict__.keys()) + ['_fg', '_bg'])

    def _clone_from(self, parent: Style):
        for attr in self.renderable_attributes:
            self_val = getattr(self, attr)
            parent_val = getattr(parent, attr)
            if self_val is None and parent_val is not None:
                setattr(self, attr, parent_val)

    def __repr__(self):
        if self._fg is None or self._bg is None:
            return self.__class__.__name__ + '[uninitialized]'
        props_set = [self.fg.format_value('fg=', 'no fg'),
                     self.bg.format_value('bg=', 'no bg'), ]
        for attr_name in self.renderable_attributes:
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


class Text(Renderable):
    WIDTH_MAX_LEN_REGEXP = re.compile(r'[\d.]+$')
    ALIGN_LEFT = '<'
    ALIGN_RIGHT = '>'
    ALIGN_CENTER = '^'
    ALIGN_FUNC_MAP = {
        None: ljust_sgr,
        ALIGN_LEFT: ljust_sgr,
        ALIGN_RIGHT: rjust_sgr,
        ALIGN_CENTER: center_sgr,
    }

    def __init__(self, string: str = '', style: Style = NOOP_STYLE):
        self._fragments = []
        self.append(string, style)

    def render(self, renderer: AbstractRenderer|Type[AbstractRenderer] = None) -> str:
        if isinstance(renderer, type):
            renderer = renderer()
        return self._render_using(renderer or RendererManager.get_default())

    def _render_using(self, renderer: AbstractRenderer) -> str:
        return ''.join(renderer.render(frag.string, frag.style)
                       for frag in self._fragments)

    def raw(self) -> str:
        return ''.join(frag.string for frag in self._fragments)

    def append(self, string: str|Text, style: Style = NOOP_STYLE):
        if isinstance(string, str):
            self._fragments.append(self._TextFragment(string, style))
        elif isinstance(string, Text):
            if style != NOOP_STYLE:
                raise ValueError('Style is already defined in first argument')
            self._fragments += string._fragments
        else:
            raise TypeError('Only str or another Text can be added to Text instance')

    def prepend(self, string: str|Text, style: Style = NOOP_STYLE):
        if isinstance(string, str):
            self._fragments.insert(0, self._TextFragment(string, style))
        elif isinstance(string, Text):
            if style != NOOP_STYLE:
                raise ValueError('Style is already defined in first argument')
            self._fragments = string._fragments + self._fragments
        else:
            raise TypeError('Only str or another Text can be added to Text instance')

    def __len__(self) -> int:
        return sum(len(frag) for frag in self._fragments)

    def __add__(self, other: str|Text) -> Text:
        self.append(other)
        return self

    def __iadd__(self, other: str|Text) -> Text:
        self.append(other)
        return self

    def __radd__(self, other: str|Text) -> Text:
        self.prepend(other)
        return self

    def __format__(self, format_spec: str) -> str:
        width, max_len, align, fill = self._parse_format_spec(format_spec)

        renderer = RendererManager.get_default()
        if max_len is None:
            result = self._render_using(renderer)
            cur_len = len(self)
        else:
            result = ''
            cur_len = 0
            cur_frag_idx = 0
            while cur_len < max_len and cur_frag_idx < len(self._fragments):
                allowed_len = max_len - cur_len
                cur_frag = self._fragments[cur_frag_idx]
                cur_frag_string = cur_frag.string[:allowed_len]
                result += renderer.render(cur_frag_string, cur_frag.style)

                cur_len += len(cur_frag_string)
                cur_frag_idx += 1

        if width is not None and width > cur_len:
            align_func_args = (result, width, (fill or ' '), cur_len)
            align_func = self.ALIGN_FUNC_MAP.get(align)
            return align_func(*align_func_args)
        return result

    @classmethod
    def _parse_format_spec(cls, format_spec_orig: str
                           ) -> Tuple[int|None, int|None, str|None, str|None]:
        format_spec = format_spec_orig
        if len(format_spec) == 0 or format_spec[-1] == 's':
            format_spec = format_spec[:-1]
        elif format_spec[-1] in '1234567890':
            pass
        else:
            "".__format__(format_spec_orig)
            raise LogicError(f"Unrecognized format spec: '{format_spec_orig}'")

        width = None
        max_len = None
        if width_and_max_len_match := cls.WIDTH_MAX_LEN_REGEXP.search(format_spec):
            width_max_len = width_and_max_len_match.group(0)
            if '.' in width_max_len:
                if width_max_len.startswith('.'):
                    max_len = int(width_max_len.replace('.', ''))
                else:
                    width, max_len = ((int(val) if val else None)
                                      for val in width_max_len.split('.'))
            else:
                width = int(width_max_len)
            format_spec = cls.WIDTH_MAX_LEN_REGEXP.sub('', format_spec)

        align = None
        if format_spec.endswith((cls.ALIGN_LEFT, cls.ALIGN_RIGHT, cls.ALIGN_CENTER)):
            align = format_spec[-1]
            format_spec = format_spec[:-1]

        fill = None
        if len(format_spec) > 0:
            fill = format_spec[-1]
            format_spec = format_spec[:-1]

        if len(format_spec) > 0:
            "".__format__(format_spec_orig)
            raise LogicError(f"Unrecognized format spec: '{format_spec_orig}'")

        return width, max_len, align, fill

    # def _get_style_delta(self, left: Style, right: Style):
    #     delta = Style(left)
    #     for attr in right.renderable_attributes:
    #         left_val = getattr(left, attr)
    #         right_val = getattr(right, attr)
    #         if left_val != right_val:
    #             setattr(delta, attr, right_val)
    #     return delta

    @dataclass
    class _TextFragment(Sized):
        _string: str = ''
        _style: Style = NOOP_STYLE

        def __len__(self) -> int:
            return len(self._string)

        @property
        def string(self) -> str:
            return self._string

        @property
        def style(self) -> Style:
            return self._style


class RendererManager:
    _default: AbstractRenderer = None

    @classmethod
    def set_default(cls, renderer: AbstractRenderer|Type[AbstractRenderer] = None) -> AbstractRenderer:
        """
        Set up renderer preferences. Affects all renderer types.

        :param renderer:
            Default renderer to use globally. Passing None will result in library
            default setting restored (`SgrRenderer`).

        :return: `AbstractRenderer` instance set as default.

        >>> DebugRenderer().render('text', Style(fg='red'))
        '|ǝ31|text|ǝ39|'

        >>> NoOpRenderer().render('text', Style(fg='red'))
        'text'
        """
        if isinstance(renderer, type):
            renderer = renderer()
        cls._default = (renderer or SgrRenderer())
        return cls._default

    @classmethod
    def get_default(cls) -> AbstractRenderer:
        """
        Get global default renderer (`SgrRenderer`, or the one provided to `setup`).
        """
        return cls._default

    @classmethod
    def set_forced_sgr_as_default(cls) -> AbstractRenderer:
        return cls.set_default(SgrRenderer().setup(force_styles=True))


class AbstractRenderer(metaclass=ABCMeta):
    """ Renderer interface. """

    @abstractmethod
    def render(self, text: Any, style: Style = NOOP_STYLE) -> str:
        """
        Apply colors and attributes described in ``style`` argument to
        ``text`` and return the result. Output format depends on renderer's
        class (which defines the implementation).
        """
        raise NotImplementedError


class Configurable:
    _force_styles: bool|None = False
    _compatibility_256_colors: bool = False
    _compatibility_16_colors: bool = False

    def setup(self,
              force_styles: bool|None = False,
              compatibility_256_colors: bool = False,
              compatibility_16_colors: bool = False,
              ) -> Configurable:
        """
        Set up renderer preferences.

        .. todo ::
            Rewrite this part. Default should be *256* OR *RGB* if COLORTERM is either
            ``truecolor`` or ``24bit``. `setup()` overrides this, of course.

        :param force_styles:

            * If set to *None*, renderer will pass input text through itself
              without any changes (i.e. no colors and attributes will be applied).
            * If set to *True*, renderer will always apply the formatting regardless
              of other internal rules and algorithms.
            * If set to *False* [default], the final decision will be made
              by every renderer independently, based on their own algorithms.

        :param compatibility_256_colors:

            Disable *RGB* (or True Color) output mode. *256-color* sequences will
            be printed out instead of disabled ones. Useful when combined with
            ``curses`` -- that way you can check the terminal capabilities from the
            inside of that terminal and switch to different output mode at once.

        :param compatibility_16_colors:

            Disable *256-color* output mode and default *16-color* sequences instead.
            If this setting is set to *True*, the value of ``compatibility_256_colors``
            will be ignored completely.

        :return: self
        """
        self._force_styles = force_styles
        self._compatibility_256_colors = compatibility_256_colors
        self._compatibility_16_colors = compatibility_16_colors
        return self


class SgrRenderer(AbstractRenderer, Configurable):
    """
    Default renderer invoked by `Text._render()`. Transforms `Color` instances
    defined in ``style`` into ANSI control sequence bytes and merges them with
    input string.

    Respects compatibility preferences (see `Configurable.setup()`) and
    maps RGB colors to closest *indexed* colors if terminal doesn't support
    RGB output. In case terminal doesn't support even 256 colors, falls back
    to 16-color pallete and picks closest counterparts again the same way.

    Type of output ``SequenceSGR`` depends on type of `Color` variables in
    ``style`` argument. Keeping all that in mind, let's summarize:

    1. `ColorRGB` can be rendered as True Color sequence, 256-color sequence
       or 16-color sequence depending on compatibility settings.
    2. `ColorIndexed256` can be rendered as 256-color sequence or 16-color
       sequence.
    3. `ColorIndexed16` can be rendered as 16-color sequence.
    4. Nothing of the above will happen and all Colors will be discarded
       completely if output is not a terminal emulator or if the developer
       explicitly set up the renderer to do so (**force_styles** = False).

    >>> SgrRenderer().setup(True).render('text', Style(fg='red', bold=True))
    '\\x1b[1;31mtext\\x1b[22;39m'
    """

    def render(self, text: Any, style: Style = NOOP_STYLE):
        opening_seq = self._render_attributes(style, squash=True) + \
                      self._render_color(style.fg, False) + \
                      self._render_color(style.bg, True)

        # in case there are line breaks -- split text to lines and apply
        # SGRs for each line separately. it increases the chances that style
        # will be correctly displayed regardless of implementation details of
        # user's pager, multiplexer, terminal emulator etc.
        rendered_text = ''
        for line in str(text).splitlines(keepends=True):
            rendered_text += Span(opening_seq).wrap(line)
        return rendered_text

    def _render_attributes(self, style: Style, squash: bool) -> List[SequenceSGR]|SequenceSGR:
        if not self.is_sgr_usage_allowed():
            return NOOP_SEQ if squash else [NOOP_SEQ]

        result = []
        if style.blink:             result += [Seqs.BLINK_SLOW]
        if style.bold:              result += [Seqs.BOLD]
        if style.crosslined:        result += [Seqs.CROSSLINED]
        if style.dim:               result += [Seqs.DIM]
        if style.double_underlined: result += [Seqs.DOUBLE_UNDERLINED]
        if style.inversed:          result += [Seqs.INVERSED]
        if style.italic:            result += [Seqs.ITALIC]
        if style.overlined:         result += [Seqs.OVERLINED]
        if style.underlined:        result += [Seqs.UNDERLINED]

        if squash:
            return reduce(lambda p, c: p + c, result, NOOP_SEQ)
        return result

    def _render_color(self, color: Color, bg: bool) -> SequenceSGR:
        hex_value = color.hex_value

        if not self.is_sgr_usage_allowed() or hex_value is None:
            return NOOP_SEQ

        if isinstance(color, ColorRGB):
            if self._compatibility_16_colors:
                return ColorIndexed16.find_closest(hex_value).to_sgr(bg=bg)
            if self._compatibility_256_colors:
                return ColorIndexed256.find_closest(hex_value).to_sgr(bg=bg)
            return color.to_sgr(bg=bg)

        elif isinstance(color, ColorIndexed256):
            if self._compatibility_16_colors:
                return ColorIndexed16.find_closest(hex_value).to_sgr(bg=bg)
            return color.to_sgr(bg=bg)

        elif isinstance(color, ColorIndexed16):
            return color.to_sgr(bg=bg)

        raise NotImplementedError(f'Unknown Color inhertior {color!s}')

    def is_sgr_usage_allowed(self) -> bool:
        if self._force_styles is True:
            return True
        if self._force_styles is None:
            return False
        return sys.stdout.isatty()


class TmuxRenderer(SgrRenderer):
    """
    tmux
    """

    SGR_TO_TMUX_MAP = {
        NOOP_SEQ:           '',
        Seqs.RESET:         'default',

        Seqs.BOLD:          'bold',
        Seqs.DIM:           'dim',
        Seqs.ITALIC:        'italics',
        Seqs.UNDERLINED:    'underscore',
        Seqs.BLINK_SLOW:    'blink',
        Seqs.BLINK_FAST:    'blink',
        Seqs.BLINK_DEFAULT: 'blink',
        Seqs.INVERSED:      'reverse',
        Seqs.HIDDEN:        'hidden',
        Seqs.CROSSLINED:    'strikethrough',
        Seqs.DOUBLE_UNDERLINED: 'double-underscore',
        Seqs.OVERLINED:     'overline',

        Seqs.BOLD_DIM_OFF:   'nobold nodim',
        Seqs.ITALIC_OFF:     'noitalics',
        Seqs.UNDERLINED_OFF: 'nounderscore',
        Seqs.BLINK_OFF:      'noblink',
        Seqs.INVERSED_OFF:   'noreverse',
        Seqs.HIDDEN_OFF:     'nohidden',
        Seqs.CROSSLINED_OFF: 'nostrikethrough',
        Seqs.OVERLINED_OFF:  'nooverline',

        Seqs.BLACK:     'fg=black',
        Seqs.RED:       'fg=red',
        Seqs.GREEN:     'fg=green',
        Seqs.YELLOW:    'fg=yellow',
        Seqs.BLUE:      'fg=blue',
        Seqs.MAGENTA:   'fg=magenta',
        Seqs.CYAN:      'fg=cyan',
        Seqs.WHITE:     'fg=white',
        Seqs.COLOR_OFF: 'fg=default',

        Seqs.BG_BLACK:     'bg=black',
        Seqs.BG_RED:       'bg=red',
        Seqs.BG_GREEN:     'bg=green',
        Seqs.BG_YELLOW:    'bg=yellow',
        Seqs.BG_BLUE:      'bg=blue',
        Seqs.BG_MAGENTA:   'bg=magenta',
        Seqs.BG_CYAN:      'bg=cyan',
        Seqs.BG_WHITE:     'bg=white',
        Seqs.BG_COLOR_OFF: 'bg=default',

        Seqs.GRAY:       'fg=brightblack',
        Seqs.HI_RED:     'fg=brightred',
        Seqs.HI_GREEN:   'fg=brightgreen',
        Seqs.HI_YELLOW:  'fg=brightyellow',
        Seqs.HI_BLUE:    'fg=brightblue',
        Seqs.HI_MAGENTA: 'fg=brightmagenta',
        Seqs.HI_CYAN:    'fg=brightcyan',
        Seqs.HI_WHITE:   'fg=brightwhite',

        Seqs.BG_GRAY:       'bg=brightblack',
        Seqs.BG_HI_RED:     'bg=brightred',
        Seqs.BG_HI_GREEN:   'bg=brightgreen',
        Seqs.BG_HI_YELLOW:  'bg=brightyellow',
        Seqs.BG_HI_BLUE:    'bg=brightblue',
        Seqs.BG_HI_MAGENTA: 'bg=brightmagenta',
        Seqs.BG_HI_CYAN:    'bg=brightcyan',
        Seqs.BG_HI_WHITE:   'bg=brightwhite',
    }

    def render(self, text: Any, style: Style = NOOP_STYLE):
        opening_sgrs = [
            *self._render_attributes(style, False),
            self._render_color(style.fg, False),
            self._render_color(style.bg, True),
        ]
        opening_tmux_style = self._sgr_to_tmux_style(*opening_sgrs)
        closing_tmux_style = ''.join(
            self._sgr_to_tmux_style(Span(sgr).closing_seq) for sgr in opening_sgrs
        )

        rendered_text = ''
        for line in str(text).splitlines(keepends=True):
            rendered_text += opening_tmux_style + line + closing_tmux_style
        return rendered_text

    def _sgr_to_tmux_style(self, *sgrs: SequenceSGR) -> str:
        result = ''
        for sgr in sgrs:
            if sgr.is_color_extended:
                target = 'fg'
                if sgr.params[0] == IntCodes.BG_COLOR_EXTENDED:
                    target = 'bg'

                if sgr.params[1] == IntCodes.EXTENDED_MODE_256:
                    color = 'color{}'.format(sgr.params[2])
                elif sgr.params[1] == IntCodes.EXTENDED_MODE_RGB:
                    color = '#{:06x}'.format(
                        ColorRGB.rgb_channels_to_hex_value(*sgr.params[2:])
                    )
                else:
                    raise ValueError(f"Unknown SGR param #2 (idx 1): {sgr!r}")

                result += f'#[{target}={color}]'
                continue

            tmux_style_decl = self.SGR_TO_TMUX_MAP.get(sgr)
            if tmux_style_decl is None:
                raise LogicError(f'No tmux definiton is present for {sgr!r}')
            if len(tmux_style_decl) > 0:
                result += f'#[{tmux_style_decl}]'
        return result


class NoOpRenderer(AbstractRenderer):
    """
    Special renderer type that does nothing with the input string and just
    returns it as is. That's true only when it _is_ a str beforehand;
    otherwise argument will be casted to str and then returned.

    >>> NoOpRenderer().render('text', Style(fg='red', bold=True))
    'text'
    """

    def render(self, text: Any, style: Style = NOOP_STYLE) -> str:
        if isinstance(text, Renderable):
            return text.render(self)
        return str(text)


class HtmlRenderer(AbstractRenderer):
    """
    html

    >>> HtmlRenderer().render('text',Style(fg='red', bold=True))
    '<span style="color: #800000; font-weight: 700">text</span>'
    """

    DEFAULT_ATTRS = ['color', 'background-color', 'font-weight', 'font-style',
                     'text-decoration', 'border', 'filter', ]

    def render(self, text: Any, style: Style = NOOP_STYLE) -> str:
        span_styles: Dict[str, Set[str]] = dict()
        for attr in self._get_default_attrs():
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

        span_class_str = '' \
            if style.class_name is None \
            else f' class="{style.class_name}"'
        span_style_str = '; '.join(f"{k}: {' '.join(v)}"
                                   for k, v in span_styles.items()
                                   if len(v) > 0)
        return f'<span{span_class_str} style="{span_style_str}">' + str(
            text) + '</span>'  # @TODO  # attribues

    def _get_default_attrs(self) -> List[str]:
        return self.DEFAULT_ATTRS


class DebugRenderer(SgrRenderer):
    """
    DebugRenderer

    >>> DebugRenderer().setup(True).render('text',Style(fg='red', bold=True))
    '|ǝ1;31|text|ǝ22;39|'
    """

    def render(self, text: Any, style: Style = NOOP_STYLE) -> str:
        return ReplaceSGR(r'|ǝ\3|').apply(super().render(str(text), style))

    def is_sgr_usage_allowed(self) -> bool:
        return True


class Styles(Registry[Style]):
    """
    Some ready-to-use styles. Can be used as examples.

    This registry has unique keys in comparsion with other ones (`Seqs` / `Spans` /
    `IntCodes`). Therefore there is no risk of key/value duplication and all
    presets can be listed in the initial place -- at API docs page directly.
    """

    WARNING = Style(fg=Colors.YELLOW)
    WARNING_LABEL = Style(WARNING, bold=True)
    WARNING_ACCENT = Style(fg=Colors.HI_YELLOW)

    ERROR = Style(fg=Colors.RED)
    ERROR_LABEL = Style(ERROR, bold=True)
    ERROR_ACCENT = Style(fg=Colors.HI_RED)

    CRITICAL = Style(bg=Colors.HI_RED, fg=Colors.HI_WHITE)
    CRITICAL_LABEL = Style(CRITICAL, bold=True)
    CRITICAL_ACCENT = Style(CRITICAL, bold=True, blink=True)


RendererManager.set_default()
