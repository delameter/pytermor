# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022. A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
from __future__ import annotations

from typing import List, Sized, Any

from . import Style


class Text:
    def __init__(self, text: Any = None, style: Style|str = None):
        self._runs: List[_TextRun] = [_TextRun(text, style)]

    def render(self) -> str:
        return ''.join(r.render() for r in self._runs)

    def append(self, text: str|Text):
        if isinstance(text, str):
            self._runs.append(_TextRun(text))
        elif isinstance(text, Text):
            self._runs += text._runs
        else:
            raise TypeError('Can add Text to another Text instance or str only')

    def prepend(self, text: str|Text):
        if isinstance(text, str):
            self._runs.insert(0, _TextRun(text))
        elif isinstance(text, Text):
            self._runs = text._runs + self._runs
        else:
            raise TypeError('Can add Text to another Text instance or str only')

    def __str__(self) -> str:
        return self.render()

    def __len__(self) -> int:
        return sum(len(r) for r in self._runs)

    def __format__(self, *args, **kwargs) -> str:
        runs_amount = len(self._runs)
        if runs_amount == 0:
            return ''.__format__(*args, **kwargs)
        if runs_amount > 1:
            raise RuntimeError(
                f'Can only __format__ Texts consisting of 0 or 1 TextRuns, '
                f'got {runs_amount})')
        return self._runs[0].__format__(*args, **kwargs)

    def __add__(self, other: str|Text) -> Text:
        self.append(other)
        return self

    def __iadd__(self, other: str|Text) -> Text:
        self.append(other)
        return self

    def __radd__(self, other: str|Text) -> Text:
        self.prepend(other)
        return self


class _TextRun(Sized):
    def __init__(self, string: Any = None, style: Style|str = None):
        self._string: str = str(string)
        if isinstance(style, str):
            style = Style(fg=style)
        self._style: Style|None = style

    def render(self) -> str:
        if not self._style:
            return self._string
        return self._style.render(self._string)

    def __len__(self) -> int:
        return len(self._string)

    def __format__(self, *args, **kwargs) -> str:
        self._string = self._string.__format__(*args, **kwargs)
        return self.render()


def distribute_padded(values: List[str|Text], max_len: int, pad_before: bool = False,
                      pad_after: bool = False, ) -> str:
    if pad_before:
        values.insert(0, '')
    if pad_after:
        values.append('')

    values_amount = len(values)
    gapes_amount = values_amount - 1
    values_len = sum(len(v) for v in values)
    spaces_amount = max_len - values_len
    if spaces_amount < gapes_amount:
        raise ValueError(f'There is not enough space for all values with padding')

    result = ''
    for value_idx, value in enumerate(values):
        gape_len = spaces_amount // (gapes_amount or 1)  # for last value
        result += value + ' ' * gape_len
        gapes_amount -= 1
        spaces_amount -= gape_len

    return result
