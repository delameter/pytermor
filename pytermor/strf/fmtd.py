# -----------------------------------------------------------------------------
# pytermor [ANSI formatted terminal output toolset]
# (C) 2022 A. Shavykin <0.delameter@gmail.com>
# -----------------------------------------------------------------------------
from . import ReplaceSGR


def ljust_fmtd(s: str, width: int, fillchar: str = ' ') -> str:
    """
    SGR-formatting-aware implementation of str.ljust().

    Return a left-justified string of length width. Padding is done
    using the specified fill character (default is a space).
    """
    sanitized = ReplaceSGR().apply(s)
    return s + fillchar * max(0, width - len(sanitized))


def rjust_fmtd(s: str, width: int, fillchar: str = ' ') -> str:
    """
    SGR-formatting-aware implementation of str.rjust().

    Return a right-justified string of length width. Padding is done
    using the specified fill character (default is a space).
    """
    sanitized = ReplaceSGR().apply(s)
    return fillchar * max(0, width - len(sanitized)) + s


def center_fmtd(s: str, width: int, fillchar: str = ' ') -> str:
    """
    SGR-formatting-aware implementation of str.center().

    Return a centered string of length width. Padding is done using the
    specified fill character (default is a space).
    """
    sanitized = ReplaceSGR().apply(s)
    fill_len = max(0, width - len(sanitized))
    if fill_len == 0:
        return s
    right_fill_len = fill_len // 2
    left_fill_len = fill_len - right_fill_len
    return (fillchar * left_fill_len) + s + (fillchar * right_fill_len)
