# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2023. A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
"""
Library fine tuning.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field

from .common import logger


def _bool_field(key: str, default: bool = False):
    return field(default_factory=lambda k=key, d=default: os.getenv(k, d))


def _renderer_class_factory():
    return os.getenv("PYTERMOR_RENDERER_CLASS", "SgrRenderer")

def _output_mode_factory():
    return os.getenv("PYTERMOR_OUTPUT_MODE", "AUTO")


@dataclass(frozen=True)
class Config:
    """
    Configuration variables container. Values can be modified in two ways:

        1) create new `Config` instance from scratch and activate with `replace_config()`;
        2) or preliminarily set the corresponding environment variables to intended values,
           and the default config instance will catch them up on initialization.

       .. seealso:: Environment variable list is located in `/guide/configuration`
                    guide section.

    :param renderer_class: renderer_class
    :param output_mode:    output_mode
    :param trace_renders:  Set to *True* to log hex dumps of rendered strings.
                           Note that default logger is :class:`logging.NullHandler` with
                           ``WARNING`` level, so in order to see the traces
                           attached handler is required.
    :param prefer_rgb:     By default SGR renderer transforms `Color256` instances
                           to ``ESC [38;5;<N>m`` sequences even if True Color support
                           is detected. With this flag set to *True*, the behaviour
                           is different, and `Color256` will be rendered as
                           ``ESC [38;2;<R>;<G>;<B>m`` sequence (if True Color is
                           available).
    """

    renderer_class: str = field(default_factory=_renderer_class_factory)
    output_mode: str = field(default_factory=_output_mode_factory)
    trace_renders: bool = _bool_field("PYTERMOR_TRACE_RENDERS")
    prefer_rgb: bool = _bool_field("PYTERMOR_PREFER_RGB")

    ATTRS = [  # @fixme maybe there is a better way to iterate over all fields...
        'renderer_class', 'output_mode', 'trace_renders', 'prefer_rgb',
    ]

    def __post_init__(self):
        attr_dict = {k: getattr(self, k) for k in self.ATTRS}
        logger.info(f"Config initialized with: {attr_dict!s}")


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
