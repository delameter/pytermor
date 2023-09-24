import pytermor as pt

subtitle_st = pt.Style(fg=pt.cv.YELLOW, bold=True)
command_st = pt.Style(fg=pt.cv.GREEN)
text = pt.FrozenText(
    ("work on the current change ", subtitle_st),
    "(see also: ",
    "git help everyday", command_st,
    ")"
)
pt.echo(text)
