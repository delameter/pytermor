# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022. A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------

from __future__ import annotations

import os.path
import shutil
import typing as t
from os.path import abspath, join, dirname

import yaml

import pytermor as pt
import pytermor.index_256
import pytermor.utilstr
import pytermor.utilsys


def sort_by_name(cdef: dict) -> str:
    return cdef["name"]


def sort_by_hue(cdef: dict) -> t.Tuple[float, ...]:
    # partitioning by hue, sat and val, grayscale group first:
    h, s, v = pt.Color.hex_to_hsv(cdef["value"])
    result = (h // 18 if s > 0 else -v), h // 18, s * 5 // 1, v * 20 // 1
    return result


class RgbListPrinter:
    MAX_NAME_L = 30
    MAX_ORIG_L = 30

    def print(self, colors: t.List[t.Dict]):
        for idx, c in enumerate(sorted(colors, key=sort_by_hue)):
            pad = "".ljust(2)
            vari_style = pt.Style(fg=pt.index_256.GRAY_42)
            orig_style = pt.Style(fg=pt.index_256.GRAY_30)

            style = pt.Style(bg=pt.ColorRGB(c["value"])).autopick_fg()
            style2 = pt.Style(fg=style.bg)

            name = pt.Text(c["name"]) + pad + pt.Text(c.get("variation", ""), vari_style)
            orig_name = pt.Text(c.get("original_name", ""), orig_style)

            print(
                pad
                + pt.render(f"{pad}{idx + 1:>4d}{pad}", style)
                + pad
                + pt.render(f"0x{c['value']:06x}", style2)
                + pad
                + pad
                + f"{name:<{self.MAX_NAME_L}.{self.MAX_NAME_L}s}"
                + pad
                + f"{orig_name:>{self.MAX_ORIG_L}.{self.MAX_ORIG_L}s}"
            )


class RgbTablePrinter:
    DEFAULT_CELLS_ON_SCREEN = 8, 16

    def __init__(self, cell_size: int = None, cell_height: int = None):
        self._cell_padding_x = 2
        self._cell_padding_y = 2
        self._term_width = pytermor.utilsys.get_terminal_width()
        self._term_height = shutil.get_terminal_size().lines

        if not cell_size:
            cell_size = min(
                self._term_width // self.DEFAULT_CELLS_ON_SCREEN[0],
                2 * self._term_height // self.DEFAULT_CELLS_ON_SCREEN[1],
            )
            cell_size = max(1, min(16, cell_size))

            if cell_size <= 5:
                self._cell_padding_x = 0
                self._cell_padding_y = 1

        self._cell_width = cell_size
        self._cell_height = cell_height or max(1, self._cell_width // 2)
        self._cell_margin_x = " " * min(2, max(0, self._cell_width // 3 - 3))
        self._cell_margin_y = "\n" * (len(self._cell_margin_x) // 2)

    def print(self, colors: t.List[t.Dict]):
        style_idx = pt.Style(bold=True)

        lines = [""] * self._cell_height
        cur_x = 0
        max_idx = len(colors)

        for idx, c in enumerate(sorted(colors, key=sort_by_hue)):
            style = pt.Style(bg=pt.ColorRGB(c["value"])).autopick_fg()

            sparse_x = max(0, self._cell_width - self._cell_padding_x)
            sparse_y = max(0, self._cell_height - self._cell_padding_y)
            parts = []
            dyn_tx = ''

            if sparse_y - len(parts) > 0:
                idxstr = str(idx + 1)
                if sparse_x >= len(str(max_idx)):
                    parts.append(pt.render(idxstr, style_idx))
                else:
                    dyn_tx += idxstr + ' '

            if sparse_y - len(parts) > 0:
                valstr = f"{c['value']:06x}"
                if sparse_x >= 6:
                    parts.append(valstr)
                else:
                    dyn_tx += valstr

            if sparse_y - len(parts) > 0:
                vari = c.get("variation", "")
                name = c["name"] + ("\n(" + vari + ")" if vari else "")
                if sparse_y - len(parts) > 3:
                    name = "\n" + name
                dyn_tx += name

            while sparse_y - len(parts) > 0 and len(dyn_tx) > 0:
                part = dyn_tx[: self._cell_width - self._cell_padding_x]
                dyn_tx = dyn_tx[self._cell_width - self._cell_padding_x :].strip()
                if "\n" in part:
                    part, part_exc = part.split("\n", 1)
                    dyn_tx = part_exc + dyn_tx
                parts.append(part.strip())

            empty_parts = max(0, self._cell_height - len(parts))
            empty_parts_before = empty_parts // 2
            parts = [
                *[""] * empty_parts_before,
                *parts,
                *[""] * (empty_parts - empty_parts_before),
            ]

            result_len = self._cell_width + len(self._cell_margin_x)
            cur_x += result_len

            for pid, part in enumerate(parts):
                part = (
                    pt.render(pytermor.utilstr.center_sgr(part, self._cell_width), style)
                    + self._cell_margin_x
                )
                lines[pid] += part

            if cur_x + result_len > self._term_width:
                for pid, line in enumerate(lines):
                    print(line)
                    lines[pid] = ""
                print(end=self._cell_margin_y)
                cur_x = 0


if __name__ == "__main__":
    PROJECT_ROOT = abspath(join(dirname(__file__), ".."))
    CONFIG_PATH = join(PROJECT_ROOT, "config")
    INPUT_CONFIG_FILENAME = "rgb.yml"
    with open(os.path.join(CONFIG_PATH, INPUT_CONFIG_FILENAME), "rt") as f:
        colors = yaml.safe_load(f).get('colors')

    #pt.RendererManager.set_default_to_force_formatting()

    RgbListPrinter().print(colors)
    print()

    RgbTablePrinter(
        int(os.environ.get("CELL_SIZE", 0)), int(os.environ.get("CELL_HEIGHT", 0))
    ).print(colors)
    print()

    from pytermor.utilstr import distribute_padded
    print((distribute_padded([
        pt.Text('111', pt.Styles.WARNING), '22'], 10)))
