# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under GNU Lesser General Public License v3.0
# -----------------------------------------------------------------------------
"""
.. note ::
    Almost all public classes are imported into the first package level
    on its initialization, i.e., "short" forms like ``from pytermor import ColorRGB``
    are available in addition to full import statements.

"""

from ._version import __version__ as __version__
from ._version import __updated__ as __updated__
from .common import logger as logger
from .config import init_config as init_config
from .renderer import init_renderer as init_renderer

from .common import ArgCountError as ArgCountError
from .common import ArgTypeError as ArgTypeError
from .common import ConflictError as ConflictError
from .common import LogicError as LogicError
from .common import UserAbort as UserAbort
from .common import UserCancel as UserCancel

from .common import RGB as RGB
from .common import HSV as HSV
from .common import XYZ as XYZ
from .common import LAB as LAB

from .color import CT as CT
from .color import CDT as CDT
from .style import FT as FT
from .text import RT as RT

# constants except util*
from .cval import CVAL
from .ansi import NOOP_SEQ as NOOP_SEQ
from .color import DEFAULT_COLOR as DEFAULT_COLOR
from .color import NOOP_COLOR as NOOP_COLOR
from .common import CSI_SEQ_REGEX as CSI_SEQ_REGEX
from .common import ESCAPE_SEQ_REGEX as ESCAPE_SEQ_REGEX
from .common import SGR_SEQ_REGEX as SGR_SEQ_REGEX
from .common import ALIGN_CENTER as ALIGN_CENTER
from .common import ALIGN_LEFT as ALIGN_LEFT
from .common import ALIGN_RIGHT as ALIGN_RIGHT
from .parser import RCP_REGEX as RCP_REGEX
from .style import NOOP_STYLE as NOOP_STYLE

# interfaces
from .ansi import ISequence as ISequence
from .color import IColor as IColor
from .renderer import IRenderer as IRenderer
from .text import IRenderable as IRenderable
from .filter import IFilter as IFilter

# -----------------------------------------------------------------------------
from .common import Align as Align
from .common import ExtendedEnum as ExtendedEnum
from .common import chunk as chunk
from .common import flatten1 as flatten1
from .common import get_preferable_wrap_width as get_preferable_wrap_width
from .common import get_qname as get_qname
from .common import get_terminal_width as get_terminal_width
from .common import median as median
from .common import percentile as percentile
from .ansi import ColorTarget as ColorTarget
from .ansi import IntCode as IntCode
from .ansi import SeqIndex as SeqIndex
from .ansi import SequenceCSI as SequenceCSI
from .ansi import SequenceFe as SequenceFe
from .ansi import SequenceFp as SequenceFp
from .ansi import SequenceFs as SequenceFs
from .ansi import SequenceNf as SequenceNf
from .ansi import SequenceOSC as SequenceOSC
from .ansi import SequenceSGR as SequenceSGR
from .ansi import SequenceST as SequenceST
from .ansi import SubtypedParam as SubtypedParam
from .ansi import compose_hyperlink as assemble_hyperlink
from .ansi import compose_hyperlink as compose_hyperlink
from .ansi import enclose as enclose
from .ansi import get_closing_seq as get_closing_seq
from .ansi import make_clear_display as make_clear_display
from .ansi import make_clear_display_after_cursor as make_clear_display_after_cursor
from .ansi import make_clear_display_before_cursor as make_clear_display_before_cursor
from .ansi import make_clear_history as make_clear_history
from .ansi import make_clear_line as make_clear_line
from .ansi import make_clear_line as make_clear_line
from .ansi import make_clear_line_after_cursor as make_clear_line_after_cursor
from .ansi import make_clear_line_before_cursor as make_clear_line_before_cursor
from .ansi import make_color_256 as make_color_256
from .ansi import make_color_rgb as make_color_rgb
from .ansi import make_disable_alt_screen_buffer as make_disable_alt_screen_buffer
from .ansi import make_enable_alt_screen_buffer as make_enable_alt_screen_buffer
from .ansi import make_erase_in_display as make_erase_in_display
from .ansi import make_erase_in_line as make_erase_in_line
from .ansi import make_hide_cursor as make_hide_cursor
from .ansi import make_move_cursor_down as make_move_cursor_down
from .ansi import make_move_cursor_left as make_move_cursor_left
from .ansi import make_move_cursor_right as make_move_cursor_right
from .ansi import make_move_cursor_to_start_and_down as make_move_cursor_to_start_and_down
from .ansi import make_move_cursor_to_start_and_up as make_move_cursor_to_start_and_up
from .ansi import make_move_cursor_up as make_move_cursor_up
from .ansi import make_query_cursor_position as make_query_cursor_position
from .ansi import make_reset_cursor as make_reset_cursor
from .ansi import make_restore_cursor_position as make_restore_cursor_position
from .ansi import make_restore_screen as make_restore_screen
from .ansi import make_save_cursor_position as make_save_cursor_position
from .ansi import make_save_screen as make_save_screen
from .ansi import make_set_cursor as make_set_cursor
from .ansi import make_set_cursor_column as make_set_cursor_column
from .ansi import make_set_cursor_line as make_set_cursor_line
from .ansi import make_show_cursor as make_show_cursor
from .parser import contains_sgr as contains_sgr
from .parser import decompose_report_cursor_position as decompose_report_cursor_position
from .color import ApxResult as ApxResult
from .color import Color16 as Color16
from .color import Color256 as Color256
from .color import ColorRGB as ColorRGB
from .color import approximate as approximate
from .color import find_closest as find_closest
from .color import resolve_color as resolve_color
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
from .text import Composite as Composite
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
from .term import confirm as confirm
from .term import get_char_width as get_char_width
from .term import guess_char_width as guess_char_width
from .term import measure_char_width as measure_char_width
from .term import wait_key as wait_key
from .conv import hex_to_hsv as hex_to_hsv
from .conv import hex_to_rgb as hex_to_rgb
from .conv import hsv_to_hex as hsv_to_hex
from .conv import hsv_to_rgb as hsv_to_rgb
from .conv import lab_to_rgb as lab_to_rgb
from .conv import lab_to_xyz as lab_to_xyz
from .conv import rgb_to_hex as rgb_to_hex
from .conv import rgb_to_hsv as rgb_to_hsv
from .conv import rgb_to_lab as rgb_to_lab
from .conv import rgb_to_xyz as rgb_to_xyz
from .conv import xyz_to_lab as xyz_to_lab
from .conv import xyz_to_rgb as xyz_to_rgb
from .filter import CONTROL_CHARS as CONTROL_CHARS
from .filter import NON_ASCII_CHARS as NON_ASCII_CHARS
from .filter import PRINTABLE_CHARS as PRINTABLE_CHARS
from .filter import WHITESPACE_CHARS as WHITESPACE_CHARS
from .filter import BytesTracer as BytesTracer
from .filter import CsiStringReplacer as CsiStringReplacer
from .filter import EscSeqStringReplacer as EscSeqStringReplacer
from .filter import NonPrintsOmniVisualizer as NonPrintsOmniVisualizer
from .filter import NonPrintsStringVisualizer as NonPrintsStringVisualizer
from .filter import NoopFilter as NoopFilter
from .filter import OmniDecoder as OmniDecoder
from .filter import OmniEncoder as OmniEncoder
from .filter import OmniMapper as OmniMapper
from .filter import OmniSanitizer as OmniSanitizer
from .filter import SgrStringReplacer as SgrStringReplacer
from .filter import StringMapper as StringMapper
from .filter import StringReplacer as StringReplacer
from .filter import StringTracer as StringTracer
from .filter import StringUcpTracer as StringUcpTracer
from .filter import TracerExtra as TracerExtra
from .filter import apply_filters as apply_filters
from .filter import center_sgr as center_sgr
from .filter import dump as dump
from .filter import ljust_sgr as ljust_sgr
from .filter import pad as pad
from .filter import padv as padv
from .filter import rjust_sgr as rjust_sgr
from .numfmt import dual_registry as dual_registry
from .numfmt import BaseUnit as BaseUnit
from .numfmt import DualBaseUnit as DualBaseUnit
from .numfmt import DynamicFormatter as DynamicFormatter
from .numfmt import DualFormatter as DualFormatter
from .numfmt import Highlighter as Highlighter
from .numfmt import StaticFormatter as StaticFormatter
from .numfmt import format_auto_float as format_auto_float
from .numfmt import format_bytes_human as format_bytes_human
from .numfmt import format_si as format_si
from .numfmt import format_si_binary as format_si_binary
from .numfmt import format_thousand_sep as format_thousand_sep
from .numfmt import format_time as format_time
from .numfmt import format_time_ms as format_time_ms
from .numfmt import format_time_ns as format_time_ns
from .numfmt import format_time_delta as format_time_delta
from .numfmt import highlight as highlight

# -----------------------------------------------------------------------------

cv = CVAL()
"""
Shortcut to `CVAL()` color registry.
"""

init_config()
init_renderer()
