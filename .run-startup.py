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
pt.echo(
    f":[fg=HiCyan]pytermor :[bold]{pt.__version__}:[-fg]:[-bold]", parse_template=True
)
