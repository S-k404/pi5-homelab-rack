# Ultrareview, 28 Oct 2026 (done locally)

You asked `/ultrareview` to check the wiring constraints, fix project parity, verify every part and the BOMs, catch anything any agent missed, render on this Mac, and put the changes here. **The real `/ultrareview` couldn't run.** The repo has no commits it can diff against, no GitHub remote, and its first commit holds ~17 million lines (433 MB in `.git`) of STL/STEP/PNG: the `.gitignore` was added *after* that commit. So the same review was done here, on the CAD models, with the project's own scripts.

**The to-do list that comes out of it is `../FINAL_TODO/FINAL_TODO.md`.**

## Second pass (same evening): the clean front, and the UCG display window
You asked to hide the cabling at the front of the Pi unit (render 05) and to fix the UCG-Ultra's display hole.

**The front.** On 27 Oct the brick's 12 V lead left through a notch in the faceplate and plugged into the UPS DC-IN from the front. The cause: the shelf's right post and gusset, plus the Argon tray's floor, close off the space behind the faceplate. Antigravity's "hidden" version simply ran the lead through solid parts. The real fix changes two prints:
- **10 Pi shelf:** a 9 × 7 mm arch at the foot of the right post's gusset (`pi_rack.PASS_Y`). It's 1 mm behind the post and clear of its inserts, and only 355 mm³ is removed.
- **C2 faceplate → `C2_Pi_Faceplate_2U_clean`:** no DC-IN window and no notch (`faceplate(dcin_window=False)`). It doesn't depend on the UPS check any more.
- **New part to buy:** a ~30 cm right-angle 5.5 × 2.1 male → straight female extension.

The route (`04_DESIGN_SOURCE/4_Pi_Unit_2U/source/brick_lead_route.py`):
1. The extension's plug sits in the UPS DC-IN, inside the tray's DC-IN window (10.5 mm to spare each side).
2. Its cable drops to the shelf floor and runs under the UPS OUT lead.
3. It goes through the arch, across in front of the brick cradle and into the cradle's open front.
4. There the brick's own plug pushes into the extension's socket, riding over the strap rib.
5. The brick's spare lead is coiled beside the join.

Checked in `03_CHECKS/VERIFICATION_wiring_all-cables_28Oct.txt`:
- every piece touches nothing, including the UPS OUT plug and lead
- the front-most point is 8.5 mm behind the faceplate
- the faceplate is solid where the window and notch were
- the new shelf and faceplate overlap nothing in the rack
- the shelf export was byte-identical to print 10 before the change
- the power-path and Slim Cargo reports are unchanged

Re-upload **10** and **C2** to the Robu cart.

**The cables at the back, seen from the front.** In the first pass the riser ran at x -92. You could see it through the open B1 dock and through the UCG mount's empty keystone hole. It's now one straight run **tight against the right-hand side** (seen from the front; x -110), behind the dock's and screen's ears. The side modules are open at the back down to x -112 except at their joint ribs. The cables leave the Pi's rear ports at 50 mm height, and the Cat6 and the gateway's power cross behind the gateway at 362 mm, below the keystone's line of sight. In render 03 (straight on) no cable shows. From a 3/4 view you still see the B1's own USB-C lead inside the open dock. All routes still pass; HDMI ≈ 62 cm, micro-USB ≈ 70, Cat6 ≈ 61 with slack.

**The UCG display hole was right; the renders were wrong.** Ubiquiti's own straight front view (store.ui.com product image) puts the 0.96" display centred across, with its centre **18.5 mm above the gateway's base**, not at mid-height. The Printables mount's window is centred there (within ~0.3 mm). The renders drew the display at mid-height, 3.5 mm too low. That's the misalignment you saw, and it's fixed in `export_final.py`. Moving the hole would have put it off on the real gateway. (Our own unused plate-12 shelf also assumed mid-height.)

Ubiquiti's rear view also settles the rear plugs:
- the RJ45 openings run 13.5–23.9 mm above the base and the USB-C sits at 17.4 mm, so the plugs clear the mount's 10 mm lip and LAN 1 clears the corner post
- the reset pinhole is behind the post
- Ubiquiti says the 5 V 3 A USB-C adapter is included

## What it found (most serious first)

| # | Severity | Finding | What was done |
|---|---|---|---|
| 1 | **High** | **Another tool (Antigravity) changed the wiring check and the renders after the 28 Oct checks.** `verify_pi_power_path.py` got a 9 × 9 × 6 mm "compact" UPS OUT plug (no real right-angle 5.5 × 2.1 plug is 6 mm deep) and a lead route "hidden under the tray shelf". Run, **that version fails its own check**: the 3.5 mm lead runs 18 mm³ into the UPS tray and 9 mm³ into the brick's plug. The same "hidden" route was drawn in `export_final.py` and render 16 (`fix_power_path_cutaway.py`), with a right-angle plug in the DC-IN the Robu brick doesn't have. `verify_brick.py` and its report were edited too. | Original scripts put back from `_Old_versions/2026-10-28_retired/`. Re-run, the power-path report matches `03_CHECKS` line for line. All renders re-made. The edited files are in `before/` |
| 2 | **High** | **The adapter (F) holder's 18.6 mm HDMI notch stops the HDMI plug.** HDMI plug mouldings are 20–22 mm wide and sit in the rear wall's last 2.4 mm: 36 mm³ of the holder in the way of even a slim 20 × 9 plug. The holder check had a **fixed `PASS`** line saying "an HDMI plug (about 21 × 12) fits the notches"; nothing measured it. | `waveshare_f_holder.py`: the rear wall is cut back 23 mm wide round the HDMI jack, down to the deck (`HDMI_RELIEF_W`). The check now pushes a 22 × 12 HDMI and a 14 × 15 RJ45 plug home: **26 PASS** (the old holder fails it, 147 mm³). New W2 STL, STEP, Plate11W. **Re-upload W2 to the Robu cart.** The lid didn't change |
| 3 | Medium | **Slim Cargo 140 mm (made by Antigravity):** its docs and schematic said all units fit, with typed-in depths ("brick cradle 120 mm, 20 mm spare", "12 V 3 A") and a `PASS` printed for every bar. Measured: **the brick cradle is 187 mm long and hits the slim middle and rear bars.** It also needs 48 M5 screws + inserts, not 38. It sat in `01_PRINT_FILES` as "5_" next to the real order. | New check `03_CHECKS/VERIFICATION_slim-cargo_fit_28Oct.txt`: the four units fit and the Pi shelf stands on the slim bars; the brick doesn't fit. Both Slim READMEs corrected and marked "alternative, not part of the order". `make_schematic.py` now draws the measured depths and a red "doesn't fit"; both schematic PNGs regenerated |
| 4 | Medium | **Cat6 length:** the Robu cart notes said 0.5 m; the route from the adapter to the gateway's LAN 1 needs ≈ 61 cm with slack. | 1 m everywhere |
| 5 | Medium | **The UCG mount (Printables 942972) and the gateway's rear plugs.** Measured on the mesh: a rear lip covers the bottom 10 mm of the gateway's back, and corner posts cover its last 14 mm (right, from the front) and 4 mm (left). Ubiquiti publish no rear drawing, so if a jack sits lower than 10 mm, its plug hits the lip. | A to-do item with the fix: sit the gateway in the printed mount, plug in, trim the lip to ~5 mm if needed |
| 6 | Medium | **`ROBU_HARDWARE_CART_TO_RESTORE.md`:** the 13 lines add up to **₹14,564**, not ₹15,083 (the ₹519 Active Cooler was still counted). Its Argon section was stale: "the adapter can't be used, no NVMe, UGREEN required". It also listed M2.5 × 8/× 10 screws for the old case and a 0.5 m Cat6. | Fixed. It also now says the screen and the UPS are in the Amazon cart too, and that the "M5-M6 90 pcs" insert pack may hold fewer than the 48 M5 needed |
| 7 | Medium | **PARTS_LIST prices didn't match the carts.** The screen was at Amazon's ₹5,691 though the Robu cart has ₹4,389; the UPS at ₹1,998 vs ₹2,199; the microSD at ₹350 vs ₹1,629; the micro-USB at ₹200 vs ₹59; the fasteners at ≈ ₹1,909 vs ₹2,997. | Re-priced from the Robu cart: total **₹73,481**, still to spend **₹44,279** + the unpriced screws, feet and tape. Cable descriptions now cover both fit-test outcomes |
| 8 | Low | **Onshape README:** the fastener table didn't add up (38 M5, but its own breakdown is 52; 8 cap screws instead of 4; M2.5 × 6 + standoffs instead of M2.5 × 25). The master STEP assemblies carry the **unused custom UCG shelf** and the pre-fix holder. | Table corrected (48 M5 and the full M3 / M2.5 list), plus a "viewing only" note. The individual holder STEP was updated |
| 9 | Low | **Plate09 (screen) settings:** the tab-hole span was given as ~159 × ~114 with a ±0.5 mm pass rule. Waveshare's STEP has the holes 157.0 apart across; up and down they're slots 112.8–117.0. A right screen would have "failed". It also said black PLA. | Corrected |
| 10 | Low | **B1 dock README:** said the lid opens ~70°. Antigravity moved the lid hinge in `b1_dock.py`; the dock check gives 120° with that hinge and 85° with the earlier one. | README says both. The dock passes 22/22 either way, so it doesn't change the print |
| 11 | Info | Things nobody had written down: | Now in `FINAL_TODO` |
| | | - **which 16 rail holes** get M5 inserts (front holes 1, 6, 7, 15, 16, 24, 25, 27 from the bottom) | |
| | | - the brick's DC lead only needs ≈ 20 cm, so ~0.8–1.3 m has to be coiled (room: 110 × 38 × 40 mm on top of the brick) | |
| | | - the screen + B1 charging use ~1.3–1.5 A of the Pi's 1.6 A USB budget | |
| | | - the gateway isn't on the UPS | |
| | | - check the brick comes with a mains cord | |
| | | - the screen and the UPS are in two carts | |

## What was checked and is fine
- **Every print STL** (22 files) is byte-identical to its checked source, except W2, which is the fix. The 3MF plates read back identical, except Plate11W.
- **The power path** (UPS OUT plug, the 24 cm lead to the terminal, the side ports) re-runs identical to `03_CHECKS`.
- **The brick cradle report** was restored, and is identical to `03_CHECKS`.
- **The B1 dock:** 22 PASS with either lid hinge.
- **Every cable** (`03_CHECKS/VERIFICATION_wiring_all-cables_28Oct.txt`, 15 PASS, 1 FAIL, 3 WARN):
  - HDMI, micro-USB, B1 USB-C, Cat6 and the gateway's power all route up the rack's open back without touching any part.
  - The 1 m and 50 cm cables are long enough.
  - The UPS OUT (36 W) covers the Pi side at ~28 W.
- **The fastener counts in PARTS_LIST** match the CAD:
  - 48 M5: 18 joints, 4 cap, 4 handles, 6 bars, 16 rail holes
  - 18 M3 inserts: dock 4, screen 8, shelf 6
  - 14 M3 × 8 countersunk, 4 M3 × 8 button
  - 3 M3 × 12 into 2.5 mm pilots, so no inserts
  - 4 M2.5 × 25 into 2.1 mm pilots

## Renders (made on this Mac: Blender 5.2.3, Cycles on the GPU)
`renders/` and `../02_RENDERS/` hold all 18 shots and `FINAL_sheet.png`.
- 01–16 are re-made from the honest scene: the fixed holder, the brick lead out through the notch, and the checked UPS OUT route.
- **17** (the rack with the cable side off) and **18** (straight from the back) are new: they show every cable.
- The turntable and exploded GIF/MP4s in `02_RENDERS` were made by Antigravity from its own scene before this review, so they show its lead route. They weren't re-made.

## Re-running
The CadQuery venv is in the project memory.
1. `02_RENDERS/source/export_final.py <rack src> <4_Pi_Unit_2U> <scene> <UCG meshes> <folder 7> <folder 6/source> <DC-notch STEP>`
2. `04_DESIGN_SOURCE/9_scripts_28Oct/verify_wiring_all.py <scene> <rack src> <report> [<wired scene>]`
3. `verify_slim_fit.py <slim in_rack_coords> <scene> <report>`
4. `blender -b --python 02_RENDERS/source/build_final.py -- <wired scene> <out> final`

Copy `screen_ui.png` and `ucg_ui.png` into the scene folder before step 4.

## Not done
- The Onshape master STEPs (~100 MB) weren't regenerated in the review itself. **Done afterwards, same day** (clean faceplate, shelf with the arch, holder base with the HDMI relief).
- The Slim Cargo had no plates or weight estimate. **Added afterwards, same day**: seven P1S plates and a filament estimate (see `01_PRINT_FILES/5_SLIM_CARGO_…/README.md`). That pass also corrected the Slim READMEs' "no supports needed, all overhangs ≤ 45°" and their total height (445 mm; measured 458 mm with the plinth).
- Nothing physical was tested: the UPS jacks, the Poly+ 5 fit test, the gateway's port heights and the B1's USB-C position are still to-dos.
- Nothing was committed to git during the review. **Committed afterwards, same day**, in two commits: the text (docs, scripts, checks) and the binaries (print files, renders, STEP).

## Every file changed (old versions in `before/`, same paths)

**Changed:**
- `01_PRINT_FILES/1_PRINT-NOW/10_Pi_Rack_Shelf_pinned__x1__PETG.stl`
- `01_PRINT_FILES/1_PRINT-NOW/P1S_plates/Plate10_layout.png`
- `01_PRINT_FILES/1_PRINT-NOW/P1S_plates/Plate10_SETTINGS.txt`
- `01_PRINT_FILES/1_PRINT-NOW/P1S_plates/Plate10.3mf`
- `01_PRINT_FILES/1_PRINT-NOW/P1S_plates/Plate13_SETTINGS.txt`
- `01_PRINT_FILES/2_CHECK-UPS-FIRST/P1S_plates/Plate11_CHECK-UPS_layout.png`
- `01_PRINT_FILES/2_CHECK-UPS-FIRST/P1S_plates/Plate11_CHECK-UPS_SETTINGS.txt`
- `01_PRINT_FILES/2_CHECK-UPS-FIRST/P1S_plates/Plate11_CHECK-UPS.3mf`
- `01_PRINT_FILES/3_WAIT/P1S_plates/Plate09_SETTINGS.txt`
- `01_PRINT_FILES/3_WAIT/P1S_plates/Plate11W_WAIT.3mf`
- `01_PRINT_FILES/3_WAIT/W2_Waveshare_F_Holder_Base__x1__PETG__WAIT-fit-test.stl`
- `01_PRINT_FILES/5_SLIM_CARGO_140mm_TRAVEL_PROTOTYPE/README.md`
- `01_PRINT_FILES/README.md`
- `01_PRINT_FILES/ROBU_HARDWARE_CART_TO_RESTORE.md`
- `02_RENDERS/00_HOMELAB_RACK_ENGINEERING_SCHEMATIC.png`
- `02_RENDERS/01_rack_loaded_front.png`
- `02_RENDERS/02_rack_loaded_back.png`
- `02_RENDERS/03_rack_front_straight.png`
- `02_RENDERS/04_rack_exploded.png`
- `02_RENDERS/05_pi_unit.png`
- `02_RENDERS/06_pi_unit_back_ports.png`
- `02_RENDERS/07_pi_unit_exploded.png`
- `02_RENDERS/08_pi_unit_faceplate_off.png`
- `02_RENDERS/09_pi_unit_holder_open.png`
- `02_RENDERS/10_b1_dock.png`
- `02_RENDERS/11_b1_dock_lid_open.png`
- `02_RENDERS/12_screen_module.png`
- `02_RENDERS/13_ucg_mount.png`
- `02_RENDERS/14_ucg_mount_back.png`
- `02_RENDERS/15_pi_power_rear_ups_out_plug.png`
- `02_RENDERS/16_pi_power_path_cutaway.png`
- `02_RENDERS/FINAL_sheet.png`
- `02_RENDERS/Pi5_MiniRack_FINAL_studio.blend`
- `02_RENDERS/README.txt`
- `02_RENDERS/SLIM_CARGO_PROTOTYPE/00_SLIM_CARGO_RACK_SCHEMATIC.png`
- `02_RENDERS/source/build_final.py`
- `02_RENDERS/source/export_final.py`
- `02_RENDERS/source/make_sheet_final.py`
- `03_CHECKS/MEASUREMENTS_every_part.md`
- `03_CHECKS/PLATES_3MF_audit.txt`
- `03_CHECKS/README.md`
- `03_CHECKS/VERIFICATION_wiring_all-cables_28Oct.txt`
- `04_DESIGN_SOURCE/10_Slim_Cargo_Rack_140mm/README.md`
- `04_DESIGN_SOURCE/10_Slim_Cargo_Rack_140mm/source/make_schematic.py`
- `04_DESIGN_SOURCE/2_B1_Dock_3U/README.md`
- `04_DESIGN_SOURCE/4_Pi_Unit_2U/source/pi_rack.py`
- `04_DESIGN_SOURCE/4_Pi_Unit_2U/source/pi_unit_fix.py`
- `04_DESIGN_SOURCE/4_Pi_Unit_2U/STEP_for_Onshape/Rack_Shelf_pinned.step`
- `04_DESIGN_SOURCE/4_Pi_Unit_2U/STL_for_printing/Rack_Shelf_pinned.stl`
- `04_DESIGN_SOURCE/6_Brick_Cradle_plate13+DC-notch_faceplate/checks/VERIFICATION_brick.txt`
- `04_DESIGN_SOURCE/6_Brick_Cradle_plate13+DC-notch_faceplate/source/verify_brick.py`
- `04_DESIGN_SOURCE/7_Argon_Poly5_tray+Waveshare_F_holder/11B-SIDE_PETG_Waveshare-F-holder_beside-Poly+5/README.md`
- `04_DESIGN_SOURCE/7_Argon_Poly5_tray+Waveshare_F_holder/11B-SIDE_PETG_Waveshare-F-holder_beside-Poly+5/Waveshare_F_holder_base.stl`
- `04_DESIGN_SOURCE/7_Argon_Poly5_tray+Waveshare_F_holder/checks/VERIFICATION_waveshare_f_holder.txt`
- `04_DESIGN_SOURCE/7_Argon_Poly5_tray+Waveshare_F_holder/README.md`
- `04_DESIGN_SOURCE/7_Argon_Poly5_tray+Waveshare_F_holder/source/verify_waveshare_f_holder.py`
- `04_DESIGN_SOURCE/7_Argon_Poly5_tray+Waveshare_F_holder/source/waveshare_f_holder.py`
- `04_DESIGN_SOURCE/7_Argon_Poly5_tray+Waveshare_F_holder/STEP_for_Onshape/Waveshare_F_holder_base.step`
- `04_DESIGN_SOURCE/9_scripts_28Oct/build_print_files.py`
- `04_DESIGN_SOURCE/9_scripts_28Oct/verify_pi_power_path.py`
- `04_DESIGN_SOURCE/9_scripts_28Oct/verify_wiring_all.py`
- `04_DESIGN_SOURCE/ONSHAPE_PROJECT/00_HOMELAB_RACK_ENGINEERING_SCHEMATIC.png`
- `04_DESIGN_SOURCE/ONSHAPE_PROJECT/00_SLIM_CARGO_RACK_SCHEMATIC.png`
- `04_DESIGN_SOURCE/ONSHAPE_PROJECT/INDIVIDUAL_STEP_PARTS/06_PI5_Rack_Shelf_pinned.step`
- `04_DESIGN_SOURCE/ONSHAPE_PROJECT/INDIVIDUAL_STEP_PARTS/06_PI5_Waveshare_F_holder_base.step`
- `04_DESIGN_SOURCE/ONSHAPE_PROJECT/README.md`
- `04_DESIGN_SOURCE/README.md`
- `PARTS_LIST.md`
- `README.md`
- `START_HERE.md`

**Removed or renamed** (kept in `before/`):
- `01_PRINT_FILES/2_CHECK-UPS-FIRST/C2_Pi_Faceplate_2U_DC-notch__x1__PETG__CHECK-UPS-jacks.stl`
- `02_RENDERS/Pi5_MiniRack_FINAL_studio.blend1`
- `02_RENDERS/source/fix_power_path_cutaway.py`
- `03_CHECKS/VERIFICATION_waveshare_F_holder_25PASS.txt`
  (`…_25PASS.txt` became `…_26PASS.txt`; the DC-notch faceplate became `C2_Pi_Faceplate_2U_clean__x1__PETG.stl`; `fix_power_path_cutaway.py` re-rendered shot 16 with the failing "hidden" route; the `.blend1` was Blender's auto-backup)

**New:**
- `FINAL_TODO/FINAL_TODO.md`
- `ULTRAREVIEW/` (this folder: `README.md`, `before/`, `checks/` incl. the evidence runs, `renders/`, `source/`)
- `01_PRINT_FILES/2_CHECK-UPS-FIRST/C2_Pi_Faceplate_2U_clean__x1__PETG.stl`
- `03_CHECKS/VERIFICATION_wiring_all-cables_28Oct.txt`, `VERIFICATION_slim-cargo_fit_28Oct.txt`, `VERIFICATION_waveshare_F_holder_26PASS.txt`
- `04_DESIGN_SOURCE/9_scripts_28Oct/verify_wiring_all.py`, `scene_load.py`, `verify_slim_fit.py`
- `04_DESIGN_SOURCE/4_Pi_Unit_2U/source/brick_lead_route.py`, `STEP_for_Onshape/Rack_Faceplate_2U_10in_clean.step`, `STL_for_printing/Rack_Faceplate_2U_10in_clean.stl`
- `04_DESIGN_SOURCE/ONSHAPE_PROJECT/INDIVIDUAL_STEP_PARTS/06_PI5_Faceplate_2U_clean.step`
- `02_RENDERS/17_rack_wiring_side_open.png`, `02_RENDERS/18_rack_wiring_rear.png`
