# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under GNU Lesser General Public License v3.0
# -----------------------------------------------------------------------------
from __future__ import annotations

import os.path
import time
import typing as t
from collections.abc import Iterable
from functools import partial
from pathlib import Path

import pytermor as pt

from PIL import Image, ImageFont, ImageDraw

DistanceResult = Iterable[pt.ApxResult[pt.ResolvableColor]]


def _calc_distance(
    space: type[pt.IColorValue], cls: type[pt.ResolvableColor], value: pt.IColorValue
) -> DistanceResult:
    for el in cls._index:
        yield pt.ApxResult(el, space.diff(value, el))


class ApproxDemo:
    LABEL_HEIGHT = 50
    SCALE_WIDTH = 20

    PROJECT_ROOT = Path(os.path.dirname(__file__)).parent
    INPUT_FILEPATH = f"{PROJECT_ROOT}/docs/_generated/approx/input-bgwhite-v2.png"
    OUTPUT_FILEPATH_TPL = f"{PROJECT_ROOT}/docs/_generated/approx/output-%s.png"

    FONT_DIRPATH = f"{PROJECT_ROOT}/docs/_static/fonts"
    FONT_HEADER = dict(font=f"{FONT_DIRPATH}/asm-bold.woff", size=16)
    FONT_LABEL = dict(font=f"{FONT_DIRPATH}/asm-regular.woff", size=12)

    SAMPLES: t.List[t.Tuple[pt.Color16 | pt.Color256 | pt.ColorRGB, str]] = [
        (pt.ColorRGB, "16M colors"),
        (pt.Color256, "256 colors"),
        (pt.Color16, "16 colors"),
    ]

    DIFF_FNS: t.List[
        t.Tuple[
            t.Callable[[t.Type[pt.ResolvableColor], pt.IColorValue], DistanceResult], str
        ]
    ] = [
        (partial(_calc_distance, pt.RGB), "RGB"),
        (partial(_calc_distance, pt.HSV), "HSV"),
        (partial(_calc_distance, pt.LAB), "LAB"),
        (partial(_calc_distance, pt.XYZ), "XYZ"),
    ]

    def __init__(self):
        self.font_header = ImageFont.truetype(**self.FONT_HEADER)
        self.font_default = ImageFont.truetype(**self.FONT_LABEL)
        self.input_im = Image.open(self.INPUT_FILEPATH, "r")

    def run(self):
        run_num = 0
        runs_total = len(self.DIFF_FNS) * len(self.SAMPLES)
        for diff_fn, diff_fn_label in self.DIFF_FNS:
            output_size = (
                self.input_im.width * len(self.SAMPLES),
                self.input_im.height + self.LABEL_HEIGHT,
            )
            output_filepath = self.OUTPUT_FILEPATH_TPL % diff_fn_label.lower()
            if os.path.exists(output_filepath):
                output_im_existing = Image.open(output_filepath, "r")
                output_im = output_im_existing.copy()
                output_im_existing.close()
            else:
                output_im = Image.new("RGB", size=output_size, color=(255, 255, 255))

            for sample_num, sample in enumerate(self.SAMPLES):
                [cls, label] = sample
                if cls == pt.ColorRGB:
                    caption = "%s, no approximation" % label
                else:
                    caption = "%s, approx. by %s distance" % (label, diff_fn_label)
                run_num += 1
                cls._approximator.invalidate_cache()
                self._draw_sample(
                    diff_fn, sample_num, run_num, runs_total, cls, caption, output_im
                )

            output_im.save(output_filepath)

    def _draw_sample(
        self,
        diff_fn: t.Callable,
        sample_num: int,
        run_num: int,
        runs_total: int,
        cls: pt.Color,
        caption: str,
        output_im: Image,
    ):
        x1 = sample_num * self.input_im.width
        y1 = 0
        y2 = self.input_im.height

        if cls is pt.ColorRGB:
            output_im.paste(self.input_im, (x1, y1))
            self._print_status(run_num, runs_total, caption, None, None, 1)
            print()
        else:
            cls._color_diff_fn = partial(diff_fn, cls)
            approx_speed = None
            approx_interval = None
            for va in range(0, self.input_im.width, 1):
                ts_before = time.monotonic_ns()
                for vb in range(0, self.input_im.height, 1):
                    val = pt.RGB.from_channels(*self.input_im.getpixel((va, vb)))
                    # cval = cls.approximate(val, max_results=1)[0].color
                    cval = cls.find_closest(val)
                    output_im.putpixel((x1 + va, y1 + vb), (*cval.rgb,))

                    if va % (self.input_im.width // 100) == 0:
                        perc = va / self.input_im.width
                        self._print_status(
                            run_num,
                            runs_total,
                            caption,
                            approx_speed,
                            approx_interval,
                            perc,
                        )
                ts_after = time.monotonic_ns()
                approx_interval = ts_after - ts_before
                approx_speed = (self.input_im.height * 1e9) / approx_interval
            print()

        ImageDraw.Draw(output_im).text(
            (x1 + self.input_im.width / 2, y2 + self.LABEL_HEIGHT / 4),
            anchor="mm",
            font=self.font_header,
            fill=(0, 0, 0),
            text=pt.get_qname(cls) + " class",
        )
        ImageDraw.Draw(output_im).text(
            (x1 + self.input_im.width / 2, y2 + self.LABEL_HEIGHT / 1.75),
            anchor="mm",
            font=self.font_default,
            fill=(0, 0, 0),
            text=caption,
        )

    def _print_status(
        self,
        run_num: int,
        runs_total: int,
        caption: str,
        approx_speed: float | None,
        approx_interval: float | None,
        perc: float,
    ):
        speed_str = '---- kpx/s'
        interval_str = ' ---ms/col.'
        if approx_speed:
            speed_str = f'{pt.format_si(approx_speed):>6s}px/s'
        if approx_interval:
            interval_str = f"{pt.format_time_ns(approx_interval):>6s}/col."
        perc_num = round(100*perc)
        perc_chr = round(self.SCALE_WIDTH * perc)
        msg = (
            f"\r{perc_num:>4d}% "
            f'{"█"*perc_chr}{"░"*(self.SCALE_WIDTH-perc_chr)}|  '
            f"{speed_str}  "
            f"{interval_str} | "
            f"Sample {run_num:>{len(str(runs_total))}d}/{runs_total} | "
            f"{caption:<40s}"
        )
        print(msg, end='')


if __name__ == "__main__":
    ApproxDemo().run()
