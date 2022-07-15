import sys
import timeit
from ctypes import sizeof
from typing import Tuple

import PIL.ImageFont

from pytermor import color, sequence, ColorRGB, ColorIndexed, ColorDefault
from math import floor
import profile
import gc
import sys
from PIL import Image
from PIL.ImageFont import ImageFont


# from https://stackoverflow.com/a/53705610/5834973
def get_obj_size(obj):
    marked = {id(obj)}
    obj_q = [obj]
    sz = 0

    while obj_q:
        sz += sum(map(sys.getsizeof, obj_q))

        # Lookup all the object referred to by the object in obj_q.
        # See: https://docs.python.org/3.7/library/gc.html#gc.get_referents
        all_refr = ((id(o), o) for o in gc.get_referents(*obj_q))

        # Filter object that are already marked.
        # Using dict notation will prevent repeated objects.
        new_refr = {o_id: o for o_id, o in all_refr if
                    o_id not in marked and not isinstance(o, type)}

        # The new obj_q will be the ones that were not marked,
        # and we will update marked with their ids so we will
        # not traverse them again.
        obj_q = new_refr.values()
        marked.update(new_refr.keys())

    return sz


def lab2rgb(l_s: float, a_s: float, b_s: float) -> Tuple[float, float, float]:
    var_Y: float = (l_s + 16.) / 116.
    var_X: float = a_s / 500. + var_Y
    var_Z: float = var_Y - b_s / 200.

    if pow(var_Y, 3) > 0.008856:
        var_Y = pow(var_Y, 3)
    else:
        var_Y = (var_Y - 16. / 116.) / 7.787
    if pow(var_X, 3) > 0.008856:
        var_X = pow(var_X, 3)
    else:
        var_X = (var_X - 16. / 116.) / 7.787
    if pow(var_Z, 3) > 0.008856:
        var_Z = pow(var_Z, 3)
    else:
        var_Z = (var_Z - 16. / 116.) / 7.787

    X: float = 95.047 * var_X  # ref_X =  95.047     Observer= 2°, Illuminant= D65
    Y: float = 100.000 * var_Y  # ref_Y = 100.000
    Z: float = 108.883 * var_Z  # ref_Z = 108.883

    var_X = X / 100.  # X from 0 to  95.047      (Observer = 2°, Illuminant = D65)
    var_Y = Y / 100.  # Y from 0 to 100.000
    var_Z = Z / 100.  # Z from 0 to 108.883

    var_R: float = var_X * 3.2406 + var_Y * -1.5372 + var_Z * -0.4986
    var_G: float = var_X * -0.9689 + var_Y * 1.8758 + var_Z * 0.0415
    var_B: float = var_X * 0.0557 + var_Y * -0.2040 + var_Z * 1.0570

    if var_R > 0.0031308:
        var_R = 1.055 * pow(var_R, (1 / 2.4)) - 0.055
    else:
        var_R = 12.92 * var_R
    if var_G > 0.0031308:
        var_G = 1.055 * pow(var_G, (1 / 2.4)) - 0.055
    else:
        var_G = 12.92 * var_G
    if var_B > 0.0031308:
        var_B = 1.055 * pow(var_B, (1 / 2.4)) - 0.055
    else:
        var_B = 12.92 * var_B

    return (var_R * 255.), (var_G * 255.), (var_B * 255.)


def hsv_to_rgb(h, s, v):
    if s == 0.0: v *= 255; return (v, v, v)
    i = int(h * 6.)  # XXX assume int() truncates!
    f = (h * 6.) - i;
    p, q, t = int(255 * (v * (1. - s))), int(255 * (v * (1. - s * f))), int(
        255 * (v * (1. - s * (1. - f))));
    v *= 255;
    i %= 6
    if i == 0: return (v, t, p)
    if i == 1: return (q, v, p)
    if i == 2: return (p, v, t)
    if i == 3: return (p, q, v)
    if i == 4: return (t, p, v)
    if i == 5: return (v, p, q)


reset = sequence.RESET.encode()


def render_terminal(params_to_rgb_fn):
    for v in range(0, 100, 2):
        t = ['', '', '']
        for h in range(0, 360, 2):
            r, g, b = params_to_rgb_fn(h, v)
            hex = (floor(r) << 16) + (floor(g) << 8) + floor(b)
            t[0] += ColorRGB(hex).to_sgr_rgb(bg=True).encode() + ' '
            t[1] += ColorRGB(hex).to_sgr_indexed(bg=True).encode() + ' '
            t[2] += ColorRGB(hex).to_sgr_default(bg=True).encode() + ' '
        print(f'{reset}  '.join(t) + reset, file=sys.stdout)


image_id = 0
from PIL import ImageDraw


def render_image(params_to_rgb_fn, title):
    im = Image.new('RGB', (360 * 3, 380))
    ImageDraw.Draw(im).text((0, 360), title)
    for y in range(0, 360, 1):
        v = y / 3.6
        for x in range(0, 360, 1):
            h = x
            r, g, b = params_to_rgb_fn(h, v)
            hex = (floor(r) << 16) + (floor(g) << 8) + floor(b)
            im.putpixel((x, y), hex)
            im.putpixel((360 + x, y), ColorIndexed.find_closest(hex).hex_value)
            im.putpixel((720 + x, y), ColorDefault.find_closest(hex).hex_value)

    global image_id
    im.save(f'approx/im{image_id:d}.png')
    print(f'Created image {image_id:d}')
    image_id += 1


def run_image():
    render_image(lambda h, v: hsv_to_rgb(h / 360, 1, v / 100),
                 'H=[0,360], S=1, V=[0,1]')
    render_image(lambda h, v: hsv_to_rgb(h / 360, .5, v / 100),
                 'H=[0,360], S=0.5, V=[0,1]')
    render_image(lambda h, v: hsv_to_rgb(h / 360, .25, v / 100),
                 'H=[0,360], S=0.25, V=[0,1]')
    render_image(lambda h, v: hsv_to_rgb(h / 360, 0, v / 100),
                 'H=[0,360], S=0, V=[0,1]')
    render_image(lambda h, v: hsv_to_rgb(h / 360, v / 100, 1),
                 'H=[0,360], S=[0,1], V=1')
    render_image(lambda h, v: hsv_to_rgb(h / 360, v / 100, .5),
                 'H=[0,360], S=[0,1], V=0.5')
    render_image(lambda h, v: hsv_to_rgb(h / 360, v / 100, .25),
                 'H=[0,360], S=[0,1], V=0.25')
    render_image(lambda h, v: hsv_to_rgb(.0, v / 100, h / 360),
                 'H=0, S=[0,1], V=[0,1]')
    render_image(lambda h, v: hsv_to_rgb(.166, v / 100, h / 360),
                 'H=60, S=[0,1], V=[0,1]')
    render_image(lambda h, v: hsv_to_rgb(.33, v / 100, h / 360),
                 'H=120, S=[0,1], V=[0,1]')
    render_image(lambda h, v: hsv_to_rgb(.5, v / 100, h / 360),
                 'H=180, S=[0,1], V=[0,1]')
    render_image(lambda h, v: hsv_to_rgb(.66, v / 100, h / 360),
                 'H=240, S=[0,1], V=[0,1]')
    render_image(lambda h, v: hsv_to_rgb(.833, v / 100, h / 360),
                 'H=300, S=[0,1], V=[0,1]')


def run_terminal():
    print(f'{"ColorRGB":^72s}  {"ColorIndexed":^72s}  {"ColorDefault":^72s}')

    render_terminal(lambda h, v: hsv_to_rgb(h / 360, 1, v / 100))
    print()

    render_terminal(lambda h, v: hsv_to_rgb(h / 360, .5, v / 100))
    print()

    render_terminal(lambda h, v: hsv_to_rgb(h / 360, .25, v / 100))
    print()

    render_terminal(lambda h, v: hsv_to_rgb(h / 360, v / 100, 1))
    print()

    render_terminal(lambda h, v: hsv_to_rgb(h / 360, v / 100, .5))
    print()

    render_terminal(lambda h, v: hsv_to_rgb(h / 360, v / 100, .25))
    print()

    render_terminal(lambda h, v: hsv_to_rgb(h / 360, 0, v / 100))
    print()

    render_terminal(lambda h, v: hsv_to_rgb(.0, v / 100, h / 360))
    print()

    render_terminal(lambda h, v: hsv_to_rgb(.166, v / 100, h / 360))
    print()

    render_terminal(lambda h, v: hsv_to_rgb(.33, v / 100, h / 360))
    print()

    render_terminal(lambda h, v: hsv_to_rgb(.5, v / 100, h / 360))
    print()

    render_terminal(lambda h, v: hsv_to_rgb(.66, v / 100, h / 360))
    print()

    render_terminal(lambda h, v: hsv_to_rgb(.833, v / 100, h / 360))
    print()


if __name__ == '__main__':
    # ss = timeit.repeat(run_image, number=1, repeat=1)
    # print(ss)
    # print(get_obj_size(ColorRGB._color_map))
    # print(get_obj_size(ColorDefault._color_map))

    LABEL_HEIGHT = 50

    inp = Image.open('_include/approx/input-bgwhite.png', 'r')
    samples = [
        (None, '(16M colors)'),
        (ColorIndexed, '(256 colors)'),
        (ColorDefault, '(16 colors)'),
    ]
    font_header = PIL.ImageFont.truetype('../docs/_static/fonts/mononoki-Bold.ttf', size=16)
    font_default = PIL.ImageFont.truetype('../docs/_static/fonts/mononoki-Regular.ttf', size=12)

    im = Image.new('RGB', size=(inp.width * len(samples), inp.height + LABEL_HEIGHT), color=(255, 255, 255))
    for ids, (s, caption) in enumerate(samples):
        x1 = ids * inp.width
        x2 = (ids + 1) * inp.height
        y1 = 0
        y2 = inp.height

        if s is None:
            im.paste(inp, (x1, y1))
        else:
            for va in range(0, inp.width, 1):
                for vb in range(0, inp.height, 1):
                    (r, g, b) = inp.getpixel((va, vb))
                    c = s.find_closest((r << 16) + (g << 8) + b)
                    im.putpixel((x1 + va, y1 + vb), c.hex_value_to_rgb_channels(c.hex_value))

                if va%(inp.width//100) == 0:
                    perc = 1+round(100*va/inp.width)
                    print(f'\rSample {ids+1}/{len(samples)}: {perc:>3d}%',
                          end=f' [{"#"*perc}{"."*(100-perc)}]')
            print()

        ImageDraw.Draw(im).text(
            (x1 + inp.width/2, y2 + LABEL_HEIGHT/4),
            anchor='mm', font=font_header, fill=(0, 0, 0),
            text=(s.__name__ if s else ColorRGB.__name__) + ' class')

        ImageDraw.Draw(im).text(
            (x1 + inp.width/2, y2 + LABEL_HEIGHT/1.75),
            anchor='mm', font=font_default, fill=(0, 0, 0),
            text=caption)

    im.save('_include/approx/output-bgwhite.png')
