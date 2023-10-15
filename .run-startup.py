#!venv-demo/bin/python
# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under GNU Lesser General Public License v3.0
# -----------------------------------------------------------------------------
# In this example we implement the output of several lines of formatted text at
# the moment of this script execution, using different approaches from the lib.
# In general the result should look like this (except that it will be colored):
#
#   imported rich.inspect as _
#   imported pytermor as pt
#   imported re, sys
#   imported examples.*
#   python   3.10.11 (main, Apr  5 2023, 14:15:10)
#   pytermor 2.75.0.dev0 (2023-06-02 20:56:27+03:00)
#
#       print_self()  display the startup script source code
#    print_history()  display python console history
#
#   >>>
#
# To launch it, run this command: './run-cli' from the project root.
# If you didn't initialized venv, the script will try to do it by itself.
# -----------------------------------------------------------------------------

try:
    from rich import inspect as _
except ImportError:
    _ = print

import pytermor as pt
import signal, re, sys
from examples import *  # noqa

signal.signal(signal.SIGINT, signal.SIG_DFL)  # for ^C to terminate the demo instantly


# EXAMPLE USAGE / LOW ABSTRACTION LEVEL
# ---------------------------------------------------------

# (1) build sequence instances directly (don't):
print(pt.SequenceCSI("J", 2).assemble(), end="")  # clears the whole terminal

# (2) assemble and combine sequences manually:
pt.echo(pt.make_reset_cursor().assemble(), nl=False)
print(f"{pt.SeqIndex.CYAN}imported{pt.SeqIndex.RESET} rich.inspect", end="")

# (3) or semi-automatically (renderer terminates the formatting):
pt.echo(pt.enclose(pt.SeqIndex.CYAN, " as ") + "_")


# EXAMPLE USAGE / HIGH ABSTRACTION LEVEL
# ---------------------------------------------------------

# 4) render separately and combine..
st = pt.Style(fg="cyan")
ren = pt.renderer.SgrRenderer()
print(ren.render("imported", st) + " pytermor " + ren.render("as", st) + " pt")

# 5) or build as fragments..
pt.echo(pt.Fragment("imported ", st) + "signal, re, sys")

# 6) or build as text..
pt.echo(
    pt.Text(
        "imported ",
        st,
        "examples.",
        pt.NOOP_STYLE,
        "*",
        pt.Style(st, bold=True),
    )
)

# 7) or replace regex groups..
pt.echo(
    re.sub(
        r"([\d.]{5,})|(\(.+?\))|\[.+?\]",
        pt.render(r"\1", pt.Style(fg="hi-green", bold=True)) + pt.render(r"\2", "gray35"),
        "python   " + sys.version,
    )
)

# 8) or utilize the templates..
te = pt.TemplateEngine()
pt.echo(
    te.substitute(
        f"@v:[diamond bold]"
        f"@upd:[gray35]"
        f"pytermor "
        f":[v]{pt.__version__}:[-] "
        f":[upd]({pt.__updated__}):[-]"
        f"\n"
    )
)

# 9) or utilize f-strings
pfn_st = pt.Style(fg="magenta")
pdemo_text = pt.Fragment("print_self", pfn_st)
pt.echo(f"{pdemo_text:>14s}()  display the startup script source code")

# 10) or use FrozenText class supporting aligning and padding
pt.echo(pt.FrozenText("print_history", pfn_st, "()", width=16, align="right"), nl=False)
pt.echo(pt.pad(2) + "display python console history\n")


# some utility functions
# ---------------------------------------------------------
def print_history():
    import readline

    termw = pt.get_terminal_width()
    maxn = readline.get_current_history_length()
    nlen = len(str(maxn))
    ilen = termw - nlen - 1
    n = 1
    while (n := n + 1) <= maxn:
        num_frag = pt.Fragment(str(n), pt.Style(fg="green", bold=True))
        item_frag = highlight(readline.get_history_item(n).strip()[:ilen])
        pt.echo(f"{num_frag:>{nlen}s} {item_frag:s}", nl=False)


def print_self():
    with open(".run-startup.py", "rt") as f:
        print(highlight(f.read()), pt.SeqIndex.RESET)


def highlight(text: str):
    try:
        import pygments
        from pygments.lexers import get_lexer_for_filename
        from pygments.formatters import Terminal256Formatter
    except ImportError:
        return text
    else:
        lexer = get_lexer_for_filename(".py")
        fmter = Terminal256Formatter(style="manni")
        return pygments.highlight(text, lexer=lexer, formatter=fmter)
