# -----------------------------------------------------------------------------
# pytermor [ANSI formatted terminal output toolset]
# (C) 2022 A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
from .intcode import *
from .sequence import build, color_indexed, color_rgb, SequenceSGR
from .span import autocomplete, Span
from ._version import __version__
