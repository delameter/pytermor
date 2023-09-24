# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under GNU Lesser General Public License v3.0
# -----------------------------------------------------------------------------
from __future__ import annotations

import sys
import typing as t
from os.path import dirname
from subprocess import CalledProcessError, DEVNULL, PIPE, run

import pytermor
from pytermor._version import __updated__, __version__


class Main:
    """
    USAGE:
        python -m pytermor [-s|--short]

    Print library version.
    """

    def __init__(self):
        short = False
        for arg in sys.argv[1:]:
            if arg in ("-s", "--short"):
                short = True
                continue
            print(f"ERROR: Invalid argument/option: {arg}")
            print(Main.__doc__)
            exit(1)
        self.run(short)

    def run(self, short: bool) -> None:
        errors = []
        iter_fns: t.List[t.Callable] = [
            self._get_version_from_package,
            self._get_version_from_git,
        ]
        while iter_fns and (fn := iter_fns.pop(0)):
            try:
                if gen := [*fn(short)]:
                    print("\n".join(gen))
                    return
            except (FileNotFoundError, CalledProcessError, UnicodeDecodeError) as e:
                errors.append(f"ERROR: {e.__class__.__name__}: {e}")
        print("\n".join((*errors, f"Failed to determine the version")))

    def _get_version_from_package(self, short: bool) -> t.Generator[str]:
        yield __version__
        if short:
            return
        yield __updated__

    def _get_version_from_git(self, short: bool) -> t.Iterable[str]:
        yield self._call_git("describe", "--tags")
        if short:
            return
        yield self._call_git("show", "-s", "--format=%cd", "--date=format:%-e-%b-%y")

    def _call_git(self, *args) -> str:
        gitdir = dirname(__file__)
        cp = run(["git", "-C", gitdir, *args], stdout=PIPE, stderr=DEVNULL, check=True)
        return cp.stdout.strip().decode()


if __name__ == "__main__":
    Main()
