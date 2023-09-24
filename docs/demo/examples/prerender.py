import pytermor as pt

subtitle = pt.render("start a working area", pt.Style(fg=pt.cv.YELLOW, bold=True))
subtitle += " (see also: "
subtitle += pt.render("git help tutorial", pt.cv.GREEN)
subtitle += ")"

pt.echo(subtitle)
