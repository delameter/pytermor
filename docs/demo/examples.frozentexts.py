import pytermor as pt

data = [
    ("add", "Add file contents to the index"),
    ("mv", "Move or rename a file, a directory, or a symlink"),
    ("restore", "Restore working tree files"),
]
st = pt.Style(fg=pt.cv.GREEN)

for name, desc in data:
    pt.echo([pt.FrozenText("  ", name, st, width=18, pad=4), desc])
