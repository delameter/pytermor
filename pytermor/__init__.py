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
from .border import BORDER_ASCII_DOUBLE as BORDER_ASCII_DOUBLE
from .border import BORDER_ASCII_SINGLE as BORDER_ASCII_SINGLE
from .border import BORDER_DOTTED_COMPACT as BORDER_DOTTED_COMPACT
from .border import BORDER_DOTTED_DOUBLE as BORDER_DOTTED_DOUBLE
from .border import BORDER_DOTTED_DOUBLE_SEMI as BORDER_DOTTED_DOUBLE_SEMI
from .border import BORDER_DOTTED_REGULAR as BORDER_DOTTED_REGULAR
from .border import BORDER_LINE_BOLD as BORDER_LINE_BOLD
from .border import BORDER_LINE_DASHED as BORDER_LINE_DASHED
from .border import BORDER_LINE_DASHED_2 as BORDER_LINE_DASHED_2
from .border import BORDER_LINE_DASHED_3 as BORDER_LINE_DASHED_3
from .border import BORDER_LINE_DASHED_BOLD as BORDER_LINE_DASHED_BOLD
from .border import BORDER_LINE_DASHED_BOLD_2 as BORDER_LINE_DASHED_BOLD_2
from .border import BORDER_LINE_DASHED_BOLD_3 as BORDER_LINE_DASHED_BOLD_3
from .border import BORDER_LINE_DOUBLE as BORDER_LINE_DOUBLE
from .border import BORDER_LINE_SINGLE as BORDER_LINE_SINGLE
from .border import BORDER_LINE_SINGLE_ROUND as BORDER_LINE_SINGLE_ROUND
from .border import BORDER_SOLID_12_COMPACT as BORDER_SOLID_12_COMPACT
from .border import BORDER_SOLID_12_DIAGONAL as BORDER_SOLID_12_DIAGONAL
from .border import BORDER_SOLID_12_EXTENDED as BORDER_SOLID_12_EXTENDED
from .border import BORDER_SOLID_12_REGULAR as BORDER_SOLID_12_REGULAR
from .border import BORDER_SOLID_18_COMPACT as BORDER_SOLID_18_COMPACT
from .border import BORDER_SOLID_18_DIAGONAL as BORDER_SOLID_18_DIAGONAL
from .border import BORDER_SOLID_18_REGULAR as BORDER_SOLID_18_REGULAR
from .border import BORDER_SOLID_FULL as BORDER_SOLID_FULL
from .border import Border as Border
from .color import ApxResult as ApxResult
from .color import Color as Color
from .color import Color16 as Color16
from .color import Color256 as Color256
from .color import ColorRGB as ColorRGB
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
from .common import CDT as CDT
from .common import CXT as CXT
from .common import ExtendedEnum as ExtendedEnum
from .common import FT as FT
from .common import OVERFLOW_CHAR as OVERFLOW_CHAR
from .common import RT as RT
from .common import but as but
from .common import char_range as char_range
from .common import chunk as chunk
from .common import cut as cut
from .common import filterf as filterf
from .common import filterfv as filterfv
from .common import filtern as filtern
from .common import filternv as filternv
from .common import fit as fit
from .common import flatten as flatten
from .common import flatten1 as flatten1
from .common import get_qname as get_qname
from .common import get_subclasses as get_subclasses
from .common import isiterable as isiterable
from .common import only as only
from .common import others as others
from .common import ours as ours
from .common import pad as pad
from .common import padv as padv
from .config import Config as Config
from .cval import cv as cv
from .cval import cvr as cvr
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
from .renderer import NoOpRenderer as NoOpRenderer
from .renderer import OutputMode as OutputMode
from .renderer import SgrDebugger as SgrDebugger
from .renderer import SgrRenderer as SgrRenderer
from .renderer import TmuxRenderer as TmuxRenderer
from .renderer import force_ansi_rendering as force_ansi_rendering
from .renderer import force_no_ansi_rendering as force_no_ansi_rendering
from .style import FrozenStyle as FrozenStyle
from .style import MergeMode as MergeMode
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
from .config import ConfigManager as ConfigManager
from .renderer import RendererManager as RendererManager

getLogger(__package__).addHandler(NullHandler())  # discard all logs by default
ConfigManager.set_default()
RendererManager.set_default()

"""
# - 8< - - - - - - - - - in your project: - - - - - - - - - - - - - -

fmt = '[%(levelname)5.5s][%(name)s.%(module)s] %(message)s'
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
handler.setFormatter(logging.Formatter(fmt))
logger = logging.getLogger('pytermor')
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - >8-
"""
