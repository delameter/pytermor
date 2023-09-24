import pytermor as pt

def tones(col: pt.IColorValue):
    h,s,v = col.hsv
    for V in range(max(0, int(100*v-50)),  min(100, int(100*v+50)), 1):
            col = pt.HSV(h, s, V/100)
            col2 = pt.ColorRGB.find_closest(col)
            col3 = pt.Color256.find_closest(col)
            w = pt.get_terminal_width()//3
            print(pt.render(''.center(w), pt.Style(bg=col2)), end='')
            print(pt.render(''.center(w), pt.Style(bg=col)), end='')
            print(pt.render(''.center(w), pt.Style(bg=col3)))
            print(pt.render(repr(col2).center(w), pt.Style(bg=col2)), end='')
            print(pt.render(repr(col).center(w), pt.Style(bg=col)), end='')
            print(pt.render(repr(col3).center(w), pt.Style(bg=col3)))
            print(pt.render(''.center(w), pt.Style(bg=col2)),end='')
            print(pt.render(''.center(w), pt.Style(bg=col)), end='')
            print(pt.render(''.center(w), pt.Style(bg=col3)))


import sys
sys.argv.pop(0)

if not sys.argv:
    sys.argv.append(0x00006c)

while sys.argv:
    tones(pt.RGB(int(sys.argv.pop(0), 16)))
    print()
