# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under GNU Lesser General Public License v3.0
# -----------------------------------------------------------------------------
from __future__ import annotations

from dataclasses import dataclass
from typing import overload

import pytest

from pytermor import (
    DEFAULT_COLOR,
    NOOP_COLOR,
    Color, Style, RenderColor,
)
from pytermor import DynamicColor, FrozenStyle
from pytermor import ExtendedEnum, RendererManager
from pytermor.config import Config, init_config, replace_config
from pytermor.cval import cv

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


@pytest.fixture(scope="function")
def dynamic_color(request) -> type[DynamicColor]:
    """
    Dynamic style constructor.


        >>> @pytest.mark.dynamic_color(deferred=False)
        ... def fn(dynamic_color: type): pass

    :return: type[DynamicColor]
    """

    setup = request.node.get_closest_marker("dynamic_color")
    setup = getattr(setup, 'kwargs', dict())
    setup.setdefault('deferred', False)

    @dataclass
    class _ExampleState:
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

    class _ExampleColor(DynamicColor[_ExampleState]):
        _DEFERRED = setup.get('deferred')

        @classmethod
        @overload
        def update(cls, *, current_mode: str) -> None:
            ...

        @classmethod
        def update(cls, **kwargs) -> None:
            super().update(**kwargs)

        @classmethod
        def _update_impl(cls, *, current_mode: str = "main") -> _ExampleState:
            return _ExampleState(
                auto=(current_mode == "auto"),
                help=(current_mode == "help"),
            )

    yield _ExampleColor


@pytest.fixture(scope="function")
def dynamic_style(request, dynamic_color: type[DynamicColor]) -> Style:
    if setup := request.node.get_closest_marker("dynamic_style"):
        if setup.kwargs:
            dynamic_color.update(**setup.kwargs)

    yield FrozenStyle(fg=dynamic_color("fg"), bg=dynamic_color("bg"))
