"""
The Waveshare Pi5 Connector Adapter (F) as simple shapes, in the frame of waveshare_f_wall_frame.py.
Positions measured off Waveshare's dimension drawing (6.76 px/mm); heights marked est. are estimates (top view only).
Used by verify_wall_frame.py (collisions) and render_wall_frame.py (colours).
"""
import cadquery as cq
import waveshare_f_wall_frame as F


def box(x0, x1, y0, y1, z0, z1):
    return cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0)).val()


def cylv(x, y, z0, z1, d):
    return cq.Workplane("XY").circle(d / 2).extrude(z1 - z0).translate((x, y, z0)).val()


def rod_x(x0, x1, yc, zc, d):
    return cq.Workplane("YZ").circle(d / 2).extrude(x1 - x0).translate((x0, yc, zc)).val()


def parts():
    """name -> (solid, finish). finish picks the render material; "hidden" parts are only for the checks."""
    T, B = F.PCB_TOP, F.ZB
    pcb = box(0, F.PCB_L, 0, F.PCB_W, B, T)
    pcb = pcb.cut(box(27.0, 79.0, -1, 2.7, B - 1, T + 1))                       # recessed plug edge
    for hx, hy in F.HOLES:
        pcb = pcb.cut(cylv(hx, hy, B - 1, T + 1, 2.7))
    rj = box(F.JACK_FACE_X, 19.1, *F.RJ45_Y, T, T + F.RJ45_H)
    rj = rj.cut(box(F.JACK_FACE_X - 1, F.JACK_FACE_X + 14, 25.6, 34.9, T + 3.0, T + 10.0))   # socket mouth
    hd = box(F.JACK_FACE_X + 0.1, 7.8, *F.HDMI_Y, T, T + F.HDMI_H)
    hd = hd.cut(box(F.JACK_FACE_X - 1, F.JACK_FACE_X + 9, 2.2, 15.4, T + 1.2, T + 5.3))
    hd = hd.fuse(box(F.JACK_FACE_X + 0.5, 7.0, 3.0, 14.6, T + 2.6, T + 3.9))                  # tongue
    term = box(79.2, 87.0, *F.TERM_Y, T - 0.5, T + 9.0)                                       # header
    term = term.fuse(box(87.0, F.TERM_X1, *F.TERM_Y, T - 0.5, T + 12.0))                      # plug
    for sy in (9.1, 12.8):
        term = term.cut(cylv(F.TERM_X1 - 4.4, sy, T + 10.5, T + 12.5, 2.6))                              # screw wells
    return {
        "PCB": (pcb, "pcb"),
        "RJ45 (13.5 tall)": (rj, "steel"),
        "HDMI-A (6.5 tall)": (hd, "gold"),
        "PWR rod (est. 3 tall)": (rod_x(-3.6, 11.0, sum(F.ROD_Y) / 2, T + 1.5, 2.5), "steel"),
        "7-24 V terminal (est. 12 tall)": (term, "green"),
        "terminal screws": (cylv(F.TERM_X1 - 4.4, 9.1, T + 10.0, T + 11.6, 2.4).fuse(
            cylv(F.TERM_X1 - 4.4, 12.8, T + 10.0, T + 11.6, 2.4)), "steel"),
        "UART sockets (est. 6 tall)": (box(79.0, 86.0, 41.2, 46.4, T, T + 4.5).fuse(box(80.6, 84.0, 35.5, 40.7, T, T + 6.0)), "white"),
        "3-pin socket (est. 6 tall)": (box(28.5, 39.6, 2.2, 9.2, T, T + 6.0), "white"),
        "micro-HDMI plug": (box(56.2, 64.2, F.PLUG_TIP_Y, 9.2, T - 0.5, T + 3.5), "gold"),
        "USB-C plug": (box(70.5, 78.2, F.PLUG_TIP_Y, 9.2, T - 0.5, T + 3.5), "steel"),
        "PoE transformer (est. 10 tall)": (box(33.7, 47.7, 38.4, 52.3, T, T + 10.0), "ferrite"),
        "inductors (est. 7 tall)": (box(11.4, 18.8, 41.3, 50.9, T, T + 7.0).fuse(box(77.5, 85.0, 17.0, 26.6, T, T + 7.0))
                                    .fuse(box(66.2, 76.6, 37.7, 48.1, T, T + 6.0)), "ferrite"),
        "22 uF / 470 uF caps (est. 8 tall)": (cylv(25.9, 32.5, T, T + 8.0, 8.0).fuse(cylv(56.3, 40.7, T, T + 8.0, 6.3)), "alu"),
        "M.2 socket (est. 4.2 tall)": (box(69.0, 76.5, 10.4, 36.0, T, T + 4.2), "ferrite"),
        "2230 SSD": (box(39.5, 69.5, 10.2, 32.2, T + 2.4, T + 3.2), "ssd"),
        "SSD chips": (box(44.0, 54.0, 14.0, 28.0, T + 3.2, T + 4.4).fuse(box(57.0, 66.0, 15.0, 27.0, T + 3.2, T + 4.2)), "ferrite"),
        "FFC socket": (box(54.2, 66.8, 14.3, 19.9, T, T + 2.0), "white"),
        "RTL8125 chip": (box(43.0, 52.0, 21.0, 30.0, T, T + 1.0), "ferrite"),
        # through-hole pin tails under the board (est. 2.5)
        "pin tails under RJ45 / HDMI / terminal (est. 2.5)": (box(0.5, 19.0, 0.5, 38.5, B - 2.5, B).fuse(
            box(79.5, 84.5, 6.5, 15.4, B - 2.5, B)), "hidden"),
    }
