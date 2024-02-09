# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under GNU Lesser General Public License v3.0
# -----------------------------------------------------------------------------
from __future__ import annotations

import os.path
import time
import typing as t
from collections import deque
from collections.abc import Iterable
from pathlib import Path

from PIL import Image, ImageDraw

import pytermor as pt
from pytermor.common import CacheStats

DistanceResult = Iterable[pt.ApxResult[pt.ResolvableColor]]


class ApproxDemo:
    SCALE_WIDTH = 20

    PROJECT_ROOT = Path(os.path.dirname(__file__)).parent
    INPUT_FILEPATH = f"{PROJECT_ROOT}/docs/_generated/approx/input-bgtransp-v5.png"
    OUTPUT_FILEPATH_TPL = f"{PROJECT_ROOT}/docs/_generated/approx/output-%s-%s.png"

    SAMPLES: t.List[t.Tuple[pt.Color16 | pt.Color256 | pt.ColorRGB, str]] = [
        (pt.ColorRGB, "ColorRGB"),
        (pt.Color256, "Color256"),
        (pt.Color16, "Color16"),
    ]

    SPACES: t.List[t.Type[pt.IColorValue]] = [pt.RGB, pt.HSV, pt.LAB, pt.XYZ]
    #SPACES: t.List[t.Type[pt.IColorValue]] = [pt.LAB]

    def __init__(self):
        self._avg_speed = deque(maxlen=20)
        self._avg_eta = deque(maxlen=5)
        self._input_im = Image.open(self.INPUT_FILEPATH, "r")
        self._eta_fmter = pt.DualFormatter(
            units=[
                pt.DualBaseUnit("sec", 60),
                pt.DualBaseUnit("min", 60, collapsible_after=10, custom_short="min"),
                pt.DualBaseUnit("hour", 24, collapsible_after=24),
                pt.DualBaseUnit("day", 30, collapsible_after=10),
                pt.DualBaseUnit("month", 12),
                pt.DualBaseUnit("year", overflow_after=999),
            ],
            allow_negative=True,
            allow_fractional=True,
            unit_separator=" ",
            plural_suffix="s",
        )
        # self._label_font = ImageFont.load("arial.pil")
        self._run_start_ts = time.monotonic_ns() / 1e9

    def run(self):
        run_num = 0
        runs_total = len(self.SPACES) * len(self.SAMPLES)
        for space in self.SPACES:
            for (cls, label) in self.SAMPLES:
                output_size = (self._input_im.width, self._input_im.height)
                fmt_class = lambda o: pt.get_qname(o).strip("<>").lower()
                output_filepath = self.OUTPUT_FILEPATH_TPL % (fmt_class(space), fmt_class(cls))
                if os.path.exists(output_filepath):
                    output_im_existing = Image.open(output_filepath, "r")
                    output_im = output_im_existing.copy()
                    output_im_existing.close()
                else:
                    output_im = Image.new("RGBA", size=output_size, color=(255, 255, 255, 0))

                caption = "%s, %s" % (pt.get_qname(space).lower(), label)
                cls._approximator.assign_space(space)
                run_num += 1

                self._draw_sample(run_num, runs_total, cls, caption, output_im)
                self._draw_label(cls, caption, output_im)

                output_im.save(output_filepath)
                output_im.show()

    def _draw_sample(
        self,
        run_num: int,
        runs_total: int,
        cls: pt.Color,
        caption: str,
        output_im: Image,
    ):
        print(f"Running on {cls._approximator}, {output_im}")
        ts_start = time.monotonic_ns() / 1e9
        ts_status_upd = 0
        eta_sec = None

        for va in range(0, self._input_im.width, 1):
            for vb in range(0, self._input_im.height, 1):
                pxval = self._input_im.getpixel((va, vb))
                rgbval = pt.RGB.from_channels(*pxval[:3])
                cval = cls.find_closest(rgbval, True, True) or pt.ColorRGB(0)
                output_im.putpixel((va, vb), (*cval.rgb, pxval[-1]))

                ts_now = time.monotonic_ns() / 1e9
                approx_interval = ts_now - ts_start
                cache_stats = cls._approximator._stats

                if not ts_status_upd or ts_now - ts_status_upd > 0.25:
                    ts_status_upd = ts_now
                    perc = va / self._input_im.width
                    if perc == 0:
                        continue
                    approx_speed = approx_interval / perc
                    self._avg_speed.append(approx_speed)
                    eta_sec = (
                        (1 - perc + runs_total - run_num)
                        * sum(self._avg_speed)
                        / len(self._avg_speed)
                    )
                    elapsed_sec = ts_now - self._run_start_ts
                    self._print_status(
                        run_num, runs_total, caption, perc, eta_sec, elapsed_sec, cache_stats
                    )

        elapsed_sec = time.monotonic_ns() / 1e9 - self._run_start_ts
        self._print_status(run_num, runs_total, caption, 1, eta_sec, elapsed_sec, cache_stats)
        print()

    def _draw_label(self, cls: pt.Color, caption: str, output_im: Image):
        cls_str = pt.get_qname(cls, name_only=True)
        apx_str = pt.get_qname(cls._approximator)
        meth_str = pt.get_qname(cls._approximator._space)

        ImageDraw.Draw(output_im).text(
            (0, 0),
            fill=(0, 0, 0, 255),
            stroke_fill=(255, 255, 255, 255),
            stroke_width=1,
            text=f"{apx_str} {meth_str} {cls_str}",

            # font=self._label_font,
        )

    def _print_status(
        self,
        run_num: int,
        runs_total: int,
        caption: str,
        perc: float,
        eta_sec: float = None,
        elapsed_sec: float = False,
        cache_stats: pt.common.CacheStats = None,
    ):
        eta_str = "--- "
        elapsed_str = "--- "
        if eta_sec:
            eta_str = self._eta_fmter.format(eta_sec) + " ETA"
        if elapsed_sec:
            elapsed_str = self._eta_fmter.format(elapsed_sec)
        perc_num = round(100 * perc)
        perc_chr = round(self.SCALE_WIDTH * perc)
        msg = (
            f"\r"
            f"[{elapsed_str:>8s}]  {eta_str:>12s}"
            f"  | "
            f"Sample {run_num:>{len(str(runs_total))}d}/{runs_total} |"
            f"{perc_num:>4d}% "
            f'{"█"*perc_chr}{"░"*(self.SCALE_WIDTH-perc_chr)}|  '
            f"{caption:<40s}"
        )
        print(msg + ("  " + ApproxDemo._print_cache_info(cache_stats)), end="")

    @staticmethod
    def _print_cache_info(ci: CacheStats):
        return "%s hits, %s misses (%3.1f%% ratio), size %d/%d" % (
            pt.format_thousand_sep(ci.hits),
            pt.format_thousand_sep(ci.misses),
            100 * ci.hit_ratio,
            ci.cursize,
            ci.maxsize,
        )


if __name__ == "__main__":
    ApproxDemo().run()
