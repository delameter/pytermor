# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under GNU Lesser General Public License v3.0
# -----------------------------------------------------------------------------
"""
Library fine tuning module.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field


def _bool_field(key: str, default: bool = False):
    return field(default_factory=lambda k=key, d=default: os.getenv(k, d))


def _renderer_class_factory():
    return os.getenv("PYTERMOR_RENDERER_CLASS", "SgrRenderer")


def _force_output_mode_factory():
    return os.getenv("PYTERMOR_FORCE_OUTPUT_MODE", "auto")


def _default_output_mode_factory():
    return os.getenv("PYTERMOR_DEFAULT_OUTPUT_MODE", "xterm_256")


@dataclass(frozen=True)
class Config:
    """
    Configuration variables container. Values can be modified in two ways:

        1) create new :class:`Config` instance from scratch and activate with
           `replace_config()`;
        2) or preliminarily set the corresponding environment variables to intended values,
           and the default config instance will catch them up on initialization.

    .. seealso:: Environment variable list is located in `config` guide section.

    :param renderer_class:      Explicitly set renderer class (e.g. `TmuxRenderer`).
                                See `config.renderer_class`.
    :param force_output_mode:   Explicitly set output mode (e.g. ``xterm_16``; any *value*
                                from `OutputMode` enum is valid).
                                See `config.force_output_mode`.
    :param default_output_mode: Output mode to use as a fallback value when renderer is
                                unsure about user's terminal capabilities (e.g. ``xterm_16``;
                                any *value* from `OutputMode` enum is valid). Initial value
                                is ``xterm_256``. See `Config.default_output_mode`.
    :param prefer_rgb:          By default SGR renderer uses 8-bit color mode sequences
                                for `Color256` instances (as it should), even when the
                                output device supports more advanced 24-bit/True Color
                                mode. With this option set to *True* `Color256` will be
                                rendered using True Color sequences instead, provided the
                                terminal emulator supports them. Most of the time the
                                results from different color modes are indistinguishable from
                                each other, however, there *are* rare cases, when it does
                                matter. See `Config.prefer_rgb`.
    :param trace_renders:       Set to *True* to log hex dumps of rendered strings.
                                Note that default handler is :class:`logging.NullHandler`
                                with ``WARNING`` level, so in order to see the traces
                                attached handler is required. See
                                `Config.trace_renders`.
    """

    renderer_class: str = field(default_factory=_renderer_class_factory)
    force_output_mode: str = field(default_factory=_force_output_mode_factory)
    default_output_mode: str = field(default_factory=_default_output_mode_factory)
    trace_renders: bool = _bool_field("PYTERMOR_TRACE_RENDERS")
    prefer_rgb: bool = _bool_field("PYTERMOR_PREFER_RGB")

    def __post_init__(self):
        attr_dict = {k: v for (k, v) in self.__dict__.items()}
        logging.getLogger(__package__).debug(f"Config initialized with: {attr_dict!s}")


class ConfigManager:
    _default: Config = None

    @classmethod
    def set_default(cls, config: Config = None):
        cls._default = config or Config()

    @classmethod
    def get_default(cls) -> Config:
        return cls._default
