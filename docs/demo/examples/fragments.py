from collections.abc import Iterable
import pytermor as pt

data = [
    ("clone", "Clone a repository into a new directory"),
    ("init", "Create an empty Git repository or reinitialize an existing one"),
]

st = pt.Style(fg=pt.cv.GREEN)
for name, desc in data:
    frag = pt.Fragment(name.ljust(16), st)
    pt.echo('  ' + frag + desc)
