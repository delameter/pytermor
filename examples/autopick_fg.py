#!/bin/env python3
# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2024. A. Shavykin <0.delameter@gmail.com>
#  Licensed under GNU Lesser General Public License v3.0
# -----------------------------------------------------------------------------
from math import inf

import pytermor as pt
import itertools

cr_min = inf
cr_max = -inf


def Main():
    pt.force_ansi_rendering()

    H = [*range(0, 361, 30)]
    S = [0.50, 1.00, 0.0]
    V = [v / 100 for v in sorted([*range(45, 55), *range(0, 101, 20)])]

    for h, s, v in itertools.product(H, S, V):
        if s < 0.5 and h < 360:
            continue
        if v == V[0]:
            print(" ")
        col = pt.HSV(h, s, v)
        st = pt.Style(bg=col.xyz).autopick_fg()
        print_color(st)

    print()
    print_color(pt.Style(fg=pt.cv.GRAY_100, bg=pt.cv.GRAY_0))
    print_color(pt.Style(fg=pt.cv.GRAY_0, bg=pt.cv.GRAY_100))

    pt.echoi("\n\n" + "LEGEND:".center(25) + "MIN CR:".center(25) + "MAX CR:".center(25))
    pt.echoi(
        "\n\n"
        + "[fg] -> [bg] = [cratio]".center(25)
        + f"{cr_min:5.5f}".center(25)
        + f"{cr_max:5.5f}".center(25)
    )
    print()
    print()


def print_color(st: pt.Style):
    sti = pt.Style(bg=st.bg, fg=pt.RGB.from_ratios(*(1 - p for p in st.fg.rgb.as_ratios())))

    def C(fg, bg):
        l1 = max(fg.xyz.y, bg.xyz.y) / 100
        l2 = min(fg.xyz.y, bg.xyz.y) / 100
        return (l1 + 0.05) / (l2 + 0.05)

    contrast1 = C(st.fg, st.bg)
    contrast2 = C(sti.fg, sti.bg)
    #    if contrast1 > contrast2:
    #        return
    pt.echoi(
        pt.Text(
            f"{st.bg.int:06x} ",
            pt.Style(fg=st.bg),
            f"{contrast1:4.1f}",
            pt.Style(st, bold=True),
            f"{contrast2:4.1f}",
            pt.Style(sti, bold=True),
            " ",
        )
    )
    global cr_min, cr_max
    cr_min = min(cr_min, contrast1, contrast2)
    cr_max = max(cr_max, contrast1, contrast2)


if __name__ == "__main__":
    try:
        Main()
    except Exception as e:
        pt.echo(f"[ERROR] {type(e).__qualname__}: {e}\n", fmt=pt.Styles.ERROR)
        # raise e
