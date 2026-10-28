"""Waveshare Pi5 Connector Adapter (F) placed in the v3 frame, from case_v3.py data:
PCB 85 x 52.5 (drawing frame), plug edge at x=55, port end at y=4.45, PCB on shims z 41.5-43.6.
Port bodies sized to sit inside v3's front cut-outs (HDMI x 35.45-54.45, RJ45 x 14.4-34.15)."""
import cadquery as cq
def box(x0,x1,y0,y1,z0,z1): return cq.Workplane("XY").box(x1-x0,y1-y0,z1-z0,centered=False).translate((x0,y0,z0))
ZB = 42.5                      # PCB underside (middle of the shim range)
T = 1.6
def adapter():
    pcb = box(2.5, 55.0, 4.45, 89.45, ZB, ZB+T)
    hdmi = box(44.95-7.5, 44.95+7.5, 3.45, 15.0, ZB+T, ZB+T+6.0)      # full-size HDMI-A out
    rj45 = box(24.3-8.0, 24.3+8.0, 3.45, 24.5, ZB+T, ZB+T+13.5)       # 2.5G PoE RJ45
    return pcb.union(hdmi).union(rj45).val()
