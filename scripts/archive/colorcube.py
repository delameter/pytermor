import time

import matplotlib.axes
import matplotlib.markers
import matplotlib.figure
import matplotlib.pyplot as plt
import pytermor as pt

# plt.style.use("_mpl-gallery")

# Make data
# np.random.seed(19680801)
# n = 10
# rng = np.random.default_rng()
# xs = rng.uniform(0, 255, n)
# ys = rng.uniform(0, 255, n)
# zs = rng.uniform(0, 255, n)


S = 1

last_render = 0
CC = []
cn = 0
mode = "cube"
def edge(r, g, b):
    c = sum(n in (0,255) for n in (r,g,b))
    return c==2
cond = edge
# cond = lambda r, g, b: ((abs(r-b) == 0  and (g == 0 or g == 255 or r == 0 or r ==255)) or ((g == 0 or b == 0) and( b == r or r == 0 or b == 255)))
# cond = lambda r, g, b: ((g == 0 or b == 0 or r == 255))
# cond = lambda r, g, b: (abs(r-b) < 1 or (g == 0 and b >= r))
for r in range(0, 255 + S, S):
    for b in range(0, 255 + S, S):
        for g in range(0, 255 + S, S):
            r = min(r, 255)
            g = min(g, 255)
            b = min(b, 255)
            cn += 1
            if cond(r, g, b):
                CC.append(pt.RGB.from_channels(r, g, (255 - b)).rgb)
            if time.time_ns() - last_render > 5e8:
                last_render = time.time_ns()
                print(f"\r[{pt.format_auto_float((100*cn)/(256**3), 3, False)}%] Preparing", end="")
print(f"\r[DONE] {pt.format_thousand_sep(len(CC))} points")

dist = {
    pt.LAB: 5,
    pt.RGB: 15,
    pt.HSV: 0.1,
    pt.XYZ: 5,
}
for palette in [None, pt.Color16, pt.Color256, pt.ColorRGB]:
    for approx_space in [pt.LAB, pt.RGB, pt.HSV, pt.XYZ]:
        if palette:
            lbl = f"{pt.get_qname(palette)} palette approx. in {pt.get_qname(approx_space)}"
        else:
            lbl = "RGB color cube"
        xyzc = []
        if palette and hasattr(palette, "_approximator"):
            palette._approximator.assign_space(approx_space)
        for (idx, c) in enumerate(CC):
            if time.time_ns() - last_render > 5e8:
                last_render = time.time_ns()
                print(f"\r[{pt.format_auto_float(100*idx/len(CC), 3)}%] {lbl}", end="")
            r, g, b = c
            if palette and hasattr(palette, "find_closest") and approx_space:
                apx = palette.find_closest(c, read_cache=False, write_cache=True)
                C = (cc / 255 for cc in apx.rgb)
            else:
                C = (cc / 255 for cc in c)
            C = (0,0,0)
            xyzc.append((g, b, r, (*C, 1)))
        print("\r[DONE] " + lbl, palette._approximator._stats.format() if palette else "")

        xs, ys, zs, cs = [], [], [], []
        if xyzc:
            xs, ys, zs, cs = zip(*xyzc)
        fig: matplotlib.figure.Figure = plt.figure(
            figsize=(6, 5),
        )
        fig.suptitle(lbl, fontsize=16)
        ax: matplotlib.axes.Axes = fig.add_subplot(111, projection="3d")
        ax.scatter(xs, ys, zs, c=cs, s=2, marker="s", linewidths=0, aa=0)
        ax.set_xlabel("G")
        ax.set_ylabel("B")
        ax.set_zlabel("R")
        ax.view_init(30, 135, 0)

        plt.savefig(f"{mode}_edge2{lbl}.png", dpi=300)
        plt.show()

        if palette is None:
            # plt.show()
            plt.close()
            break
        else:
            plt.close()

            # for angle in range(0, 360*4 + 1):
            #        # Normalize the angle to the range [-180, 180] for display
            #        angle_norm = (angle + 180) % 360 - 180
            #
            #        # Cycle through a full rotation of elevation, then azimuth, roll, and all
            #        elev = azim = roll = 0
            #        if angle <= 360:
            #               elev = angle_norm
            #        elif angle <= 360*2:
            #               azim = angle_norm
            #        elif angle <= 360*3:
            #               roll = angle_norm
            #        else:
            #               elev = azim = roll = angle_norm
            #
            #        # Update the axis view and title
            #        ax.view_init(elev, azim, roll)
            #        plt.title('Elevation: %d°, Azimuth: %d°, Roll: %d°' % (elev, azim, roll))
            #
            #        plt.draw()
            #        plt.pause(.0001)
