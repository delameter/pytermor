import sys
import pytermor as pt

### --- usage: low-level --- ###

print(f"{pt.SeqIndex.CYAN}imported{pt.SeqIndex.RESET} sys")

### --- usage: mid-level --- ###

st = pt.Style(fg='cyan')
ren = pt.renderer.SgrRenderer()
print(ren.render("imported", st) + " pytermor " + ren.render("as", st) + " pt")

### --- usage: high-level --- ###

# build manually
pt.echo(
    pt.Fragment("python ") +
    pt.Fragment("%s.%s.%s" % sys.version_info[:3], "yellow")
)

# or use templates
pt.echo(f"pytermor :[fg=green]{pt.__version__}:[-fg]", parse_template=True)

