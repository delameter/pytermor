# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under GNU Lesser General Public License v3.0
# -----------------------------------------------------------------------------
from __future__ import annotations
import sys
import time
from abc import abstractmethod, ABCMeta
from os.path import join, abspath, dirname
from typing import TextIO

import pytermor as pt
from pytermor import (
    Fragment,
    Text,
)

PROJECT_ROOT = abspath(join(dirname(__file__), ".."))
CONFIG_PATH = join(PROJECT_ROOT, "config")


def warning(string: str | pt.IRenderable):
    get_stdout().write(
        pt.render(
            pt.Fragment("[WARN] ", pt.Styles.WARNING_LABEL)
            + pt.Text(string + "\n", pt.Styles.WARNING)
        )
    )


def error(string: str | pt.IRenderable):
    get_stdout().write(pt.render(pt.Fragment("[ERROR] ", pt.Styles.ERROR) + string + "\n"))
    exit(1)


class TaskRunner(metaclass=ABCMeta):
    def run(self, *args, **kwargs) -> None:
        ts_before = time.time_ns()
        self._run_callback(self._run(*args, **kwargs))
        elapsed_sec = (time.time_ns() - ts_before) / 1e9
        if elapsed_sec > 1:
            get_stdout().write(f"Execution time: {pt.format_time_delta(elapsed_sec)}")
        else:
            get_stdout().write(f"Execution time: {pt.format_si(elapsed_sec, 's')}")

    @abstractmethod
    def _run(self, *args, **kwargs):
        raise NotImplementedError

    def _run_callback(self, *args, **kwargs):
        pass

    def _render_fin_result(self, fin: TextIO, filepath: str):
        return self.__render_file_result(fin, filepath, "Read", "<-", "yellow")

    def _render_fout_result(self, fout: TextIO, filepath: str):
        return self.__render_file_result(fout, filepath, "Wrote", "->", "green")

    def __render_file_result(self, f: TextIO, filepath: str, act: str, arr: str, sizecolor: str):
        size = pt.format_si(f.tell(), unit="b", auto_color=False)
        size = Text(size, sizecolor, width=8)
        return pt.render(
            pt.Text(f"{act:<5s}", size, arr, Fragment(filepath, "blue"), width=100)
        )


def get_stdout():
    return sys.stdout


class ProgressBar:
    def __init__(self, renderer: pt.IRenderer, f: TextIO, col: pt.Color):
        self._renderer = renderer
        self._f = f
        self._col = col
        self._step_amount = 0
        self._step_num = 0

    def init_steps(self, step_amount: int):
        self._step_amount = step_amount

    def next_step(self, step_name: str):
        slen = len(str(self._step_amount))
        self._step_num += 1
        s = f"[{self._step_num:>{slen}d}/{self._step_amount:<{slen}d}]  {step_name}"
        self.echo(pt.render(s, self._col, self._renderer), False)

    def close(self):
        self._f.write("\n")
        self._f.flush()

    def echo(self, s: str, persist: bool):
        if not persist:
            clr = pt.make_clear_line()
            self._f.write("\r" + clr.assemble())
        self._f.write(s)
        if persist:
            self._f.write("\n")
        self._f.flush()
