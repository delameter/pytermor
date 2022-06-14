# -----------------------------------------------------------------------------
# pytermor [ANSI formatted terminal output toolset]
# (C) 2022 A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
import doctest
import sys

from pytermor import span, util, style, sequence, renderer

verbose = '-v' in sys.argv

doctest.testmod(renderer, verbose=verbose)
doctest.testmod(sequence, verbose=verbose)
doctest.testmod(span, verbose=verbose)
doctest.testmod(style, verbose=verbose)
doctest.testmod(util.auto_float, verbose=verbose)
doctest.testmod(util.prefixed_unit, verbose=verbose)
doctest.testmod(util.string_filter, verbose=verbose)
doctest.testmod(util.time_delta, verbose=verbose)
