# PRINT FILES (final, updated 28 Oct 2026)

**Every file you need to print is in this folder, and nothing else.** Renders: `../02_RENDERS/`. Check reports: `../03_CHECKS/`. CAD source: `../04_DESIGN_SOURCE/`. Older print folders: `../_Old_versions/2026-10-28_retired/`.

**The build:**
- the v7.2 9U rack
- B1 dock v5
- the 7" screen module
- the Pi 5 in the **Argon Poly+ 5**, with the Waveshare adapter (F) in a holder beside it
- the Printables 942972 **UCG-Ultra mount**
- the **12 V brick cradle**
- the **DC-notch faceplate**

**How it's sorted:**
| Folder | What to do |
|---|---|
| **`1_PRINT-NOW/`** | Order or print today (13 files, 28 parts) |
| **`2_CHECK-UPS-FIRST/`** | UPS tray + faceplate: look at the real Cuzor UPS (or a photo) first. Two files |
| **`3_WAIT/`** | Poly+ 5 tray (measure the case), adapter holder (fit test), screen body (screen arrives 4 Nov). Four files |
| **`4_OPTIONAL_spare-spacers/`** | Only if your brick isn't ~30 mm thick |
| **`5_SLIM_CARGO_140mm_TRAVEL_PROTOTYPE/`** | 140 mm ultra-slim ruggedized frame for carry-on suitcase transit (6 files, 15 parts) |

**What's in each folder:**
- **The STLs:** send these to Robu.
  - **One part per file.** `__x4__` in a name means order or print 4 of it.
  - **Colours:** PLA = silver, PETG = black.
- **`P1S_plates/`:** the same parts laid out on the 256 mm bed for printing yourself.
  - Open the `.3mf` (choose "load geometry only" if asked) and slice.
  - Each plate's settings are in its `_SETTINGS.txt`.

**Front/left/right:** seen from the **front**, the brick cradle is on the **left** of the Pi unit.

## 1_PRINT-NOW (13 files, 28 parts)
| File | Qty | Robu: material · infill | Size on the bed, mm | ≈ g each | What it is |
|---|---|---|---|---|---|
| `01_Rack_SideModule_2U_Base__x2__PLA.stl` | 2 | PLA silver · 15 % | 200 × 108.9 × 40 | 93 | rack: bottom side modules |
| `02_Rack_SideModule_3U__x4__PLA.stl` | 4 | PLA silver · 15 % | 200 × 136.4 × 28 | 104 | rack: 3U side modules |
| `03_Rack_SideModule_1U_Top__x2__PLA.stl` | 2 | PLA silver · 15 % | 200 × 47.5 × 28 | 50 | rack: 1U top side modules |
| `04_Rack_CapHalf__x2__PLA.stl` | 2 | PLA silver · 15 % | 147.8 × 200 × 30 | 96 | rack: vented cap halves |
| `05_Rack_Handle__x2__PLA.stl` | 2 | PLA silver · 20 % | 172 × 45 × 14 | 36 | rack: U handles |
| `06_Rack_BaseBar__x3__PLA.stl` | 3 | PLA silver · 15 % | 165.7 × 165.7 × 11 | 21 | rack: base bars |
| `07_Unit_Ear_3U__x4__PLA.stl` | 4 | PLA silver · 15 % | 28 × 132.6 × 3 | 10 | ears: 2 for the dock + 2 for the screen module |
| `08_Display7C_Clip__x4__PLA.stl` | 4 | PLA silver · 30 % | 20 × 9 × 3 | 1 | screen-module corner clips |
| `09_B1_Dock_v5_Body__x1__PLA.stl` | 1 | PLA silver · 15 % | 214 × 95 × 130 | 120 | B1 dock v5 (real B1, 132 × 91 × 62) |
| `10_Pi_Rack_Shelf_pinned__x1__PETG.stl` | 1 | PETG black · 20 % | 170.1 × 116.7 × 68 | 96 | Pi unit: shelf |
| `11_Brick_Cradle_12V__x1__PETG.stl` | 1 | PETG black · 20 % | 43.3 × 187.4 × 35.4 | 63 | 12 V brick cradle |
| `12_Brick_Spacer_8mm__x1__PETG.stl` | 1 | PETG black · 20 % | 110 × 31.6 × 10.4 | 17 | spacer for Robu's 30 mm brick |
| `13_UCG-Ultra_1U_Mount_Printables-942972__x1__PETG.stl` | 1 | PETG black · 15 % | 254 × 43.7 × 136 | 117 | UCG-Ultra mount, 3 keystones. For your own use only: don't re-share |

**Plates:**
- Plates 01–08, 10, 12-ALT2 and 13.
- **Plate 03 first:** heat-set one M5 insert (Ø6.4 × 10 hole) before printing the rest of the rack.
- Plate 13 has all 4 brick spacers: delete the ones you don't need.

## 2_CHECK-UPS-FIRST (2 files)
| File | Qty | Robu | ≈ g | What it is |
|---|---|---|---|---|
| `C1_Pi_UPS_Tray_pinned__x1__PETG__CHECK-UPS-jacks.stl` | 1 | PETG black · 20 % | 62 | Pi unit: Cuzor UPS tray |
| `C2_Pi_Faceplate_2U_DC-notch__x1__PETG__CHECK-UPS-jacks.stl` | 1 | PETG black · 20 % | 64 | Pi unit: faceplate, 8 × 9 mm notch for the brick's 12 V lead |

**Check on the real Cuzor Mini UPS Pro** (a photo is enough):
- the switch, LED and OUT are on one end face
- the DC-IN is on the opposite end face, at the end that lines up with the faceplate's DC-IN window
- it's no longer than 101 mm

**Why:** Cuzor publish no drawing. The tray and faceplate windows were drawn from product photos, and the UPS's CAD model puts DC-IN at the other end. If it doesn't match, ask Claude to move the windows.

**Plate:** `Plate11_CHECK-UPS`, both parts. **Brim off:** the faceplate is 254 mm on a 256 mm bed.

## 3_WAIT (4 files)
| File | Qty | Robu | ≈ g | Wait for |
|---|---|---|---|---|
| `W1_Argon_Poly5_Tray__x1__PETG__WAIT-measure-case.stl` | 1 | PETG black · 20 % | 43 | **The Poly+ 5:** the tray takes up to 96.0 × 66.5 (listed 93.5 × 64 × 30, ± 1 cm). Bigger: don't print |
| `W2_Waveshare_F_Holder_Base__x1__PETG__WAIT-fit-test.stl` | 1 | PETG black · 20 % | 35 | **The fit test** below |
| `W3_Waveshare_F_Holder_Lid__x1__PETG__WAIT-fit-test.stl` | 1 | PETG black · 20 % | 17 | same |
| `W4_Display7C_3U_Body__x1__PLA__WAIT-screen-4Nov.stl` | 1 | PLA silver · 15 % | 71 | **The screen (4 Nov):** check 164.9 wide, 124.2 over the corner tabs, 8.0 deep, the tab size |

**Plates:** `Plate11W_WAIT` (Poly+ 5 tray + holder base + lid) and `Plate09` (screen body).

**The fit test.** The holder sits 3–5 mm from the Poly+ 5's side ports (USB-C power, both micro-HDMI), so nothing else can plug in there. It only works if the adapter (F) plugs straight into the Pi through the case's side cut-outs.
1. Put the Pi in the Poly+ 5 and close it.
2. Push the adapter's USB-C and micro-HDMI into the cut-outs. Both must click fully home (≈ 6 mm) with the adapter level.
3. Check that the 16-pin FFC can leave the case.
- **Passes:** print W2 + W3. The UPS OUT → adapter terminal lead powers it all.
- **Fails:** skip the holder. Power the Pi with a 12 V → 5 V USB-C step-down from the UPS OUT, and use the UGREEN extender for HDMI. You lose the NVMe and the 2.5G port.

## 4_OPTIONAL_spare-spacers (3 files)
The cradle needs one spacer that suits the brick's thickness: the 8 mm one (in `1_PRINT-NOW`) is for 29–30.5 mm. If your brick measures something else, print one of these instead:
- 30.5–32.5 mm: `O1_…6mm`
- 32.5–34.5 mm: `O2_…4mm`
- 34.5–36.5 mm: `O3_…2mm`

36.5–38.2 mm needs no spacer.

There's no separate plate for these: all four spacers are already on `1_PRINT-NOW/P1S_plates/Plate13`.

## Filament
| | PLA | PETG |
|---|---|---|
| Print now | ≈ 1.19 kg | ≈ 0.29 kg |
| After the UPS check | — | ≈ 0.13 kg |
| After waiting | ≈ 0.07 kg | ≈ 0.10 kg |
| **Buy** | **2 spools** | **1 spool** |

## Robu print cart: changes (vs the 27 Oct audit: 17 lines, ₹6,702; I haven't seen the cart since)
| Cart line | Change |
|---|---|
| `Rack_Faceplate_2U_10in` (plain, ₹222) | **Replace** with `C2_Pi_Faceplate_2U_DC-notch`, checked out after the UPS check. The plain one blocks the brick's 12 V lead |
| `Pi5_UPS_v3_ups_tray_pinned` (₹296) | Keep; check out after the UPS check |
| `Pi5_UPS_v3_shims` (₹30) | **Remove**: not used |
| — | **Add** `11_Brick_Cradle_12V` + `12_Brick_Spacer_8mm` (PETG black, 20 %) |
| `Pi5_ArgonPoly5_tray` (₹152) | Keep; check out once the case is measured |
| `Waveshare_F_holder_base` (₹192) + `_lid` (₹89) | Keep; check out only if the fit test passes |
| the other 11 lines | correct as they are |
| later | `W4_Display7C_3U_Body` after 4 Nov |

The hardware to re-add after the print order is in `ROBU_HARDWARE_CART_TO_RESTORE.md` (in this folder).

**Also buy:**
- a right-angle 5.5 × 2.1 pigtail with bare ends, **at least 30 cm** (UPS OUT → adapter terminal)
- 4 × M2.5 × 25 pan-head (if the holder passes)

## The 12 V wiring (checked on the models, 28 Oct)
**Brick → UPS DC-IN:**
- The lead runs along the cradle and out through the faceplate's bottom notch.
- From there it runs ~13 mm along the front into the DC-IN window.

**UPS OUT → adapter terminal:**
- **Plug:** the right-angle plug fits the UPS tray's rear window, with only 0.5 mm under it. File the window's bottom edge if yours is fatter.
- **Route:** the 4 mm lead runs:
  1. along the channel beside the UPS
  2. over the UPS's top edge at the M3 joint post (only 2.95 mm beside the post)
  3. through the front window and behind the faceplate
  4. up the tray's lead hole and into the holder's front notch, to the terminal

  That's about 24 cm in all.
- **Polarity:** check it before switching on.

## Renders, checks and source (next to this folder)
- **`../02_RENDERS/`:** 16 renders of this build, `FINAL_sheet.png` (all on one page), the Blender scene. 15 = the plug in the UPS OUT, 16 = a cutaway of the lead route.
- **`../03_CHECKS/`:** every check report:

  | Check | Result |
  |---|---|
  | brick cradle with this Pi unit | 42 PASS |
  | full rack | 38 PASS |
  | F holder | 25 PASS |
  | power path + side ports | see the report |
  | UCG mount | 8 PASS, 1 WARN |
  | dock v5 | 22 PASS |
  | screen | 23 PASS |
  | Poly+ 5 tray | 29 PASS |
  | every STL measured (`MEASUREMENTS_every_part.md`) | all pass |
  | every 3MF read back (`PLATES_3MF_audit.txt`) | all pass |
  | why the Antigravity faceplate was dropped | see the report |

- **`../04_DESIGN_SOURCE/`:** the CAD source and STEP files.
  - `9_scripts_28Oct/build_print_files.py` rebuilds this folder (md5-checked).
  - `9_scripts_28Oct/verify_pi_power_path.py` is the wiring check.

All checks are calculations on the 3D models, not physical tests. The Poly+ 5, the adapter's parts and the UPS jacks are stand-ins from listings and drawings.
