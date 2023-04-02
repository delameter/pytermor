# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under GNU Lesser General Public License v3.0
# -----------------------------------------------------------------------------
from __future__ import annotations

import random
import time
import typing as t

import pytermor as pt
import pytermor.color
import pytermor.common
import pytermor.style
from pytermor import NOOP_STYLE, Fragment
from pytermor.renderer import NoOpRenderer
from pytermor.common import percentile


class Main:
    def __init__(self):
        RenderBemchmarker().run()


class RenderBemchmarker:
    NUM = 1600
    STEPS = 16
    STEPN = NUM // STEPS
    PREVIEW = 64

    outer_times_sum = 0
    outer_times = []
    inner_times_sum = 0
    inner_times = []

    def __init__(self):
        self.prev_frame_ts = 0
        self.st = pt.Style(fg="moonstone", bg="#040301", bold=True, underlined=True)
        self.sources = []
        src1 = "".join([str(i) for i in (random.randint(100, 999) for _ in range(100))])
        src2 = pt.Text()
        src3 = pt.Text()
        for i in (random.randint(1, 255) for _ in range(2)):
            st = pt.Style(self.st, fg=f"color{i}")
            src2 += Fragment(f"{i:03d}" * 50, st)
        for i in (random.randint(1, 255) for _ in range(10)):
            st = pt.Style(self.st, fg=f"color{i}")
            src3 += Fragment(f"{i:03d}" * 10, st)
        self.sources = [
            (src1, [pt.Text, pt.FrozenText, pt.Fragment, str]),
            (src2, [pt.Text, str]),
            (src3, [pt.Text, str]),
        ]

        self.fmter = pt.StaticFormatter(
            max_value_len=4,
            pad=True,
            prefix_refpoint_shift=-3,
            unit="s",
            color=True,
            value_mapping={0.0: "--"},
        )

    def echo_meters(self, avg: bool = True, add_st: pytermor.style.FT = NOOP_STYLE):
        self._echo_meters(
            "Outer",
            RenderBemchmarker.outer_times_sum,
            RenderBemchmarker.outer_times,
            avg,
            add_st,
        )
        if not avg:
            return
        pt.echoi("|  ")
        self._echo_meters(
            "Inner",
            RenderBemchmarker.inner_times_sum,
            RenderBemchmarker.inner_times,
            avg,
            add_st,
        )

    def _echo_meters(
        self,
        label: str,
        times_sum: float,
        times: t.List[float],
        avg: bool = True,
        add_st: pytermor.style.FT = NOOP_STYLE,
    ):
        self._echo_meter(f"{label} ", add_st, times_sum, 2)
        if not avg:
            return

        exact_time_p50 = 0
        exact_time_p99 = 0
        if times:
            times.sort()
            exact_time_p50 = percentile(times, 0.50)
            exact_time_p99 = percentile(times, 0.99)

        self._echo_meter("p501 ", add_st, exact_time_p50, 0)
        self._echo_meter("p991 ", add_st, exact_time_p99, 0)

    def _echo_meter(self, label: str, add_st: pytermor.style.FT, val: float, pad: int):
        fmted = self.fmter.format(val, auto_color=not add_st)
        if not val:
            fmted = "--".center(self.fmter.get_max_len())
        pt.echoi(label + fmted + pt.pad(pad), fmt=add_st)

    @staticmethod
    def _render_wrapper(origin: t.Callable):
        def _measure(*args, **kwargs):
            start = time.time_ns()
            result = origin(*args, **kwargs)
            delta = time.time_ns() - start
            RenderBemchmarker.inner_times_sum += delta
            RenderBemchmarker.inner_times.append(delta)
            return result

        return _measure

    def make_sample(self, src: str | pt.Text, dst: t.Type):
        if type(src) == dst:
            return src
        if isinstance(src, str):
            if dst is str:
                return src
            sample_ = dst(src, self.st)
        else:
            if dst is str:
                return pt.render(src, renderer=NoOpRenderer())
            sample_ = dst(src)

        sample_.render = self._render_wrapper(sample_.render)
        return sample_

    def run(self):
        for idx, (sample_src, classes) in enumerate(reversed(self.sources)):
            pt.echo(
                pt.Text(
                    f"Sample #{idx+1}/{len(self.sources)}",
                    width=pytermor.common.get_terminal_width(),
                    align="center",
                    fill='-'
                )
            )

            pt.echoi(pt.Text(f"Sample:", width=12))
            pt.echo(f"{len(sample_src)} chars")

            pt.echoi(pt.Text(f"Repeats:", width=12))
            pt.echo(pt.format_thousand_sep(self.NUM))
            pt.echo()

            for om in [
                pt.OutputMode.TRUE_COLOR,
                pt.OutputMode.XTERM_256,
                pt.OutputMode.XTERM_16,
                pt.OutputMode.NO_ANSI,
            ]:
                renderer = pt.SgrRenderer(om)
                for class_ in classes:
                    sample = self.make_sample(sample_src, class_)
                    RenderBemchmarker.outer_times_sum = 0
                    RenderBemchmarker.outer_times = []
                    RenderBemchmarker.inner_times_sum = 0
                    RenderBemchmarker.inner_times = []

                    for n in range(self.NUM + 1):
                        start = time.time_ns()
                        pt.render(sample, renderer=renderer)
                        end = time.time_ns()
                        delta = end - start
                        RenderBemchmarker.outer_times_sum += delta
                        RenderBemchmarker.outer_times.append(delta)

                        if (
                            n == 1
                            or n % self.STEPN == 0
                            or (end - self.prev_frame_ts) > 0.4 * 1e9
                        ):
                            add_st = NOOP_STYLE
                            q = pt.Fragment(pytermor.common.get_qname(class_), pt.Style(bold=True))
                            if class_ is str:
                                add_st = "gray50"
                                q = pt.Fragment("[CONTROL] ", add_st) + q
                            pt.echoi(pt.ansi.make_set_cursor_x_abs(1).assemble())
                            pt.echoi(pt.ansi.make_erase_in_line().assemble())
                            q.set_width(14)
                            pt.echoi(q)
                            pt.echoi(pt.Text(f" ({om.value.upper()})", width=15))
                            pt.echoi("|  ")
                            self.echo_meters(avg=(n == self.NUM), add_st=add_st)
                            if n != self.NUM:
                                pt.echoi(f'[{"*" * (n // self.STEPN):<{self.STEPS}s}]  ')
                            self.prev_frame_ts = end
                    pt.echo()
                print()


if __name__ == "__main__":
    try:
        Main()
    except Exception as e:
        pt.echo(f"[ERROR] {type(e).__qualname__}: {e}\n", fmt=pt.Styles.ERROR)
        raise e
