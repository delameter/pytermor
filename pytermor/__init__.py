# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
"""
.. note ::
    Almost all public classes are imported into the first package level
    on its initialization, i.e., "short" forms like ``from pytermor import ColorRGB``
    are supported, not only "full forms" as ``from pytermor.color import ColorRGB``.

"""

from ._version import __version__ as __version__
from .common import logger as logger
from .config import init_config as init_config
from .renderer import init_renderer as init_renderer

from .common import ArgCountError as ArgCountError
from .common import ArgTypeError as ArgTypeError
from .common import ConflictError as ConflictError
from .common import LogicError as LogicError
from .common import UserAbort as UserAbort
from .common import UserCancel as UserCancel

from .color import CT as CT
from .color import CDT as CDT
from .style import FT as FT
from .text import RT as RT

# constants except util*
from .common import ALIGN_CENTER as ALIGN_CENTER
from .common import ALIGN_LEFT as ALIGN_LEFT
from .common import ALIGN_RIGHT as ALIGN_RIGHT
from .color import DEFAULT_COLOR as DEFAULT_COLOR
from .cval import CVAL
from .ansi import NOOP_SEQ as NOOP_SEQ
from .color import NOOP_COLOR as NOOP_COLOR
from .style import NOOP_STYLE as NOOP_STYLE

# interfaces
from .ansi import ISequence as ISequence
from .ansi import ISequenceFe as ISequenceFe
from .color import IColor as IColor
from .renderer import IRenderer as IRenderer
from .text import IRenderable as IRenderable
from .utilstr import IFilter as IFilter, trace as trace, measure as measure

# -----------------------------------------------------------------------------
from .ansi import IntCode as IntCode
from .ansi import SeqIndex as SeqIndex
from .ansi import SequenceCSI as SequenceCSI
from .ansi import SequenceOSC as SequenceOSC
from .ansi import SequenceSGR as SequenceSGR
from .ansi import SequenceST as SequenceST
from .ansi import assemble_hyperlink as assemble_hyperlink
from .ansi import decompose_request_cursor_position as decompose_request_cursor_position
from .ansi import enclose as enclose
from .ansi import get_closing_seq as get_closing_seq
from .ansi import make_color_256 as make_color_256
from .ansi import make_color_rgb as make_color_rgb
from .ansi import make_erase_in_line as make_erase_in_line
from .ansi import make_hyperlink_part as make_hyperlink_part
from .ansi import make_query_cursor_position as make_query_cursor_position
from .ansi import make_set_cursor_x_abs as make_set_cursor_x_abs
from .color import ApxResult as ApxResult
from .color import Color16 as Color16
from .color import Color256 as Color256
from .color import ColorRGB as ColorRGB
from .color import approximate as approximate
from .color import find_closest as find_closest
from .color import resolve_color as resolve_color
from .common import Align as Align
from .common import chunk as chunk
from .common import flatten1 as flatten1
from .common import get_preferable_wrap_width as get_preferable_wrap_width
from .common import get_qname as get_qname
from .common import get_terminal_width as get_terminal_width
from .common import median as median
from .common import percentile as percentile
from .config import Config as Config
from .config import get_config as get_config
from .config import replace_config as replace_config
from .style import Style as Style
from .style import Styles as Styles
from .style import make_style as make_style
from .style import merge_styles as merge_styles
from .renderer import HtmlRenderer as HtmlRenderer
from .renderer import OutputMode as OutputMode
from .renderer import RendererManager as RendererManager
from .renderer import SgrRenderer as SgrRenderer
from .renderer import TmuxRenderer as TmuxRenderer
from .text import Fragment as Fragment
from .text import FrozenText as FrozenText
from .text import SimpleTable as SimpleTable
from .text import TemplateEngine as TemplateEngine
from .text import Text as Text
from .text import distribute_padded as distribute_padded
from .text import echo as echo
from .text import echoi as echoi
from .text import render as render
from .text import wrap_sgr as wrap_sgr
from .utilmisc import confirm as confirm
from .utilmisc import get_char_width as get_char_width
from .utilmisc import guess_char_width as guess_char_width
from .utilmisc import hex_to_hsv as hex_to_hsv
from .utilmisc import hex_to_rgb as hex_to_rgb
from .utilmisc import hsv_to_hex as hsv_to_hex
from .utilmisc import hsv_to_rgb as hsv_to_rgb
from .utilmisc import lab_to_rgb as lab_to_rgb
from .utilmisc import measure_char_width as measure_char_width
from .utilmisc import rgb_to_hex as rgb_to_hex
from .utilmisc import rgb_to_hsv as rgb_to_hsv
from .utilmisc import total_size as total_size
from .utilmisc import wait_key as wait_key
from .utilnum import dual_registry as dual_registry
from .utilnum import BaseUnit as BaseUnit
from .utilnum import DualBaseUnit as DualBaseUnit
from .utilnum import DynamicFormatter as DynamicFormatter
from .utilnum import DualFormatter as DualFormatter
from .utilnum import Highlighter as Highlighter
from .utilnum import StaticFormatter as StaticFormatter
from .utilnum import format_auto_float as format_auto_float
from .utilnum import format_bytes_human as format_bytes_human
from .utilnum import format_si as format_si
from .utilnum import format_si_binary as format_si_binary
from .utilnum import format_thousand_sep as format_thousand_sep
from .utilnum import format_time as format_time
from .utilnum import format_time_ms as format_time_ms
from .utilnum import format_time_ns as format_time_ns
from .utilnum import format_time_delta as format_time_delta
from .utilnum import highlight as highlight
from .utilstr import CONTROL_CHARS as CONTROL_CHARS
from .utilstr import CSI_SEQ_REGEX as CSI_SEQ_REGEX
from .utilstr import ESCAPE_SEQ_REGEX as ESCAPE_SEQ_REGEX
from .utilstr import NON_ASCII_CHARS as NON_ASCII_CHARS
from .utilstr import PRINTABLE_CHARS as PRINTABLE_CHARS
from .utilstr import SGR_SEQ_REGEX as SGR_SEQ_REGEX
from .utilstr import WHITESPACE_CHARS as WHITESPACE_CHARS
from .utilstr import BytesTracer as BytesTracer
from .utilstr import CsiStringReplacer as CsiStringReplacer
from .utilstr import EscSeqStringReplacer as EscSeqStringReplacer
from .utilstr import NonPrintsOmniVisualizer as NonPrintsOmniVisualizer
from .utilstr import NonPrintsStringVisualizer as NonPrintsStringVisualizer
from .utilstr import NoopFilter as NoopFilter
from .utilstr import OmniDecoder as OmniDecoder
from .utilstr import OmniEncoder as OmniEncoder
from .utilstr import OmniMapper as OmniMapper
from .utilstr import OmniSanitizer as OmniSanitizer
from .utilstr import SgrStringReplacer as SgrStringReplacer
from .utilstr import StringMapper as StringMapper
from .utilstr import StringReplacer as StringReplacer
from .utilstr import StringTracer as StringTracer
from .utilstr import StringUcpTracer as StringUcpTracer
from .utilstr import TracerExtra as TracerExtra
from .utilstr import apply_filters as apply_filters
from .utilstr import center_sgr as center_sgr
from .utilstr import dump as dump
from .utilstr import ljust_sgr as ljust_sgr
from .utilstr import measure as measure
from .utilstr import pad as pad
from .utilstr import padv as padv
from .utilstr import rjust_sgr as rjust_sgr
from .utilstr import trace as trace

# -----------------------------------------------------------------------------

cv = CVAL()
"""
Shortcut to `CVAL()` color registry.
"""

init_config()
init_renderer()
