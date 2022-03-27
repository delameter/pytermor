# ------------------------------------------------------------------------------
# pytermor [ANSI formatted terminal output toolset]
# (C) 2022 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------
from __future__ import annotations

import abc
from typing import AnyStr, List, Any


class CSISequence(metaclass=abc.ABCMeta):
    CONTROL_CHARACTER = '\033'
    INTRODUCER = '['
    SEPARATOR = ';'

    def __init__(self, *params: int):
        self._params: List[int] = list(params)

    @property
    def params(self) -> List[int]:
        return self._params

    @abc.abstractmethod
    def __str__(self) -> AnyStr: raise NotImplementedError


# CSI sequence sub-type
class SGRSequence(CSISequence):
    TERMINATOR = 'm'

    def __init__(self, *params: int):
        super(SGRSequence, self).__init__(*params)

    def __str__(self) -> AnyStr:
        return f'{self.CONTROL_CHARACTER}{self.INTRODUCER}' \
               f'{self.SEPARATOR.join([str(param) for param in self._params])}' \
               f'{self.TERMINATOR}'

    def __add__(self, other: SGRSequence) -> SGRSequence:
        self._ensure_sequence(other)
        return SGRSequence(*self._params, *other._params)

    def __radd__(self, other: SGRSequence) -> SGRSequence:
        self._ensure_sequence(other)
        return SGRSequence(*other._params, *self._params)

    def __iadd__(self, other: SGRSequence) -> SGRSequence:
        self._ensure_sequence(other)
        return SGRSequence(*self._params, *other._params)

    # noinspection PyMethodMayBeStatic
    def _ensure_sequence(self, subject: Any):
        if not isinstance(subject, SGRSequence):
            raise TypeError(
                f'Add operation is allowed only for <SGRSequence> + <SGRSequence>, got {type(subject)}'
            )
