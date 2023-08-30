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
from pytermor import ArgTypeError, Color, CDT, FT, IT, Style, Color256
from pytermor.exception import ArgCountError
from tests import format_test_params


def word_normalize(word: str | type) -> str:
    if isinstance(word, (type, t.TypeVar)):
        return word.__name__
    return word


def words_to_regex(words: t.Iterable[str | type]) -> t.Pattern:
    if not words:
        return re.compile("^$")
    return re.compile(".*".join(map(re.escape, map(word_normalize, words))))


class TestArgTypeError:
    # noinspection PyTypeChecker
    @pytest.mark.parametrize(
        "exp_words, fn",
        [
            (["Argument", "string", "int"], lambda: pt.render(0)),
            (
                ["Argument", "fmt", FT, f"<{word_normalize(Style)}>"],
                lambda: pt.make_style(pt.Style),
            ),
            (
                ["Argument", "arg", CDT, Color, "list"],
                lambda: setattr(pt.Style(), "fg", [None]),
            ),
            (
                ["Argument", "override", "Dict", IT, "None", "float"],
                lambda: pt.OmniMapper(14.88),
            ),
            (
                ["Argument", "fallback", Style, Color256],
                lambda: pt.Style(pt.cv.RED_3),
            ),
            (
                ["Argument", "fallback", Style, "str"],
                lambda: pt.Style("red"),
            ),
        ],
        ids=format_test_params,
    )
    def test_exception(self, exp_words: t.Iterable[str | type], fn: t.Callable):
        regex = words_to_regex(exp_words)
        with pytest.raises(ArgTypeError, match=regex):
            fn()


class TestArgCountError:
    def test(self):
        err = str(ArgCountError(29, 35))
        assert all(num in err for num in ('29', '35'))
