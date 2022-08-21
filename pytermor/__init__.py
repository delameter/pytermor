# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022. A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
from .registry import IntCodes, Colors, Seqs, Spans, Styles
from .color import Color, ColorRGB, ColorIndexed, ColorDefault, NOOP_COLOR
from .ansi import SequenceSGR, Span, NOOP_SEQ, NOOP_SPAN
from .render import Style, Text, SGRRenderer, RendererManager, NOOP_STYLE

from ._version import __version__

import logging
from logging import NullHandler

logging.getLogger(__name__).addHandler(NullHandler())
