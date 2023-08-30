# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under GNU Lesser General Public License v3.0
# -----------------------------------------------------------------------------
import sys
import typing as t

import pytermor as pt


class IoProxy:
    CSI_EL0 = pt.make_clear_line_after_cursor().assemble()
    RESET = pt.SeqIndex.RESET.assemble()

    PBAR_MODE_ANY_MSG_START = pt.make_set_cursor_column(1).assemble() + CSI_EL0
    PBAR_MODE_ANY_MSG_END = pt.SeqIndex.BG_COLOR_OFF.assemble()

    _progress_bar_mode: t.ClassVar = False

    def __init__(self, io: t.IO):
        self._io = io
        self._renderer = pt.RendererManager.get_default()
        self._broken = False

    def render(self, string: t.Union[pt.RT, list[pt.RT]] = "", fmt: pt.FT = pt.NOOP_STYLE) -> str:
        return pt.render(string, fmt, self._renderer)

    def echo(self, string: t.Union[str, pt.ISequence] = "", *, nl=True) -> None:
        if isinstance(string, pt.ISequence):
            string = string.assemble()
            nl = False

        if IoProxy._progress_bar_mode:
            string = self.PBAR_MODE_ANY_MSG_START + string + self.PBAR_MODE_ANY_MSG_END

        try:
            print(string, file=self._io, end=("", "\n")[nl], flush=not bool(string))
        except BrokenPipeError:
            self._broken = True
            IoProxy._pacify_flush_wrapper()

    @t.overload
    def echo_rendered(self, inp: str, style: pt.Style, *, nl=True) -> None:
        ...
    @t.overload
    def echo_rendered(self, inp: t.Union[str, pt.IRenderable], *, nl=True) -> None:
        ...
    def echo_rendered(self, *args, nl=True) -> None:
        if 1 <= len(args) <= 2:
            rendered = self.render(*args[:2])
            self.echo(rendered, nl=nl)
        else:
            raise pt.exception.ArgCountError(len(args), 1, 2)

    def echo_progress_bar(self, string: str = ""):
        self.echo(string + self.RESET + self.CSI_EL0, nl=False)
        self.io.flush()

    def set_progress_bar_mode(self, enabled=True):
        if not enabled:
            self.echo(nl=False)  # clear the bar
        IoProxy._progress_bar_mode = enabled

    @property
    def io(self) -> t.IO:
        return self._io

    @property
    def renderer(self) -> pt.IRenderer:
        return self._renderer

    @property
    def is_broken(self) -> bool:
        return self._broken

    @classmethod
    def _pacify_flush_wrapper(cls) -> None:
        sys.stdout = t.cast(t.TextIO, _PacifyFlushWrapper(sys.stdout))
        sys.stderr = t.cast(t.TextIO, _PacifyFlushWrapper(sys.stderr))


class _PacifyFlushWrapper:
    """This wrapper is used to catch and suppress BrokenPipeErrors resulting
    from ``.flush()`` being called on broken pipe during the shutdown/final-GC
    of the Python interpreter. Notably ``.flush()`` is always called on
    ``sys.stdout`` and ``sys.stderr``. So as to have minimal impact on any
    other cleanup code, and the case where the underlying file is not a broken
    pipe, all calls and attributes are proxied.
    """

    # origin: click.utils.PacifyFlushWrapper

    def __init__(self, wrapped: t.IO[t.Any]) -> None:
        self.wrapped = wrapped

    def flush(self) -> None:
        try:
            self.wrapped.flush()
        except OSError as e:
            import errno

            if e.errno != errno.EPIPE:
                raise

    def __getattr__(self, attr: str) -> t.Any:
        return getattr(self.wrapped, attr)


_stdout: t.Optional[IoProxy] = None
_stderr: t.Optional[IoProxy] = None


def get_stdout(require: object = True) -> t.Optional[IoProxy]:
    global _stdout
    if not _stdout:
        if require:
            raise RuntimeError("Stdout proxy is uninitialized")
        return None
    return _stdout


def get_stderr(require=True) -> t.Optional[IoProxy]:
    global _stderr
    if not _stderr:
        if require:
            raise RuntimeError("Stderr proxy is uninitialized")
        return None
    return _stderr


def set_stdout(proxy: IoProxy):
    global _stdout
    _stdout = proxy


def set_stderr(proxy: IoProxy):
    global _stderr
    _stderr = proxy


def init_io(
    stdout: t.IO = sys.stdout,
    stderr: t.IO = sys.stderr,
) -> tuple[IoProxy, IoProxy]:
    global _stdout, _stderr
    if _stdout:
        raise RuntimeError("Stdout proxy is already initialized")
    if _stderr:
        raise RuntimeError("Stderr proxy is already initialized")

    _stdout = IoProxy(stdout)
    _stderr = IoProxy(stderr)
    return _stdout, _stderr


def destroy_io():
    global _stdout, _stderr
    _stdout = None
    _stderr = None
