# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under GNU Lesser General Public License v3.0
# -----------------------------------------------------------------------------
from __future__ import annotations

import re
import typing as t

import pytest

import pytermor as pt
from pytermor import ArgTypeError
from tests import format_test_params


def words_to_regex(words: t.Iterable[str]) -> t.Pattern:
    if not words:
        return re.compile("^$")
    return re.compile(".*".join(map(re.escape, words)))


class TestArgTypeError:
    # noinspection PyTypeChecker
    @pytest.mark.parametrize(
        "exp_words, fn",
        [
            (["Argument", "string", "render()", "int"], lambda: pt.render(0)),
            (
                ["Argument", "fmt", "make_style()", "FT", "<Style>"],
                lambda: pt.make_style(pt.Style),
            ),
            (
                ["Argument", "arg", "_resolve_color()", "CDT", "IColor", "list"],
                lambda: setattr(pt.Style(), "fg", [None]),
            ),
            (
                ["Argument", "override", "_make_premap()", "MPT", "None", "float"],
                lambda: pt.OmniMapper(14.88),
            ),
            (
                ["Argument", "fallback", "__init__()", "Style", "Color256"],
                lambda: pt.Style(pt.cv.RED_3),
            ),
            (
                ["Argument", "fallback", "__init__()", "Style", "str"],
                lambda: pt.Style("red"),
            ),
        ],
        ids=format_test_params,
    )
    def test_exception(self, exp_words: t.Iterable[str], fn: t.Callable):
        regex = words_to_regex(exp_words)
        with pytest.raises(ArgTypeError, match=regex):
            fn()
