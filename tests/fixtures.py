# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under GNU Lesser General Public License v3.0
# -----------------------------------------------------------------------------
from __future__ import annotations

import typing as t
from collections import deque
from dataclasses import dataclass
from typing import overload

import pytest

from pytermor import (
    DEFAULT_COLOR,
    NOOP_COLOR,
    Style,
    RenderColor,
)
from pytermor import DynamicColor, FrozenStyle
from pytermor import ExtendedEnum, RendererManager
from pytermor.config import Config, init_config, replace_config
from pytermor.cval import cv
from pytermor.exception import NotInitializedError

_default_config = Config()


@pytest.fixture(scope="function", autouse=True)
def config(request):
    """
    Global module config replacement, recreated for each test with
    default values or ones specified by ``config`` mark:

        >>> @pytest.mark.config(prefer_rgb=True)
        ... def fn(): pass

    :return: Config
    """
    current_config = _default_config
    setup = request.node.get_closest_marker("config")

    if setup is not None:
        kwargs = dict()
        for k, v in setup.kwargs.items():
            if isinstance(v, ExtendedEnum):
                v = v.value
            kwargs[k] = v
        current_config = Config(**kwargs)

    replace_config(current_config)
    RendererManager.set_default()
    yield current_config
    init_config()
    RendererManager.set_default()


@dataclass
class _TestState:
    _STYLE_MAP = {
        "help": FrozenStyle(fg=cv.HI_GREEN, bg=cv.DARK_GREEN),
        "auto": FrozenStyle(fg=cv.HI_RED, bg=cv.DARK_RED_2),
        "auto+help": FrozenStyle(fg=cv.HI_GREEN, bg=cv.DARK_RED_2),
        None: FrozenStyle(fg=DEFAULT_COLOR, bg=NOOP_COLOR),
    }
    auto: bool
    help: bool

    @property
    def _style_key(self) -> str | None:
        if self.auto and self.help:
            return "auto+help"
        if self.auto:
            return "auto"
        if self.help:
            return "help"
        return None

    @property
    def fg(self) -> RenderColor:
        return self._STYLE_MAP.get(self._style_key).fg

    @property
    def bg(self) -> RenderColor:
        return self._STYLE_MAP.get(self._style_key).bg


@pytest.fixture(scope="function")
def dynamic_style(request) -> Style:
    class _TestDynamicColor(DynamicColor[_TestState]):
        @classmethod
        @overload
        def update(cls, *, current_mode: str) -> None:
            ...

        @classmethod
        def update(cls, **kwargs) -> None:
            super().update(**kwargs)

        @classmethod
        def _update_impl(cls, *, current_mode: str = "main") -> _TestState:
            return _TestState(
                auto=(current_mode == "auto"),
                help=(current_mode == "help"),
            )

    if setup := request.node.get_closest_marker("dynamic_style"):
        if setup.kwargs:
            _TestDynamicColor.update(**setup.kwargs)

    yield FrozenStyle(fg=_TestDynamicColor("fg"), bg=_TestDynamicColor("bg"))


@pytest.fixture(scope="function")
def deferred() -> tuple[Style, any]:
    class _TestDeferredModeResolver:
        _mode: t.ClassVar[str] = None
        _callbacks: t.ClassVar[deque[t.Callable]] = deque()

        @classmethod
        def resolve(cls) -> str | None:
            if cls._mode is None:
                raise NotInitializedError()
            return cls._mode

        @classmethod
        def set_callback(cls, fn: t.Callable[[], t.Any]):
            if fn not in cls._callbacks:
                cls._callbacks.append(fn)

        @classmethod
        def initialize(cls, mode: str):
            cls._mode = mode
            while cls._callbacks:
                cls._callbacks.popleft()()

    resolver = _TestDeferredModeResolver()

    class _TestDeferredColor(DynamicColor[_TestState]):
        _DEFERRED = True

        @classmethod
        @overload
        def update(cls, *, current_mode: str) -> None:
            ...

        @classmethod
        def update(cls, **kwargs) -> None:
            super().update(**kwargs)

        @classmethod
        def _update_impl(cls) -> _TestState:
            try:
                current_mode = resolver.resolve()
                return _TestState(
                    auto=(current_mode == "auto"),
                    help=(current_mode == "help"),
                )
            except NotInitializedError:
                resolver.set_callback(cls.update)
                raise

    yield FrozenStyle(
        fg=_TestDeferredColor("fg"),
        bg=_TestDeferredColor("bg"),
    ), resolver
