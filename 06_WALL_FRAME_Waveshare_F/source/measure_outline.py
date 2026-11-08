import sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

im = np.asarray(Image.open(sys.argv[1]).convert("RGB")).astype(int)
mx, mn = im.max(-1), im.min(-1)
black = (mx < 70)
# the board: biggest dark blob (fill holes so parts on it count)
lab, n = ndi.label(ndi.binary_closing(black, iterations=3))
sizes = ndi.sum(np.ones_like(lab), lab, range(1, n + 1))
board = lab == (1 + int(np.argmax(sizes)))
board = ndi.binary_fill_holes(board)
ys, xs = np.nonzero(board)
print("board bbox x %d..%d  y %d..%d" % (xs.min(), xs.max(), ys.min(), ys.max()))
# bottom / top edge profile (every 20 px), left / right edge profile
for x in range(180, 760, 20):
    col = np.flatnonzero(board[:, x])
    if len(col):
        print(f"x {x:3d}: top {col.min():3d} bottom {col.max():3d}")
for y in range(105, 460, 25):
    row = np.flatnonzero(board[y])
    if len(row):
        print(f"y {y:3d}: left {row.min():3d} right {row.max():3d}")
# the four silver hole rings: light, low-saturation blobs, roughly round, ~25-35 px across
light = (mn > 150) & (mx - mn < 30)
lab2, n2 = ndi.label(light)
for i, sl in enumerate(ndi.find_objects(lab2), 1):
    h, w = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
    if 20 <= h <= 40 and 20 <= w <= 40 and abs(h - w) <= 4:
        yy, xx = np.nonzero(lab2[sl] == i)
        print(f"ring at x {sl[1].start + (w - 1) / 2:.1f}, y {sl[0].start + (h - 1) / 2:.1f}  ({w}x{h} px)")
