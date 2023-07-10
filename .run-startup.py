#!venv/bin/python
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
#   imported examples.*
#   python   3.10.11 (main, Apr  5 2023, 14:15:10)
#   pytermor 2.75.0.dev0 (2023-06-02 20:56:27+03:00)
#   >>>
#
# To launch it, run this command: './run-cli' from the project root.
# If you didn't initialized venv, the script will try to do it by itself.
# -----------------------------------------------------------------------------

import re
import sys

import pytermor as pt
from examples import *  # noqa
from rich import inspect as _  # noqa

pt.init_config()
pt.init_renderer()


# EXAMPLE USAGE / LOW LEVEL
# ---------------------------------------------------------

# (1) build sequence instances directly (don't):
print(pt.SequenceCSI('J', 2).assemble(), end='')   # clears the whole terminal

# (2) assemble and combine sequences manually:
pt.echo(pt.make_reset_cursor().assemble(), nl=False)
print(f"{pt.SeqIndex.CYAN}imported{pt.SeqIndex.RESET} rich.inspect", end='')

# (3) or semi-automatically (renderer terminates the formatting):
pt.echo(pt.enclose(pt.SeqIndex.CYAN, " as ")+"_")


# EXAMPLE USAGE / HIGH ABSTRACTION LEVEL
# ---------------------------------------------------------

# 4) render separately and combine..
st = pt.Style(fg="cyan")
ren = pt.renderer.SgrRenderer()
print(ren.render("imported", st) + " pytermor " + ren.render("as", st) + " pt")

# 5) or build as fragments..
pt.echo(
    pt.Fragment("imported ", st) +
    pt.Fragment("examples.") +
    pt.Fragment("*", pt.Style(st, bold=True))
)

# 6) or replace regex groups..
pt.echo(re.sub(
    r'([\d.]{5,})|(\(.+?\))|\[.+?\]',
    pt.render(r'\1', 'green') +
    pt.render(r'\2', 'gray35'),
    'python   '+sys.version)
)

# 7) or utilize the templates
te = pt.TemplateEngine()
pt.echo(te.substitute(
    f"@v:[diamond]"
    f"@upd:[gray35]"
    f"pytermor "
    f":[v]{pt.__version__}:[-] "
    f":[upd]({pt.__updated__}):[-]"
))
