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
    V = [v / 100 for v in range(0, 101, 20)]

    for h, s, v in itertools.product(H, S, V):
        if s < .5 and h < 360:
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
    pt.echoi("\n\n" + "[fg] -> [bg] = [cratio]".center(25) + f"{cr_min:5.5f}".center(25)  + f"{cr_max:5.5f}".center(25))
    print()
    print()

def print_color(st: pt.Style):
    l1 = max(st.fg.xyz.y, st.bg.xyz.y) / 100
    l2 = min(st.fg.xyz.y, st.bg.xyz.y) / 100
    contrast = (l1 + 0.05) / (l2 + 0.05)
    pt.echoi(pt.Text(
       f" {st.bg.int:06x}->{st.fg.int:06x} = ", st,
       f"{contrast:4.1f}", pt.Style(st, bold=True),
       f":1 ", st
    ))
    global cr_min, cr_max
    cr_min = min(cr_min, contrast)
    cr_max = max(cr_max, contrast)

if __name__ == "__main__":
    try:
        Main()
    except Exception as e:
        pt.echo(f"[ERROR] {type(e).__qualname__}: {e}\n", fmt=pt.Styles.ERROR)
        # raise e
