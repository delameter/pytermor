# -----------------------------------------------------------------------------
# pytermor [ANSI formatted terminal output toolset]
# (C) 2022 A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
from . import ReplaceSGR


def ljust_fmtd(s: str, width: int, fillchar: str = ' ') -> str:
    """
    Correctly justifies input that can include SGR sequences. Apart from
    that is very similar to regular str.ljust().

    :param s: string to extend
    :param width: target string length
    :param fillchar: append this char to target
    :return: **s** padded to the left side with *fillchars* so that now it's
            length corresponds to *width*
    """
    sanitized = ReplaceSGR().apply(s)
    return s + fillchar * max(0, width - len(sanitized))


def rjust_fmtd(s: str, width: int, fillchar: str = ' ') -> str:
    """
    SGR-aware implementation of str.rjust(). @see: ljust_fmtd
    """
    sanitized = ReplaceSGR().apply(s)
    return fillchar * max(0, width - len(sanitized)) + s


def center_fmtd(s: str, width: int, fillchar: str = ' ') -> str:
    """
    SGR-aware implementation of str.rjust().

    .. seealso:: ljust_fmtd
    .. note:: blabla
    .. todo:: blabla
    """
    sanitized = ReplaceSGR().apply(s)
    fill_len = max(0, width - len(sanitized))
    if fill_len == 0:
        return s
    right_fill_len = fill_len // 2
    left_fill_len = fill_len - right_fill_len
    return (fillchar * left_fill_len) + s + (fillchar * right_fill_len)
