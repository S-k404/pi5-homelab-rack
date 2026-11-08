import sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

im = np.asarray(Image.open(sys.argv[1]).convert("RGB")).astype(int)
R, G, B = im[..., 0], im[..., 1], im[..., 2]
mx, mn = im.max(-1), im.min(-1)
for p in [(190, 390), (200, 360), (580, 470), (585, 440), (230, 250)]:
    print("px", p, im[p[1], p[0]])
sat = (mx - mn) / np.maximum(mx, 1)
gold = (sat > 0.3) & (mx > 120) & (R >= G) & (G > B) & (R - B > 50)


def bbox_in(mask, x0, x1, y0, y1):
    sub = np.zeros_like(mask)
    sub[y0:y1, x0:x1] = mask[y0:y1, x0:x1]
    lab, n = ndi.label(ndi.binary_closing(sub, iterations=2))
    sizes = ndi.sum(np.ones_like(lab), lab, range(1, n + 1))
    i = 1 + int(np.argmax(sizes))
    ys, xs = np.nonzero(lab == i)
    return xs.min(), xs.max(), ys.min(), ys.max()


silver = (mn > 120) & (mx - mn < 28) & (mx < 245)
print("HDMI-A gold        ", bbox_in(gold, 140, 260, 320, 470))
print("micro-HDMI gold    ", bbox_in(gold, 540, 625, 380, 510))
print("RJ45 silver        ", bbox_in(silver, 140, 320, 185, 320))
gold2 = (R - B > 35) & (R > 150) & (G > 110)
print("HDMI-A gold v2     ", bbox_in(gold2, 140, 260, 320, 470))
print("micro-HDMI gold v2 ", bbox_in(gold2, 540, 625, 380, 510))
# RJ45: row profile of silver in x 160..290 (the shell), to find its top/bottom edges
prof = silver[150:340, 160:290].mean(1)
edges = [150 + i for i in range(1, len(prof)) if (prof[i] > 0.5) != (prof[i - 1] > 0.5)]
print("RJ45 shell rows where silver coverage crosses 50%:", edges)
colp = silver[200:300, 140:330].mean(0)
edges = [140 + i for i in range(1, len(colp)) if (colp[i] > 0.5) != (colp[i - 1] > 0.5)]
print("RJ45 shell cols where silver coverage crosses 50%:", edges)
