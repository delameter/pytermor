# -----------------------------------------------------------------------------
# pytermor [ANSI formatted terminal output toolset]
# (C) 2022 A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
from __future__ import annotations

import abc
from typing import AnyStr, List, Any, Set


class ModifierGroup:
    def __init__(self, breaker: SequenceSGR, starters: List[SequenceSGR]):
        self._breaker = breaker
        self._starters = starters

        self._back_ref_sequences()

    def _back_ref_sequences(self):
        for seq in self._starters:
            seq.add_modifier_group(self)

        self._breaker.add_modifier_group(self, True)

    def __repr__(self):
        return f'${self._breaker}|^{self._starters}'

    @property
    def breaker(self) -> SequenceSGR:
        return self._breaker

    @property
    def starters(self) -> List[SequenceSGR]:
        return self._starters


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

    def __repr__(self):
        return f'{self.__class__} {self._params}'


# CSI sequence sub-type
class SequenceSGR(SequenceCSI):
    TERMINATOR = 'm'

    def __init__(self, *params: int):
        super(SequenceSGR, self).__init__(*params)
        self._mgroups_breaker: Set[ModifierGroup] = set()
        self._mgroups_starter: Set[ModifierGroup] = set()

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

    # @TODO update mgroups!
    def __iadd__(self, other: SequenceSGR) -> SequenceSGR:
        self._ensure_sequence(other)
        return SequenceSGR(*self._params, *other._params)

    def add_modifier_group(self, mgroup, is_breaker: bool = False):
        mgroups = self._mgroups_starter
        if is_breaker:
            mgroups = self._mgroups_breaker
        mgroups.add(mgroup)

    def get_modifier_groups_starter(self) -> Set[ModifierGroup]:
        return self._mgroups_starter

    # noinspection PyMethodMayBeStatic
    def _ensure_sequence(self, subject: Any):
        if not isinstance(subject, SequenceSGR):
            raise TypeError(
                f'Add operation is allowed only for <SequenceSGR> + <SequenceSGR>, got {type(subject)}'
            )
