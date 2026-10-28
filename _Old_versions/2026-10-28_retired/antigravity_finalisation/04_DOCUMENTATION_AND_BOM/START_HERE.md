> **⚠ 28 Oct 2026, read first:** the print list for your build (Argon Poly+ 5 + F holder, 12-ALT2 UCG mount, plate 13, DC-notch faceplate) is **`FINAL_PRINTS_2026-10-28/`** in the project root, re-checked today. The "v7.3 final" hidden-slit / switch faceplate and the switch extender (plate 14) **do not work** (the Cuzor switch faces the rack rear; the brick-lead notch was lost). They were moved to `_superseded_and_alternatives/BROKEN_antigravity-faceplate+switch-extender_2026-10-28/`, and plates 11 / 11B use the DC-notch faceplate again. Plate counts below: one 3U module per plate (4 in all), one ear on plates 06 and 07 (4 in all); plate 04 is ≈128 g.

# Pi 5 HomeLab: Antigravity Finalization Master Guide

**The finalized design is here in `antigravity_finalisation/`.**
Everything you need to 3D print, order, assemble, and verify is organized cleanly across 4 dedicated folders:

| Folder | What's Inside |
|---|---|
| `FINAL_PRINT_STLs_ONLY/` | **Standalone STL Collection**: Every individual `.stl` file with clear subsystem names, materials, and exact print quantities (ideal for print services like Robu or any custom slicer). |
| `01_PRINT_READY_PLATES/` | All 14 plates for the Bambu P1S (Plates 01–14). Includes the newly updated Plate 11 with the hidden cable slit faceplate, switch access window, and Plate 14 / Plate 11 Switch Extender print. |
| `02_CAD_AND_SOURCE/` | Full CAD package: STEP models for Onshape/CAD, native Python source scripts (CadQuery/Build123d), and component reference models. |
| `03_BLENDER_RENDERS/` | Full Blender studio scene (`Pi5_MiniRack_antigravity_studio.blend`) and photorealistic Cycles renders of the entire rack, Pi unit, switch extender, and dock. |
| `04_DOCUMENTATION_AND_BOM/` | Master BOM (`BOM_Pi5-MiniRack_FINAL.xlsx`), complete parts list (`PARTS_LIST_FINAL.md`), and build guides. |

---

## What was Changed & Added in this Finalization

1. **Hidden Cable Slit (UPS OUT → Waveshare 7–24 V Screw Terminal)**:
   - Previously, running a cable to the front jacks required looping outside the faceplate, exposing ~2 cm of cable on the front of the rack.
   - **Fix:** We added an internal vertical cable pass-through slit on the rear face of the faceplate (`x = 97..106 mm`, `z = 4..38 mm`, 2.5 mm deep) and through the shelf front lip.
   - The outer 1.5 mm of the front faceplate remains solid and closed.
   - **Result:** The 12 V cable from the UPS OUT barrel plug routes directly up inside the channel into the upper board tray and screws into the Waveshare terminal block **100% hidden behind the front faceplate**!

2. **Dedicated UPS ON/OFF Switch Access Opening**:
   - The Cuzor Mini UPS Pro power switch (at `x = 62.6 mm, z = 13.0 mm`) was previously blocked behind solid faceplate plastic.
   - **Fix:** Added a beveled switch access slot (`16 × 11 mm` with 2.5 mm radius corners and a 1.2 mm front finger dish) directly in line with the UPS switch. You can now toggle the UPS power effortlessly from the front panel.

3. **Custom 3D-Printable UPS Switch Extender (`UPS_Switch_Extender`)**:
   - A dedicated 3D-printable slider lever (`Plate14_PETG_UPS-switch-extender.3mf` or on Plate 11).
   - Features a rear pocket that snaps onto the Cuzor switch nub, a sliding arm through the slot, and a front-panel tactile toggle knob with finger grip ribs.
   - Takes only ~8 minutes to print (~2.5 g PETG).

4. **Clean Workspace Folder Structure**:
   - Obsolete and duplicate versions (`Pi5-MiniRack_v7_STL_recovered*`, `Pi 5 Test step files`, `Pi5-Mini-Server_10in-2U-Rack_2026-10-25`, `rework-01`) have been archived into `_Old_versions/`.
   - The entire production project is unified and ready in `antigravity_finalisation/`.

5. **Updated Blender Studio Renders**:
   - Generated high-resolution Cycles renders with studio lighting on Apple M5 Max Metal GPU.
   - Highlight views of the loaded rack, rear ports, exploded assemblies, Pi unit close-up with switch extender, and a master contact sheet (`FINAL_summary_sheet.png`).

---

## Printing Overview (Bambu P1S, 256 × 256 Bed)

Total print time ≈ 47 h. PLA ≈ 1.28 kg (2 spools), PETG ≈ 0.52 kg (1 spool).

| Plate | Contents | Material | Print Profile |
|---|---|---|---|
| **03** | 3U side module + 2 handles | PLA 0.24 | **Print first**: test M5 heat-set insert in Ø6.4 hole |
| **01, 02, 04, 05, 06, 07** | Rack sides, base bars, 1U tops, cap halves, ears | PLA 0.24 | Print any time |
| **08** | NIIMBOT B1 dock v5 (built around real B1 132 × 91 × 62) | PLA 0.20 | Print any time |
| **09** | 7" Screen module (Display7C) | PLA 0.20 | Wait: measure screen arrival (4 Nov) |
| **10** | Pi shelf (pinned) + UPS tray + shims | PETG 0.20 | Print any time, enclosure closed |
| **11** | Pi board tray + lid + final faceplate + switch extender (`Plate11_FINAL_hidden-slit_switch.3mf`) | PETG 0.20 | Brim OFF (faceplate is 254 mm on 256 bed) |
| **12-ALT2** | UCG-Ultra 1U mount (Printables 942972, trimmed 0.8 mm) | PETG 0.20 | Print any time |
| **13** | 12 V brick cradle + spacers (for internal mounting) | PETG 0.20 | Print any time |
| **14** | UPS Switch Extender (standalone quick-print) | PETG 0.20 | ~8 min quick print |

