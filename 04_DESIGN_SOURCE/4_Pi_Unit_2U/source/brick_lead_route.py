"""
The brick's 12 V lead behind the faceplate (28 Oct 2026, ultrareview): nothing shows at the front.

UPS DC-IN <- a right-angle 5.5 x 2.1 plug (on a 30 cm right-angle male -> straight female extension), its cable leaving
sideways (-x) inside the UPS tray's DC-IN window -> forward and down into the pocket behind the faceplate -> along the shelf
floor, below the UPS OUT lead -> through the arch in the right gusset (pi_rack.PASS_Y) -> across the front of the brick
cradle -> into its open front, where the extension's socket takes the brick's own straight plug. The brick's spare lead is
coiled in the cradle's empty front part, beside the join.

Rack frame (x across, +x = the viewer's LEFT from the front; y up from the base-bar tops; z back from the front rails), mm.
Plain data: export_final.py draws it, verify_wiring_all.py checks it.
"""
PI_CX, PI_Z0, PI_PY0 = 56.95, -8.0, 112.5          # units.py: Pi unit (v3 frame) -> rack


def v3(x, y, z):
    """v3 frame (x left -> right, y rack rear -> front, z up) to the rack frame"""
    return (x - PI_CX, z - PI_Z0, PI_PY0 - y)


JACK = v3(96.0, 80.6, 17.0)          # UPS DC-IN: the centre of the tray's DC-IN window, on the UPS's front face (z 31.9)
PLUG_W, PLUG_H, PLUG_D = 11.0, 12.0, 16.0           # right-angle overmould: across, tall, out of the jack face
CABLE_Z = JACK[2] - PLUG_D + 4.6                    # the cable leaves the elbow 4.6 mm from the plug's back
SR_D, SR_L = 6.5, 5.0                               # strain relief, out to -x
LEAD_D = 4.0                                        # extension and brick lead

jx, jy, jz = JACK
PLUG_BOX = (jx - PLUG_W / 2, jx + PLUG_W / 2, jy - PLUG_H / 2, jy + PLUG_H / 2, jz - PLUG_D, jz)
SR = ((jx - PLUG_W / 2, jy, CABLE_Z), (jx - PLUG_W / 2 - SR_L, jy, CABLE_Z), SR_D)   # start, end, dia

# extension cable: plug -> pocket floor -> gusset arch (x 61.15..67.15, z 9.5..18.5, y 4.5..11.5) -> cradle front
EXT_PATH = [(jx - PLUG_W / 2 - SR_L, jy, CABLE_Z),
            (25.5, 22.0, 15.5),                     # forward out of the window, in front of the tray wall (z 23.3)
            (25.5, 9.0, 13.5),                      # down to the shelf floor (top y 4.5), behind the front lip (z 0..8)
            (40.0, 8.0, 13.5), (58.0, 8.0, 13.5),   # along the floor, under the UPS OUT lead (y >= 20 here)
            (64.0, 8.0, 13.5),                      # through the gusset arch
            (68.5, 7.5, 11.0),                      # out of the shelf, in front of the cradle's inner wall (from z 14)
            (77.0, 7.0, 10.5),
            (85.0, 11.0, 16.0),                     # into the cradle's open front, over its floor (top y 2)
            (90.0, 13.0, 21.0)]
# the join rides over the cradle's strap rib (z 23..29, 6.5 high): its underside at y 7.5
SOCKET = ((90.0, 13.0, 21.0), (90.0, 13.0, 49.0), 11.0)      # extension's female socket: start, end, dia
BRICK_PLUG = ((90.0, 13.0, 49.0), (90.0, 13.0, 74.0), 10.5)  # the brick's straight plug pushed into it
BRICK_SR = ((90.0, 13.0, 74.0), (90.0, 13.0, 82.0), 6.0)

# the brick's own lead: from its front face (centre, z 88.3) into the coil, then to the plug
BRICK_FACE = (93.8, 27.5, 88.3)
COIL_X = (99.5, 106.5)                                      # loops stacked across, beside the join
COIL_LOOP = [(78.0, 24.0), (32.0, 24.0), (32.0, 6.5), (78.0, 6.5)]   # (z, y): in at the top rear, out at the bottom rear
COIL_TURNS = 5
LEAD_IN = [BRICK_FACE, (BRICK_FACE[0], BRICK_FACE[1], 85.0), (99.5, 24.0, 80.0), (99.5, 24.0, 78.0)]
LEAD_OUT = [(106.5, 6.5, 78.0), (104.0, 8.0, 85.0), (94.0, 13.0, 86.0), (90.0, 13.0, 84.0), (90.0, 13.0, 82.0)]


def coil_path():
    pts = []
    for k in range(COIL_TURNS):
        x = COIL_X[0] + (COIL_X[1] - COIL_X[0]) * k / (COIL_TURNS - 1)
        for z, y in COIL_LOOP:
            pts.append((x, y, z))
    return pts


def brick_lead_path():
    return LEAD_IN + coil_path() + LEAD_OUT


def length(pts):
    return sum(sum((b[i] - a[i]) ** 2 for i in range(3)) ** 0.5 for a, b in zip(pts, pts[1:]))


EXT_LENGTH = PLUG_D + SR_L + length(EXT_PATH) + (SOCKET[1][2] - SOCKET[0][2])      # what the extension has to span
