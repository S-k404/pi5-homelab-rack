"""The four units placed in the T0-look rack (rack coordinates: x across, y up from the rack space bottom,
z back from the front rail face). The Pi unit is loaded from its own STEP files, in its v3 frame, and moved in."""
import os
import cadquery as cq
import rack_t0 as r
import b1_dock as dk
import display as dp
import ucg_shelf as ug

YB = r.module_bottoms()
YC_PI = YB[0] + r.MODULES[0] * r.U / 2
YC_DOCK = YB[1] + r.MODULES[1] * r.U / 2
YC_DISP = YB[2] + r.MODULES[2] * r.U / 2
YC_UCG = YB[3] + r.MODULES[3] * r.U / 2

# Pi unit v3 frame -> rack: x_r = x - CX, y_r = z - Z0, z_r = PY0 - y  (Z0 = panel bottom, PY0 = faceplate back face)
PI_CX, PI_Z0, PI_PY0 = (-2.2 + 116.1) / 2, -8.0, 112.2 + 0.3
PI_FILES = {"Pi shelf": "Rack_Shelf_pinned.step", "Pi faceplate": "Rack_Faceplate_2U_10in.step",
            "Pi UPS tray": "Pi5_UPS_v3_ups_tray_pinned.step", "Pi board tray": "Pi5_UPS_v3_board_tray_HDMIexit.step",
            "Pi lid": "Pi5_UPS_v3_lid.step"}


def pi_to_rack(shape):
    return shape.rotate((0, 0, 0), (1, 0, 0), -90).translate((-PI_CX, -PI_Z0, PI_PY0))


def pi_unit(step_dir):
    out = {}
    for nm, f in PI_FILES.items():
        s = cq.Workplane().add(cq.importers.importStep(os.path.join(step_dir, f)).val())
        out[nm] = pi_to_rack(s)
    return out


def dock_parts():
    """dock v5: the real B1 (132 x 91 x 62, official) in its cradle; no spacers any more"""
    t = (0, YC_DOCK, -dk.EAR_T)
    return {"B1 dock": dk.body().translate(t), "dock ear R": dk.ear(1).translate(t), "dock ear L": dk.ear(-1).translate(t),
            "B1 (132 x 91 x 62)": dk.b1_dummy().translate(t)}


def display_parts():
    t = (0, YC_DISP, -dp.Z0)
    p = {"display": dp.body().translate(t), "screen glass": dp.glass_dummy().translate(t),
         "driver board": dp.driver_dummy().translate(t),
         "display ear R": dp.ear(1).translate(t), "display ear L": dp.ear(-1).translate(t)}
    for i, c in enumerate(dp.clips()):
        p[f"display clip {i}"] = c.translate(t)
    return p


def ucg_parts():
    t = (0, YC_UCG, -ug.PANEL_T)
    return {"UCG shelf": ug.body().translate(t), "UCG-Ultra": ug.gateway_dummy().translate(t)}
