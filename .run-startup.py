# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under GNU Lesser General Public License v3.0
# -----------------------------------------------------------------------------
import sys
import pytermor as pt
from examples import *

pt.init_config()
pt.init_renderer()

# --- usage: low-level ---

pt.echo(pt.make_clear_display().assemble(), nl=False)
pt.echo(pt.make_reset_cursor().assemble(), nl=False)
pt.echo(f"{pt.SeqIndex.CYAN}imported{pt.SeqIndex.RESET} sys")

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
    f"@name:[icathian-yellow bold]" "@v:[superuser]" "@upd:[dim]"
    f""
    f":[name]pytermor:[-] "
    f":[v]{pt.__version__}:[-] "
    f":[upd]({pt.__updated__}):[-]"
))

