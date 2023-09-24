import pytermor as pt

data = [
    ("bisect", "Use binary search to find the commit that introduced a bug"),
    ("diff", "Show changes between commits, commit and working tree, etc"),
    ("grep", "Print lines matching a pattern"),
]

st = pt.Style(fg=pt.cv.GREEN)
for name, desc in data:
    frag = pt.Fragment(name, st)
    pt.echo(f"  {frag:<16s}    {desc}")
