# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under GNU Lesser General Public License v3.0
# -----------------------------------------------------------------------------
from __future__ import annotations

import logging
import sys
import time
from functools import update_wrapper
from typing import Any, Callable, TypeVar, cast, overload


_F = TypeVar("_F", bound=Callable[..., Any])

TRACE = 5
_logger = logging.getLogger(__package__)

logging.addLevelName(TRACE, "TRACE")
_logger.addHandler(logging.NullHandler())  # discards logs by default

# - 8< - - - - - - - - - in your project: - - - - - - - - - - - - - -
#   logger = logging.getLogger('pytermor')
#   handler = logging.StreamHandler()
#   fmt = '[%(levelname)5.5s][%(name)s.%(module)s] %(message)s'
#   handler.setFormatter(logging.Formatter(fmt))
#   logger.addHandler(handler)
#   logger.setLevel(logging.DEBUG)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - >8-


def _format_sec(val: float) -> str:  # pragma: no cover
    if val >= 2:
        return f"{val:.1f}s"
    if val >= 2e-3:
        return f"{val*1e3:.0f}ms"
    if val >= 2e-6:
        return f"{val*1e6:.0f}µs"
    if val >= 1e-9:
        return f"{val*1e9:.0f}ns"
    return "<1ns"


def _now_s() -> float:
    return time.time_ns() / 1e9


def _trace_render(origin: _F) -> _F:
    """
    Decorrator
    """

    @measure(
        template_enter_fn=lambda renderer, inp, st: f"╭ {renderer!r} applying {st!r}",
        template_exit="╰ %s",
    )
    def new_func(*args, **kwargs):
        result = origin(*args, **kwargs)

        inp = args[1]
        no_changes = result == inp
        li = str(len(inp or ""))
        lo = str(len(result or ""))
        maxl = max(len(li), len(lo))
        try:
            if no_changes:
                _logger.log(level=TRACE, msg=f"│ I=O ({li:>{maxl}s}): {inp!r}")
            else:
                _logger.log(level=TRACE, msg=f"│ IN  ({li:>{maxl}s}): {inp!r}")
                _logger.log(level=TRACE, msg=f"│ OUT ({lo:>{maxl}s}): {result!r}")
        except Exception as e:  # pragma: no cover
            _logger.exception(e)
        return result

    return update_wrapper(cast(_F, new_func), origin)


def get_logger() -> logging.Logger:
    return _logger


def init_logger():  # pragma: no cover
    from .config import get_config

    if get_config().trace_renders:
        fmt = "[%(levelname)5.5s][%(name)s.%(module)s] %(message)s"
        h = logging.StreamHandler(sys.stderr)
        h.setLevel(TRACE)
        h.setFormatter(logging.Formatter(fmt))
        _logger.addHandler(h)
        _logger.setLevel(TRACE)


@overload
def measure(__origin: _F) -> _F:
    ...


@overload
def measure(
    *,
    template_enter_fn: Callable[..., str] = None,
    template_exit="Done in %s",
    level=TRACE,
) -> Callable[[_F], _F]:
    ...


def measure(
    __origin: Callable[..., Any] = None,
    *,
    template_enter_fn: Callable[..., str] = None,
    template_exit="Done in %s",
    level=TRACE,
):
    """
    Decorrator
    """

    def decorator(origin: Callable[..., Any]):
        def wrapper(*args, **kwargs):
            try:
                if template_enter_fn:
                    _logger.log(level=level, msg=template_enter_fn(*args, **kwargs))
            except Exception as e:  # pragma: no cover
                _logger.exception(e)

            before_s = _now_s()
            result = origin(*args, **kwargs)
            delta_s = _now_s() - before_s

            try:
                _logger.log(level=level, msg=template_exit % _format_sec(delta_s))
            except Exception as e:  # pragma: no cover
                _logger.exception(e)
            return result

        return update_wrapper(cast(_F, wrapper), origin)

    if __origin is not None:
        return decorator(__origin)
    else:
        return decorator
