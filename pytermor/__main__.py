# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under GNU Lesser General Public License v3.0
# -----------------------------------------------------------------------------
from __future__ import annotations

import typing as t
from subprocess import PIPE, run, CalledProcessError, DEVNULL
from os import stat
from os.path import dirname, join
from datetime import datetime

from pytermor._version import __version__


class Main:
    def __init__(self):
        _iter_fns: t.List[t.Callable] = [
            self._get_version_from_git,
            self._get_version_from_fs,
        ]
        while len(_iter_fns) > 0:
            fn = _iter_fns.pop(0)
            if (result := fn()) is not None:
                print("v" + ":".join(result))
                return
        print("Failed to determine the version")

    def _call_git(self, *args) -> str:
        gitdir = dirname(__file__)
        cp = run(["git", "-C", gitdir, *args], stdout=PIPE, stderr=DEVNULL, check=True)
        return cp.stdout.strip().decode()

    def _get_version_from_git(self) -> t.Tuple[str, str]|None:
        try:
            v = self._call_git("describe", "--tags")
            dt = self._call_git("showw", "-s", "--format=%cd", "--date=format:%b-%y")
            return v, dt
        except (FileNotFoundError, CalledProcessError, UnicodeDecodeError):
            return None

    def _get_version_from_fs(self) -> t.Tuple[str, str]|None:
        try:
            vfile = join(dirname(__file__), "_version.py")
            mtime = stat(vfile).st_mtime
            dt = datetime.fromtimestamp(mtime).strftime("%b-%y")
            return __version__, dt
        except FileNotFoundError:
            return None


if __name__ == "__main__":
    Main()
