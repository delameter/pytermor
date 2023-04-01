# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
from __future__ import annotations

import sys
import time
from abc import abstractmethod, ABCMeta
from os.path import join, abspath, dirname
from typing import TextIO

import pytermor as pt
from pytermor import Fragment, SimpleTable, Text

PROJECT_ROOT = abspath(join(dirname(__file__), ".."))
CONFIG_PATH = join(PROJECT_ROOT, "config")


def error(string: str | pt.IRenderable):
    print(pt.render("[ERROR] ", pt.Styles.ERROR_LABEL) + string, file=sys.stderr)
    exit(1)


class TaskRunner(metaclass=ABCMeta):
    def run(self, *args, **kwargs) -> None:
        ts_before = time.time_ns()
        self._run_callback(self._run(*args, **kwargs))
        elapsed_sec = (time.time_ns() - ts_before) / 1e9
        if elapsed_sec > 1:
            print(f"Execution time: {pt.format_time_delta(elapsed_sec)}", file=sys.stderr)
        else:
            print(f"Execution time: {pt.format_si(elapsed_sec, 's')}", file=sys.stderr)

    @abstractmethod
    def _run(self, *args, **kwargs):
        raise NotImplementedError

    def _run_callback(self, *args, **kwargs):
        pass

    def _print_fin_result(self, fin: TextIO, filepath: str):
        self.__print_file_result(fin, filepath, "Read", "<-", 'yellow')

    def _print_fout_result(self, fout: TextIO, filepath: str):
        self.__print_file_result(fout, filepath, "Wrote", "->", 'green')

    def __print_file_result(self, f: TextIO, filepath: str, act: str, arr: str, sizecolor: str):
        size = pt.format_si(f.tell(), unit="b", auto_color=False)
        size = Text(size, sizecolor, width=8)
        pt.echo(SimpleTable(width=100).pass_row(f"{act:<5s}", size, arr, Fragment(filepath, "blue")), file=sys.stderr)
