# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
from __future__ import annotations

import logging
import random
import time
import typing as t

import pytermor as pt
from pytermor import NOOP_STYLE
from pytermor.utilmisc import percentile


class RenderBemchmarker:
    NUM = 16000
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
            src2.append(f"{i:03d}" * 50, st)
        for i in (random.randint(1, 255) for _ in range(10)):
            st = pt.Style(self.st, fg=f"color{i}")
            src3.append(f"{i:03d}" * 10, st)
        self.sources = [
            (src1, [pt.Text, pt.FrozenText, pt.FixedString, pt.String, str]),
            (src2, [pt.Text, pt.FrozenText, str]),
            (src3, [pt.Text, pt.FrozenText, str]),
        ]

        self.fmter = pt.StaticBaseFormatter(
            max_value_len=4,
            pad=True,
            prefix_refpoint_shift=-3,
            unit="s",
            color=True,
            value_mapping={0.0: "--"},
        )

    def echo_meters(self, avg: bool = True, add_st: pt.FT = NOOP_STYLE):
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
        add_st: pt.FT = NOOP_STYLE,
    ):
        self._echo_meter(f"{label} total ", add_st, times_sum, 2)
        if not avg:
            return

        exact_time_p50 = 0
        exact_time_p99 = 0
        if times:
            times.sort()
            exact_time_p50 = percentile(times, 0.50)
            exact_time_p99 = percentile(times, 0.99)

        self._echo_meter("p50 ", add_st, exact_time_p50, 2)
        self._echo_meter("p99 ", add_st, exact_time_p99, 2)

    def _echo_meter(self, label: str, add_st: pt.FT, val: float, pad: int):
        fmted = self.fmter.format(val, color_ov=not add_st)
        if not val:
            fmted = "--".center(self.fmter.get_max_len())
        pt.echoi(label + fmted + pt.pad(pad), add_st)

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

    def make_sample(self, src: str | pt.Text, dst: t.Type, preview: bool):
        if isinstance(src, str):
            if preview:
                src = src[: self.PREVIEW]
            if dst is str:
                return src
            sample_ = dst(src, self.st)
        else:
            if dst is str:
                return src.raw
            if preview:
                src = src.render_fixed(max_len=self.PREVIEW)
            sample_ = dst(src)

        sample_.render = self._render_wrapper(sample_.render)
        return sample_

    def run(self):
        for idx, (sample_src, classes) in enumerate(reversed(self.sources)):
            pt.echo(
                pt.FixedString(
                    f"Sample #{idx+1}/{len(self.sources)}",
                    width=pt.get_terminal_width(),
                    align="center",
                ).raw.replace(" ", "-")
            )

            preview = self.make_sample(sample_src, classes[0], preview=True)
            pt.echoi(pt.FixedString(f"Sample:", width=12))
            pt.echoi(pt.render(preview))
            pt.echo(f".. (+{len(sample_src) - self.PREVIEW} chars)")

            pt.echoi(pt.FixedString(f"Fragments:", width=12))
            pt.text.echo(
                f"{len(sample_src.fragments)}"
                if not isinstance(sample_src, str)
                else "1"
            )

            pt.echoi(pt.FixedString(f"Repeats:", width=12))
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
                    sample = self.make_sample(sample_src, class_, preview=False)
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
                            q = pt.Text(pt.get_qname(class_), pt.Style(bold=True))
                            if class_ is str:
                                add_st = "gray50"
                                q = pt.Text("[CONTROL] ", add_st) + q
                            pt.echoi(pt.ansi.make_set_cursor_x_abs(1).assemble())
                            pt.echoi(pt.ansi.make_erase_in_line().assemble())
                            pt.echoi(f"{q:>14s}")
                            pt.echoi(pt.FixedString(f" ({om.value.upper()})", width=15))
                            pt.echoi("|  ")
                            self.echo_meters(avg=(n == self.NUM), add_st=add_st)
                            if n != self.NUM:
                                pt.echoi(f'[{"*" * (n // self.STEPN):<{self.STEPS}s}]  ')
                            self.prev_frame_ts = end
                    pt.echo()
                print()


if __name__ == "__main__":
    lf = logging.getLogger("pytermor")
    # lf.addHandler(logging.StreamHandler(sys.stderr))
    # lf.addHandler(logging.FileHandler('/tmp/pt.log'))
    # lf.setLevel(logging.DEBUG)

    RenderBemchmarker().run()
