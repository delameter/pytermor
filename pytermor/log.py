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
from functools import update_wrapper
from typing import cast, overload, Optional, Union

from .common import get_qname, cut, isiterable

_F = t.TypeVar("_F", bound=t.Callable[..., t.Any])
_MFT = t.TypeVar("_MFT", bound=t.Callable[[str, t.Any, ...], Optional[Union[str, t.Iterable[str]]]])

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
                    for m in (msg if isiterable(msg) else [msg]):
                        _logger.log(level=level, msg=m)
            except Exception as e:  # pragma: no cover
                _logger.exception(e)
            return result

        return update_wrapper(cast(_F, wrapper), origin)

    if __origin is not None:
        return decorator(__origin)
    else:
        return decorator


def _now_s() -> float:
    return time.time_ns() / 1e9


def _trace_render(origin: _F) -> _F:
    def measure_format_in_out(delta_s: str, out: t.Any, *args, **_) -> t.Iterable[str]:
        actor, inp, extra = args
        no_changes = out == inp
        inp_start = cut(inp, 40)
        out_start = cut(out, 40)
        if no_changes:
            yield f"○ {get_qname(actor)} noop in {delta_s} ({len(inp)}): {inp_start!r}"
        else:
            inplen, outlen = (str(len(s or "")) for s in [inp, out])
            maxlen = max(len(inplen), len(outlen))
            yield f"╭ {actor!r} applying {extra!r}"
            yield f"│ IN  ({inplen:>{maxlen}s}): {inp_start!r}"
            yield f"│ OUT ({outlen:>{maxlen}s}): {out_start!r}"
            yield f"╰ {delta_s}"

    @measure(formatter=measure_format_in_out)
    def new_func(*args, **kwargs):
        return origin(*args, **kwargs)

    return update_wrapper(cast(_F, new_func), origin)


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
