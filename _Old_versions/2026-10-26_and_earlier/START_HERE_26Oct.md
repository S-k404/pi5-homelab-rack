# Pi 5 Mini Rack — all files (26 Oct 2026)

This is an 8U, 10-inch rack you can print, in the style of the DeskPi RackMate. From bottom to top it holds:
1. **Pi unit (2U).** Its own files are in `Pi5-Mini-Server_10in-2U-Rack_2026-10-25.zip` from 25 Oct, not in this bundle.
2. **NIIMBOT B1 face-out dock (3U):** in `2_B1_Dock_3U/`.
3. **7" REES52 touch screen module (3U):** in `3_Display_7in_3U/`.

The rack itself is in `1_Rack_8U_RackMate-look/`. Each folder has its own README, print-ready STLs (already oriented), STEP files for Onshape, preview images, a check report and the CadQuery source.

## Everything to print
PETG (or PLA away from heat), 0.2 mm layers, no supports. All parts fit a 220 mm bed. Total ≈ 1.1 kg of filament, so buy two spools.

| Folder | File | Qty |
|---|---|---|
| 1_Rack | Rack_SideFrame_2U_x2.stl | 2 |
| 1_Rack | Rack_SideFrame_3U_x4.stl | 4 |
| 1_Rack | Rack_SidePanel_Lower_x2.stl | 2 |
| 1_Rack | Rack_SidePanel_Upper_x2.stl | 2 |
| 1_Rack | Rack_TopHalf_x2.stl | 2 |
| 1_Rack | Rack_Handle_x2.stl | 2 |
| 1_Rack | Rack_BaseBar_x2.stl | 2 |
| 1_Rack | Rack_Splice_x12.stl | 12 |
| 2_B1_Dock | B1_Dock_3U_Body.stl | 1 |
| 2_B1_Dock | B1_Dock_3U_Ear_x2.stl | **4** (2 for the dock, 2 for the screen module) |
| 3_Display | Display7_3U_Body.stl | 1 |
| 3_Display | Display7_Clip_x4.stl | 4 |

## Everything to buy (hardware)
| Item | Qty |
|---|---|
| M5 heat-set inserts, 6.4 mm hole, 8–10 mm long | 44 used, buy 60 |
| M5 × 12 countersunk screws | 28 |
| M5 × 12 button-head screws | 16 |
| M5 washers | 12 |
| M3 heat-set inserts, Ø4 hole, 6 mm long | 36 used, buy 50 |
| M3 × 8 button-head screws | 28 |
| M3 × 8 countersunk screws | 8 |
| Stick-on rubber feet, 10–15 mm | 4 |
| 1 mm foam tape (screen clips, driver board) and felt (B1 cradle, optional) | — |
| For the screen: a short HDMI cable (check full vs mini), a USB cable to the Pi, and a 5 V 2 A USB power adapter | 1 each |

## Build order
1. Rack: frames → splices → base bars → top halves (dovetails) → handles → side panels → feet.
2. Screen module: inserts → glass with foam → 4 clips → driver board on the tray → ears.
3. B1 dock: inserts → ears.
4. Rack the units from the bottom up: Pi unit, B1 dock, screen. Each takes 4 M5 × 12 screws with washers.

## Alternatives
- **Open-frame v5:** `Printable-10in-8U-MiniRack_v5_2026-10-26.zip`. It's lighter (≈ 625 g) and has open sides and one centre handle.
- **2U pull-out drawer for the B1:** `NIIMBOT-B1-Drawer_10in-2U_2026-10-26.zip`. You have to pull it out to print.

## Checks
All checks pass: rack 30, B1 dock 19, screen module 13. They are calculations on the 3D models, not a physical test. Measure the screen and the B1 before printing their modules.
