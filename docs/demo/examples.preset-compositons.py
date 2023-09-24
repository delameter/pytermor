import pytermor as pt

col_sgr = pt.make_color_256(214, pt.ColorTarget.BG) + pt.ansi.SeqIndex.BLACK
seq = pt.compose_clear_line_fill_bg(col_sgr)
pt.echo(seq + 'AAAA    BBBB')
