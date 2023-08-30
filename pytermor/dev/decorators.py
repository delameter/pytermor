# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under GNU Lesser General Public License v3.0
# -----------------------------------------------------------------------------
import logging
import typing as t
from functools import update_wrapper
from typing import overload

from .iterx import filternv
from .progressbar import ProgressBar, _DummyProgressBar
from .tstatectl import TerminalInputMode, TerminalStateController

_F = t.TypeVar("_F", bound=t.Callable[..., t.Any])


@overload
def _with_progress_bar(__origin: _F) -> _F:
    ...
@overload
def _with_progress_bar(
    *,
    tasks_amount: int = None,
    task_num: int = None,
    task_label: str = None,
    steps_amount: int = None,
    step_num: int = None,
    print_step_num: bool = None,
) -> _F:
    ...
def _with_progress_bar(__origin: _F = None, **kwargsdec) -> _F:
    def decorator(__origin: _F):
        def wrapper(*args, **kwargs):
            if not (tstatectl := kwargs.get("tstatectl", None)):
                _origin = _with_terminal_state(no_cursor=True, input_mode=TerminalInputMode.DISABLED)(__origin)
            try:
                pbar = ProgressBar(
                    tstatectl,
                    **filternv(kwargsdec or dict()),
                )
            except Exception as e:
                logging.getLogger(__package__).warning(f"Failed to set up progress bar component: {e}")
                pbar = _DummyProgressBar()
            try:
                # pbar MUST be present in decorated constructor args:
                __origin(*args, pbar=pbar, **kwargs)
            finally:
                pbar.close()
            return __origin

        return update_wrapper(t.cast(_F, wrapper), __origin)

    if __origin is not None:
        return decorator(__origin)
    else:
        return decorator


@overload
def _with_terminal_state(__origin: _F) -> _F:
    ...
@overload
def _with_terminal_state(
    *,
    alt_buffer: bool = None,
    no_cursor: bool = None,
    input_mode: TerminalInputMode = None,
) -> _F:
    ...

def _with_terminal_state(
    __origin: _F = None,
    *,
    alt_buffer: bool = None,
    no_cursor: bool = None,
    input_mode: TerminalInputMode = None,
) -> _F:
    def decorator(__origin: _F):
        def wrapper(*args, **kwargs):
            tstatectl = TerminalStateController()

            if alt_buffer:
                tstatectl.enable_alt_screen_buffer()
            if no_cursor:
                tstatectl.hide_cursor()
            if input_mode:
                tstatectl.setup_input(input_mode)

            try:
                # tstatectl CAN be present in decorated constructor args:
                __origin(tstatectl=tstatectl, *args, **kwargs)
            finally:
                tstatectl.restore_state()
            return __origin

        return update_wrapper(t.cast(_F, wrapper), __origin)

    if __origin is not None:
        return decorator(__origin)
    else:
        return decorator
