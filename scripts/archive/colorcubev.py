import math

import matplotlib.markers
import matplotlib.pyplot as plt
import pytermor as pt
plt.style.use('_mpl-gallery')

# Make data
# np.random.seed(19680801)
# n = 10
# rng = np.random.default_rng()
# xs = rng.uniform(0, 255, n)
# ys = rng.uniform(0, 255, n)
# zs = rng.uniform(0, 255, n)
CC = []
S = 5
palette = pt.LAB
pt.ColorRGB._approximator.assign_space(palette)
pt.cvr.AIR_FORCE_BLUE
for c in [*pt.Color256]: #, *pt.ColorRGB]:
    r,g,b = c.rgb
    print(r,g,b,end='\r')
    CC.append(pt.RGB.from_channels(r,g,b))
CC.append(pt.RGB.from_channels(255,255,255))

CC.clear()
for h in range(0,360):
    for s in range(0,100+S,S):
        for v in range(0,100+S,S):
            CC.append(pt.HSV(h,s/100,v/100))
for fm in matplotlib.markers.MarkerStyle.filled_markers:
    print(fm)
xyzc = []
for idx,c in enumerate(CC):
    print(f'\r{100*idx/len(CC):3.1f}',end="")
    apx = pt.Color256._approximator.find_closest(c, read_cache=False, write_cache=True)
    h,s,v = c.hsv
    r = 2*math.pi*h/360
    x, y = s * math.cos(r), s * math.sin(r)
    z = v
    xyzc.append(
        (x,y,z, (*(cc/255 for cc in apx.rgb),1,), )
    )
xs, ys, zs, cs = zip(*xyzc)
# xs, ys, zs, cs = zip(*[(*c.rgb, (*(cc/255 for cc in c.rgb),)) for c in CC])

for m in "s":# ".ov^<>8sp*hHDdPX" :
    # Plot
    # fig, ax = plt.subplots(subplot_kw={"projection": "3d"})
    fig = plt.figure(figsize=(6,5))
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(xs, ys, zs, c=cs, s=40, marker='s')#, linewidths=1, edgecolors=(0,0,0))#cmap='hsv')
    ax.set_zlabel('V')
    ax.view_init(25, 25, 0)

    plt.savefig('z.png', dpi=300)
    plt.show()
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