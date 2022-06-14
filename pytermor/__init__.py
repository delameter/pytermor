# -----------------------------------------------------------------------------
# pytermor [ANSI formatted terminal output toolset]
# (C) 2022 A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
from .color import Color, ColorRGB, ColorIndexed, ColorDefault
from .sequence import build, color_indexed, color_rgb
from .span import Span
from .style import Style
from ._version import __version__
