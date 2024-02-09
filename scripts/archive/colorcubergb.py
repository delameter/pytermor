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
S = 2
pt.ColorRGB._approximator.assign_space(pt.HSV)
pt.cvr.AIR_FORCE_BLUE
for c in [*pt.Color256]: #, *pt.ColorRGB]:
    r,g,b = c.rgb
    print(r,g,b,end='\r')
    CC.append(pt.RGB.from_channels(r,g,b))
CC.append(pt.RGB.from_channels(255,255,255))
for fm in matplotlib.markers.MarkerStyle.filled_markers:
       print(fm)
xyzc = []
for c in CC:
   h,s,v = c.hsv
   xyzc.append(
          (2*h*3.14/360,v+s,s*100, (*(cc/255 for cc in c.rgb),), )
   )
xs, ys, zs, cs = zip(*xyzc)
# xs, ys, zs, cs = zip(*[(*c.rgb, (*(cc/255 for cc in c.rgb),)) for c in CC])

for m in "s":# ".ov^<>8sp*hHDdPX" :
    # Plot
    # fig, ax = plt.subplots(subplot_kw={"projection": "3d"})
    fig = plt.figure(figsize=(6,5))
    ax = fig.add_subplot(111, projection='polar')
    ax.scatter(xs, ys, s=zs, c=cs, linewidths=1, edgecolors=(0,0,0))#cmap='hsv')
    ax.set_xlabel('R')
    ax.set_ylabel('G')
    ax.set_label('B')
    # ax.view_init(25, 25, 0)

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
