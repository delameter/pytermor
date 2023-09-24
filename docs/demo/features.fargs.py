import pytermor as pt

ex_st = pt.Style(bg='#ffff00', fg='black')
text = pt.FrozenText(
    'This is red ', pt.cv.RED,
    "This is white ",
    "This is black on yellow", ex_st,
)
pt.echo(text)
