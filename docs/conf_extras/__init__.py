# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under GNU Lesser General Public License v3.0
# -----------------------------------------------------------------------------
from pathlib import Path


def read_x(filename: str) -> str:
    with open((Path(__file__).parent / filename), "rt") as f:
        return f.read()
