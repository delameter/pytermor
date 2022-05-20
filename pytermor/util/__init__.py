# -----------------------------------------------------------------------------
# pytermor [ANSI formatted terminal output toolset]
# (C) 2022 A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
"""
Utility package for removing some of the boilerplate code when
dealing with escape sequences.
"""
from .string_filter import apply_filters, StringFilter, ReplaceSGR, ReplaceCSI, ReplaceNonAsciiBytes
from .stdlib_ext import ljust_sgr, rjust_aware, center_aware
