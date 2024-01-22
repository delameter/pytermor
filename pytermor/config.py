# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under GNU Lesser General Public License v3.0
# -----------------------------------------------------------------------------
"""
Library fine tuning module.
"""

from __future__ import annotations
import typing as t
import os


_T = t.TypeVar("_T")


class Config:
    """
    Configuration variables container. Values can be modified in three ways:

        a) create new :class:`Config` instance from scratch and activate with
           `ConfigManager.set()`:

           >>> ConfigManager.set(Config(force_output_mode='auto'))

        b) modify attribute(s) of exising :class:`Config` instance returned by
           `ConfigManager.get()`:

           >>> ConfigManager.get().prefer_rgb = False

        c) preliminarily set the corresponding :envvar:`\\ ` environment variables to intended
           values, and the default config instance will catch them up on creating
           (suitable for the development or debugging).

    .. seealso:: Environment variable list is located in `config` guide section.

    """

    __slots__ = (
        'renderer_classname',
        'force_output_mode',
        'default_output_mode',
        'trace_renders',
        'prefer_rgb',
    )

    def __init__(
        self,
        *,
        renderer_classname: str = None,
        force_output_mode: str = None,
        default_output_mode: str = None,
        trace_renders: bool = None,
        prefer_rgb: bool = None,
    ):
        """
        :param renderer_classname:  Explicitly set renderer class (e.g. `TmuxRenderer`).
        :param force_output_mode:   Explicitly set output mode (e.g. ``xterm_16``; any *value*
                                    from `OutputMode` enum is valid).
        :param default_output_mode: Output mode to use as a fallback value when renderer is
                                    unsure about user's terminal capabilities (e.g. ``xterm_16``;
                                    any *value* from `OutputMode` enum is valid). Initial value
                                    is ``xterm_256``.
        :param prefer_rgb:          By default SGR renderer uses 8-bit color mode sequences
                                    for `Color256` instances (as it should), even when the
                                    output device supports more advanced 24-bit/True Color
                                    mode. With this option set to *True* `Color256` will be
                                    rendered using True Color sequences instead, provided the
                                    terminal emulator supports them. Most of the time the
                                    results from different color modes are indistinguishable from
                                    each other, however, there *are* rare cases, when it does
                                    matter.
        :param trace_renders:       Set to *True* to log hex dumps of rendered strings.
                                    Note that default handler is :class:`logging.NullHandler`,
                                    so in order to see the traces another attached handler is
                                    required.
        """
        def __arg_or_env(arg: t.Optional[t.Any], env_var: str, default: t.Any):
            if arg is None:
                return os.getenv(env_var, default)
            return arg

        self.renderer_classname: str = __arg_or_env(renderer_classname, "RENDERER_CLASSNAME", "SgrRenderer")
        self.force_output_mode: str = __arg_or_env(
            force_output_mode, "FORCE_OUTPUT_MODE", "auto"
        )
        self.default_output_mode: str = __arg_or_env(
            default_output_mode, "DEFAULT_OUTPUT_MODE", "xterm_256"
        )
        self.trace_renders: bool = __arg_or_env(trace_renders, "TRACE_RENDERS", False)
        self.prefer_rgb: bool = __arg_or_env(prefer_rgb, "PREFER_RGB", False)


class ConfigManager:
    """
    YES
    """
    _default: Config = None

    @classmethod
    def set(cls, config: Config = None):
        """why"""
        cls._default = config or Config()

    @classmethod
    def get(cls) -> Config:
        """because"""
        return cls._default


def force_ansi_rendering():
    """
    Shortcut for forcing all control sequences to be present in the
    output of a global renderer.

    Note that it applies only to the renderer that is set up as default at
    the moment of calling this method, i.e., all previously created instances,
    as well as the ones that will be created afterwards, are unaffected.
    """
    ConfigManager.get().force_output_mode = "true_color"


def force_no_ansi_rendering():
    """
    Shortcut for disabling all output formatting of a global renderer.
    """
    ConfigManager.get().force_output_mode = "no_ansi"
