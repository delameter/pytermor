# -----------------------------------------------------------------------------
#  pytermor [ANSI formatted terminal output toolset]
#  (c) 2022-2023. A. Shavykin <0.delameter@gmail.com>
#  Licensed under GNU Lesser General Public License v3.0
# -----------------------------------------------------------------------------
import sys

import pytermor as pt

# --- usage: low-level ---

print(f"{pt.SeqIndex.CYAN}imported{pt.SeqIndex.RESET} sys")

# --- usage: mid-level ---

st = pt.Style(fg="cyan")
ren = pt.renderer.SgrRenderer()
print(ren.render("imported", st) + " pytermor " + ren.render("as", st) + " pt")

# --- usage: high-level --- #

# build manually
pt.echo(pt.Fragment("imported ", st) + pt.Fragment("examples.*"))

# or use templates
te = pt.TemplateEngine()
pt.echo(te.substitute(
    f"@name:[fg=icathian_yellow]@version:[fg=superuser]"
    f":[name bold]pytermor :[version]{pt.__version__}:[-version]:[-bold] {pt.__updated__}:[-name]"
))

