# Design source (28 Oct 2026)

**What's here:** the CAD source, STEP files and check scripts for every part in the current build. Use it to change a part, re-run a check, or open the parts in Onshape.

### 🌟 Official Onshape Project & Master Schematics
For opening or importing the entire 9U rack and all components into **Onshape**, go to:
👉 **[`ONSHAPE_PROJECT/`](file://~/Downloads/Pi%205%20HomeLab%201/04_DESIGN_SOURCE/ONSHAPE_PROJECT/)**
- **`Pi5_HomeLab_9U_Complete_ASSEMBLY.step`**: Full 35+ part solid master assembly (Standard 200 mm DeskPi T0-look rack + all 4 units in place).
- **`SlimCargo_HomeLab_9U_Complete_ASSEMBLY.step`**: Full master assembly for the 140 mm Slim Cargo travel prototype.
- **`Pi5_HomeLab_9U_Onshape_Project_Package.zip`**: Complete one-click drag-and-drop import archive.
- **`00_HOMELAB_RACK_ENGINEERING_SCHEMATIC.png`**: High-resolution dimensioned EIA-310 10-inch engineering schematic.
- **`INDIVIDUAL_STEP_PARTS/`**: 30 modular component STEP files for custom mating and kinematics in Onshape.

---

**Don't print from here.** Some folders also hold old or alternative STLs and 3MFs. The print files are in `../01_PRINT_FILES/`.

| Folder | What it is | Print file it makes (`01_PRINT_FILES`) |
|---|---|---|
| **`ONSHAPE_PROJECT/`** | **Master Onshape Assemblies (Standard & Slim Cargo), ZIP package, schematics & STEP parts library** | **Complete CAD Package** |
| `1_Rack_9U_T0-look/` | The 9U T0-look rack: side modules, cap, handles, base bars. `source/rack_t0.py`, `units.py`, `verify_rack_t0.py`, plus copies of the dock, screen and UCG scripts the rack check imports | 01–06 |
| `2_B1_Dock_3U/` | B1 dock v5 + ears (`source/b1_dock.py`) | 07, 09 |
| `3_Display_7in_3U/` | Display7C screen module + clips, Waveshare's STEP of the screen (its ears are the dock's) | 08, W4 |
| `4_Pi_Unit_2U/` | Pi shelf, UPS tray, faceplate (plain, and the 28 Oct **clean** one: `faceplate(dcin_window=False)`) and the bare-Pi v3 board tray + lid; component STEPs (Pi 5, adapter (F), Cuzor UPS, …). 28 Oct: the shelf's right gusset has an arch for the 12 V lead (`pi_rack.PASS_Y`), and `source/brick_lead_route.py` is the lead's route behind the faceplate | 10, C1, C2 |
| `5_UCG-Ultra_1U/` | The custom UCG shelf (plate 12). **Not used:** the build uses the ready-made mount in folder 8 | — |
| `6_Brick_Cradle_plate13+DC-notch_faceplate/` | 12 V brick cradle, spacers, and the faceplate with the 12 V lead notch (`source/brick_cradle.py`, `verify_brick.py`). The notch faceplate was replaced on 28 Oct by the clean one in folder 4 | 11, 12, O1–O3 |
| `7_Argon_Poly5_tray+Waveshare_F_holder/` | Argon Poly+ 5 tray (and the NEO 5 alternative), the adapter (F) holder (`source/argon_tray.py`, `waveshare_f_holder.py` and their checks). 28 Oct: the holder base got an HDMI plug relief | W1, W2, W3 |
| `8_UCG_mount_12-ALT2_Printables-942972/` | The ready-made UCG-Ultra mount: the original download (`_downloads/`), the cleaned + trimmed STL, scripts and checks. For your own use only: don't re-share | 13 |
| `9_scripts_28Oct/` | Scripts from 28 Oct: `build_print_files.py` (rebuilds `01_PRINT_FILES`, md5-checked; W2/W3 now come from folder 7), `verify_pi_power_path.py` (UPS OUT plug, lead route, side ports; the original, restored), `fp_check.py` (the Antigravity faceplate audit), and from the ultrareview: `verify_wiring_all.py` + `scene_load.py` (every cable, on the scene from `02_RENDERS/source/export_final.py`), `verify_slim_fit.py` (the build in the Slim Cargo rack) | — |
| `10_Slim_Cargo_Rack_140mm/` | The 140 mm travel frame (made by another tool, 28 Oct): `source/slim_rack.py`, STLs, STEPs, `make_schematic.py`. An alternative to folder 1; the brick cradle doesn't fit it | `5_SLIM_CARGO…` |

## Running things
**Python:** use the CadQuery venv noted in the project memory.

**Scripts:** they take folders as arguments, and the usage line is at the top of each.

**Frames:**
- **Pi-unit parts:** the v3 frame (x across, y from the rack rear to the front, z up).
- **Rack parts:** x across, y up, z back from the front rails.
- **Seen from the front of the rack, +x is to the LEFT.**

**`verify_rack_t0.py`:** run it from a scratch folder. It writes `VERIFICATION_rack.txt` into the current folder.

**Reports:** all current check reports are in `../03_CHECKS/`.

**Older material:**
- The full v7.2 bundle this was copied from (with its BOM xlsx, print plan and old renders) is `../_Old_versions/rework-01/`.
- The 27–28 Oct print folders are in `../_Old_versions/2026-10-28_retired/`.
