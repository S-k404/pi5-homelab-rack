import sys
import numpy as np
from PIL import Image
im = np.asarray(Image.open(sys.argv[1]).convert("RGB")).astype(int)
mx, mn = im.max(-1), im.min(-1)
white = mn > 235                       # background seen through the hole
silver = (mn > 120) & (mx - mn < 30) & ~white
for name, (cx, cy) in {"top-left": (337.5, 119.5), "top-right": (729.5, 119.5),
                       "bottom-left": (337.5, 437), "bottom-right": (729.5, 437)}.items():
    x0, y0 = int(cx) - 25, int(cy) - 25
    w = white[y0:y0 + 50, x0:x0 + 50]
    s = silver[y0:y0 + 50, x0:x0 + 50] | w
    # inner white disc and outer ring: equivalent diameters from areas, centre from the white disc
    yy, xx = np.nonzero(w)
    keep = np.hypot(xx - 25, yy - 25) < 12
    yy, xx = yy[keep], xx[keep]
    d_in = 2 * np.sqrt(len(yy) / np.pi)
    ys, xs = np.nonzero(s)
    keep2 = np.hypot(xs - 25, ys - 25) < 22
    d_out = 2 * np.sqrt(keep2.sum() / np.pi)
    print(f"{name:12s} hole centre x {x0 + xx.mean():.1f} y {y0 + yy.mean():.1f}  hole d {d_in:.1f} px  ring d {d_out:.1f} px  "
          f"-> hole {d_in / 6.78:.2f} mm, pad {d_out / 6.78:.2f} mm")
