# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under GNU Lesser General Public License v3.0
# -----------------------------------------------------------------------------
"""
.. note ::
    Almost all public classes are imported into the first package level
    on its initialization, which makes kind of a contract on library's API.
    The exceptions include some abstract superclasses or metaclasses, which 
    generally should not be used outside of the library, but still can be 
    imported directly using a full module path.

"""
from __future__ import annotations

from ._version import __updated__ as __updated__
from ._version import __version__ as __version__
from . import log

# ========================= COMMONS =================================

from .common import chunk as chunk
from .common import flatten as flatten
from .common import flatten1 as flatten1
from .common import get_qname as get_qname
from .common import ExtendedEnum as ExtendedEnum

# exceptions:
from .exception import ArgTypeError as ArgTypeError
from .exception import LogicError as LogicError
from .exception import ConflictError as ConflictError
from .exception import UserAbort as UserAbort
from .exception import UserCancel as UserCancel

# color model descriptors:
from .conv import RGB
from .conv import HSV
from .conv import XYZ
from .conv import LAB

# type vars:
from .color import CDT as CDT
from .color import CT as CT
from .style import FT as FT
from .text import RT as RT

# constants:
from .ansi import NOOP_SEQ as NOOP_SEQ
from .style import NOOP_STYLE as NOOP_STYLE
from .color import NOOP_COLOR as NOOP_COLOR
from .color import DEFAULT_COLOR as DEFAULT_COLOR
from .filter import CONTROL_CHARS as CONTROL_CHARS
from .filter import NON_ASCII_CHARS as NON_ASCII_CHARS
from .filter import PRINTABLE_CHARS as PRINTABLE_CHARS
from .filter import WHITESPACE_CHARS as WHITESPACE_CHARS
from .parser import CSI_SEQ_REGEX as CSI_SEQ_REGEX
from .parser import ESCAPE_SEQ_REGEX as ESCAPE_SEQ_REGEX
from .parser import RCP_REGEX as RCP_REGEX
from .parser import SGR_SEQ_REGEX as SGR_SEQ_REGEX
from .text import SELECT_WORDS_REGEX as SELECT_WORDS_REGEX

# enums:
from .ansi import ColorTarget as ColorTarget
from .filter import Align as Align
from .renderer import OutputMode as OutputMode
from .style import Styles as Styles

# interfaces:
from .ansi import ISequence as ISequence
from .color import IColor as IColor
from .renderer import IRenderer as IRenderer
from .text import IRenderable as IRenderable
from .filter import IFilter as IFilter

# ======================== CORE API =================================

# low level:
from .ansi import SeqIndex as SeqIndex
from .ansi import SequenceSGR as SequenceSGR
from .ansi import make_color_256 as make_color_256
from .ansi import make_color_rgb as make_color_rgb
from .color import Color16 as Color16
from .color import Color256 as Color256
from .color import ColorRGB as ColorRGB
from .color import find_closest as find_closest
from .color import resolve_color as resolve_color
from .filter import SgrStringReplacer as SgrStringReplacer
from .filter import apply_filters as apply_filters
from .parser import parse as parse

# high level:
from .cval import cv as cv
from .cval import cvr as cvr
from .style import Style as Style
from .style import make_style as make_style
from .style import merge_styles as merge_styles
from .template import TemplateEngine as TemplateEngine
from .renderer import SgrRenderer as SgrRenderer
from .text import Fragment as Fragment
from .text import FrozenText as FrozenText
from .text import Text as Text
from .text import echo as echo
from .text import echoi as echoi
from .text import render as render

# ========================== EXTRAS =================================

from .ansi import IntCode as IntCode
from .ansi import SequenceCSI as SequenceCSI
from .ansi import SequenceFe as SequenceFe
from .ansi import SequenceFp as SequenceFp
from .ansi import SequenceFs as SequenceFs
from .ansi import SequenceNf as SequenceNf
from .ansi import SequenceOSC as SequenceOSC
from .ansi import SequenceST as SequenceST
from .ansi import SubtypedParam as SubtypedParam
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
from .ansi import make_disable_alt_screen_buffer as make_disable_alt_screen_buffer
from .ansi import make_enable_alt_screen_buffer as make_enable_alt_screen_buffer
from .ansi import make_erase_in_display as make_erase_in_display
from .ansi import make_erase_in_line as make_erase_in_line
from .ansi import make_hide_cursor as make_hide_cursor
from .ansi import make_move_cursor_down as make_move_cursor_down
from .ansi import make_move_cursor_down_to_start as make_move_cursor_down_to_start
from .ansi import make_move_cursor_left as make_move_cursor_left
from .ansi import make_move_cursor_right as make_move_cursor_right
from .ansi import make_move_cursor_up as make_move_cursor_up
from .ansi import make_move_cursor_up_to_start as make_move_cursor_up_to_start
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
from .ansi import seq_from_dict as seq_from_dict

from .color import ApxResult as ApxResult
from .color import approximate as approximate

from .config import Config as Config
from .config import get_config as get_config
from .config import replace_config as replace_config

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
from .filter import StringAligner as StringAligner
from .filter import StringLinearizer as StringLinearizer
from .filter import StringMapper as StringMapper
from .filter import StringReplacer as StringReplacer
from .filter import StringTracer as StringTracer
from .filter import StringUcpTracer as StringUcpTracer
from .filter import TracerExtra as TracerExtra
from .filter import WhitespaceRemover as WhitespaceRemover
from .filter import center_sgr as center_sgr
from .filter import dump as dump
from .filter import get_max_ucs_chars_cp_length as get_max_ucs_chars_cp_length
from .filter import get_max_utf8_bytes_char_length as get_max_utf8_bytes_char_length
from .filter import ljust_sgr as ljust_sgr
from .filter import pad as pad
from .filter import padv as padv
from .filter import rjust_sgr as rjust_sgr

from .numfmt import BaseUnit as BaseUnit
from .numfmt import DualBaseUnit as DualBaseUnit
from .numfmt import DualFormatter as DualFormatter
from .numfmt import DynamicFormatter as DynamicFormatter
from .numfmt import Highlighter as Highlighter
from .numfmt import NumFormatter as NumFormatter
from .numfmt import StaticFormatter as StaticFormatter
from .numfmt import SupportsFallback as SupportsFallback
from .numfmt import dual_registry as dual_registry
from .numfmt import format_auto_float as format_auto_float
from .numfmt import format_bytes_human as format_bytes_human
from .numfmt import format_si as format_si
from .numfmt import format_si_binary as format_si_binary
from .numfmt import format_thousand_sep as format_thousand_sep
from .numfmt import format_time as format_time
from .numfmt import format_time_delta as format_time_delta
from .numfmt import format_time_delta_longest as format_time_delta_longest
from .numfmt import format_time_delta_shortest as format_time_delta_shortest
from .numfmt import format_time_ms as format_time_ms
from .numfmt import format_time_ns as format_time_ns
from .numfmt import formatter_bytes_human as formatter_bytes_human
from .numfmt import formatter_si as formatter_si
from .numfmt import formatter_si_binary as formatter_si_binary
from .numfmt import formatter_time as formatter_time
from .numfmt import formatter_time_ms as formatter_time_ms
from .numfmt import highlight as highlight

from .parser import contains_sgr as contains_sgr
from .parser import decompose_report_cursor_position as decompose_report_cursor_position

from .renderer import HtmlRenderer as HtmlRenderer
from .renderer import NoOpRenderer as NoOpRenderer
from .renderer import RendererManager as RendererManager
from .renderer import SgrDebugger as SgrDebugger
from .renderer import TemplateRenderer as TemplateRenderer
from .renderer import TmuxRenderer as TmuxRenderer

from .term import confirm as confirm
from .term import get_char_width as get_char_width
from .term import get_preferable_wrap_width as get_preferable_wrap_width
from .term import get_terminal_width as get_terminal_width
from .term import guess_char_width as guess_char_width
from .term import measure_char_width as measure_char_width
from .term import wait_key as wait_key

from .text import Composite as Composite
from .text import SimpleTable as SimpleTable
from .text import as_fragments as as_fragments
from .text import distribute_padded as distribute_padded
from .text import flatten1 as flatten1
from .text import apply_style_selective as apply_style_selective
from .text import apply_style_words_selective as apply_style_words_selective
from .text import wrap_sgr as wrap_sgr

# ======================= INITIALIZATION ============================

from .config import init_config as init_config
from .renderer import init_renderer as init_renderer

init_config()
init_renderer()
