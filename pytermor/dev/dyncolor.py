# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under GNU Lesser General Public License v3.0
# -----------------------------------------------------------------------------
# ------------------------------------------------------------------------------
#  es7s/core
#  (c) 2023 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------

import typing as t
from abc import abstractmethod

import pytermor as pt
from pytermor import ColorTarget, Color, SequenceSGR

_T = t.TypeVar("_T", bound=object)

_ExtractorT = t.Union[str, t.Callable[[_T], pt.Color], None]


class DynamicColor(t.Generic[_T], pt.Color):
    _DEFERRED = False
    _state: _T

    @classmethod
    def update(cls, **kwargs) -> None:
        cls._state = cls._update(**kwargs)

    @classmethod
    @abstractmethod
    def _update(cls, **kwargs) -> _T:
        raise NotImplementedError

    def __new__(cls, *args, **kwargs):
        inst = super().__new__(cls)
        if not cls._DEFERRED:
            inst.update()
        return inst

    def __init__(self, extractor: _ExtractorT[_T]):
        self._extractor: _ExtractorT[_T] = extractor
        super().__init__(0)

    def _extract(self) -> pt.Color:
        if not hasattr(self, '_state'):
            self.__class__.update()

        state = self.__class__._state
        if self._extractor is None:
            return t.cast(state, pt.Color)

        if isinstance(self._extractor, t.Callable):
            return self._extractor(state)

        return getattr(state, self._extractor, pt.NOOP_COLOR)

    @property
    def int(self) -> int:
        return self._extract().int

    def to_sgr(self, target: ColorTarget = ColorTarget.FG, upper_bound: t.Type[Color] = None) -> SequenceSGR:
        return self._extract().to_sgr(target, upper_bound)

    def to_tmux(self, target: ColorTarget = ColorTarget.FG) -> str:
        return self._extract().to_tmux(target)

    def repr_attrs(self, verbose: bool = True) -> str:
        return f"{{dynamic}}{self._extract().repr_attrs(verbose)}"
