# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022. A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------

from __future__ import annotations
import random
import sys
import typing


import pytermor as pt


class Main:
    WIDTH = 100

    def __init__(self, argv: typing.List):
        sample_values = []
        for arg in argv:
            try:
                val = int(arg, 16)
                if not 0 <= val < 16777216:
                    raise ValueError(f"Argument is not valid RGB value: 0x{val:X}")
                sample_values.append(val)
            except ValueError as e:
                raise ValueError(
                    f"{e}\n" + "Expected argument format: '[0-9a-f]{1,6}', i.e. a "
                    "hexadecimal integer X, where 0 <= X <= 0xFFFFFF."
                ) from e

        if len(sample_values) == 0:
            random_rgb = (random.randint(40, 255) for _ in range(3))
            self.run(pt.Color.rgb_to_hex(*random_rgb), "Random")
        else:
            for sample_value in sample_values:
                self.run(sample_value, "Argument")
            return

        epilog = (
            "",
            " In this example the library assumes that your terminal supports all color "
            "modes including 256-color and True Color, and forces the renderer to act "
            "accordingly. If that's not the case, weird results may (and will) happen. "
            "Run 'examples/terminal_color_mode.py' for the details.",
            "",
            " You can specify any amount of colors as arguments to this program, and "
            "they will be approximated instead of the default random one. Required "
            "format is a string 1-6 characters long representing an integer(s) in a "
            "hexadecimal form: 'FFFFFF' (case insensitive):"
            "",
            "",
            f"  {sys.argv[0]} 3AEBA1 0bceaa 6",
        )
        pt.echo(epilog, wrap=True)

    def run(self, sample_val: int, color_type: str):
        sample = pt.ColorRGB(sample_val)

        results = []
        descriptions = [
            "No approximation (direct output)",
            "Closest color in pytermor Named RGB list",
            "Closest color in xterm-256 Index table",
            "Closest color in xterm-16 Index table",
            "SGR formatting disabled",
        ]

        for idx, om in enumerate([pt.OutputMode.TRUE_COLOR, *reversed(pt.OutputMode)]):
            if om == pt.OutputMode.AUTO:
                continue
            renderer = pt.SgrRenderer(om)
            style = pt.NOOP_STYLE

            sample_approx = pt.NOOP_COLOR
            if upper_bound := renderer._COLOR_UPPER_BOUNDS.get(om, None):
                sample_approx = upper_bound.find_closest(sample.hex_value)
                if idx == 0:
                    sample_approx = sample
                style = pt.Style(bg=sample_approx).autopick_fg()
            string = f" {om.name:<10s} -> {sample_approx}"
            results.append((string, style, renderer))

        prim_len = max(len(s[0]) for s in results)
        direct_renderer = pt.SgrRenderer(pt.OutputMode.TRUE_COLOR)

        pt.echo()
        pt.echo(f'  {color_type+" color:":<14s}  ', nl=False)
        pt.echo("  ", pt.Style(bg=sample), direct_renderer, nl=False)
        pt.echo(f" {sample.format_value()}\n\n ", nl=False)
        header = (" Output mode".ljust(15) + " Approximated color").ljust(prim_len + 1)
        pt.echo(header, pt.Style(underlined=True))

        for string, style, renderer in results:
            pt.echo(" ", nl=False)
            pt.echo(f"{string:<{prim_len}s} ", style, renderer, nl=False)
            pt.echo("  " + descriptions.pop(0), pt.Style(fg="gray"))

        pt.echo()


if __name__ == "__main__":
    try:
        Main(sys.argv[1:])
    except Exception as e:
        pt.echo(str(e), style=pt.Styles.ERROR)
