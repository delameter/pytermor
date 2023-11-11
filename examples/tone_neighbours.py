import pytermor as pt

def tones(col: pt.IColorValue):
    h, s, v = col.hsv
    w = pt.get_terminal_width()//6
    for V in range(max(0, int(100*v-50)),  min(100, int(100*v+50)), 1):
        c_orig = pt.HSV(h, s, V/100)
        c_rgb = pt.ColorRGB.find_closest(c_orig)
        c_256 = pt.Color256.find_closest(c_orig)
        for row in range(3):
            for c in [c_256, c_orig, c_rgb]:
                label = ''
                match row:
                    case 0:
                        label = pt.get_qname(c)
                        align = '<'
                    case 1:
                        label = c.name if isinstance(c, pt.ResolvableColor) else ''
                        label = c.format_value()
                        align = '<'
                    case 2:
                        label = hex(c.int)
                        align = '>'

                st = pt.Style(bg=c).autopick_fg()
                pt.echo(pt.fit(label, w, align=align), st, nl=False)

                if c is c_rgb:
                    print()
#            print(pt.render(''.center(w), pt.Style(bg=col2).autopick_fg()), end='')
#            print(pt.render(''.center(w), pt.Style(bg=col).autopick_fg()), end='')
#            print(pt.render(''.center(w), pt.Style(bg=col3).autopick_fg()))
#            print(pt.render(repr(col2).center(w), pt.Style(bg=col2).autopick_fg()), end='')
#            print(pt.render(repr(col).center(w), pt.Style(bg=col).autopick_fg()), end='')
#            print(pt.render(repr(col3).center(w), pt.Style(bg=col3).autopick_fg()))
#            print(pt.render(''.center(w), pt.Style(bg=col2).autopick_fg()),end='')
#            print(pt.render(''.center(w), pt.Style(bg=col).autopick_fg()), end='')
#            print(pt.render(''.center(w), pt.Style(bg=col3).autopick_fg()))


import sys
args = sys.argv[1:]

if not args:
    args.append('00006c')

while args:
    tones(pt.RGB(int(args.pop(0), 16)))
    print()
