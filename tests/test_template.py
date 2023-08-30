# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under GNU Lesser General Public License v3.0
# -----------------------------------------------------------------------------
from __future__ import annotations

import pytest

from pytermor import (
    LogicError,
    OutputMode,
    TemplateEngine, RendererManager,
)
from tests import format_test_params


class TestTemplate:
    def setup_class(self):
        self._tpleng = TemplateEngine()

    @pytest.mark.parametrize(
        "tpl, exp",
        [
            (
                "@s1:[fg=green bold] ?s1:[fg=red] :[s1]GnB:[-s1]",
                "  " "\x1b[1;32m" "GnB" "\x1b[22;39m",
            ),
            (
                "@s2:[fg=green bold] !s2:[fg=red] :[s2]RB:[-s2]",
                "  " "\x1b[1;31m" "RB" "\x1b[22;39m",
            ),
            (
                "@s3:[fg=green bold] @s3:[fg=red] :[s3]R:[-s3]",
                "  " "\x1b[31m" "R" "\x1b[39m",
            ),
            (":[fg=blue] Be :[-]", "" "\x1b[34m" " Be " "\x1b[39m"),
            (":[bg=red]:[bg=blue] Be :[-]", "" "\x1b[44m" " Be " "\x1b[49m"),
            (":[^]", "\x1b[1;1H"),
            (":[bg=red]:[^]R:[-]0", "\x1b[1;1H" "\x1b[41m" "R" "\x1b[49m" "0"),
            (":[<<]", "\x1b[1J"),
            (":[<]", "\x1b[1K"),
            (":[<>]", "\x1b[2K"),
            (":[<<>>]", "\x1b[2J"),
            (":[>]", "\x1b[0K"),
            (":[>>]", "\x1b[0J"),
            (
                "@s4:[bold] :[s4 fg=red]IV:[-]",
                " " "\x1b[1;31m" "IV" "\x1b[22;39m",
            ),
            (
                ":[|underlined]12 34 56:[-]",
                "\x1b[4m12\x1b[24m \x1b[4m34\x1b[24m \x1b[4m56\x1b[24m",
            ),
            (
                ":[underline_color=gray50]1234:[-]",
                "\x1b[58;5;244m1234\x1b[59m",
            ),
            (
                ":[,overlined]12,34, 56:[-]",
                "\x1b[53m12\x1b[55m,\x1b[53m34\x1b[55m, \x1b[53m56\x1b[55m",
            ),
            (":[+inversed]I:[-inversed]", "\x1b[7mI\x1b[27m"),
            (
                ":[fg=red bg=blue]RB:[-fg=red bg=blue]0",
                "\x1b[31;44m" "RB" "\x1b[39;49m" "0",
            ),
            pytest.param(
                ":[fg=red bg=blue]RB:[-fg=red]0",
                "",
                marks=pytest.mark.xfail(raises=LogicError),
            ),
            (
                ":[fg=red]:[bg=blue]RB:[-]R:[-]0",
                "\x1b[31;44m" "RB" "\x1b[39;49m" "\x1b[31m" "R" "\x1b[39m" "0",
            ),
            (":[fg=red bg=blue]RB:[-]0", "\x1b[31;44m" "RB" "\x1b[39;49m" "0"),
            (":[fg=red bg=blue]RB:[$]0", "\x1b[31;44m" "RB" "\x1b[39;49m" "\x1b[0m" "0"),
            (
                ":[fg=air-superiority-blue]A:[-]0",
                "\x1b[38;2;114;160;193m" "A" "\x1b[39m" "0",
            ),
            (
                ":[air-superiority-blue]A:[-]0",
                "\x1b[38;2;114;160;193m" "A" "\x1b[39m" "0",
            ),
            (
                ":[bg=#003366]A:[-]0",
                "\x1b[48;2;0;51;102m" "A" "\x1b[49m" "0",
            ),
            pytest.param(
                ":[fg=non-existing]A:[-]0",
                "",
                marks=pytest.mark.xfail(raises=LookupError),
            ),
            pytest.param(
                ":[non-existing]A:[-]0",
                "",
                marks=pytest.mark.xfail(raises=ValueError),
            ),
            pytest.param(
                "@s1:[red] @s2:[blue] :[s1 s2]A:[-]0",
                "",
                marks=pytest.mark.xfail(raises=LogicError),
            ),
            ("@s1:[] :[s1]0 :[]0 ", " 0 0 "),
            (" :[fg=red  ]0:[-] ", " " "\x1b[31m" "0" "\x1b[39m" " "),
            (
                ":[fg=red]R:[fg=blue]B:[$]0:[-]0",
                "\x1b[31m" "R" "\x1b[39m" "\x1b[34m" "B" "\x1b[39m" "\x1b[0m" "00",
            ),
        ],
        ids=format_test_params,
    )
    @pytest.mark.setup(force_output_mode=OutputMode.TRUE_COLOR)
    def test_render(self, tpl: str, exp: str):
        self._tpleng.reset()
        assert self._tpleng.render(tpl, RendererManager.get_default()) == exp
