import io
import math
import re
import typing as t
import pytermor as pt
from pytermor import IRenderer, FT, make_style, Color16

n = lambda j: math.pi**j
r = range

# DRAFT

class RudimentaryLatexRenderer(IRenderer):
    def render(self, string: str, fmt: FT = None) -> str:
        if not string:
            return ""
        style = make_style(fmt)
        if not style.fg:
            return string
        if isinstance(style.fg, Color16):
            return f':{style.fg.name}:`{string}`'
        print(style)
        raise NotImplementedError


def p(fn: t.Callable, rmin=5, rmax=21, color=True):
    buf = io.StringIO()
    print(["+-", ""][color] + "-" * 35 + ["--", "-+"][color], file=buf)
    buf.seek(0)
    sep = buf.read()
    print(
        ["| ", ""][color] + ["", fn.__name__.center(70)][color] + ["  ", " |"][color],
        file=buf,
    )
    print(sep, end="|", file=buf)
    [
        pt.echo(
            pt.rjust_sgr(pt.render(fn(n(i), auto_color=color), renderer=pt.SgrRenderer).replace('`:', '`\ :'), 10)
            + "  "
            + ["", "|\n|", ""][i % 3],
            nl=False,
            file=buf,
        )
        for i in r(rmin, rmax)
    ]
    print("\n" + sep + "\n", end="|", file=buf)
    buf.seek(0)
    return buf


bufs = [[], [], []]
for color in [False, True]:
    bufs[0].append(p(pt.format_si, 5, 20, color))
    bufs[1].append(p(pt.format_time_ns, 5, 35, color))
    bufs[2].append(p(pt.format_time_delta, 2, 17, color))


split = lambda b: b.read().splitlines()
for bufl in bufs:
    prevt = None
    for l, r in zip(*[split(buf) for buf in bufl]):
        t = (l + r).strip()
        if t == prevt:
            continue
        prevt = t
        if len(t) > 3 or len(t) == 0:
            print(re.sub(r'[+|-]', ' ', t))
