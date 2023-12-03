#!/bin/env python3
# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under GNU Lesser General Public License v3.0
# -----------------------------------------------------------------------------

from __future__ import annotations

import abc
import os.path
import shutil
import sys
import typing as t
from abc import abstractmethod
from os.path import abspath, join, dirname

import yaml

import pytermor as pt
import pytermor.common
import pytermor.filter
import pytermor.term
from pytermor import Text


def _sorter_by_name(cdef: _IColorRGB) -> str:
    return cdef.name


def _sorter_by_hue(cdef: _IColorRGB) -> t.Tuple[float, ...]:
    # partitioning by hue, sat and val, grayscale group first:
    h, s, v = pt.RGB(cdef.value).hsv
    result = int(h/18 if s > 0 else -v), int(s*5), int(v*20), h, s, v
    return result


class _IColorRGB(metaclass=abc.ABCMeta):
    @property
    @abstractmethod
    def value(self) -> int:
        raise NotImplementedError

    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def original_name(self) -> str | None:
        raise NotImplementedError

    @property
    @abstractmethod
    def variation(self) -> str | None:
        raise NotImplementedError


class _ColorRGBConfigAdapter(_IColorRGB):
    def __init__(self, data: t.Dict):
        self._data = data

    @property
    def value(self) -> int:
        return self._data.get("value")

    @property
    def name(self) -> str:
        return self._data.get("name")

    @property
    def original_name(self) -> str | None:
        return self._data.get("original_name")

    @property
    def variation(self) -> str | None:
        return self._data.get("variation")


class _ColorRGBOriginAdapter(_IColorRGB):
    SEP = pt.color._ColorRegistry._TOKEN_SEPARATOR

    def __init__(self, origin: pt.ColorRGB, tokens: list[str]):
        self._origin = origin
        self._name = self.SEP.join(tokens)

    def __repr__(self):
        return f'<{pt.get_qname(self)}[{self.value:06x}, {_sorter_by_hue(self), {self.name}}]>'

    @property
    def value(self) -> int:
        return self._origin.int

    @property
    def name(self) -> str:
        if base := self._origin.base:
            return base.name
        return self._name

    @property
    def original_name(self) -> str | None:
        return None

    @property
    def variation(self) -> str | None:
        if base := self._origin.base:
            return self._name.replace(base.name, "").lstrip(self.SEP)
        return None


class ILoader:
    @abstractmethod
    def load(self):
        ...


class _OriginLoader(ILoader):
    def load(self) -> t.Iterable[_IColorRGB]:
        for v in pt.ColorRGB._registry._set:
            yield _ColorRGBOriginAdapter(v, [v.name])


class _ConfigLoader(ILoader):
    PROJECT_ROOT = abspath(join(dirname(__file__), ".."))
    CONFIG_PATH = join(PROJECT_ROOT, "config")
    INPUT_CONFIG_FILENAME = "rgb.yml"

    def load(self) -> t.Iterable[_IColorRGB]:
        with open(os.path.join(self.CONFIG_PATH, self.INPUT_CONFIG_FILENAME), "rt") as f:
            for c in yaml.safe_load(f).get("colors"):
                yield _ColorRGBConfigAdapter(c)

                for v in c.get("variations", []):
                    yield _ColorRGBConfigAdapter(v)

                for a in c.get("aliases", []):
                    c.update({"name": a})
                    yield _ColorRGBConfigAdapter(c)


class _RgbListPrinter:
    MAX_NAME_L = 30
    MAX_ORIG_L = 30

    def print(self, colors: t.Sequence[_IColorRGB]):
        for idx, c in enumerate(sorted(colors, key=_sorter_by_hue)):
            pad = "".ljust(2)
            vari_style = pt.Style(fg=pt.cv.GRAY_42)
            orig_style = pt.Style(fg=pt.cv.GRAY_30)

            style = pt.Style(bg=pt.ColorRGB(c.value)).autopick_fg()
            style2 = pt.Style(fg=style.bg)

            name = [
                pt.Fragment(c.name),
                pt.Fragment(pad),
                pt.Fragment(c.variation or "", vari_style),
            ]
            orig_name = pt.Fragment(c.original_name or "", orig_style)

            print(
                pad
                + pt.render(f"{pad}{idx + 1:>4d}{pad}", style)
                + pad
                + pt.render(f"0x{c.value:06x}", style2)
                + pad
                + pad
                + pt.render(Text(*name, width=self.MAX_NAME_L))
                + pad
                + pt.render(Text(orig_name, width=self.MAX_ORIG_L))
            )


class _RgbTablePrinter:
    DEFAULT_CELLS_ON_SCREEN = 8, 16

    def __init__(self, cell_size: int = None, cell_height: int = None):
        self._cell_padding_x = 2
        self._cell_padding_y = 2
        self._term_width = pytermor.term.get_terminal_width()
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
        self._cell_margin_x = pytermor.common.pad(min(2, max(0, self._cell_width // 3 - 3)))
        self._cell_margin_y = pytermor.common.padv(len(self._cell_margin_x) // 2)

    def print(self, colors: t.Sequence[_IColorRGB]):
        style_idx = pt.Style(bold=True)

        lines = [""] * self._cell_height
        cur_x = 0
        max_idx = len(colors)
        sorted_colors = sorted(colors, key=_sorter_by_hue)
        for idx, c in enumerate(sorted_colors):
            style = pt.Style(bg=pt.ColorRGB(c.value)).autopick_fg()

            sparse_x = max(0, self._cell_width - self._cell_padding_x)
            sparse_y = max(0, self._cell_height - self._cell_padding_y)
            parts = []
            dyn_tx = ""

            if sparse_y - len(parts) > 0:
                idxstr = str(idx + 1)
                if sparse_x >= len(str(max_idx)):
                    parts.append(pt.render(idxstr, style_idx))
                else:
                    dyn_tx += idxstr + " "

            if sparse_y - len(parts) > 0:
                valstr = f"{c.value:06x}"
                if sparse_x >= 6:
                    parts.append(valstr)
                else:
                    dyn_tx += valstr

            if sparse_y - len(parts) > 0:
                vari = c.variation or ""
                name = c.name + ("\n(" + vari + ")" if vari else "")
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
                    pt.render(pytermor.filter.center_sgr(part, self._cell_width), style)
                    + self._cell_margin_x
                )
                lines[pid] += part

            if cur_x + result_len > self._term_width or idx == len(sorted_colors) - 1:
                for pid, line in enumerate(lines):
                    print(line)
                    lines[pid] = ""
                print(end=self._cell_margin_y)
                cur_x = 0



class Main():
    def __init__(self):
        pt.force_ansi_rendering()
        #pt.RendererManager.set_default(pt.HtmlRenderer)
        pt.cvr.load()
        # config_list = [*_ConfigLoader().load()]
        origin_list = [*_OriginLoader().load()]
        self.run(origin_list)

    def run(self, colors: t.Sequence[_IColorRGB]):
        if '--help' in sys.argv or 'help' in sys.argv:
            self._print_help(0)

        mode = 'list'
        cell_size = 0
        cell_height = 0
        try:
            sys.argv.pop(0)
            if len(sys.argv):
                mode = sys.argv.pop(0)
            if mode not in ['list', 'grid']:
                raise ValueError(f"Invalid mode: {mode}")
            if mode == 'grid' and len(sys.argv):
                cell_size = int(sys.argv.pop(0))
            if mode == 'grid' and len(sys.argv):
                cell_height = int(sys.argv.pop(0))
        except (IndexError, ValueError):
            self._print_help()
            raise

        if mode == 'list':
            _RgbListPrinter().print(colors)
        elif mode == 'grid':
            _RgbTablePrinter(cell_size, cell_height).print(colors)
        print()

    def _print_help(self, exit_code: int = None):
        print("""
USAGE: 
    list_named_rgb [MODE [CELL_SIZE [CELL_HEIGHT]]]
    
Where MODE can be either "list" (default) or "grid". In the latter case the
application takes two more optional arguments - CELL_SIZE, an integer which
specifies grid cell width, and CELL_HEIGHT, an integer which specifies grid 
cell height. If CELL_HEIGHT is not present, cell height is set to width / 2,
rounded down.

EXAMPLES:
    list_named_rgb list
    list_named_rgb grid 2
    list_named_rgb grid 6 3
    list_named_rgb grid 16 6
""")
        if exit_code is not None:
            exit(exit_code)


if __name__ == "__main__":
    try:
        Main()
    except Exception as e:
        pt.echo(f"[ERROR] {type(e).__qualname__}: {e}\n", fmt=pt.Styles.ERROR)
        # raise e
