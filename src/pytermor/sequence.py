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

    @property
    @abc.abstractmethod
    def str(self) -> AnyStr:
        pass


class SGRSequence(CSISequence):
    TERMINATOR = 'm'

    def __init__(self, *params: int):
        super(SGRSequence, self).__init__(*params)

    @property
    def str(self) -> AnyStr:
        return '{0}{1}{2}{3}'.format(self.CONTROL_CHARACTER,
                                     self.INTRODUCER,
                                     self.SEPARATOR.join([str(param) for param in self._params]),
                                     self.TERMINATOR)

    def __add__(self, other: SGRSequence) -> SGRSequence:
        self._ensure_sequence(other)
        return SGRSequence(*self._params, *other._params)

    def __radd__(self, other: SGRSequence) -> SGRSequence:
        self._ensure_sequence(other)
        return SGRSequence(*other._params, *self._params)

    def __iadd__(self, other: SGRSequence) -> SGRSequence:
        self._ensure_sequence(other)
        return SGRSequence(*self._params, *other._params)

    def _ensure_sequence(self, subject: Any):
        if not isinstance(subject, SGRSequence):
            raise TypeError(
                'Concatenating is allowed only for <SGRSequence> + <SGRSequence>, got {0}'.format(type(subject))
            )
