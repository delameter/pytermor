# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under GNU Lesser General Public License v3.0
# -----------------------------------------------------------------------------
import sys

import pytermor as pt
from examples import *

# --- usage: low-level ---

print(pt.make_clear_display(), end='')
print(pt.make_reset_cursor(), end='')
print(f"{pt.SeqIndex.CYAN}imported{pt.SeqIndex.RESET} sys")

# --- usage: high-level --- #

# render by parts
st = pt.Style(fg="cyan")
ren = pt.renderer.SgrRenderer()
print(ren.render("imported", st) + " pytermor " + ren.render("as", st) + " pt")

# build as fragments
pt.echo(pt.Fragment("imported ", st) + pt.Fragment("examples.*"))

# or use templates
te = pt.TemplateEngine()
pt.echo(te.substitute(
    f"@name:[icathian-yellow]" "@v:[superuser]" "@upd:[dim]"
    f":[name bold]pytermor:[-] "
    f":[v]{pt.__version__}:[-] "
    f":[upd]({pt.__updated__}):[-]"
))

