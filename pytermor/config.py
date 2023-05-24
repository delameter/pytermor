# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under GNU Lesser General Public License v3.0
# -----------------------------------------------------------------------------
"""
Library fine tuning.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field

import logging


def _bool_field(key: str, default: bool = False):
    return field(default_factory=lambda k=key, d=default: os.getenv(k, d))


def _renderer_class_factory():
    return os.getenv("PYTERMOR_RENDERER_CLASS", "SgrRenderer")

def _force_output_mode_factory():
    return os.getenv("PYTERMOR_FORCE_OUTPUT_MODE", "auto")

def _auto_output_mode_factory():
    return os.getenv("PYTERMOR_AUTO_OUTPUT_MODE", "xterm_256")


@dataclass(frozen=True)
class Config:
    """
    Configuration variables container. Values can be modified in two ways:

        1) create new `Config` instance from scratch and activate with `replace_config()`;
        2) or preliminarily set the corresponding environment variables to intended values,
           and the default config instance will catch them up on initialization.

       .. seealso:: Environment variable list is located in `/guide/configuration`
                    guide section.

    :param renderer_class:    explicitly set renderer class (e.g. `TmuxRenderer`)
    :param force_output_mode: explicitly set output mode (e.g. "xterm_16", a variable
                              *value* from `OutputMode`)
    :param auto_output_mode:  override default output mode that is used when renderer
                              is not sure about user's terminal capabilities (same format
                              as for ``output_mode``) [default="xterm_256"]
    :param prefer_rgb:        By default SGR renderer transforms `Color256` instances
                              to ``ESC [38;5;<N>m`` sequences even if True Color support
                              is detected. With this flag set to *True*, the behaviour
                              is different, and `Color256` will be rendered as
                              ``ESC [38;2;<R>;<G>;<B>m`` sequence (if True Color is
                              available).
    :param trace_renders:     Set to *True* to log hex dumps of rendered strings.
                              Note that default handler is :class:`logging.NullHandler` with
                              ``WARNING`` level, so in order to see the traces
                              attached handler is required.
    """

    renderer_class: str = field(default_factory=_renderer_class_factory)
    force_output_mode: str = field(default_factory=_force_output_mode_factory)
    auto_output_mode: str = field(default_factory=_auto_output_mode_factory)
    trace_renders: bool = _bool_field("PYTERMOR_TRACE_RENDERS")
    prefer_rgb: bool = _bool_field("PYTERMOR_PREFER_RGB")

    ATTRS = [  # @fixme maybe there is a better way to iterate over all fields...
        'renderer_class', 'force_output_mode',
        'auto_output_mode', 'trace_renders',
        'prefer_rgb',
    ]

    def __post_init__(self):
        attr_dict = {k: getattr(self, k) for k in self.ATTRS}
        logging.info(f"Config initialized with: {attr_dict!s}")


_config = Config()


def get_config() -> Config:
    """
    Return the current config instance.
    """
    return _config


def init_config():
    """
    Reset all config vars to default values.
    """
    replace_config(Config())


def replace_config(cfg: Config):
    """
    Replace the global config instance with provided one.
    """
    global _config
    _config = cfg
