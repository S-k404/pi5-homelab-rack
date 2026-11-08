import sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

im = np.asarray(Image.open(sys.argv[1]).convert("RGB")).astype(int)
R, G, B = im[..., 0], im[..., 1], im[..., 2]
mx, mn = im.max(-1), im.min(-1)


def blob_bbox(mask, near, min_px=150):
    """bbox of the connected blob of mask closest to point `near` (x, y)."""
    lab, n = ndi.label(ndi.binary_closing(mask, iterations=1))
    best = None
    for i, sl in enumerate(ndi.find_objects(lab), 1):
        if (lab[sl] == i).sum() < min_px:
            continue
        cy, cx = (sl[0].start + sl[0].stop) / 2, (sl[1].start + sl[1].stop) / 2
        d = np.hypot(cx - near[0], cy - near[1])
        if best is None or d < best[0]:
            best = (d, sl)
    sl = best[1]
    return sl[1].start, sl[1].stop - 1, sl[0].start, sl[0].stop - 1


gold = (R > 150) & (G > 100) & (B < 110) & (R - B > 70)
green = (G > 120) & (G - R > 40) & (G - B > 30)
silver = (mn > 120) & (mx - mn < 28) & (mx < 245)       # metal shells (not the white background)
white_conn = (mn > 200) & (R - B > 8)                    # cream connector housings
feats = {
    "HDMI-A jack (gold)": blob_bbox(gold, (200, 390)),
    "micro-HDMI plug (gold)": blob_bbox(gold, (582, 450)),
    "terminal (green)": blob_bbox(green, (790, 380)),
    "RJ45 shell (silver)": blob_bbox(silver, (230, 250)),
    "PWR rod (silver)": blob_bbox(silver, (200, 146), min_px=60),
    "USB-C plug (silver)": blob_bbox(silver, (680, 465)),
}
for k, (x0, x1, y0, y1) in feats.items():
    print(f"{k:24s} px x {x0}..{x1}  y {y0}..{y1}")
