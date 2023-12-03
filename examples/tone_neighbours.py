# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under GNU Lesser General Public License v3.0
# -----------------------------------------------------------------------------
import random
import re
import typing as t

import pytermor as pt

def tones(col: pt.IColorValue):
    BORDER = pt.Border(*"▌▌")

    W = min(60, pt.get_terminal_width() // 3)

    h, s, v = col.hsv
    vmin = max(0, int(100 * v - 50))
    vmax = min(100, int(100 * v + 50))

    inputs = []

    self = (h, s, v)
    inputs_s = []
    for S in {*range(0, 101, 5)}:
        if S == round(100 * s):
            inputs_s.append(self)
            self = None
        else:
            inputs_s.append((h, S / 100, v))
    if self:
        inputs_s.append(self)
    inputs.extend(sorted({*inputs_s}, key=lambda hsv: hsv[1]))

    inputs.append([None] * 3)

    self = (h, s, v)
    inputs_h = []
    for V in range(vmin, vmax + 1, 2):
        if V == round(100 * v):
            inputs_h.append(self)
            self = None
        else:
            inputs_h.append((h, s, V / 100))
    if self:
        inputs_s.append(self)
    inputs.extend(sorted({*inputs_h}, key=lambda hsv: hsv[2]))

    prev = dict()
    rep = 0
    for HH, SS, VV in inputs:
        if HH is None:
            print()
            prev.clear()
            continue
        c_orig = pt.HSV(HH, SS, VV)
        apx_rgb = pt.ColorRGB.approximate(c_orig, 1)[0]
        apx_256 = pt.Color256.approximate(c_orig, 1)[0]
        colors = [apx_256.color, c_orig, apx_rgb.color]

        def bordered(b: pt.Border, max_width: int):
            def wrapper(origin: t.Callable):
                def generator(*args, **kwargs):
                    gen = origin(*args, **kwargs)
                    indent = [9, 2][max_width < 18]
                    lines = pt.wrap_sgr([*gen], max_width-2, indent_subseq=indent).splitlines()

                    yield b.make_top(max_width, lines.pop(0), '<')
                    for line in lines:
                        yield b.make_middle(max_width, line, '<')

                return generator

            return wrapper

        @bordered(BORDER, W)
        def get_label(c: pt.Color) -> list[str]:
            match type(c):
                case pt.HSV:
                    c1 = re.split(R"[][]", str(c.rgb))[1].lower()
                    c2 = re.split(
                        R"[][]",
                        re.sub(
                            R"(\d+)",
                            lambda m: pt.fit(m.group(), 3, fill=" ", align=">"),
                            str(c.hsv),
                        ),
                    )[1]
                    yield f" {c1} {c2} "
                case pt.ColorRGB:
                    yield c.format_value(" #") + f" {c.name} "
                case pt.Color256:
                    yield c.format_value(" #") + f" [x{c.code}] {c.name} "

        labels: dict[t.Type, t.Generator[str]] = {type(c): get_label(c) for c in colors}

        while len(labels.keys()):
            lines = []
            for c in colors:
                if type(c) in labels.keys():
                    try:
                        lines.append(next(labels.get(type(c))))
                    except StopIteration:
                        labels.pop(type(c))
                        lines.append(None)
                else:
                    lines.append(None)

            if not any(lines):
                break

            for c in colors:
                st = pt.Style(fg=0, bg=c)
                stf = pt.Style(st)
                stf2 = pt.Style(st)
                st.flip()
                stf.flip()
                stf.autopick_fg()
                stf2.autopick_fg()
                stf3 = pt.Style(stf2, bold=True)
                stfb = pt.Style(stf2)
                stfp = pt.Style(stf2, dim=True)
                st = pt.Style(st, inversed=True)
                bchars = "".join(re.escape("".join(BORDER.chars)))

                line = lines.pop(0) or pt.pad(W)

                if type(c) not in prev.keys():
                    prev[type(c)] = ""
                if line == prev[type(c)]:
                    rep += 1
                else:
                    prev[type(c)] = line
                    rep = 0
                st.overlined = stf.overlined = stf2.overlined = stf3.overlined = stfp.overlined= stfb.overlined = rep == 0

                regex = re.compile(R"([" + bchars + "]+)")
                for pdx, part in enumerate(pt.flatten1(regex.split(line))):
                    if regex.match(part):
                        if pdx == 1:
                            pt.echo(part[0], pt.Style(st, fg=col, overlined=False), nl=False)
                            part = part[1:]
                        if rep == 0:
                            st.bg = stf3.fg
                        pt.echo(part, st, nl=False)  # sti to inverse border
                    else:
                        if part.isspace():
                            pt.echo(part, st, nl=False)
                        else:
                            if re.search(valrex := R"([0-9a-f]{6})", part):
                                pfx, val, sfx = re.split(valrex, part, 1)
                                if c.hsv == col.hsv:
                                    pt.echo("▶", stfb, nl=False)
                                    pfx = pfx[1:]
                                pt.echo(pfx, stfp, nl=False)
                                pt.echo(val, stf3, nl=False)
                                if c.hsv == col.hsv:
                                    pt.echo(sfx, stf3, nl=False)
                                else:
                                    pt.echo(sfx, stf2, nl=False)
                            else:
                                pt.echo(part, stf2, nl=False)

                # print(end=' ')
                if c is apx_rgb.color:
                    print()


def _print_help(self, exit_code: int = None):
    print(
        """
USAGE: 
    tone_neighbours [COLOR...]

Print example output of combinations of all the renderers defined in the
library and all possible output modes. No arguments or options. Table width 
adjusts for terminal size.
"""
    )
    if exit_code is not None:
        exit(exit_code)


import sys

args = sys.argv[1:]

if not args:
    args.append(hex(pt.RGB.from_channels(*(random.randint(40, 255) for _ in range(3))).int))

while args:
    tones(pt.RGB(int(args.pop(0), 16)))
    print()
