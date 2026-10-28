# 5_SLIM_CARGO_140mm_TRAVEL_PROTOTYPE (Suitcase-Ready Homelab Rack)

> **Read first (checked 28 Oct, ultrareview: `../../03_CHECKS/VERIFICATION_slim-cargo_fit_28Oct.txt`):**
> - This is an **alternative** to the standard rack (files 01–06 in `1_PRINT-NOW`). Print one rack or the other, not both. It isn't in the Robu order.
> - The B1 dock, the screen module, the UCG mount and the Pi unit fit it, and the Pi shelf stands on its front and middle base bars.
> - **The 12 V brick and its cradle (plate 13) don't fit.** The cradle is 187 mm long (it ends at z 201 in a 140 mm rack) and runs into the slim middle and rear bars. In this rack the brick has to sit outside, with its lead in through the faceplate notch.
> - The gateway's rear plugs and the UPS OUT plug stick out behind a 140 mm rack when cabled up (fine in use; unplug them to pack it).
> - It takes **48** M5 screws and 48 inserts, like the standard rack (18 joints + 4 cap + 4 handles + 6 base bars + 16 for the units), not 38.
> - No print plates (3MF), weight estimate or Robu settings were made for it, and nothing here has been printed or test-fitted.

Alternative 9U rack frame for airline luggage / carry-on cargo transport.
- **Depth:** 140 mm (-30% volume vs standard 200 mm rack). Fits inside 20-inch carry-on luggage or checked bags.
- **Strength:** Double wall thickness (2.4 mm skin), 14 mm reinforced posts, integrated diagonal anti-racking trusses.
- **Handles:** Low-profile 16 mm rise (445 mm total height) prevents zipper snagging and snap-offs.
- **Compatibility:** Uses the exact same 10-inch EIA-310 standard mounting holes (236.5 mm pitch). Holds all 4 homelab units, but **not the 12 V brick cradle** (see above).

## Print Files:
| File | Qty | Material | Infill | Bed Layout (mm) | What it is |
|---|:---:|---|---|---|---|
| `SlimCargo_SideModule_2U_Base_x2.stl` | 2 | PETG / ABS / ASA | 25% Gyroid | 140 × 109 × 40 | 2U Plinth base module with base-bar ledges |
| `SlimCargo_SideModule_3U_x4.stl` | 4 | PETG / ABS / ASA | 25% Gyroid | 140 × 136 × 28 | 3U Interlocking structural side modules |
| `SlimCargo_SideModule_1U_Top_x2.stl` | 2 | PETG / ABS / ASA | 25% Gyroid | 140 × 48 × 28 | 1U Top side modules with cap joints |
| `SlimCargo_CapHalf_x2.stl` | 2 | PETG / ABS / ASA | 20% Gyroid | 148 × 140 × 24 | Top vented protective cap halves (dovetail join) |
| `SlimCargo_LowProfile_Handle_x2.stl` | 2 | PETG / ABS / ASA | 35% Gyroid | 128 × 24 × 16 | Flush-fit luggage carry handles |
| `SlimCargo_BaseBar_x3.stl` | 3 | PETG / ABS / ASA | 30% Gyroid | 166 × 166 × 11 | Reinforced bottom tie rods |

## Print Settings:
- **Nozzle:** 0.40 mm or 0.60 mm.
- **Layer height:** 0.20 mm.
- **Walls:** 4–5 perimeters (min 2.0 mm solid skin).
- **Supports:** NONE required (all overhangs <= 45°).
- **Bed:** Fits flat on standard 220 × 220 mm (Ender-3) and 256 × 256 mm (Bambu Lab P1S/X1C) beds.

