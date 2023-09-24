import pytermor as pt

col = pt.RGB(0xDA9AC4)
for v in [col.rgb, col.hsv, col.xyz, col.lab]:
    print(repr(v))
