# PRINT FILES (final, updated 28 Oct 2026; ultrareview fixes the same evening)

**Every file you need to print is in this folder, and nothing else.** (`5_SLIM_CARGO…` is an *alternative* rack frame you'd print instead of 01–06, not an extra: leave it out of the Robu order.)  
**To-do list:** `../FINAL_TODO/FINAL_TODO.md`. **What the 28 Oct review changed:** `../ULTRAREVIEW/README.md`. Renders: `../02_RENDERS/`. Check reports: `../03_CHECKS/`. CAD source: `../04_DESIGN_SOURCE/`. Older print folders: `../_Old_versions/2026-10-28_retired/`.

**The build:**
- the v7.2 9U rack
- B1 dock v5
- the 7" screen module
- the Pi 5 in the **Argon Poly+ 5**, with the Waveshare adapter (F) in a holder beside it
- the Printables 942972 **UCG-Ultra mount**
- the **12 V brick cradle**
- the **clean faceplate**: no DC-IN window, no notch. The brick's 12 V lead stays behind it (28 Oct)

**How it's sorted:**
| Folder | What to do |
|---|---|
| **`1_PRINT-NOW/`** | Order or print today (13 files, 28 parts) |
| **`2_CHECK-UPS-FIRST/`** | UPS tray + faceplate: look at the real Cuzor UPS (or a photo) first. Two files |
| **`3_WAIT/`** | Poly+ 5 tray (measure the case), adapter holder (fit test), screen body (screen arrives 4 Nov). Four files |
| **`4_OPTIONAL_spare-spacers/`** | Only if your brick isn't ~30 mm thick |
| `5_SLIM_CARGO_140mm_TRAVEL_PROTOTYPE/` | **Alternative frame, not part of this order.** A 140 mm deep travel version of 01–06 (6 files, 15 parts, made by another tool on 28 Oct; seven P1S plates `SlimPlate01–07` and a weight estimate added the same day: ≈ 1.24 kg PETG, not printed). The dock, screen, UCG mount and Pi unit fit it, but **the 12 V brick and its cradle don't** (the cradle is 187 mm long; checked 28 Oct). Read its README first |

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
| `10_Pi_Rack_Shelf_pinned__x1__PETG.stl` | 1 | PETG black · 20 % | 170.1 × 116.7 × 68 | 96 | Pi unit: shelf. **Changed 28 Oct:** a 9 × 7 mm arch at the foot of the right post's gusset lets the brick's 12 V lead through behind the faceplate |
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
| `C2_Pi_Faceplate_2U_clean__x1__PETG.stl` | 1 | PETG black · 20 % | 67 | Pi unit: faceplate, **clean front** (28 Oct): no DC-IN window, no notch. It doesn't depend on the UPS any more; it's here because it shares plate 11 with the tray |

**Check on the real Cuzor Mini UPS Pro** (a photo is enough):
- the switch, LED and OUT are on one end face
- the DC-IN is on the opposite end face, at the end that lines up with the UPS tray's DC-IN window (where the right-angle extension plugs in)
- it's no longer than 101 mm

**Why:** Cuzor publish no drawing. The tray's windows were drawn from product photos, and the UPS's CAD model puts DC-IN at the other end. If it doesn't match, ask Claude to move the windows.

**Plate:** `Plate11_CHECK-UPS`, both parts. **Brim off:** the faceplate is 254 mm on a 256 mm bed.

## 3_WAIT (4 files)
| File | Qty | Robu | ≈ g | Wait for |
|---|---|---|---|---|
| `W1_Argon_Poly5_Tray__x1__PETG__WAIT-measure-case.stl` | 1 | PETG black · 20 % | 43 | **The Poly+ 5:** the tray takes up to 96.0 × 66.5 (listed 93.5 × 64 × 30, ± 1 cm). Bigger: don't print |
| `W2_Waveshare_F_Holder_Base__x1__PETG__WAIT-fit-test.stl` | 1 | PETG black · 20 % | 35 | **The fit test** below. **Changed 28 Oct:** the rear wall is cut back round the HDMI jack, because a 20–22 mm HDMI plug didn't fit the old 18.6 mm notch |
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
| `Rack_Faceplate_2U_10in` (plain, ₹222) | **Replace** with `C2_Pi_Faceplate_2U_clean` (28 Oct: no DC-IN window, no notch; it no longer needs the UPS check) |
| the Pi shelf line (`Rack_Shelf_pinned`) | **Re-upload** `10_Pi_Rack_Shelf_pinned` (28 Oct: the gusset arch for the 12 V lead) |
| `Pi5_UPS_v3_ups_tray_pinned` (₹296) | Keep; check out after the UPS check |
| `Pi5_UPS_v3_shims` (₹30) | **Remove**: not used |
| — | **Add** `11_Brick_Cradle_12V` + `12_Brick_Spacer_8mm` (PETG black, 20 %) |
| `Pi5_ArgonPoly5_tray` (₹152) | Keep; check out once the case is measured |
| `Waveshare_F_holder_base` (₹192) + `_lid` (₹89) | Keep; check out only if the fit test passes. **Upload the 28 Oct `W2_…` file for the base** (the one in the cart is the old file, whose HDMI notch is too narrow). The lid is unchanged |
| the other 10 lines | correct as they are |
| later | `W4_Display7C_3U_Body` after 4 Nov |

The hardware to re-add after the print order is in `ROBU_HARDWARE_CART_TO_RESTORE.md` (in this folder).

**Also buy:**
- a right-angle 5.5 × 2.1 pigtail with bare ends, **at least 30 cm** (UPS OUT → adapter terminal)
- a **right-angle 5.5 × 2.1 male → straight female extension, ~30 cm** (UPS DC-IN → the brick's plug, behind the faceplate)
- 4 × M2.5 × 25 pan-head (if the holder passes)

## The 12 V wiring (checked on the models, 28 Oct)
**Brick → UPS DC-IN, all behind the faceplate (28 Oct, `brick_lead_route.py`; render 08 and 16):**
- A **right-angle extension**'s plug goes into the UPS DC-IN, inside the UPS tray's DC-IN window (10.5 mm to spare each side).
- Its cable leaves sideways, drops to the shelf floor and runs along it, under the UPS OUT lead, to the shelf's right post.
- It goes through the **arch at the foot of the gusset**, across the front of the brick cradle and into the cradle's open front.
- There the brick's own straight plug pushes into the extension's socket. The join rides over the cradle's strap rib.
- The brick's spare lead is coiled beside the join.
- It needs ~14 cm of the extension, so 30 cm is plenty. Nothing shows at the front.
- **Fit order:** plug the extension into the UPS and thread it through the arch before the faceplate goes on.

**UPS OUT → adapter terminal:**
- **Plug:** the right-angle plug fits the UPS tray's rear window, with only 0.5 mm under it. File the window's bottom edge if yours is fatter.
- **Route:** the 4 mm lead runs:
  1. along the channel beside the UPS
  2. over the UPS's top edge at the M3 joint post (only 2.95 mm beside the post)
  3. through the front window and behind the faceplate
  4. up the tray's lead hole and into the holder's front notch, to the terminal

  That's about 24 cm in all.
- **Polarity:** check it before switching on.

**The other cables (checked on the models, 28 Oct, ultrareview: `../03_CHECKS/VERIFICATION_wiring_all-cables_28Oct.txt`):**
- HDMI (adapter → screen), micro-USB (Pi → screen) and Cat6 (adapter → gateway) leave the Pi's rear ports, drop to 50 mm and run up the back in one straight riser **tight against the right side** (seen from the front; x -110), where the dock's and screen's ears hide it. The Cat6 crosses behind the gateway below the mount's open keystone hole. They need ≈ 62, 70 and 61 cm with slack: the 1 m cables are fine, **a 0.5 m Cat6 isn't**. Seen straight on (render 03), no cable shows anywhere.
- The 50 cm USB-C reaches the B1 wherever its port turns out to be (≤ 34 cm).
- The adapter's HDMI plug didn't fit the holder's old 18.6 mm notch: **W2 now has a 23 mm relief** (any plug moulding up to 22 × 12).
- **The gateway's plugs vs its mount:** the mount's rear lip covers the bottom 10 mm of the gateway's back, and its corner posts cover the last 14 mm (right) and 4 mm (left). On Ubiquiti's own rear view, the RJ45 plugs clear the lip by ~1.4 mm and the USB-C by ~3.9 mm, and LAN 1 clears the post by 4.5 mm. The reset pinhole is behind the post, so slide the gateway out to press it. The display window lines up with the display (it's 18.5 mm up, not at mid-height).
- **The brick's DC lead** goes to the join in the cradle's front: coil its spare there (~0.6 m fits beside the join), and any more on top of the brick (110 × 38 × 40 mm under the dock).
- The full cable table is in `../FINAL_TODO/FINAL_TODO.md` §5.

## Renders, checks and source (next to this folder)
- **`../02_RENDERS/`:** 18 renders of this build, `FINAL_sheet.png` (all on one page), the Blender scene. 15 = the plug in the UPS OUT, 16 = a cutaway of the lead route, 17–18 = every cable up the rack's back (re-rendered 28 Oct, ultrareview).
- **`../03_CHECKS/`:** every check report:

  | Check | Result |
  |---|---|
  | brick cradle with this Pi unit | 42 PASS |
  | full rack | 38 PASS |
  | F holder (now also tests the HDMI and RJ45 plugs) | 26 PASS |
  | power path + side ports | see the report |
  | **every cable** (28 Oct) | 15 PASS, 1 FAIL (a 0.5 m Cat6), 3 WARN |
  | Slim Cargo frame with this build (28 Oct) | the brick cradle doesn't fit |
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
