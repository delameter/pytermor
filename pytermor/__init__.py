# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under GNU Lesser General Public License v3.0
# -----------------------------------------------------------------------------
from __future__ import annotations

from ._version import __updated__ as __updated__
from ._version import __version__ as __version__
from .ansi import ALL_COLORS as ALL_COLORS
from .ansi import BG_COLORS as BG_COLORS
from .ansi import BG_HI_COLORS as BG_HI_COLORS
from .ansi import COLORS as COLORS
from .ansi import ColorTarget as ColorTarget
from .ansi import ESCAPE_SEQ_REGEX as ESCAPE_SEQ_REGEX
from .ansi import HI_COLORS as HI_COLORS
from .ansi import ISequence as ISequence
from .ansi import IntCode as IntCode
from .ansi import NOOP_SEQ as NOOP_SEQ
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
from .ansi import contains_sgr as contains_sgr
from .ansi import enclose as enclose
from .ansi import get_closing_seq as get_closing_seq
from .ansi import get_resetter_codes as get_resetter_codes
from .ansi import parse as parse
from .ansi import seq_from_dict as seq_from_dict
from .border import ASCII_DOTTED as ASCII_DOTTED
from .border import ASCII_DOUBLE as ASCII_DOUBLE
from .border import ASCII_SINGLE as ASCII_SINGLE
from .border import BLOCK_DOTTED_COMPACT as BLOCK_DOTTED_COMPACT
from .border import BLOCK_DOTTED_REGULAR as BLOCK_DOTTED_REGULAR
from .border import BLOCK_DOTTED_UNIFORM_LB as BLOCK_DOTTED_UNIFORM_LB
from .border import BLOCK_DOTTED_UNIFORM_LT as BLOCK_DOTTED_UNIFORM_LT
from .border import BLOCK_DOTTED_UNIFORM_RB as BLOCK_DOTTED_UNIFORM_RB
from .border import BLOCK_DOTTED_UNIFORM_RT as BLOCK_DOTTED_UNIFORM_RT
from .border import BLOCK_FULL as BLOCK_FULL
from .border import BLOCK_THICK as BLOCK_THICK
from .border import BLOCK_THICK_INNER as BLOCK_THICK_INNER
from .border import BLOCK_THICK_ROUNDED as BLOCK_THICK_ROUNDED
from .border import BLOCK_THIN as BLOCK_THIN
from .border import BLOCK_THIN_INNER as BLOCK_THIN_INNER
from .border import BLOCK_THIN_ROUNDED as BLOCK_THIN_ROUNDED
from .border import Border as Border
from .border import DOTS as DOTS
from .border import DOTS_HEAVY as DOTS_HEAVY
from .border import DOTS_INNER as DOTS_INNER
from .border import DOTS_LIGHT as DOTS_LIGHT
from .border import DOTS_ROUNDED as DOTS_ROUNDED
from .border import LINE_BOLD as LINE_BOLD
from .border import LINE_DASHED as LINE_DASHED
from .border import LINE_DASHED_2 as LINE_DASHED_2
from .border import LINE_DASHED_3 as LINE_DASHED_3
from .border import LINE_DASHED_BOLD as LINE_DASHED_BOLD
from .border import LINE_DASHED_BOLD_2 as LINE_DASHED_BOLD_2
from .border import LINE_DASHED_BOLD_3 as LINE_DASHED_BOLD_3
from .border import LINE_DASHED_HALF as LINE_DASHED_HALF
from .border import LINE_DASHED_HALF_BOLD as LINE_DASHED_HALF_BOLD
from .border import LINE_DOUBLE as LINE_DOUBLE
from .border import LINE_ROUNDED as LINE_ROUNDED
from .border import LINE_SINGLE as LINE_SINGLE
from .color import ApxResult as ApxResult
from .color import Color as Color
from .color import Color16 as Color16
from .color import Color256 as Color256
from .color import ColorRGB as ColorRGB
from .color import CDT as CDT
from .color import DEFAULT_COLOR as DEFAULT_COLOR
from .color import DefaultColor as DefaultColor
from .color import DynamicColor as DynamicColor
from .color import ExtractorT as ExtractorT
from .color import HSV as HSV
from .color import IColorValue as IColorValue
from .color import LAB as LAB
from .color import NOOP_COLOR as NOOP_COLOR
from .color import NoopColor as NoopColor
from .color import RGB as RGB
from .color import RealColor as RealColor
from .color import RenderColor as RenderColor
from .color import ResolvableColor as ResolvableColor
from .color import XYZ as XYZ
from .color import approximate as approximate
from .color import find_closest as find_closest
from .color import resolve_color as resolve_color
from .common import Align as Align
from .common import CacheStats as CacheStats
from .common import ExtendedEnum as ExtendedEnum
from .common import OVERFLOW_CHAR as OVERFLOW_CHAR
from .common import but as but
from .common import char_range as char_range
from .common import chunk as chunk
from .common import coale as coale
from .common import coalf as coalf
from .common import coaln as coaln
from .common import cut as cut
from .common import filtere as filtere
from .common import filterev as filterev
from .common import filterf as filterf
from .common import filterfv as filterfv
from .common import filtern as filtern
from .common import filternv as filternv
from .common import fit as fit
from .common import flatten as flatten
from .common import flatten1 as flatten1
from .common import flip_unpack as flip_unpack
from .common import get_qname as get_qname
from .common import get_subclasses as get_subclasses
from .common import instantiate as instantiate
from .common import isimmutable as isimmutable
from .common import isiterable as isiterable
from .common import ismutable as ismutable
from .common import joine as joine
from .common import joinf as joinf
from .common import joinn as joinn
from .common import only as only
from .common import others as others
from .common import ours as ours
from .common import pad as pad
from .common import padv as padv
from .config import Config as Config
from .config import ConfigManager as ConfigManager
from .config import force_ansi_rendering as force_ansi_rendering
from .config import force_no_ansi_rendering as force_no_ansi_rendering
from .cval import cv as cv
from .cval import cvr as cvr
from .exception import ApproximatorLockedException as ApproximatorLockedException
from .exception import ApproximatorUnlockedException as ApproximatorUnlockedException
from .exception import ArgCountError as ArgCountError
from .exception import ArgTypeError as ArgTypeError
from .exception import ColorCodeConflictError as ColorCodeConflictError
from .exception import ColorNameConflictError as ColorNameConflictError
from .exception import ConflictError as ConflictError
from .exception import LogicError as LogicError
from .exception import NotInitializedError as NotInitializedError
from .exception import ParseError as ParseError
from .exception import UserAbort as UserAbort
from .exception import UserCancel as UserCancel
from .filter import AbstractNamedGroupsRefilter as AbstractNamedGroupsRefilter
from .filter import AbstractStringTracer as AbstractStringTracer
from .filter import AbstractTracer as AbstractTracer
from .filter import BytesTracer as BytesTracer
from .filter import CONTROL_CHARS as CONTROL_CHARS
from .filter import CSI_SEQ_REGEX as CSI_SEQ_REGEX
from .filter import CsiStringReplacer as CsiStringReplacer
from .filter import ESCAPE_SEQ_REGEX as ESCAPE_SEQ_REGEX
from .filter import EscSeqStringReplacer as EscSeqStringReplacer
from .filter import IFilter as IFilter
from .filter import IRefilter as IRefilter
from .filter import IT as IT
from .filter import MPT as MPT
from .filter import NON_ASCII_CHARS as NON_ASCII_CHARS
from .filter import NonPrintsOmniVisualizer as NonPrintsOmniVisualizer
from .filter import NonPrintsStringVisualizer as NonPrintsStringVisualizer
from .filter import NoopFilter as NoopFilter
from .filter import OT as OT
from .filter import OmniDecoder as OmniDecoder
from .filter import OmniEncoder as OmniEncoder
from .filter import OmniMapper as OmniMapper
from .filter import OmniPadder as OmniPadder
from .filter import OmniSanitizer as OmniSanitizer
from .filter import PRINTABLE_CHARS as PRINTABLE_CHARS
from .filter import PTT as PTT
from .filter import RPT as RPT
from .filter import SGR_SEQ_REGEX as SGR_SEQ_REGEX
from .filter import SgrStringReplacer as SgrStringReplacer
from .filter import StringLinearizer as StringLinearizer
from .filter import StringMapper as StringMapper
from .filter import StringReplacer as StringReplacer
from .filter import StringReplacerChain as StringReplacerChain
from .filter import StringTracer as StringTracer
from .filter import StringUcpTracer as StringUcpTracer
from .filter import TracerExtra as TracerExtra
from .filter import UCS_CHAR_CPS as UCS_CHAR_CPS
from .filter import UTF8_BYTES_CHARS as UTF8_BYTES_CHARS
from .filter import WHITESPACE_CHARS as WHITESPACE_CHARS
from .filter import WhitespaceRemover as WhitespaceRemover
from .filter import apply_filters as apply_filters
from .filter import center_sgr as center_sgr
from .filter import dump as dump
from .filter import get_max_ucs_chars_cp_length as get_max_ucs_chars_cp_length
from .filter import get_max_utf8_bytes_char_length as get_max_utf8_bytes_char_length
from .filter import ljust_sgr as ljust_sgr
from .filter import rjust_sgr as rjust_sgr
from .numfmt import BaseUnit as BaseUnit
from .numfmt import DualBaseUnit as DualBaseUnit
from .numfmt import DualFormatter as DualFormatter
from .numfmt import DualFormatterRegistry as DualFormatterRegistry
from .numfmt import DynamicFormatter as DynamicFormatter
from .numfmt import Highlighter as Highlighter
from .numfmt import NumFormatter as NumFormatter
from .numfmt import PREFIXES_SI_DEC as PREFIXES_SI_DEC
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
from .renderer import HtmlRenderer as HtmlRenderer
from .renderer import IRenderer as IRenderer
from .renderer import NoopRenderer as NoopRenderer
from .renderer import OutputMode as OutputMode
from .renderer import RendererManager as RendererManager
from .renderer import SgrDebugger as SgrDebugger
from .renderer import SgrRenderer as SgrRenderer
from .renderer import TmuxRenderer as TmuxRenderer
from .style import FrozenStyle as FrozenStyle
from .style import MergeMode as MergeMode
from .style import CXT as CXT
from .style import FT as FT
from .style import NOOP_STYLE as NOOP_STYLE
from .style import Style as Style
from .style import Styles as Styles
from .style import is_ft as is_ft
from .style import make_style as make_style
from .style import merge_styles as merge_styles
from .template import TemplateEngine as TemplateEngine
from .template import render as render_template
from .template import substitute as substitute
from .term import RCP_REGEX as RCP_REGEX
from .term import compose_clear_line as compose_clear_line
from .term import compose_clear_line_fill_bg as compose_clear_line_fill_bg
from .term import compose_hyperlink as compose_hyperlink
from .term import confirm as confirm
from .term import decompose_report_cursor_position as decompose_report_cursor_position
from .term import get_char_width as get_char_width
from .term import get_preferable_wrap_width as get_preferable_wrap_width
from .term import get_terminal_width as get_terminal_width
from .term import guess_char_width as guess_char_width
from .term import make_clear_display as make_clear_display
from .term import make_clear_display_after_cursor as make_clear_display_after_cursor
from .term import make_clear_display_before_cursor as make_clear_display_before_cursor
from .term import make_clear_history as make_clear_history
from .term import make_clear_line as make_clear_line
from .term import make_clear_line_after_cursor as make_clear_line_after_cursor
from .term import make_clear_line_before_cursor as make_clear_line_before_cursor
from .term import make_color_256 as make_color_256
from .term import make_color_rgb as make_color_rgb
from .term import make_disable_alt_screen_buffer as make_disable_alt_screen_buffer
from .term import make_enable_alt_screen_buffer as make_enable_alt_screen_buffer
from .term import make_erase_in_display as make_erase_in_display
from .term import make_erase_in_line as make_erase_in_line
from .term import make_hide_cursor as make_hide_cursor
from .term import make_hyperlink as make_hyperlink
from .term import make_move_cursor_down as make_move_cursor_down
from .term import make_move_cursor_down_to_start as make_move_cursor_down_to_start
from .term import make_move_cursor_left as make_move_cursor_left
from .term import make_move_cursor_right as make_move_cursor_right
from .term import make_move_cursor_up as make_move_cursor_up
from .term import make_move_cursor_up_to_start as make_move_cursor_up_to_start
from .term import make_query_cursor_position as make_query_cursor_position
from .term import make_reset_cursor as make_reset_cursor
from .term import make_restore_cursor_position as make_restore_cursor_position
from .term import make_restore_screen as make_restore_screen
from .term import make_save_cursor_position as make_save_cursor_position
from .term import make_save_screen as make_save_screen
from .term import make_set_cursor as make_set_cursor
from .term import make_set_cursor_column as make_set_cursor_column
from .term import make_set_cursor_line as make_set_cursor_line
from .term import make_show_cursor as make_show_cursor
from .term import measure_char_width as measure_char_width
from .term import wait_key as wait_key
from .text import Composite as Composite
from .text import Fragment as Fragment
from .text import FrozenText as FrozenText
from .text import IRenderable as IRenderable
from .text import RT as RT
from .text import SELECT_WORDS_REGEX as SELECT_WORDS_REGEX
from .text import SimpleTable as SimpleTable
from .text import Text as Text
from .text import apply_style_selective as apply_style_selective
from .text import apply_style_words_selective as apply_style_words_selective
from .text import distribute_padded as distribute_padded
from .text import echo as echo
from .text import echoi as echoi
from .text import flatten1 as flatten1
from .text import is_rt as is_rt
from .text import render as render
from .text import wrap_sgr as wrap_sgr


from logging import getLogger, NullHandler

getLogger(__package__).addHandler(NullHandler())  # discard all logs by default
ConfigManager.set()

"""
# example configuration, insert into your project:                    
# -8< - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

import pytermor as pt
import logging

fmt = '[%(levelname)5.5s][%(name)s.%(module)s] %(message)s'
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
handler.setFormatter(logging.Formatter(fmt))
logger = logging.getLogger('pytermor')
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)  # or whatever

pt.ConfigManager.get().renderer_classname = 'SgrRenderer'

# either of:
pt.ConfigManager.get().default_output_mode = pt.OutputMode.XTERM_256
# pt.force_ansi_rendering()
# pt.force_no_ansi_rendering()

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - >8-

"""
