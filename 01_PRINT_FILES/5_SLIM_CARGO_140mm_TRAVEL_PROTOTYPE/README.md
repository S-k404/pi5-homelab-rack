# 5_SLIM_CARGO_140mm_TRAVEL_PROTOTYPE (Suitcase-Ready Homelab Rack)

> **Read first (checked 28 Oct, ultrareview: `../../03_CHECKS/VERIFICATION_slim-cargo_fit_28Oct.txt`):**
> - This is an **alternative** to the standard rack (files 01–06 in `1_PRINT-NOW`). Print one rack or the other, not both. It isn't in the Robu order.
> - The B1 dock, the screen module, the UCG mount and the Pi unit fit it, and the Pi shelf stands on its front and middle base bars.
> - **The 12 V brick and its cradle (plate 13) don't fit.** The cradle is 187 mm long (it ends at z 201 in a 140 mm rack) and runs into the slim middle and rear bars. In this rack the brick has to sit outside, with its lead in through the faceplate notch.
> - The gateway's rear plugs and the UPS OUT plug stick out behind a 140 mm rack when cabled up (fine in use; unplug them to pack it).
> - It takes **48** M5 screws and 48 inserts, like the standard rack (18 joints + 4 cap + 4 handles + 6 base bars + 16 for the units), not 38.
> - **Plates and weight (added 28 Oct):** `P1S_plates/SlimPlate01` to `SlimPlate07` (3MF + layout + SETTINGS) replace Plate01–07 of the standard rack. Read back from the 3MFs: 0 FAIL (`../../03_CHECKS/VERIFICATION_slim-cargo_plates_28Oct.txt`). The frame is about **1,193 g of PETG** (1,165 g if printed in PLA), plus about 46 g for the ears and clips. Frame only: no electronics, no screws.
> - Nothing here has been printed or test-fitted, and it has no Robu settings.

Alternative 9U rack frame for airline luggage / carry-on cargo transport.
- **Depth:** 140 mm (-30% volume vs standard 200 mm rack). Fits inside 20-inch carry-on luggage or checked bags.
- **Strength:** Double wall thickness (2.4 mm skin), 14 mm reinforced posts, integrated diagonal anti-racking trusses.
- **Handles:** Low-profile 18 mm rise. The rack is 440 mm to the top of the handles (458 mm with the plinth; the standard rack is 495 mm), which keeps them from snagging on zippers.
- **Compatibility:** Uses the exact same 10-inch EIA-310 standard mounting holes (236.5 mm pitch). Holds all 4 homelab units, but **not the 12 V brick cradle** (see above).

## Print Files:
Sizes are measured from the STLs in this folder, in print orientation. Walls and infill are the Slim design's (4–5 perimeters, 20–35 % gyroid); grams are the slicer-like estimate in PETG.

| File | Qty | Material | Measured on the bed (mm) | Walls / infill | ≈ g each | What it is |
|---|:---:|---|---|---|--:|---|
| `SlimCargo_SideModule_2U_Base_x2.stl` | 2 | PETG / ABS / ASA | 140.0 × 106.9 × 40.0 | 4 / 25% | 115 | 2U Plinth base module with base-bar ledges |
| `SlimCargo_SideModule_3U_x4.stl` | 4 | PETG / ABS / ASA | 140.0 × 136.4 × 28.0 | 4 / 25% | 134 | 3U Interlocking structural side modules |
| `SlimCargo_SideModule_1U_Top_x2.stl` | 2 | PETG / ABS / ASA | 140.0 × 47.5 × 28.0 | 4 / 25% | 61 | 1U Top side modules with cap joints |
| `SlimCargo_CapHalf_x2.stl` | 2 | PETG / ABS / ASA | 147.8 × 140.0 × 22.0 | 4 / 20% | 80 | Top vented protective cap halves (dovetail join) |
| `SlimCargo_LowProfile_Handle_x2.stl` | 2 | PETG / ABS / ASA | 116.0 × 18.0 × 16.0 | 5 / 35% | 24 | Flush-fit luggage carry handles |
| `SlimCargo_BaseBar_x3.stl` | 3 | PETG / ABS / ASA | 165.7 × 165.7 × 13.0 (saved at 45°; **223.4 × 15.0** straight) | 5 / 30% | 32 | Reinforced bottom tie rods |

The B1 dock's and the screen module's ears (4) and clips (4) are the standard rack's: `../1_PRINT-NOW/07_…` and `08_…`. They ride on plates 04S, 06S and 07S, as on Plate04/06/07.

## Plates (Bambu P1S, 256 × 256):
`P1S_plates/SlimPlate0N.3mf` (parts already placed), `_layout.png` and `_SETTINGS.txt` for each. Print these **instead of** Plate01–07.

| Plate | On it | ≈ g PETG | Replaces |
|---|---|--:|---|
| `SlimPlate01` | 2U base module × 2 | 231 | Plate01 |
| `SlimPlate02` | 3U module + 3 base bars | 230 | Plate02 |
| `SlimPlate03` | 3U module + 2 handles. **The insert test**: set one M5 insert in a rail hole and one in a joint boss before the others | 183 | Plate03 |
| `SlimPlate04` | 3U module + 2 ears + 4 clips | 159 | Plate04 |
| `SlimPlate05` | 3U module + 2 × 1U top modules | 256 | Plate05 |
| `SlimPlate06`, `SlimPlate07` | cap half + ear (each) | 91 each | Plate06, 07 |
| | **Total** | **≈ 1,240** | |

The dock (Plate08), the screen module (Plate09), the Pi unit (Plates 10, 11, 11W) and the UCG mount (Plate12-ALT2) are the standard rack's plates, unchanged. Skip Plate13 (the brick cradle doesn't fit).

**Weight.** At the Slim design's settings the frame is 1,193 g (PETG) or 1,165 g (PLA), against 1,027 g for the standard frame (PLA, 3 walls, 15 %). The Slim parts are lighter at equal settings (959 g at 3 walls / 15 %, −7 %): the thicker skin and denser infill are what add +14 %. Details: `../../03_CHECKS/VERIFICATION_slim-cargo_plates_28Oct.txt`.

## Print Settings:
- **Nozzle:** 0.40 mm or 0.60 mm.
- **Layer height:** 0.20 mm.
- **Walls:** 4 perimeters (5 for the handles and bars); infill as in the table.
- **Supports:** OFF, as for the standard rack. This is **not** "all overhangs ≤ 45°" (the README used to say that): each module has about 1.5–2 % of its surface pointing down steeper than 45° (joint bosses, key slots; 340 mm² of flat ceiling + 914 mm² sloped on a 3U). The standard rack's modules have the same, within 0.5 percentage points. If a boss prints ragged, turn on tree supports for that plate.
- **Bed:** the P1S (256 × 256) takes the plates above, with the bars lying straight. On a 220 × 220 bed (Ender-3) every loose STL fits as saved; the bars only fit because that STL is at 45° (they're 223 mm long, so don't lay them straight there).
