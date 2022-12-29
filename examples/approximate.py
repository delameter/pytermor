#!/bin/env python3
# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022. A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------

from __future__ import annotations
import re
import random
import sys
import typing


import pytermor as pt


class Main:
    def __init__(self, argv: typing.List):
        usage = [
            f"  python {sys.argv[0]} [-e] [COLOR]...",
            "",
            "Option -e|--extended enables more approximation details.",
        ]
        input_values = []
        self._extended_mode = False

        for arg in argv:
            try:
                if arg.startswith("-"):
                    if arg == "-e" or arg == "--extended":
                        self._extended_mode = True
                        continue
                    raise ValueError(f"Invalid option {arg}")

                try:
                    input_color = pt.resolve(f"#{arg}")
                except LookupError:
                    raise ValueError(f"Argument is not valid RGB value: 0x{arg}")
                input_values.append(input_color)
            except ValueError as e:
                pt.echo("USAGE:")
                pt.echo(
                    [
                        *usage,
                        "Expected COLOR format: '(0x)?[\da-f]{6}', i.e. a hexadecimal "
                        "integer X, where 0 <= X <= 0xFFFFFF.",
                    ],
                    wrap=True,
                )
                raise e

        if len(input_values) == 0:
            self.run(None, "Random")
        else:
            for sample_value in input_values:
                self.run(sample_value, "Input")

        if len(input_values) > 0 or self._extended_mode:
            return

        pt.echo(
            [
                "In this example the library assumes that your terminal supports "
                "all color modes including 256-color and True Color, and forces "
                "the renderer to act accordingly. If that's not the case, weird "
                "results may (and will) happen. Run 'examples/terminal_color_mode.py' "
                "for the details.",
                "",
                "Basic usage:",
                *usage,
                "You can specify any amount of colors as arguments, and they will be "
                "approximated instead of the default (random) one. Required format is "
                "a string 1-6 characters long representing an integer(s) in a hexadecimal "
                "form: 'FFFFFF' (case insensitive):",
                "",
                f"  python {sys.argv[0]} 3AEBA1 0bceeb 666",
            ],
            wrap=True,
            indent_first=2,
        )

    def run(self, sample: pt.ColorRGB | None, color_type: str):
        if sample is None:
            random_rgb = (random.randint(40, 255) for _ in range(3))
            sample = pt.resolve(pt.color.rgb_to_hex(*random_rgb))

        direct_renderer = pt.SgrRenderer(pt.OutputMode.TRUE_COLOR)

        pt.echo()
        pt.echo(f'  {color_type+" color:":<15s}', nl=False)
        pt.echo("  ", pt.Style(bg=sample), direct_renderer, nl=False)
        pt.echo(f" {sample.format_value()} ", pt.Style(bg=0x0), nl=False)
        pt.echo("\n\n ", nl=False)

        if self._extended_mode:
            self.run_extended(sample)
        else:
            self.run_default(sample)
        pt.echo()

    def run_default(self, sample: pt.ColorRGB):
        results = []
        descriptions = [
            "No approximation (direct output)",
            "Closest color in named colors list (pytermor)",
            "Closest color in xterm-256 index",
            "Closest color in xterm-16 index",
            "SGR formatting disabled",
        ]

        for idx, om in enumerate([pt.OutputMode.TRUE_COLOR, *reversed(pt.OutputMode)]):
            if om == pt.OutputMode.AUTO:
                continue
            renderer = pt.SgrRenderer(om)
            style = pt.NOOP_STYLE

            sample_approx = pt.NOOP_COLOR
            dist = None
            if upper_bound := renderer._COLOR_UPPER_BOUNDS.get(om, None):
                approx_results = upper_bound.approximate(sample.hex_value, 1)
                closest = approx_results[0]
                sample_approx = closest.color
                dist = closest.distance_real
                if idx == 0:
                    sample_approx = sample
                    dist = 0.0
                style = pt.Style(bg=sample_approx).autopick_fg()
            dist_str = "--" if dist is None else f"{dist:.1f}"
            sample_approx_str = re.sub(
                "<(Color)?|>|(,)",
                lambda m: " " if m.group() else "",
                repr(sample_approx),
            )
            sample_approx_str = re.sub(r"^(\s*16)", r" \1", sample_approx_str)
            string = f" {om.name:<10s} {dist_str:>6s}  {sample_approx_str}"
            results.append((string, style, renderer))

        prim_len = max(len(s[0]) for s in results)
        header = " Mode".ljust(12) + " Δ".center(7) + "  " + "Approximated color"
        pt.echo(header.ljust(prim_len + 1), pt.Style(underlined=True))

        for string, style, renderer in results:
            pt.echo(" ", nl=False)
            pt.echo(f"{string:<{prim_len}s} ", style, renderer, nl=False)
            pt.echo("  " + descriptions.pop(0), pt.Style(fg="gray"))

    def run_extended(self, sample: pt.ColorRGB):
        raise NotImplementedError("@TODO")


if __name__ == "__main__":
    try:
        Main(sys.argv[1:])
    except Exception as e:
        pt.echo(f"[ERROR] {type(e).__qualname__}: {e}\n", fmt=pt.Styles.ERROR)
        raise e
