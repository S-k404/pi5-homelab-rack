"""Measure Waveshare's adapter (F) dimension drawing by pixel analysis (not by eye)."""
import sys
import numpy as np
from PIL import Image

im = np.asarray(Image.open(sys.argv[1]).convert("RGB")).astype(int)
H, W, _ = im.shape
R, G, B = im[..., 0], im[..., 1], im[..., 2]
mx, mn = im.max(-1), im.min(-1)
grey_line = (mx < 170) & (mx - mn < 25)            # thin dimension / extension lines (grey on white)


def runs(mask1d, minlen=1):
    idx = np.flatnonzero(mask1d)
    if not len(idx):
        return []
    out, s = [], idx[0]
    for a, b in zip(idx, idx[1:]):
        if b != a + 1:
            out.append((s, a)); s = b
    out.append((s, idx[-1]))
    return [(a, b) for a, b in out if b - a + 1 >= minlen]


# vertical extension lines in the top margin (rows 20..95): x of the 86 / 85 dimension ends
top = grey_line[20:95].sum(0)
vx = [((a + b) / 2) for a, b in runs(top > 40)]
# vertical extension lines in the bottom margin (rows 470..545): the 58 dimension (hole centres)
bot = grey_line[470:545].sum(0)
bx = [((a + b) / 2) for a, b in runs(bot > 35)]
# horizontal extension lines left (cols 95..170) and right (cols 780..900)
lh = grey_line[:, 95:170].sum(1)
ly = [((a + b) / 2) for a, b in runs(lh > 40)]
rh = grey_line[:, 790:900].sum(1)
ry = [((a + b) / 2) for a, b in runs(rh > 40)]
print("top extension x:", vx)
print("bottom extension x:", bx)
print("left extension y:", ly)
print("right extension y:", ry)
