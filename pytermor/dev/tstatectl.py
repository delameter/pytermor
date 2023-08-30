# ------------------------------------------------------------------------------
#  es7s/core
#  (c) 2023 A. Shavykin <0.delameter@gmail.com>
# ------------------------------------------------------------------------------
import enum
import logging
import sys
import typing as t

import pytermor as pt

from .ioproxy import IoProxy, get_stdout


class TerminalInputMode(str, pt.ExtendedEnum):  # @TODO str enums will be available in python 3.11
    DEFAULT: str = enum.auto()
    DISABLED: str = enum.auto()
    DISCRETE: str= enum.auto()


class TerminalStateController:
    def __init__(self, io_proxy: IoProxy = None):
        self._io_proxy: IoProxy = io_proxy or get_stdout()
        self._restore_callbacks: list[t.Callable[[], None]] = []
        self._terminal_orig_settings: t.Optional[list] = None

    def assign_proxy(self, io_proxy: IoProxy):
        self._io_proxy = io_proxy
        logging.debug(f"TSC: Switched to {self._io_proxy}")

    def enable_alt_screen_buffer(self):
        self._add_restore_callback(self.disable_alt_screen_buffer)
        self._add_restore_callback(self._restore_cursor_position)
        self._send_sequence(pt.make_save_cursor_position)
        self._send_sequence(pt.make_enable_alt_screen_buffer)

    def disable_alt_screen_buffer(self):
        self._remove_restore_callback(self.disable_alt_screen_buffer)
        self._send_sequence(pt.make_disable_alt_screen_buffer)
        logging.debug("TSC: DISABLED ALT SCREEN BUFFER: stderr logging should work again")

    def hide_cursor(self):
        self._add_restore_callback(self.show_cursor)
        self._send_sequence(pt.make_hide_cursor)

    def show_cursor(self):
        self._remove_restore_callback(self.show_cursor)
        self._send_sequence(pt.make_show_cursor)

    def setup_input(self, input_mode: TerminalInputMode):
        if input_mode == TerminalInputMode.DEFAULT:
            self.restore_input()
        elif input_mode == TerminalInputMode.DISABLED:
            self.disable_input()
        elif input_mode == TerminalInputMode.DISCRETE:
            self.discrete_input()
        else:
            raise NotImplementedError(f"Unknown input mode: {input_mode}")

    def disable_input(self):
        logging.debug(f"TSC: Putting tty into cbreak mode: {sys.stdin}")
        if not self._is_a_tty():
            return
        if self._terminal_orig_settings:
            logging.warning(f"TSC: Altering tty attributes skipped: already altered")
            return

        import tty
        import termios

        self._terminal_orig_settings = termios.tcgetattr(sys.stdin)
        self._add_restore_callback(self.restore_input)
        try:
            tty.setcbreak(sys.stdin)
        except (termios.error, TypeError) as e:
            logging.error("Saving tty state failed", exc_info=e)

    def discrete_input(self):
        """
        Use with: sys.stdin.read(1)
        Origin: readchar/_posix_read.py
        """
        logging.debug(f"TSC: Enabling tty discrete input: {sys.stdin}")
        if not self._is_a_tty():
            return
        if self._terminal_orig_settings:
            logging.warning(f"TSC: Altering tty attributes skipped: already altered")
            return

        import termios

        fd = sys.stdin.fileno()
        term = termios.tcgetattr(fd)
        self._terminal_orig_settings = termios.tcgetattr(fd)
        self._add_restore_callback(self.restore_input)
        try:
            term[3] &= ~(termios.ICANON | termios.ECHO | termios.IGNBRK | termios.BRKINT)
            termios.tcsetattr(fd, termios.TCSAFLUSH, term)
        except (termios.error, TypeError) as e:
            logging.error("Saving tty state failed", exc_info=e)

    def restore_input(self):
        if not self._is_a_tty():
            logging.warning(f"TSC: Restoring tty attributes skipped: not a tty")
            return
        if not self._terminal_orig_settings:
            logging.warning(f"TSC: Restoring tty attributes skipped: nothing to restore")
            return

        logging.debug(f"TSC: Restoring tty attributes: {self._terminal_orig_settings}")
        self._remove_restore_callback(self.restore_input)

        import termios

        try:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self._terminal_orig_settings)
        except TypeError as e:
            logging.error("Restoring tty state failed", exc_info=e)
        finally:
            self._terminal_orig_settings = None

    def _restore_cursor_position(self):
        self._remove_restore_callback(self._restore_cursor_position)
        self._send_sequence(pt.make_restore_cursor_position)

    def restore_state(self):
        while self._restore_callbacks:
            logging.debug(f"TSC: Restoring state ({len(self._restore_callbacks)})")
            try:
                self._restore_callbacks.pop()()
            except:  # noqa
                pass

    def _add_restore_callback(self, fn: t.Callable[[], None]) -> None:
        logging.debug(f"TSC: Registering callback: '{fn.__name__}'")
        self._restore_callbacks.append(fn)

    def _remove_restore_callback(self, fn: t.Callable[[], None]) -> None:
        if fn not in self._restore_callbacks:
            return
        logging.debug(f"TSC: Unregistering callback: '{fn.__name__}'")
        self._restore_callbacks.remove(fn)

    def _send_sequence(self, fn: t.Callable[[], pt.ISequence]) -> None:
        if not self._is_a_tty():
            logging.debug(f"TSC: Skipping control sequence: not a tty")
            return

        sequence = fn()
        logging.debug(f"TSC: Sending control sequence: '{fn.__name__}' -> {sequence!r}")

        if sequence == pt.make_enable_alt_screen_buffer():
            logging.debug(
                "TSC: ENABLED ALT SCREEN BUFFER: ALL STDERR LOG MESSAGES ARE NOW _IGNORED_ BY THE "
                "TERMINAL (syslog should still work unless switched off explicitly)"
            )
        self._io_proxy.echo(sequence)

    def _is_a_tty(self):
        return self._io_proxy.io.isatty()
