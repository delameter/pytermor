import pytermor as pt

for outm in ['xterm_16', 'xterm_256', 'true_color']:
    print(' '+outm.ljust(12), end="")
    for c in range((W := 80) + 1):
        b = pt.RGB.from_ratios(1 - (p := c / W), 2 * min(p, 1 - p), p).int
        f = pt.Fragment(" ·"[c & 1], pt.Style(fg=(1 << 24) - b, bg=b, bold=True))
        print(f.render(pt.SgrRenderer(outm)), end=["", 2*"\n"][c >= W], flush=True)
