"""
Pi 5 NAS/router build — STEP models for Onshape.

Coordinate system (all parts and the assembly):
  X = along the Pi 5's 85 mm edge (USB/Ethernet end at +X)
  Y = along the 56 mm edge (GPIO header at +Y, USB-C/HDMI edge at Y=0)
  Z = up, PCB underside at Z=0
Units: mm.

Every dimension is a named parameter at the top of its function so you can
edit and re-run:  python3 build.py
Confidence tags:  [D] = from manufacturer drawing/spec   [E] = estimated
"""
import cadquery as cq
from cadquery import Assembly, Color, Location, Vector
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
os.makedirs(OUT, exist_ok=True)


def box(x0, y0, z0, dx, dy, dz):
    """Axis-aligned box from a min corner."""
    return cq.Workplane("XY").box(dx, dy, dz, centered=False).translate((x0, y0, z0))


# ---------------------------------------------------------------- Raspberry Pi 5
def raspberry_pi_5():
    L, W, T = 85.0, 56.0, 1.4          # [D] board 85x56; [E] PCB 1.4
    R_CORNER = 3.0                      # [D] Ø3 corner radius... drawn as R3
    HOLE_D = 2.7                        # [D] Ø2.7 mounting holes
    HOLES = [(3.5, 3.5), (61.5, 3.5), (3.5, 52.5), (61.5, 52.5)]  # [D] 58 x 49 pattern

    pcb = (cq.Workplane("XY").box(L, W, T, centered=False)
           .edges("|Z").fillet(R_CORNER)
           .faces(">Z").workplane(origin=(0, 0, T))
           .pushPoints([(x, y) for x, y in HOLES]).hole(HOLE_D))

    parts = {"PCB": (pcb, Color(0.05, 0.45, 0.20))}
    metal = Color(0.75, 0.75, 0.78)
    black = Color(0.1, 0.1, 0.1)

    # Right edge (+X): Ethernet + two USB stacks. Centres along Y are [D];
    # bodies/heights are [E] — use the official STEP for case work.
    OVH = 2.1                           # [E] overhang past board edge
    eth_w, eth_d, eth_h = 16.0, 21.5, 13.3
    usb_w, usb_d, usb_h = 13.1, 17.5, 16.0
    parts["Ethernet RJ45"] = (box(L + OVH - eth_d, 10.2 - eth_w / 2, T, eth_d, eth_w, eth_h), metal)
    parts["USB3 stack"] = (box(L + OVH - usb_d, 29.1 - usb_w / 2, T, usb_d, usb_w, usb_h), metal)
    parts["USB2 stack"] = (box(L + OVH - usb_d, 47.0 - usb_w / 2, T, usb_d, usb_w, usb_h), metal)

    # Bottom edge (Y=0): USB-C and 2x micro-HDMI. X centres [D]; bodies [E].
    parts["USB-C power"] = (box(11.2 - 4.5, -1.2, T, 9.0, 7.4, 3.2), metal)
    parts["micro-HDMI 0"] = (box(25.8 - 3.3, -1.0, T, 6.6, 7.5, 3.4), metal)
    parts["micro-HDMI 1"] = (box(39.2 - 3.3, -1.0, T, 6.6, 7.5, 3.4), metal)

    # GPIO 2x20 header: centred X=32.5, Y=52.5 [D]; 8.5 tall [E]
    hdr = box(32.5 - 25.4, 52.5 - 2.54, T, 50.8, 5.08, 2.5)
    for i in range(20):
        for j in range(2):
            px = 32.5 - 25.4 + 1.27 + i * 2.54
            py = 52.5 - 1.27 + j * 2.54
            hdr = hdr.union(box(px - 0.32, py - 0.32, T + 2.5, 0.64, 0.64, 6.0))
    parts["GPIO header"] = (hdr, black)

    # [E] SoC, PCIe FFC (left edge), microSD socket (underside)
    parts["BCM2712 SoC"] = (box(29.0 - 8.5, 31.0 - 8.5, T, 17, 17, 1.5), Color(0.6, 0.6, 0.6))
    parts["PCIe FFC 16p"] = (box(0.6, 28.0 - 7.0, T, 4.5, 14.0, 2.0), black)
    parts["microSD socket"] = (box(-2.0, 28.0 - 6.0, -1.4, 14.0, 12.0, 1.4), metal)
    return parts


# ---------------------------------------------------------------- GeeekPi Armor Lite V5
def armor_lite_v5():
    L, W, H = 58.0, 40.0, 11.0          # [D] 58 x 40 x 11 (52Pi/RobotShop listing)
    FAN_D, FAN_DEPTH = 30.0, 8.0        # [D-ish] listing says 30 mm fan; 52Pi calls it "3510"
    FIN_T, FIN_GAP = 1.2, 2.0           # [E]
    BASE = 3.0                          # [E] solid base under fins
    HOLE_D = 2.7                        # M2.5 clearance [E]
    # [E] two diagonal screw holes — measure your unit and edit
    HOLES = [(-L / 2 + 3.5, -W / 2 + 3.5), (L / 2 - 3.5, W / 2 - 3.5)]

    body = cq.Workplane("XY").box(L, W, BASE, centered=(True, True, False))
    n = int((L - FAN_D - 4) // (FIN_T + FIN_GAP))
    fins = cq.Workplane("XY")
    x = FAN_D / 2 + 2
    while x + FIN_T <= L / 2:
        for s in (1, -1):
            fx = s * x if s == 1 else -x - FIN_T
            body = body.union(box(fx, -W / 2, BASE, FIN_T, W, H - BASE))
        x += FIN_T + FIN_GAP
    # fan pocket + fan
    body = body.union(cq.Workplane("XY").circle(FAN_D / 2 + 2).circle(FAN_D / 2)
                      .extrude(H - BASE).translate((0, 0, BASE)))
    body = body.faces(">Z").workplane().pushPoints(HOLES).hole(HOLE_D)
    fan = (cq.Workplane("XY").circle(FAN_D / 2 - 0.5).circle(6).extrude(FAN_DEPTH)
           .translate((0, 0, H - FAN_DEPTH))
           .union(cq.Workplane("XY").circle(6).extrude(FAN_DEPTH).translate((0, 0, H - FAN_DEPTH))))
    return {"Heatsink": (body, Color(0.15, 0.15, 0.17)),
            "30mm fan": (fan, Color(0.3, 0.3, 0.32))}


# ---------------------------------------------------------------- EVM 2242 SATA SSD
def evm_2242():
    L, W = 42.0, 22.0                   # [D] M.2 2242
    T_PCB = 0.8                         # [D] M.2 standard
    TOP, BOT = 1.5, 1.55                # [E] split so total = 3.85 [D]
    # Key notches (B + M key = SATA). Positions per M.2 spec, approx [E]
    NOTCH_W, NOTCH_DEPTH = 1.2, 3.5
    B_KEY_X, M_KEY_X = 6.625, 19.85     # measured from the card's left edge
    SLOT_R = 1.75                       # half-round mounting slot at far end [D]

    pcb = box(0, 0, 0, L, W, T_PCB)     # X = length, connector edge at X=0
    for ky in (B_KEY_X, M_KEY_X):
        pcb = pcb.cut(box(0, ky - NOTCH_W / 2, -0.1, NOTCH_DEPTH, NOTCH_W, T_PCB + 0.2))
    pcb = pcb.cut(cq.Workplane("XY").circle(SLOT_R).extrude(T_PCB + 0.2)
                  .translate((L, W / 2, -0.1)))
    chips = box(6.0, 1.5, T_PCB, 32.0, 19.0, TOP)
    under = box(6.0, 1.5, -BOT, 30.0, 19.0, BOT)
    fingers = box(0, 0.5, T_PCB, 3.8, 21.0, 0.02)
    return {"PCB": (pcb, Color(0.05, 0.2, 0.5)),
            "NAND/controller (top)": (chips, Color(0.1, 0.1, 0.1)),
            "Label/components (bottom)": (under, Color(0.85, 0.85, 0.85)),
            "Gold fingers": (fingers, Color(0.85, 0.7, 0.2))}


# ---------------------------------------------------------------- EVM 512GB 2230 NVMe
def evm_2230_nvme():
    L, W = 30.0, 22.0                   # [D] M.2 2230
    T_PCB = 0.8                         # [D] M.2 standard
    TOP = 1.35                          # [D] M.2 single-sided (S2) max top height
    NOTCH_W, NOTCH_DEPTH = 1.2, 3.5     # M-key only (NVMe) [E position]
    M_KEY_X = 19.85
    SLOT_R = 1.75                       # half-round screw slot at far end [D]
    pcb = box(0, 0, 0, L, W, T_PCB)     # connector edge at X=0
    pcb = pcb.cut(box(0, M_KEY_X - NOTCH_W / 2, -0.1, NOTCH_DEPTH, NOTCH_W, T_PCB + 0.2))
    pcb = pcb.cut(cq.Workplane("XY").circle(SLOT_R).extrude(T_PCB + 0.2)
                  .translate((L, W / 2, -0.1)))
    chips = box(5.0, 1.5, T_PCB, 21.5, 19.0, TOP)
    return {"PCB": (pcb, Color(0.05, 0.2, 0.5)),
            "Controller/NAND": (chips, Color(0.1, 0.1, 0.1))}


# ---------------------------------------------------------------- Cuzor Mini UPS Pro
def cuzor_ups_pro():
    L, W, H = 100.0, 80.0, 28.0         # [D] Cuzor Labs product page: 10 x 8 x 2.8 cm
    R_PLAN, R_TOP = 6.0, 3.0            # [E] corner radii
    JACK_D = 8.0                        # [E] 5.5x2.1 barrel jack opening
    shell = (cq.Workplane("XY").box(L, W, H, centered=(True, True, False))
             .edges("|Z").fillet(R_PLAN).faces(">Z").edges().fillet(R_TOP))
    # Front face (+Y): switch, LED, OUT jack. Back face (-Y): IN jack. [E]
    front = shell.faces(">Y").workplane(centerOption="CenterOfBoundBox")
    shell = (front.pushPoints([(L / 2 - 14, -2)]).hole(JACK_D, 6))           # OUT
    shell = (shell.faces(">Y").workplane(centerOption="CenterOfBoundBox")
             .center(L / 2 - 38, -2).rect(10, 6).cutBlind(-3))               # switch
    shell = (shell.faces("<Y").workplane(centerOption="CenterOfBoundBox")
             .pushPoints([(L / 2 - 14, -2)]).hole(JACK_D, 6))                # IN
    return {"UPS body": (shell, Color(0.12, 0.12, 0.13))}


# ---------------------------------------------------------------- Waveshare Pi5 Connector Adapter (F)
def waveshare_adapter_f():
    """PLACEHOLDER. Waveshare publishes this board's outline only as an image.
    Edit the parameters below from that drawing and re-run.
    Origin: board corner nearest the Pi's (0,0); board extends toward -Y."""
    L, W, T = 85.0, 56.0, 1.6           # [E] !! replace with drawing values
    M2_SOCKET_X, M2_Y0 = 10.0, -40.0    # [E] M.2 socket position
    HOLES = [(3.5, -3.5), (61.5, -3.5), (3.5, -52.5), (61.5, -52.5)]  # [E]
    pcb = (box(0, -W, 0, L, W, T).edges("|Z").fillet(3)
           .faces(">Z").workplane(origin=(0, 0, T)).pushPoints(HOLES).hole(2.7))
    metal = Color(0.75, 0.75, 0.78)
    parts = {"PCB (placeholder outline)": (pcb, Color(0.08, 0.08, 0.08))}
    # Plugs that enter the Pi's ports — X positions match Pi 5 [D]
    parts["USB-C plug"] = (box(11.2 - 4.0, -0.5, T, 8.0, 7.0, 2.6), metal)
    parts["micro-HDMI plug 0"] = (box(25.8 - 3.0, -0.5, T, 6.0, 7.0, 2.8), metal)
    parts["micro-HDMI plug 1"] = (box(39.2 - 3.0, -0.5, T, 6.0, 7.0, 2.8), metal)
    # Output side [E]
    parts["HDMI-A out 0"] = (box(14.0, -W - 1.0, T, 15.0, 11.5, 6.0), metal)
    parts["HDMI-A out 1"] = (box(33.0, -W - 1.0, T, 15.0, 11.5, 6.0), metal)
    parts["RJ45 2.5G PoE"] = (box(L - 21.0, -W + 2.0, T, 22.5, 16.0, 13.5), metal)
    parts["USB-C in"] = (box(-1.0, -W + 6.0, T, 7.4, 9.0, 3.2), metal)
    parts["7-24V terminal"] = (box(0.5, -W + 20.0, T, 7.5, 7.6, 9.5), Color(0.2, 0.7, 0.3))
    # M.2 socket faces +X; a 2230 card runs 30 mm toward +X to the standoff [E]
    M2_LEN = 30.0                       # 2230 drive (board also accepts 2242)
    parts["M.2 M-key socket"] = (box(M2_SOCKET_X, M2_Y0, T, 4.5, 22.0, 4.2), Color(0.1, 0.1, 0.1))
    parts["M.2 standoff (2230)"] = (cq.Workplane("XY").circle(2.5).extrude(1.5)
                                    .translate((M2_SOCKET_X + 4.5 + M2_LEN, M2_Y0 + 11.0, T)), metal)
    parts["16p PCIe FFC"] = (box(66.0, -16.0, T, 4.5, 14.0, 2.0), Color(0.1, 0.1, 0.1))
    return parts


# ---------------------------------------------------------------- export helpers
def to_assembly(name, parts, loc=None):
    a = Assembly(name=name, loc=loc or Location())
    for pname, (shape, color) in parts.items():
        a.add(shape, name=pname.replace(" ", "_").replace("/", "-"), color=color)
    return a


def bbox(parts):
    bb = None
    for shape, _ in parts.values():
        b = shape.val().BoundingBox()
        bb = b if bb is None else bb.add(b)
    return bb


if __name__ == "__main__":
    models = {
        "RaspberryPi5_8GB": raspberry_pi_5(),
        "GeeekPi_ArmorLite_V5": armor_lite_v5(),
        "EVM_256GB_M2_2242_SATA": evm_2242(),
        "Cuzor_MiniUPS_Pro_12V3A": cuzor_ups_pro(),
        "Waveshare_Pi5_Connector_Adapter_F_PLACEHOLDER": waveshare_adapter_f(),
    }
    for name, parts in models.items():
        to_assembly(name, parts).save(os.path.join(OUT, name + ".step"), exportType="STEP")
        b = bbox(parts)
        print(f"{name:48s} X {b.xlen:6.2f}  Y {b.ylen:6.2f}  Z {b.zlen:6.2f}")

    # Full layout assembly (positions for reference; mate in Onshape)
    top = Assembly(name="Pi5_build_layout")
    top.add(to_assembly("RaspberryPi5", models["RaspberryPi5_8GB"]))
    top.add(to_assembly("ArmorLiteV5", models["GeeekPi_ArmorLite_V5"],
                        Location(Vector(32.0, 28.0, 1.4 + 1.5 + 1.0))))
    top.add(to_assembly("WaveshareAdapterF", models["Waveshare_Pi5_Connector_Adapter_F_PLACEHOLDER"],
                        Location(Vector(0, -1.5, 0))))
    top.add(to_assembly("SSD_2242", models["EVM_256GB_M2_2242_SATA"],
                        Location(Vector(10.0 + 4.5, -1.5 - 40.0, 1.6 + 1.5))))
    top.add(to_assembly("CuzorUPS", models["Cuzor_MiniUPS_Pro_12V3A"],
                        Location(Vector(160.0, 0, 0))))
    top.save(os.path.join(OUT, "Pi5_build_layout_ASSEMBLY.step"), exportType="STEP")
    print("done")
