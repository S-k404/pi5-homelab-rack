"""
Generate High-Resolution Dimensioned Technical Schematics for the 10-inch 9U Homelab Mini Rack.
Includes:
- Front Elevation with EIA-310 10" Rack standard dimensions and U-unit divisions.
- Side Elevation comparing Standard (200 mm) vs Slim Cargo Travel Prototype (140 mm).
- Component depth envelope chart (Pi unit, B1 dock, Screen, UCG-Ultra, 12V Brick).
- Hardware, fastener, and material callout table for Onshape / workshop reference.
"""
import os
import sys
from PIL import Image, ImageDraw, ImageFont

W, H = 2800, 2000
BG_COLOR = (248, 250, 252)       # Clean engineering drafting paper
GRID_COLOR = (226, 232, 240)
LINE_COLOR = (15, 23, 42)         # Deep slate blueprint ink
DIM_COLOR = (2, 132, 199)         # Cyan/Blue dimension lines
HIGHLIGHT_COLOR = (225, 29, 72)   # Red highlight for 140 mm slim profile
TEXT_MUTED = (100, 116, 139)
PANEL_BG = (241, 245, 249)

im = Image.new("RGB", (W, H), BG_COLOR)
d = ImageDraw.Draw(im)

# Grid
for x in range(0, W, 40):
    d.line([(x, 0), (x, H)], fill=GRID_COLOR, width=1)
for y in range(0, H, 40):
    d.line([(0, y), (W, y)], fill=GRID_COLOR, width=1)

# Fonts
F_BOLD = "/System/Library/Fonts/Helvetica.ttc"
font_title = ImageFont.truetype(F_BOLD, 46, index=1)
font_sec = ImageFont.truetype(F_BOLD, 28, index=1)
font_lbl = ImageFont.truetype(F_BOLD, 20, index=1)
font_dim = ImageFont.truetype(F_BOLD, 18, index=1)
font_body = ImageFont.truetype(F_BOLD, 17)
font_small = ImageFont.truetype(F_BOLD, 14)

# ---------------- TITLE BLOCK ----------------
d.rectangle([(60, 50), (W - 60, 140)], fill=(30, 41, 59))
d.text((90, 68), "PI 5 HOMELAB 10-INCH 9U MINI RACK · SYSTEM ENGINEERING SCHEMATIC", font=font_title, fill=(255, 255, 255))
d.text((90, 112), "DESKPi T0 AESTHETIC · COMMERCIAL 10\" STANDARD · DUAL SPEC: 200 mm DESKTOP / 140 mm SLIM CARGO SUITCASE EDITION",
       font=font_lbl, fill=(148, 163, 184))

# ---------------- HELPER DRAWING FUNCTIONS ----------------
def draw_dim_h(x0, x1, y, label, color=DIM_COLOR, above=True):
    d.line([(x0, y), (x1, y)], fill=color, width=2)
    d.line([(x0, y - 6), (x0, y + 6)], fill=color, width=2)
    d.line([(x1, y - 6), (x1, y + 6)], fill=color, width=2)
    # arrows
    d.polygon([(x0, y), (x0 + 8, y - 3), (x0 + 8, y + 3)], fill=color)
    d.polygon([(x1, y), (x1 - 8, y - 3), (x1 - 8, y + 3)], fill=color)
    bb = font_dim.getbbox(label)
    lw = bb[2] - bb[0]
    ty = y - 22 if above else y + 6
    d.rectangle([( (x0+x1)/2 - lw/2 - 4, ty), ((x0+x1)/2 + lw/2 + 4, ty + 18)], fill=BG_COLOR)
    d.text(((x0 + x1)/2 - lw/2, ty), label, font=font_dim, fill=color)

def draw_dim_v(x, y0, y1, label, color=DIM_COLOR, left=True):
    d.line([(x, y0), (x, y1)], fill=color, width=2)
    d.line([(x - 6, y0), (x + 6, y0)], fill=color, width=2)
    d.line([(x - 6, y1), (x + 6, y1)], fill=color, width=2)
    d.polygon([(x, y0), (x - 3, y0 + 8), (x + 3, y0 + 8)], fill=color)
    d.polygon([(x, y1), (x - 3, y1 - 8), (x + 3, y1 - 8)], fill=color)
    bb = font_dim.getbbox(label)
    lw = bb[2] - bb[0]
    tx = x - lw - 14 if left else x + 10
    d.rectangle([(tx - 2, (y0+y1)/2 - 10), (tx + lw + 2, (y0+y1)/2 + 10)], fill=BG_COLOR)
    d.text((tx, (y0 + y1)/2 - 9), label, font=font_dim, fill=color)

# ---------------- SECTION 1: FRONT ELEVATION SCHEMATIC ----------------
# Box at (120, 200) to (1000, 1850)
d.rectangle([(100, 180), (1050, 1920)], fill=(255, 255, 255), outline=(203, 213, 225), width=2)
d.text((130, 205), "VIEW A: FRONT ELEVATION SCHEMATIC (9U 10-INCH STANDARD)", font=font_sec, fill=LINE_COLOR)
d.text((130, 242), "Standard 10\" EIA-310 Spec: 236.525 mm (9.3125\") Mounting Hole Pitch · 254 mm (10.0\") Faceplate Width",
       font=font_body, fill=TEXT_MUTED)

# Front Rack Drawing
# Overall scale: rack 280 mm wide -> 560 px (scale = 2.0 px/mm)
# Total height: ~445 mm -> ~890 px
SCALE = 2.4
RX0 = 240
RY0 = 400
RW = int(280 * SCALE)      # 672 px
# Height components
H_PLINTH = int(20 * SCALE)
H_2U = int(88.9 * SCALE)   # 213 px
H_3U_B1 = int(133.35 * SCALE) # 320 px
H_3U_DISP = int(133.35 * SCALE) # 320 px
H_1U_UCG = int(44.45 * SCALE) # 107 px
H_CAP = int(25 * SCALE)
H_HANDLE = int(20 * SCALE)

TOTAL_H = H_PLINTH + H_2U + H_3U_B1 + H_3U_DISP + H_1U_UCG + H_CAP
BASE_Y = RY0 + TOTAL_H     # Bottom desk line

# Desk line
d.line([(RX0 - 60, BASE_Y), (RX0 + RW + 60, BASE_Y)], fill=(100, 116, 139), width=3)
d.text((RX0 + RW + 70, BASE_Y - 10), "DESK SURFACE (Z=0)", font=font_small, fill=TEXT_MUTED)

# Outer frame outline
d.rectangle([(RX0, BASE_Y - TOTAL_H), (RX0 + RW, BASE_Y)], fill=PANEL_BG, outline=LINE_COLOR, width=3)

# Plinth (bottom)
d.rectangle([(RX0, BASE_Y - H_PLINTH), (RX0 + RW, BASE_Y)], fill=(226, 232, 240), outline=LINE_COLOR, width=2)
d.text((RX0 + RW/2 - 50, BASE_Y - H_PLINTH/2 - 8), "PLINTH (20 mm)", font=font_lbl, fill=TEXT_MUTED)

# Unit 1: 2U Pi Unit
U1_Y0 = BASE_Y - H_PLINTH - H_2U
d.rectangle([(RX0 + int(13*SCALE), U1_Y0), (RX0 + RW - int(13*SCALE), U1_Y0 + H_2U)], fill=(30, 41, 59), outline=LINE_COLOR, width=2)
d.text((RX0 + 80, U1_Y0 + H_2U/2 - 18), "2U: RASPBERRY PI 5 + CUZOR MINI UPS PRO", font=font_lbl, fill=(255, 255, 255))
d.text((RX0 + 80, U1_Y0 + H_2U/2 + 6), "Argon Poly+ 5 Case · Waveshare Adapter (F) · 12V Brick Cradle · DC-Notch Faceplate", font=font_small, fill=(148, 163, 184))

# Unit 2: 3U NIIMBOT B1 Dock
U2_Y0 = U1_Y0 - H_3U_B1
d.rectangle([(RX0 + int(13*SCALE), U2_Y0), (RX0 + RW - int(13*SCALE), U2_Y0 + H_3U_B1)], fill=(51, 65, 85), outline=LINE_COLOR, width=2)
d.text((RX0 + 80, U2_Y0 + H_3U_B1/2 - 18), "3U: NIIMBOT B1 FACE-OUT THERMAL DOCK", font=font_lbl, fill=(255, 255, 255))
d.text((RX0 + 80, U2_Y0 + H_3U_B1/2 + 6), "Clamshell Roll Compartment Door · Top Power Button · Status LED Access", font=font_small, fill=(148, 163, 184))

# Unit 3: 3U Waveshare Screen Module
U3_Y0 = U2_Y0 - H_3U_DISP
d.rectangle([(RX0 + int(13*SCALE), U3_Y0), (RX0 + RW - int(13*SCALE), U3_Y0 + H_3U_DISP)], fill=(71, 85, 105), outline=LINE_COLOR, width=2)
d.text((RX0 + 80, U3_Y0 + H_3U_DISP/2 - 18), "3U: WAVESHARE 7-INCH CAPACITIVE TOUCH (C)", font=font_lbl, fill=(255, 255, 255))
d.text((RX0 + 80, U3_Y0 + H_3U_DISP/2 + 6), "1024x600 IPS HDMI Panel · Retaining Clips · Integrated Rear Driver Bay", font=font_small, fill=(148, 163, 184))

# Unit 4: 1U UniFi Gateway Shelf
U4_Y0 = U3_Y0 - H_1U_UCG
d.rectangle([(RX0 + int(13*SCALE), U4_Y0), (RX0 + RW - int(13*SCALE), U4_Y0 + H_1U_UCG)], fill=(100, 116, 139), outline=LINE_COLOR, width=2)
d.text((RX0 + 80, U4_Y0 + H_1U_UCG/2 - 10), "1U: UNIFI CLOUD GATEWAY ULTRA (UCG)", font=font_lbl, fill=(255, 255, 255))

# Top Cap
CAP_Y0 = U4_Y0 - H_CAP
d.rectangle([(RX0, CAP_Y0), (RX0 + RW, CAP_Y0 + H_CAP)], fill=(30, 41, 59), outline=LINE_COLOR, width=2)
d.text((RX0 + RW/2 - 40, CAP_Y0 + 6), "TOP CAP", font=font_lbl, fill=(255, 255, 255))

# Handles
HD_W = int(24 * SCALE)
d.rectangle([(RX0 + int(20*SCALE), CAP_Y0 - H_HANDLE), (RX0 + int(20*SCALE) + HD_W, CAP_Y0)], fill=(15, 23, 42), outline=LINE_COLOR)
d.rectangle([(RX0 + RW - int(20*SCALE) - HD_W, CAP_Y0 - H_HANDLE), (RX0 + RW - int(20*SCALE), CAP_Y0)], fill=(15, 23, 42), outline=LINE_COLOR)
d.line([(RX0 + int(20*SCALE) + HD_W/2, CAP_Y0 - H_HANDLE), (RX0 + RW - int(20*SCALE) - HD_W/2, CAP_Y0 - H_HANDLE)], fill=(15, 23, 42), width=int(14*SCALE))

# Dimension lines on Front Elevation
draw_dim_h(RX0, RX0 + RW, BASE_Y + 40, "280.0 mm OVERALL RACK WIDTH")
draw_dim_h(RX0 + int(13*SCALE), RX0 + RW - int(13*SCALE), U1_Y0 - 15, "254.0 mm (10.0\") FACEPLATE WIDTH")
draw_dim_h(RX0 + int(21.7*SCALE), RX0 + RW - int(21.7*SCALE), U1_Y0 + 25, "236.5 mm (9.3125\") EIA HOLE PITCH")

draw_dim_v(RX0 - 35, BASE_Y, BASE_Y - TOTAL_H, "442.0 mm (FRAME HEIGHT)")
draw_dim_v(RX0 - 75, BASE_Y, CAP_Y0 - H_HANDLE, "462.0 mm (TOTAL WITH HANDLES)")
draw_dim_v(RX0 + RW + 25, U1_Y0, U1_Y0 + H_2U, "2U (88.9 mm)", left=False)
draw_dim_v(RX0 + RW + 25, U2_Y0, U2_Y0 + H_3U_B1, "3U (133.4 mm)", left=False)
draw_dim_v(RX0 + RW + 25, U3_Y0, U3_Y0 + H_3U_DISP, "3U (133.4 mm)", left=False)
draw_dim_v(RX0 + RW + 25, U4_Y0, U4_Y0 + H_1U_UCG, "1U (44.5 mm)", left=False)

# ---------------- SECTION 2: SIDE PROFILE DEPTH COMPARISON ----------------
d.rectangle([(1100, 180), (2740, 1020)], fill=(255, 255, 255), outline=(203, 213, 225), width=2)
d.text((1130, 205), "VIEW B: SIDE PROFILE DEPTH COMPARISON (STANDARD vs SLIM CARGO)", font=font_sec, fill=LINE_COLOR)
d.text((1130, 242), "Standard Desktop Depth (200 mm) compared with Luggage/Suitcase-Optimized Slim Cargo Prototype (140 mm)",
       font=font_body, fill=TEXT_MUTED)

# Draw Standard 200 mm depth
SD_X0 = 1200
SD_Y0 = 360
SD_W = int(200 * 2.2)     # 440 px
SD_H = int(260 * 2.2)     # 572 px (representing side profile)

d.rectangle([(SD_X0, SD_Y0), (SD_X0 + SD_W, SD_Y0 + SD_H)], fill=(241, 245, 249), outline=(100, 116, 139), width=2)
d.text((SD_X0 + 20, SD_Y0 + 20), "STANDARD DESKTOP RACK", font=font_lbl, fill=LINE_COLOR)
d.text((SD_X0 + 20, SD_Y0 + 50), "• Depth: 200.0 mm\n• DeskPi T0 Homelab replica\n• Wall: 1.2 mm PLA\n• Protruding 45 mm handles\n• Bulky in carry-on luggage", font=font_body, fill=TEXT_MUTED)
draw_dim_h(SD_X0, SD_X0 + SD_W, SD_Y0 + SD_H + 30, "200.0 mm (STANDARD DEPTH)")

# Draw Slim Cargo 140 mm depth
SC_X0 = 1800
SC_W = int(140 * 2.2)     # 308 px
d.rectangle([(SC_X0, SD_Y0), (SC_X0 + SC_W, SD_Y0 + SD_H)], fill=(255, 241, 242), outline=HIGHLIGHT_COLOR, width=3)
d.text((SC_X0 + 20, SD_Y0 + 20), "SLIM CARGO PROTOTYPE (NEW)", font=font_lbl, fill=HIGHLIGHT_COLOR)
d.text((SC_X0 + 20, SD_Y0 + 50), "• Depth: 140.0 mm (-30% Slimmer!)\n• Fits inside clamshell suitcase!\n• Wall: 2.4 mm PETG / ABS\n• Low-profile 16 mm handles\n• Diagonal anti-racking trusses", font=font_body, fill=(159, 18, 57))
draw_dim_h(SC_X0, SC_X0 + SC_W, SD_Y0 + SD_H + 30, "140.0 mm (SLIM CARGO DEPTH)", color=HIGHLIGHT_COLOR)

# Delta callout
d.rectangle([(2320, SD_Y0 + 80), (2700, SD_Y0 + 240)], fill=(240, 253, 244), outline=(34, 197, 94), width=2)
d.text((2340, SD_Y0 + 105), "CARGO / SUITCASE BENEFIT:", font=font_lbl, fill=(21, 128, 61))
d.text((2340, SD_Y0 + 140), "• Saves 60 mm (2.36 inches) depth\n• Easily clears 100-120 mm suitcase half\n• Allows 25-30 mm protective foam padding\n• Eliminates fragile snagging handles\n• Rigidized unibody frame against drops", font=font_body, fill=(22, 101, 52))

# ---------------- SECTION 3: SUBSYSTEM DEPTH ENVELOPE AUDIT ----------------
d.rectangle([(1100, 1050), (2740, 1920)], fill=(255, 255, 255), outline=(203, 213, 225), width=2)
d.text((1130, 1075), "VIEW C: HOW DEEP EACH UNIT IS vs THE 140 mm SLIM RACK (measured 28 Oct)", font=font_sec, fill=LINE_COLOR)
d.text((1130, 1112), "Measured on the CAD models (03_CHECKS/VERIFICATION_slim-cargo_fit_28Oct.txt). The 4 units fit; the 12 V brick cradle does NOT:",
       font=font_body, fill=TEXT_MUTED)

# Depth bar chart
# 28 Oct (ultrareview): measured on the models (these were typed-in numbers with a fixed PASS; the brick cradle doesn't fit)
UNITS_AUDIT = [
    ("12V 5A brick in the plate 13 cradle", 201.4, "Cradle is 187 mm long: hits the slim middle + rear base bars. Brick goes outside this rack"),
    ("1U UCG-Ultra mount (Printables 942972)", 133.0, "Gateway 127.6 deep; its rear plugs stick out ~20 mm behind when cabled"),
    ("2U Pi unit (Poly+ 5 + adapter (F) holder)", 117.1, "Shelf stands on the slim front + middle bars; UPS OUT plug ends at 127.9"),
    ("3U NIIMBOT B1 dock", 92.0, "Fits"),
    ("3U 7-inch screen module", 30.0, "Fits"),
]

CHART_X0 = 1150
CHART_Y0 = 1180
BAR_SCALE = 7.0   # 140 mm = 980 px

# Limit line at 140 mm
LIMIT_X = int(CHART_X0 + 140 * BAR_SCALE)
d.line([(LIMIT_X, CHART_Y0 - 20), (LIMIT_X, CHART_Y0 + 380)], fill=HIGHLIGHT_COLOR, width=3)
d.text((LIMIT_X - 100, CHART_Y0 - 45), "SLIM LIMIT: 140.0 mm", font=font_lbl, fill=HIGHLIGHT_COLOR)

for idx, (uname, udepth, udesc) in enumerate(UNITS_AUDIT):
    by = CHART_Y0 + idx * 72
    bw = int(min(udepth, 160.0) * BAR_SCALE)
    color = (30, 41, 59) if udepth > 125 else (51, 65, 85) if udepth > 100 else (71, 85, 105)
    # bar
    d.rectangle([(CHART_X0, by), (CHART_X0 + bw, by + 36)], fill=color)
    d.text((CHART_X0 + 15, by + 8), f"{uname} · {udepth:.1f} mm", font=font_lbl, fill=(255, 255, 255))
    # annotation text
    if udepth <= 140.0:
        d.text((CHART_X0 + bw + 15, by + 8), f"FITS ({140.0 - udepth:.1f} mm spare)", font=font_lbl, fill=(34, 197, 94))
    else:
        d.text((CHART_X0 + bw + 15, by + 8), f"DOESN'T FIT (+{udepth - 140.0:.1f} mm)", font=font_lbl, fill=HIGHLIGHT_COLOR)
    d.text((CHART_X0, by + 42), udesc, font=font_small, fill=TEXT_MUTED)

# Summary notes at bottom
d.rectangle([(1130, 1630), (2710, 1890)], fill=(248, 250, 252), outline=(226, 232, 240))
d.text((1150, 1650), "MANUFACTURING & WORKSHOP SPECIFICATION (FOR ONSHAPE / CAD / 3D PRINTING):", font=font_lbl, fill=LINE_COLOR)
d.text((1150, 1685), "1. PRINT MATERIAL FOR CARGO: Print Slim Cargo frame in PETG, ABS/ASA, or PETG-CF (4-5 perimeters, 35%+ Gyroid infill). Do NOT use plain PLA for cargo flight travel.", font=font_body, fill=(51, 65, 85))
d.text((1150, 1720), "2. FASTENERS (ONE SIZE FOR RACK): 48x M5 x 12 mm button head + 48x M5 heat-set inserts (Ø6.4 x 10): 18 joints, 4 cap, 4 handles, 6 bars, 16 units.", font=font_body, fill=(51, 65, 85))
d.text((1150, 1755), "3. MODULAR PACK-FLAT CAPABILITY: Can be fully disassembled in 3 minutes into flat side modules to pack like books inside a suitcase for maximum crush protection.", font=font_body, fill=(51, 65, 85))
d.text((1150, 1790), "4. ONSHAPE ASSEMBLY STEP: Exported byte-validated 3D solid assembly available at: 04_DESIGN_SOURCE/10_Slim_Cargo_Rack_140mm/STEP_for_Onshape/SlimCargo_Rack_9U_140mm_ASSEMBLY.step", font=font_body, fill=(51, 65, 85))

# Save
out_schematic = os.path.abspath("02_RENDERS/00_HOMELAB_RACK_ENGINEERING_SCHEMATIC.png")
im.save(out_schematic, quality=95)
print(f"Generated Master Engineering Schematic -> {out_schematic}")

out_schematic_cargo = os.path.abspath("02_RENDERS/SLIM_CARGO_PROTOTYPE/00_SLIM_CARGO_RACK_SCHEMATIC.png")
im.save(out_schematic_cargo, quality=95)
print(f"Saved Cargo Prototype Schematic copy -> {out_schematic_cargo}")
