# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022. A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
from .color import Color, ColorRGB, ColorIndexed, ColorDefault, Colors
from .ansi import IntCodes, build, color_indexed, color_rgb, SequenceSGR, Seqs, Span, Spans
from .render import Style, Text
from ._version import __version__

import logging
from logging import NullHandler

logging.getLogger(__name__).addHandler(NullHandler())
