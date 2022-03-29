# -----------------------------------------------------------------------------
# pytermor [ANSI formatted terminal output toolset]
# (C) 2022 A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
from __future__ import annotations

import abc
from typing import AnyStr, List, Any


class SequenceCSI(metaclass=abc.ABCMeta):
    CONTROL_CHARACTER = '\033'
    INTRODUCER = '['
    SEPARATOR = ';'

    def __init__(self, *params: int):
        self._params: List[int] = [int(p) for p in params]

    @property
    def params(self) -> List[int]:
        return self._params

    @abc.abstractmethod
    def __str__(self) -> AnyStr: raise NotImplementedError


# CSI sequence sub-type
class SequenceSGR(SequenceCSI):
    TERMINATOR = 'm'

    def __init__(self, *params: int):
        super(SequenceSGR, self).__init__(*params)

    def __str__(self) -> AnyStr:
        return f'{self.CONTROL_CHARACTER}{self.INTRODUCER}' \
               f'{self.SEPARATOR.join([str(param) for param in self._params])}' \
               f'{self.TERMINATOR}'

    def __add__(self, other: SequenceSGR) -> SequenceSGR:
        self._ensure_sequence(other)
        return SequenceSGR(*self._params, *other._params)

    def __radd__(self, other: SequenceSGR) -> SequenceSGR:
        self._ensure_sequence(other)
        return SequenceSGR(*other._params, *self._params)

    def __iadd__(self, other: SequenceSGR) -> SequenceSGR:
        self._ensure_sequence(other)
        return SequenceSGR(*self._params, *other._params)

    # noinspection PyMethodMayBeStatic
    def _ensure_sequence(self, subject: Any):
        if not isinstance(subject, SequenceSGR):
            raise TypeError(
                f'Add operation is allowed only for <SequenceSGR> + <SequenceSGR>, got {type(subject)}'
            )
