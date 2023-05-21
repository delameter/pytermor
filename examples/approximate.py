#!/bin/env python3
# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under GNU Lesser General Public License v3.0
# -----------------------------------------------------------------------------

from __future__ import annotations

import random
import re
import sys
import typing as t

import pytermor as pt
import pytermor.conv
from pytermor import StaticFormatter, HSV


class Main:
    def __init__(self, *argv: t.List):
        Approximator(argv or []).run()


class Approximator:
    def __init__(self, argv: t.List):
        self.usage = [
            f"  venv/bin/python {sys.argv[0]} [-e] [COLOR]...",
            "",
            "Option -e|--extended increases approximation results amount.",
            "",
        ]
        self.input_values = []
        self._extended_mode = False

        for arg in argv:
            try:
                if arg.startswith("-"):
                    if arg == "-e" or arg == "--extended":
                        self._extended_mode = True
                        continue
                    raise ValueError(f"Invalid option {arg}")

                for argcolor in [arg, "#"+arg]:
                    try:
                        if input_color := pt.resolve_color(argcolor):
                            break
                    except LookupError:
                        pass
                else:
                    raise ValueError(f"Failed to resolve: '{arg}'")
                self.input_values.append(input_color)

            except ValueError as e:
                if len(argv) > 1:
                    pt.echo(f"WARNING: {e}", pt.Styles.WARNING)
                    continue
                pt.echo("USAGE:")
                pt.echo(
                    [
                        *self.usage,
                        r"Allowed COLOR format: '#?[\da-f]{6}', "
                        "i.e. a hexadecimal integer from the range [0; 0xFFFFFF], "
                        "optionally prefixed with '#'; "
                        "or a name from named colors list.",
                    ],
                    wrap=True,
                )
                raise e

    def run(self):
        if len(self.input_values) == 0:
            self._run(None, "Random")
        else:
            for sample_value in self.input_values:
                self._run(sample_value, "Input")

        if len(self.input_values) > 0 or self._extended_mode:
            return

        def fmt_arg_examples(*s: str) -> pt.Text:
            text = pt.Text()
            for w in s:
                text.append(pt.Fragment(w, pt.Style(bold=True, underlined=True)))
            text.split(re.compile("([^ _]+)([ _]+|$)"))
            return text

        pt.echo(
            [
                pt.render("Note: In this example the library assumes that your terminal supports "
                "all color modes including 256-color and True Color, and forces "
                "the renderer to act accordingly. If that's not the case, weird "
                "results may (and will) happen. Run 'examples/terminal_color_mode.py' "
                "for the details.", pt.cv.GRAY_30),
                "",
                "Basic usage:",
                *self.usage,
                "You can specify any amount of colors as arguments, and they will be "
                "approximated instead of the default (random) one. Required format is "
                "a string 1-6 characters long representing an integer(s) in a hexadecimal "
                "form: 'FFFFFF' (case insensitive), or a name of the color in any format:",
                "",
                f"  venv/bin/python {sys.argv[0]} " + fmt_arg_examples("3AEBA1 0bceeb 666"),
                f"  venv/bin/python {sys.argv[0]} " + fmt_arg_examples("red DARK_RED icathian-yellow"),
            ],
            wrap=True,
            indent_first=2,
        )

    def _run(self, sample: pt.ColorRGB | None, color_type: str):
        if sample is None:
            random_rgb = (random.randint(40, 255) for _ in range(3))
            sample = pt.resolve_color(pytermor.conv.rgb_to_hex(*random_rgb))

        direct_renderer = pt.SgrRenderer(pt.OutputMode.TRUE_COLOR)
        formatter = StaticFormatter(max_value_len=3, allow_negative=False)

        pt.echo()
        pt.echo(f'  {color_type+" color:":<15s}', nl=False)
        box = pt.render("  ", pt.Style(bg=sample), direct_renderer)
        pt.echo(box, nl=False)
        pt.echo(f" {sample.format_value(prefix='')} ", pt.Style(bg=0x0), nl=False)
        pt.echo("\n\n ", nl=False)

        results = []
        descriptions = [
            "No approximation (as input)",
            "%s color in named colors list (pytermor)",
            "%s color in xterm-256 index",
            "%s color in xterm-16 index",
        ]

        for idx, om in enumerate([pt.OutputMode.TRUE_COLOR, *reversed(pt.OutputMode)]):
            if om in [pt.OutputMode.AUTO, pt.OutputMode.NO_ANSI]:
                continue
            renderer = pt.SgrRenderer(om)
            if self._extended_mode or idx == 0:
                results.append((None, '│', None, None, None))

            approx_results = []
            if (upper_bound := renderer._COLOR_UPPER_BOUNDS.get(om, None)):
                approx_results = upper_bound.approximate(sample.hex_value, 4 if idx > 0 else 1)

            if not self._extended_mode:
                approx_results = approx_results[0:1]

            for aix, approx_result in enumerate(approx_results):
                sample_approx = approx_result.color
                dist = approx_result.distance_real
                if idx == 0:
                    sample_approx = sample
                    dist = 0.0
                style = pt.Style(bg=sample_approx).autopick_fg()

                dist_str = "0.0" if not dist else formatter.format(dist)
                code, value, name = re.search(r'(?i)(\w\d{1,3}|)?[ (]*(#[\da-h]{1,6}\??)[ (]*([^)]*)\)?', sample_approx.repr_attrs(True)).groups()
                sample_approx_str = '%4s %-8s %s' % (code or '--', value, name or '--')
                def print_hsv(hsv: HSV) -> str:
                    attrs = [
                        f"{hsv.hue:>3.0f}°",
                        f"{100*hsv.saturation:>3.0f}%",
                        f"{100*hsv.value:>3.0f}%",
                    ]
                    return ' '.join(attrs)
                string1 = f"{dist_str:>4s} │ {print_hsv(sample_approx.to_hsv()):>11s} "
                string2 = f" {sample_approx_str}  "
                desc = descriptions[0]
                if not self._extended_mode:
                    desc = desc % "Closest" if "%s" in desc else desc
                else:
                    if aix > 0:
                        desc = "%s"
                    desc = desc % f"#{aix+1} closest" if "%s" in desc else desc
                results.append((string1, string2, style, renderer, desc))
            descriptions.pop(0)

        prim_len1 = max(len(s[0]) for s in results if s[0])
        prim_len2 = max(len(s[1]) for s in results if s[1])
        header = " Δ".center(4)+ " │  " + " H    S    V  ".center(11) + "│ " + "Code  Value   Name"
        pt.echo(header.ljust(prim_len1+prim_len2 + 2))

        for string1, string2, style, renderer, desc in results:
            if not string1:
                pt.echo(' ', nl=False)
                pt.echo(f"     {string2}                {string2}" + ''.ljust(prim_len2+1), pt.Style(crosslined=True))
                continue
            pt.echo(" ", nl=False)
            pt.echo(f"{string1:<{prim_len1}s}│", nl=False)
            pt.echo(f"{string2:<{prim_len2}s} ", style, renderer, nl=False)
            pt.echo("  " + desc, pt.Style(fg="gray"))

        pt.echo()


if __name__ == "__main__":
    try:
        Main(*sys.argv[1:])
    except Exception as e:
        pt.echo(f"[ERROR] {type(e).__qualname__}: {e}\n", fmt=pt.Styles.ERROR)
        # raise e
