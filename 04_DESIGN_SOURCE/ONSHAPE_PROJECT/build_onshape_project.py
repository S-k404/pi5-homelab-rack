"""
Build the Complete Master Onshape Project Package for the Pi 5 Homelab 10-Inch 9U Mini Rack.

Generates:
1. Pi5_HomeLab_9U_ALL_IN_ONE_COMBINED.step:
   - 2-in-1 Side-by-Side Complete Master Assembly: Standard 200 mm Desktop Edition on the left,
     Slim Cargo 140 mm Suitcase Travel Edition on the right. Both with all 4 units loaded.
2. Pi5_HomeLab_9U_Complete_ASSEMBLY.step:
   - Master Assembly STEP (Standard 200 mm Depth, DeskPi T0 aesthetic) with all 4 units and 35+ named solids.
3. SlimCargo_HomeLab_9U_Complete_ASSEMBLY.step:
   - Master Assembly STEP (Slim Cargo 140 mm Travel Prototype) with all 4 units.
4. Pi5_HomeLab_9U_SingleBody_Compound_STUDIO.step:
   - Multi-body Part Studio compound solid for direct Onshape Part Studio editing.
5. Curated Library of Individual STEP Files for modular Onshape mating.
6. Dimensioned Technical Engineering Schematics.
7. Standalone Onshape Drag-and-Drop ZIP Archive.
8. Root directory mirror files for instant access.
"""
import os
import sys
import shutil
import time
import zipfile
import cadquery as cq

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SRC = os.path.join(BASE_DIR, "04_DESIGN_SOURCE", "1_Rack_9U_T0-look", "source")
ARGON = os.path.join(BASE_DIR, "04_DESIGN_SOURCE", "7_Argon_Poly5_tray+Waveshare_F_holder")
BRICK_SRC = os.path.join(BASE_DIR, "04_DESIGN_SOURCE", "6_Brick_Cradle_plate13+DC-notch_faceplate", "source")
PI_DIR = os.path.join(BASE_DIR, "04_DESIGN_SOURCE", "4_Pi_Unit_2U")
SLIM_SRC = os.path.join(BASE_DIR, "04_DESIGN_SOURCE", "10_Slim_Cargo_Rack_140mm", "source")
OUT_DIR = os.path.join(BASE_DIR, "04_DESIGN_SOURCE", "ONSHAPE_PROJECT")

sys.path.insert(0, SRC)
sys.path.insert(0, os.path.join(ARGON, "source"))
sys.path.insert(0, BRICK_SRC)
sys.path.insert(0, SLIM_SRC)

import rack_t0 as r
import units as un
import b1_dock as dk
import display as dp
import ucg_shelf as ug
import argon_tray as AT
import waveshare_f_holder as WH
import brick_cradle as BC
import slim_rack as sr

PI_STEP = os.path.join(PI_DIR, "STEP_for_Onshape")
PI_COMP = os.path.join(PI_DIR, "Component_Models")
AR_STEP = os.path.join(ARGON, "STEP_for_Onshape")
FP_CLEAN = os.path.join(PI_STEP, "Rack_Faceplate_2U_10in_clean.step")


def b(x0, x1, y0, y1, z0, z1):
    return cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0))


def cyl(x, y, z0, z1, d):
    return cq.Workplane("XY").circle(d / 2).extrude(z1 - z0).translate((x, y, z0))


def step(path):
    return cq.Workplane().add(cq.importers.importStep(path).val())


def pi_to_rack(shape):
    return shape.rotate((0, 0, 0), (1, 0, 0), -90).translate((-un.PI_CX, -un.PI_Z0, un.PI_PY0))


def argon_poly5():
    L, Wc, Hc = AT.CASES["POLY5"]["nominal"]
    x0, x1, y0, y1 = AT.X_DATUM - Wc, AT.X_DATUM, AT.Y_DATUM, AT.Y_DATUM + L
    z0 = AT.ZS + 1.0
    z1 = z0 + Hc
    zt = z1 - 4.0
    bx0 = x0 + (Wc - 56.0) / 2
    zp = z0 + 5.5
    shell = b(x0, x1, y0, y1, z0, zt).edges("|Z").fillet(5.0)
    top = b(x0, x1, y0, y1, zt + 0.25, z1).edges("|Z").fillet(5.0)
    fx, fy, fr = x0 + Wc * 0.47, y0 + L * 0.58, 14.0
    top = top.cut(cyl(fx, fy, zt - 1, z1 + 1, 2 * fr))
    fan = cyl(fx, fy, zt - 6.0, zt - 3.5, 12.0)
    rj = (bx0 + 10.25, 16.0, 13.5)
    shell = shell.cut(b(rj[0] - 8.6, rj[0] + 8.6, y0 - 1, y0 + 2.4, zp - 0.4, zp + rj[2] + 0.5))
    return shell, top, fan


def adapter_f():
    def comp(xd0, xd1, yd0, yd1, z0, z1):
        (xa, ya), (xb, yb) = WH.d2v(xd0, yd0), WH.d2v(xd1, yd1)
        return b(min(xa, xb), max(xa, xb), min(ya, yb), max(ya, yb), WH.PCB_TOP + z0, WH.PCB_TOP + z1)
    pcb = b(WH.PCB_X0, WH.XP, WH.PCB_Y0, WH.PCB_Y0 + WH.PCB_L, WH.ZB, WH.PCB_TOP)
    rj = comp(-1.0, 20.0, 30.7 - 8.0, 30.7 + 8.0, 0, 13.5)
    hd = comp(-1.0, 13.0, 10.05 - 7.6, 10.05 + 7.6, 0, 6.0)
    metal = rj.union(hd)
    term = comp(79.0, 97.0, 0.8, 16.0, 0, 10.0)
    ssd = comp(40.0, 70.0, 15.0, 37.0, 1.6, 3.0)
    return pcb, metal, term, ssd


def get_units_list():
    dark_metal = cq.Color(0.20, 0.21, 0.23)
    white_dev = cq.Color(0.94, 0.95, 0.96)
    silver = cq.Color(0.78, 0.80, 0.82)
    blue_b1 = cq.Color(0.29, 0.48, 0.59)

    parts = []
    # 1. 1U UCG-Ultra
    t_ucg = (0, un.YC_UCG, -ug.PANEL_T)
    parts.append((ug.body().translate(t_ucg), "UCG_Ultra_1U_Shelf", dark_metal))
    parts.append((ug.gateway_dummy().translate(t_ucg), "UniFi_UCG_Ultra_Gateway", white_dev))

    # 2. 3U Screen
    t_disp = (0, un.YC_DISP, -dp.Z0)
    parts.append((dp.body().translate(t_disp), "Display7C_3U_Body", silver))
    parts.append((dp.ear(1).translate(t_disp), "Display7C_Ear_R", silver))
    parts.append((dp.ear(-1).translate(t_disp), "Display7C_Ear_L", silver))
    parts.append((dp.screen_dummy().translate(t_disp), "Waveshare_7in_LCD", cq.Color(0.15, 0.17, 0.20)))
    for i, c in enumerate(dp.clips()):
        parts.append((c.translate(t_disp), f"Display7C_Clip_{i+1}", silver))

    # 3. 3U B1 Dock
    t_dock = (0, un.YC_DOCK, -dk.EAR_T)
    parts.append((dk.body().translate(t_dock), "B1_Dock_3U_Body", silver))
    parts.append((dk.ear(1).translate(t_dock), "B1_Dock_3U_Ear_R", silver))
    parts.append((dk.ear(-1).translate(t_dock), "B1_Dock_3U_Ear_L", silver))
    bp = dk.b1_parts()
    parts.append((bp["body"].translate(t_dock), "NIIMBOT_B1_Body", blue_b1))
    parts.append((bp["lid"].translate(t_dock), "NIIMBOT_B1_Lid", cq.Color(0.13, 0.13, 0.13)))
    parts.append((bp["slide"].translate(t_dock), "NIIMBOT_B1_Slide", cq.Color(0.96, 0.96, 0.96)))
    parts.append((bp["button"].translate(t_dock), "NIIMBOT_B1_Button", cq.Color(0.60, 0.63, 0.65)))
    parts.append((bp["led"].translate(t_dock), "NIIMBOT_B1_LED", cq.Color(0.20, 0.83, 0.60)))

    # 4. 2U Pi Unit
    parts.append((pi_to_rack(step(os.path.join(PI_STEP, "Rack_Shelf_pinned.step"))), "Pi5_Rack_Shelf", dark_metal))
    parts.append((pi_to_rack(step(FP_CLEAN)), "Pi5_Faceplate_2U_clean", dark_metal))
    parts.append((pi_to_rack(step(os.path.join(PI_STEP, "Pi5_UPS_v3_ups_tray_pinned.step"))), "Pi5_UPS_Tray", dark_metal))
    c_ups = step(os.path.join(PI_COMP, "Cuzor_MiniUPS_Pro_12V3A.step")).translate((50.6, 40.6, 1.0))
    parts.append((pi_to_rack(c_ups), "Cuzor_MiniUPS_Pro_12V3A", cq.Color(0.12, 0.16, 0.23)))
    parts.append((pi_to_rack(step(os.path.join(AR_STEP, "Pi5_ArgonPoly5_tray.step"))), "Pi5_ArgonPoly5_Tray", dark_metal))
    parts.append((pi_to_rack(step(os.path.join(AR_STEP, "Waveshare_F_holder_base.step"))), "Waveshare_F_Holder_Base", dark_metal))
    parts.append((pi_to_rack(step(os.path.join(AR_STEP, "Waveshare_F_holder_lid.step"))), "Waveshare_F_Holder_Lid", dark_metal))
    ar_shell, ar_top, ar_fan = argon_poly5()
    parts.append((pi_to_rack(ar_shell), "Argon_Poly5_Shell", cq.Color(0.1, 0.1, 0.1)))
    parts.append((pi_to_rack(ar_top), "Argon_Poly5_Top", cq.Color(0.15, 0.15, 0.15)))
    af_pcb, af_metal, af_term, af_ssd = adapter_f()
    parts.append((pi_to_rack(af_pcb), "Waveshare_Adapter_F_PCB", cq.Color(0.05, 0.28, 0.63)))
    parts.append((pi_to_rack(af_metal), "Adapter_F_RJ45_HDMI", cq.Color(0.8, 0.8, 0.8)))
    parts.append((pi_to_rack(af_term), "Adapter_F_12V_Terminal", cq.Color(0.1, 0.5, 0.2)))
    parts.append((pi_to_rack(af_ssd), "EVM_512GB_NVMe_SSD", cq.Color(0.1, 0.1, 0.1)))
    return parts


def build_all_in_one_side_by_side():
    print("\n--- Generating Pi5_HomeLab_9U_ALL_IN_ONE_COMBINED.step (2-in-1 Side-by-Side) ---")
    t0 = time.time()
    asm = cq.Assembly()
    DX = 200.0  # offset: Standard at -200 mm, Slim at +200 mm
    silver = cq.Color(0.78, 0.80, 0.82)
    dark_metal = cq.Color(0.20, 0.21, 0.23)

    # 1. Standard Rack (Left, X = -DX)
    P_std = r.assembly()
    for n, s in P_std.items():
        asm.add(s.translate((-DX, 0, 0)), name=f"STD_Rack_{n}", color=silver)
    for s, n, col in get_units_list():
        asm.add(s.translate((-DX, 0, 0)), name=f"STD_{n}", color=col)
    cradle = BC.brick_cradle()
    spacer8 = BC.spacer(8.0)
    brick = BC.brick_dummy(110.0, 50.0, 30.0, 8.0)
    asm.add(cradle.translate((-DX, 0, 0)), name="STD_Brick_Cradle_12V", color=dark_metal)
    asm.add(spacer8.translate((-DX, 0, 0)), name="STD_Brick_Spacer_8mm", color=dark_metal)
    asm.add(brick.translate((-DX, 0, 0)), name="STD_Power_Brick_12V_5A", color=cq.Color(0.15, 0.15, 0.15))

    # 2. Slim Cargo Rack (Right, X = +DX)
    P_slim = sr.assembly()
    for n, s in P_slim.items():
        asm.add(s.translate((DX, 0, 0)), name=f"SLIM_Rack_{n}", color=silver)
    for s, n, col in get_units_list():
        asm.add(s.translate((DX, 0, 0)), name=f"SLIM_{n}", color=col)
    brick_slim = b(69.0, 109.0, 2.0, 32.0, 15.0, 125.0).edges().fillet(2.0)
    asm.add(brick_slim.translate((DX, 0, 0)), name="SLIM_Power_Brick_12V_5A", color=cq.Color(0.15, 0.15, 0.15))

    out_file = os.path.join(OUT_DIR, "Pi5_HomeLab_9U_ALL_IN_ONE_COMBINED.step")
    asm.export(out_file)
    print(f"Exported: {out_file} ({os.path.getsize(out_file)/1024/1024:.2f} MB, {time.time()-t0:.1f}s)")
    # Also copy to root directory for immediate access
    shutil.copy2(out_file, os.path.join(BASE_DIR, "Pi5_HomeLab_9U_COMBINED_FOR_ONSHAPE.step"))
    return out_file


def build_standard_master_assembly():
    print("\n--- Generating Pi5_HomeLab_9U_Complete_ASSEMBLY.step (200 mm Standard) ---")
    t0 = time.time()
    asm = cq.Assembly()
    silver = cq.Color(0.78, 0.80, 0.82)
    dark_metal = cq.Color(0.20, 0.21, 0.23)

    P = r.assembly()
    for n, s in P.items():
        asm.add(s, name=f"Rack_{n}", color=silver)
    for s, n, col in get_units_list():
        asm.add(s, name=n, color=col)

    cradle = BC.brick_cradle()
    spacer8 = BC.spacer(8.0)
    brick = BC.brick_dummy(110.0, 50.0, 30.0, 8.0)
    asm.add(cradle, name="Brick_Cradle_12V", color=dark_metal)
    asm.add(spacer8, name="Brick_Spacer_8mm", color=dark_metal)
    asm.add(brick, name="Power_Brick_12V_5A", color=cq.Color(0.15, 0.15, 0.15))

    out_file = os.path.join(OUT_DIR, "Pi5_HomeLab_9U_Complete_ASSEMBLY.step")
    asm.export(out_file)
    print(f"Exported: {out_file} ({os.path.getsize(out_file)/1024/1024:.2f} MB, {time.time()-t0:.1f}s)")
    shutil.copy2(out_file, os.path.join(BASE_DIR, "Pi5_HomeLab_9U_Standard_Master.step"))
    return out_file


def build_slim_cargo_master_assembly():
    print("\n--- Generating SlimCargo_HomeLab_9U_Complete_ASSEMBLY.step (140 mm Slim Cargo) ---")
    t0 = time.time()
    asm = cq.Assembly()
    silver = cq.Color(0.78, 0.80, 0.82)

    P = sr.assembly()
    for n, s in P.items():
        asm.add(s, name=f"SlimCargo_{n}", color=silver)
    for s, n, col in get_units_list():
        asm.add(s, name=n, color=col)

    brick = b(69.0, 109.0, 2.0, 32.0, 15.0, 125.0).edges().fillet(2.0)
    asm.add(brick, name="Power_Brick_12V_5A", color=cq.Color(0.15, 0.15, 0.15))

    out_file = os.path.join(OUT_DIR, "SlimCargo_HomeLab_9U_Complete_ASSEMBLY.step")
    asm.export(out_file)
    print(f"Exported: {out_file} ({os.path.getsize(out_file)/1024/1024:.2f} MB, {time.time()-t0:.1f}s)")
    shutil.copy2(out_file, os.path.join(BASE_DIR, "Pi5_HomeLab_9U_SlimCargo_Master.step"))
    return out_file


def build_single_body_compound():
    print("\n--- Generating Pi5_HomeLab_9U_SingleBody_Compound_STUDIO.step ---")
    t0 = time.time()
    solids = []

    # Rack frame
    P = r.assembly()
    for s in P.values():
        solids.append(s.val())

    # Units
    for s, _, _ in get_units_list():
        solids.append(s.val())

    solids.append(BC.brick_cradle().val())
    solids.append(BC.spacer(8.0).val())
    solids.append(BC.brick_dummy(110.0, 50.0, 30.0, 8.0).val())

    compound = cq.Compound.makeCompound(solids)
    out_file = os.path.join(OUT_DIR, "Pi5_HomeLab_9U_SingleBody_Compound_STUDIO.step")
    cq.exporters.export(cq.Workplane().add(compound), out_file)
    print(f"Exported: {out_file} ({os.path.getsize(out_file)/1024/1024:.2f} MB, {time.time()-t0:.1f}s)")
    return out_file


def copy_individual_steps():
    print("\n--- Populating Curated INDIVIDUAL_STEP_PARTS Library ---")
    parts_dir = os.path.join(OUT_DIR, "INDIVIDUAL_STEP_PARTS")
    os.makedirs(parts_dir, exist_ok=True)

    sources = [
        # Standard Rack
        ("04_DESIGN_SOURCE/1_Rack_9U_T0-look/STEP_for_Onshape/Rack_SideModule_2U_Base_x2.step", "01_RACK_SideModule_2U_Base_x2.step"),
        ("04_DESIGN_SOURCE/1_Rack_9U_T0-look/STEP_for_Onshape/Rack_SideModule_3U_x4.step", "01_RACK_SideModule_3U_x4.step"),
        ("04_DESIGN_SOURCE/1_Rack_9U_T0-look/STEP_for_Onshape/Rack_SideModule_1U_Top_x2.step", "01_RACK_SideModule_1U_Top_x2.step"),
        ("04_DESIGN_SOURCE/1_Rack_9U_T0-look/STEP_for_Onshape/Rack_CapHalf_x2.step", "01_RACK_CapHalf_x2.step"),
        ("04_DESIGN_SOURCE/1_Rack_9U_T0-look/STEP_for_Onshape/Rack_Handle_x2.step", "01_RACK_Handle_x2.step"),
        ("04_DESIGN_SOURCE/1_Rack_9U_T0-look/STEP_for_Onshape/Rack_BaseBar_x3.step", "01_RACK_BaseBar_x3.step"),
        # Slim Cargo Rack
        ("04_DESIGN_SOURCE/10_Slim_Cargo_Rack_140mm/STEP_for_Onshape/SlimCargo_SideModule_2U_Base_x2.step", "02_SLIM_SideModule_2U_Base_x2.step"),
        ("04_DESIGN_SOURCE/10_Slim_Cargo_Rack_140mm/STEP_for_Onshape/SlimCargo_SideModule_3U_x4.step", "02_SLIM_SideModule_3U_x4.step"),
        ("04_DESIGN_SOURCE/10_Slim_Cargo_Rack_140mm/STEP_for_Onshape/SlimCargo_SideModule_1U_Top_x2.step", "02_SLIM_SideModule_1U_Top_x2.step"),
        ("04_DESIGN_SOURCE/10_Slim_Cargo_Rack_140mm/STEP_for_Onshape/SlimCargo_CapHalf_x2.step", "02_SLIM_CapHalf_x2.step"),
        ("04_DESIGN_SOURCE/10_Slim_Cargo_Rack_140mm/STEP_for_Onshape/SlimCargo_LowProfile_Handle_x2.step", "02_SLIM_LowProfile_Handle_x2.step"),
        ("04_DESIGN_SOURCE/10_Slim_Cargo_Rack_140mm/STEP_for_Onshape/SlimCargo_BaseBar_x3.step", "02_SLIM_BaseBar_x3.step"),
        # 1U UCG-Ultra
        ("04_DESIGN_SOURCE/5_UCG-Ultra_1U/STEP_for_Onshape/UCG_Ultra_1U_Shelf.step", "03_UCG_Ultra_1U_Shelf.step"),
        ("04_DESIGN_SOURCE/5_UCG-Ultra_1U/STEP_for_Onshape/UCG_Ultra_1U_ASSEMBLY.step", "03_UCG_Ultra_1U_ASSEMBLY.step"),
        # 3U Screen
        ("04_DESIGN_SOURCE/3_Display_7in_3U/STEP_for_Onshape/Display7C_3U_Body.step", "04_DISPLAY_7C_3U_Body.step"),
        ("04_DESIGN_SOURCE/3_Display_7in_3U/STEP_for_Onshape/Display7C_Clip_x4.step", "04_DISPLAY_7C_Clip_x4.step"),
        ("04_DESIGN_SOURCE/3_Display_7in_3U/STEP_for_Onshape/Display7C_3U_ASSEMBLY.step", "04_DISPLAY_7C_3U_ASSEMBLY.step"),
        ("04_DESIGN_SOURCE/3_Display_7in_3U/Component_Models/Waveshare_7inch_HDMI_LCD_C.step", "04_WAVESHARE_7inch_HDMI_LCD_C.step"),
        # 3U B1 Dock
        ("04_DESIGN_SOURCE/2_B1_Dock_3U/STEP_for_Onshape/B1_Dock_3U_Body.step", "05_B1_Dock_3U_Body.step"),
        ("04_DESIGN_SOURCE/2_B1_Dock_3U/STEP_for_Onshape/B1_Dock_3U_Ear_x2.step", "05_B1_Dock_3U_Ear_x2.step"),
        ("04_DESIGN_SOURCE/2_B1_Dock_3U/STEP_for_Onshape/B1_Dock_3U_ASSEMBLY.step", "05_B1_Dock_3U_ASSEMBLY.step"),
        # 2U Pi Unit
        ("04_DESIGN_SOURCE/4_Pi_Unit_2U/STEP_for_Onshape/Rack_Shelf_pinned.step", "06_PI5_Rack_Shelf_pinned.step"),
        ("04_DESIGN_SOURCE/4_Pi_Unit_2U/STEP_for_Onshape/Rack_Faceplate_2U_10in_clean.step", "06_PI5_Faceplate_2U_clean.step"),
        ("04_DESIGN_SOURCE/4_Pi_Unit_2U/STEP_for_Onshape/Pi5_UPS_v3_ups_tray_pinned.step", "06_PI5_UPS_Tray_pinned.step"),
        ("04_DESIGN_SOURCE/7_Argon_Poly5_tray+Waveshare_F_holder/STEP_for_Onshape/Pi5_ArgonPoly5_tray.step", "06_PI5_ArgonPoly5_tray.step"),
        ("04_DESIGN_SOURCE/7_Argon_Poly5_tray+Waveshare_F_holder/STEP_for_Onshape/Waveshare_F_holder_base.step", "06_PI5_Waveshare_F_holder_base.step"),
        ("04_DESIGN_SOURCE/7_Argon_Poly5_tray+Waveshare_F_holder/STEP_for_Onshape/Waveshare_F_holder_lid.step", "06_PI5_Waveshare_F_holder_lid.step"),
        ("04_DESIGN_SOURCE/6_Brick_Cradle_plate13+DC-notch_faceplate/STEP_for_Onshape/Brick_Cradle_12V.step", "06_PI5_Brick_Cradle_12V.step"),
        ("04_DESIGN_SOURCE/6_Brick_Cradle_plate13+DC-notch_faceplate/STEP_for_Onshape/Brick_Spacer_8mm.step", "06_PI5_Brick_Spacer_8mm.step"),
        ("04_DESIGN_SOURCE/4_Pi_Unit_2U/Component_Models/Cuzor_MiniUPS_Pro_12V3A.step", "06_PI5_Cuzor_MiniUPS_Pro_12V3A.step"),
    ]

    copied = 0
    for src_rel, dst_name in sources:
        src_abs = os.path.join(BASE_DIR, src_rel)
        if os.path.exists(src_abs):
            dst_abs = os.path.join(parts_dir, dst_name)
            shutil.copy2(src_abs, dst_abs)
            copied += 1
    print(f"Copied {copied} individual component STEP files to {parts_dir}")


def copy_schematics():
    print("\n--- Copying Dimensioned Engineering Schematics ---")
    schem_src = os.path.join(BASE_DIR, "02_RENDERS", "00_HOMELAB_RACK_ENGINEERING_SCHEMATIC.png")
    schem_cargo = os.path.join(BASE_DIR, "02_RENDERS", "SLIM_CARGO_PROTOTYPE", "00_SLIM_CARGO_RACK_SCHEMATIC.png")

    if os.path.exists(schem_src):
        shutil.copy2(schem_src, os.path.join(OUT_DIR, "00_HOMELAB_RACK_ENGINEERING_SCHEMATIC.png"))
        print(f"Copied Master Schematic to {OUT_DIR}")
    if os.path.exists(schem_cargo):
        shutil.copy2(schem_cargo, os.path.join(OUT_DIR, "00_SLIM_CARGO_RACK_SCHEMATIC.png"))
        print(f"Copied Slim Cargo Schematic to {OUT_DIR}")


def build_zip_package():
    print("\n--- Creating Pi5_HomeLab_9U_Onshape_Project_Package.zip ---")
    zip_path = os.path.join(OUT_DIR, "Pi5_HomeLab_9U_Onshape_Project_Package.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(OUT_DIR):
            for f in files:
                if f.endswith(".zip") or f.endswith(".py"):
                    continue
                abs_f = os.path.join(root, f)
                rel_f = os.path.relpath(abs_f, OUT_DIR)
                zf.write(abs_f, arcname=rel_f)
    print(f"Created ZIP: {zip_path} ({os.path.getsize(zip_path)/1024/1024:.2f} MB)")
    shutil.copy2(zip_path, os.path.join(BASE_DIR, "Pi5_HomeLab_9U_Onshape_Project_Package.zip"))


if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)
    build_all_in_one_side_by_side()
    build_standard_master_assembly()
    build_slim_cargo_master_assembly()
    build_single_body_compound()
    copy_individual_steps()
    copy_schematics()
    build_zip_package()
    print("\n[SUCCESS] Master Onshape Project Build Complete!")
