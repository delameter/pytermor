#!/bin/env python3
# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under GNU Lesser General Public License v3.0
# -----------------------------------------------------------------------------

from __future__ import annotations

import random
import sys

import pytermor as pt
from pytermor import StaticFormatter
from pytermor.color import *


class Main:
    def __init__(self, *argv: t.List):
        Approximator(argv or []).run()


def _calc_srgb_euclidean_distance(_, value: IColorValue, e: IColorValue) -> ApxResult[Color]:
    r, g, b = value.rgb
    er, eg, eb = e.rgb
    distance_sq: int = (er - r) ** 2 + (eg - g) ** 2 + (eb - b) ** 2
    return ApxResult(e, distance_sq)


def _calc_cie_distance(_, value: IColorValue, e: IColorValue) -> ApxResult[Color]:
    l, a, b = value.lab
    el, ea, eb = e.lab
    distance_sq: int = (el - l) ** 2 + (ea - a) ** 2 + (eb - b) ** 2
    return ApxResult(e, distance_sq)


def _calc_hsv_euclidean_distance(_, value: IColorValue, e: IColorValue) -> ApxResult[Color]:
    h, s, v = value.hsv
    eh, es, ev = e.hsv
    dh = min(abs(eh - h), 360 - abs(eh - h)) / 180.0
    ds = abs(es - s)
    dv = abs(ev - v)
    distance_sq: int = dh**2 + ds**2 + dv**2
    return ApxResult(e, distance_sq)


class Approximator:
    def __init__(self, argv: t.List):
        self.usage = [
            f"  venv/bin/python {sys.argv[0]} [-e[e…]] [-R|-H] [COLOR]...",
            "",
            "Option -e|--extended increases approximation results amount (can be "
            "used multiple times).",
            "",
            "Options -R and -H select different color difference computation algorithm "
            "(which are less accurate and are kept for demonstration only).",
            "",
        ]
        self.input_values = []
        self._extended_mode = 0
        self._delta_name = "ΔE*"  # noqa
        self._space_override = None

        for arg in argv:
            try:
                if arg.startswith("-"):
                    if arg == "-H":
                        self._space_override = HSV
                        self._delta_name = "Δₕ "
                        continue
                    if arg == "-R":
                        self._space_override = RGB
                        self._delta_name = "Δᵣ "
                        continue
                    if m := re.fullmatch("-?-(e(?:xtended)?|e+)", arg):
                        self._extended_mode = len(m.group(1))
                        continue
                    raise ValueError(f"Invalid option {arg}")

                for argcolor in [arg, "#" + arg]:
                    try:
                        if input_color := resolve_color(argcolor):
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

        if len(self.input_values) > 0 or self._extended_mode or self._space_override:
            return

        def fmt_arg_examples(*s: str) -> pt.Text:
            text = pt.Text()
            for w in s:
                text.append(pt.Fragment(w, pt.Style(bold=True, underlined=True)))
            text.split(re.compile("([^ _]+)([ _]+|$)"))
            return text

        pt.echo(
            [
                pt.render(
                    "Note: In this example the library assumes that your terminal supports "
                    "all color modes including 256-color and True Color, and forces "
                    "the renderer to act accordingly. If that's not the case, weird "
                    "results may (and will) happen. Run 'examples/terminal_color_mode.py' "
                    "for the details.",
                    pt.cv.GRAY_30,
                ),
                "",
                "Basic usage:",
                *self.usage,
                "You can specify any amount of colors as arguments, and they will be "
                "approximated instead of the default (random) one. Required format is "
                "a string 1-6 characters long representing an integer(s) in a hexadecimal "
                "form: 'FFFFFF' (case insensitive), or a name of the color in any format:",
                "",
                f"  venv/bin/python {sys.argv[0]} " + fmt_arg_examples("3AEBA1 0bceeb 666"),
                f"  venv/bin/python {sys.argv[0]} "
                + fmt_arg_examples("red DARK_RED icathian-yellow"),
            ],
            wrap=True,
            indent_first=2,
        )

    def _run(self, sample: pt.Color | None, color_type: str):
        if sample is None:
            random_rgb = RGB.from_channels(*(random.randint(40, 255) for _ in range(3)))
            sample = ColorRGB(random_rgb)

        direct_renderer = pt.SgrRenderer(pt.OutputMode.TRUE_COLOR)
        # formatter = StaticFormatter(max_value_len=3, allow_negative=False)
        formatter = StaticFormatter()
        setattr(
            formatter,
            "format",
            lambda v: pt.format_auto_float(v, 4, allow_exp_form=True),
        )

        pt.echo()
        pt.echo(f'  {color_type+" color:":<15s}', nl=False)
        box = pt.render("  ", pt.Style(bg=sample), direct_renderer)
        pt.echo(box, nl=False)
        pt.echo(f" {sample.format_value(prefix='')} ", pt.Style(bg=0x0), nl=False)
        pt.echo("\n\n ", nl=False)

        results: list[tuple[str | None, str, pt.Style | None, pt.IRenderer | None, str | None]] = []
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
                results.append((None, "│", None, None, None))

            approx_results = []
            if upper_bound := renderer._COLOR_UPPER_BOUNDS.get(om, None):
                max_results = 1
                if idx > 0:
                    max_results = self._extended_mode + 1
                    if om is pt.OutputMode.TRUE_COLOR:
                        max_results = 2 * self._extended_mode + 1
                if self._space_override:
                    upper_bound._approximator.assign_space(self._space_override)
                self._cdiff_method = upper_bound._approximator._space.__name__.strip() + " distance"
                approx_results = upper_bound.approximate(sample, max_results)

            for aix, approx_result in enumerate(approx_results):
                sample_approx = approx_result.color
                dist = approx_result.distance

                if idx == 0:
                    sample_approx = sample
                    dist = 0.0
                style = pt.Style(bg=sample_approx).autopick_fg()

                dist_str = " -- " if not dist else formatter.format(dist)
                code, value, name = re.search(
                    r"(?i)(\w\d{1,3}|)?[ (]*(#[\da-h]{1,6}\??)[ (]*([^)]*)\)?",
                    sample_approx.repr_attrs(True),
                ).groups()
                # input_on_result = '%4s %-8s %s' % (code or '--', value, name or '--')
                sample_approx_str = "%4s %-8s %-18s" % (
                    code or "--",
                    value,
                    (lambda b: b.name + " (" + name + ")" if b else (name or "--"))(
                        sample_approx._base
                    ),
                )

                def print_hsv(hsv: HSV) -> str:
                    attrs = [
                        f"{hsv.hue:>3.0f}°",
                        f"{100*hsv.saturation:>3.0f}%",
                        f"{100*hsv.value:>3.0f}%",
                    ]
                    return " ".join(attrs)

                string1 = f"{dist_str:>4s} │ {print_hsv(sample_approx.hsv):>11s} "
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
        header = (
            self._delta_name.rjust(4)
            + " │  "
            + " H    S    V  ".center(11)
            + "│ "
            + "Code  Value   Name"
        )
        pt.echo(header.ljust(prim_len1 + prim_len2 + 2), nl=False)
        pt.echo(
            f"  {self._delta_name.strip()} is {self._cdiff_method}", pt.Style(fg="gray", dim=True)
        )

        for string1, string2, style, renderer, desc in results:
            if not string1:
                pt.echo(" ", nl=False)
                pt.echo(
                    f"     {string2}                {string2}" + "".ljust(prim_len2 + 1),
                    pt.Style(crosslined=True),
                )
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
        logging.exception(e)
        # raise e
