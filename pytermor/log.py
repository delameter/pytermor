# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under GNU Lesser General Public License v3.0
# -----------------------------------------------------------------------------
from __future__ import annotations

import logging
import sys
import time
import typing as t
from .common import OVERFLOW_CHAR
from functools import update_wrapper
from typing import cast, overload, Optional

_F = t.TypeVar("_F", bound=t.Callable[..., t.Any])
_MFT = t.TypeVar("_MFT", bound=t.Callable[[str, t.Any, ...], Optional[t.Iterable[str]]])

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
    Decorator
    """

    def _format(delta_s: str, out: t.Any, *args, **_) -> t.Iterable[str]:
        renderer, inp, st = args
        no_changes = out == inp
        inp_start = inp[:40] + OVERFLOW_CHAR
        out_start = out[:40] + OVERFLOW_CHAR
        if no_changes:
            yield f"◦ {renderer!r} transit in {delta_s}: {inp_start!r}"
        else:
            li = str(len(inp or ""))
            lo = str(len(out or ""))
            maxl = max(len(li), len(lo))
            yield f"╭ {renderer!r} applying {st!r}"
            yield f"│ IN  ({li:>{maxl}s}): {inp_start!r}"
            yield f"│ OUT ({lo:>{maxl}s}): {out_start!r}"
            yield f"╰ {delta_s}"

    @measure(formatter=_format)
    def new_func(*args, **kwargs):
        return origin(*args, **kwargs)

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
    formatter: _MFT = None,
    level=TRACE,
) -> t.Callable[[_F], _F]:
    ...


def measure(
    __origin: _F = None,
    *,
    formatter: _MFT = None,
    level=TRACE,
) -> _F | t.Callable[[_F], _F]:
    """
    Decorrator
    """

    def _default_formatter(delta_s: str, *_, **__) -> t.Iterable[str]:
        yield f"Done in {delta_s}"

    def decorator(origin: t.Callable[..., t.Any]):
        def wrapper(*args, **kwargs):
            before_s = _now_s()
            result = origin(*args, **kwargs)
            delta_s = _now_s() - before_s

            try:
                fmt_fn: _MFT = formatter or _default_formatter
                if msg := fmt_fn(_format_sec(delta_s), result, *args, **kwargs):
                    if isinstance(msg, str):
                        _logger.log(level=level, msg=msg)
                    elif isinstance(msg, t.Iterable):
                        [_logger.log(level=level, msg=m) for m in msg]
            except Exception as e:  # pragma: no cover
                _logger.exception(e)
            return result

        return update_wrapper(cast(_F, wrapper), origin)

    if __origin is not None:
        return decorator(__origin)
    else:
        return decorator
