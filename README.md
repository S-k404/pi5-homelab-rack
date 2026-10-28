# Pi 5 HomeLab mini rack (updated 28 Oct 2026, ultrareview in the evening)

**To do: `FINAL_TODO/FINAL_TODO.md`.** What the 28 Oct review checked, found and changed: `ULTRAREVIEW/README.md`.

A **printed 10-inch, 9U mini rack** in the DeskPi RackMate T0 look: 280 W × 200 D, silver sides, a vented cap and U handles. It's printed by Robu's print service or on a **Bambu P1S** (256 mm bed): PLA for the rack, dock and screen; PETG near heat.

## Folders & CAD Downloads
| Folder / file | What it is |
|---|---|
| **`FINAL_TODO/`** | **The one to-do list** (orders, measuring, printing, building, wiring, power-up) |
| `ULTRAREVIEW/` | The 28 Oct review: findings, every change (with the old files in `before/`), new checks and renders |
| 🌟 **[`Pi5_HomeLab_9U_COMBINED_FOR_ONSHAPE.step`](file://~/Downloads/Pi%205%20HomeLab%201/Pi5_HomeLab_9U_COMBINED_FOR_ONSHAPE.step)** | **Master 2-in-1 Combined STEP**: Standard 200 mm & Slim Cargo 140 mm racks side-by-side in one file for Onshape. For viewing only: its UCG unit is the unused custom shelf, it has the pre-28-Oct holder, and its Slim Cargo rack shows a brick cradle that doesn't fit there (`04_DESIGN_SOURCE/ONSHAPE_PROJECT/README.md`) |
| 📦 **[`Pi5_HomeLab_9U_Onshape_Project_Package.zip`](file://~/Downloads/Pi%205%20HomeLab%201/Pi5_HomeLab_9U_Onshape_Project_Package.zip)** | **Complete Onshape Import Archive**: Both master assemblies, 30 component STEPs, and dimensioned schematics |
| **`01_PRINT_FILES/`** | **Every print file, and nothing else**, sorted: `1_PRINT-NOW`, `2_CHECK-UPS-FIRST`, `3_WAIT`, `4_OPTIONAL_spare-spacers`, and `5_SLIM_CARGO_140mm_TRAVEL_PROTOTYPE` (an *alternative* rack frame, not part of the order: the brick cradle doesn't fit it). STLs for Robu plus P1S plates. Start with its `README.md` |
| `02_RENDERS/` | 18 renders of this build, re-rendered 28 Oct with every cable (`FINAL_sheet.png` = all on one page; 17–18 = the wiring), the Blender scene; plus 360° turntable / exploded videos made by another tool before the review |
| `03_CHECKS/` | Every check report (calculations on the 3D models, not physical tests) |
| **`04_DESIGN_SOURCE/ONSHAPE_PROJECT/`** | **Official Onshape CAD Project**: Master assemblies, Part Studio compounds, component library, and technical schematics |
| `04_DESIGN_SOURCE/` | CAD source, STEP files and check scripts for every part. Don't print from here |
| `START_HERE.md` | A pointer to `FINAL_TODO/` and the other lists |
| `PARTS_LIST.md` | What to buy, with prices (corrected 28 Oct; re-checked against the Robu cart in the evening) |
| `_Old_versions/` | Everything older. Today's retired folders are in `2026-10-28_retired/`. **Don't print from here** |

## The build (decided 28 Oct)
| U | Unit | Holds | Prints |
|---|---|---|---|
| 1U | Gateway | UniFi UCG-Ultra (141.8 × 127.6 × 30) | the ready-made Printables 942972 3-keystone mount, trimmed 0.8 mm to clear the cap |
| 3U | Screen | Waveshare / REES52 7" HDMI LCD (C) touch | Display7C module + 4 clips (body waits for the screen, 4 Nov) |
| 3U | B1 dock | NIIMBOT B1 (132 × 91 × 62), face out | dock v5 |
| 2U | Pi unit | Pi 5 in the **Argon Poly+ 5** (THRML cooler inside), Waveshare adapter (F) + NVMe in a holder beside it, Cuzor Mini UPS Pro 12 V | shelf (gusset arch for the 12 V lead); **clean faceplate** (no window, no notch); UPS tray (check the UPS first); Poly+ 5 tray (measure the case); F holder (fit test) |
| — | 12 V brick | Robu 12 V 5 A (110 × 50 × 30) inside the rack, left of the Pi unit seen from the front | cradle + 8 mm spacer |

**Power:**
- **Into the UPS:** brick → a 30 cm right-angle extension → UPS DC-IN, **all behind the faceplate** (28 Oct): along the shelf floor, through an arch in the shelf's right gusset, into the brick cradle's open front. Nothing shows at the front.
- **Out to the adapter:** UPS OUT (rack rear) → right-angle pigtail (≥ 30 cm) → the adapter (F)'s screw terminal.
- **USB loads:** the screen and the B1 run off the Pi's USB (they use ~1.3–1.5 A of its 1.6 A).
- **If the holder fit test fails:** UPS OUT → 12 V → 5 V USB-C step-down → Pi, with the UGREEN extender for HDMI.
- **The gateway** runs on its own USB-C adapter from the wall, not the UPS.

**Cables** (all checked on the models, 28 Oct): HDMI and micro-USB to the screen and Cat6 to the gateway run up the back on the right (seen from the front); a 50 cm USB-C goes to the B1. Table and lengths: `FINAL_TODO/FINAL_TODO.md` §5.

**Standard:** it follows Jeff Geerling's 10-inch standard (236.525 mm rail holes, EIA pattern, 224 mm clear), so any 10-inch mount bolts in with M5 screws and washers.

## Open
| What | When |
|---|---|
| Check the Cuzor UPS's jack positions and length (≤ 101 mm), then print the UPS tray + faceplate (`2_CHECK-UPS-FIRST`) | when it arrives, or from a photo |
| Measure the Poly+ 5 (≤ 96.0 × 66.5), do the holder **fit test**, check the FFC exit. Then the tray and, if it passed, the holder (`3_WAIT`) | when it arrives |
| Measure the screen, then its body (`3_WAIT`) | Wed 4 Nov |
| Robu print cart changes: see `01_PRINT_FILES/README.md` | before checkout |
| Test one M5 insert in plate 03 before the rest of the rack | when the inserts arrive |
| The rack tips forward at ~5.8 N on the back of the gateway: fix it to the desk, or plug the gateway in before racking it | when building |
| Re-upload the holder base (W2) to the Robu cart: it changed on 28 Oct (HDMI plug relief) | before checkout |
| Sit the UCG-Ultra in its printed mount and plug in a patch cable + USB-C: the mount's rear lip (10 mm) may block low jacks | when it arrives |
| Everything else | `FINAL_TODO/FINAL_TODO.md` |

## About the "Antigravity v7.3 final" (27–28 Oct)
Its "switch window" faceplate, UPS switch extender and "hidden cable slit" **don't work**:
- the Cuzor's switch faces the rack rear
- the UPS tray's wall is behind the window
- the brick-lead notch was lost

Its renders show that faceplate and a UPS moved 29.9 mm forward, and its BOM xlsx has the wrong Poly+ 5 price. All of it is retired to `_Old_versions/2026-10-28_retired/`. If that tool runs again and adds files here, don't print from them.

## First power-up
1. Boot from the microSD, then (if the FFC route works) move the OS to the NVMe.
2. Add `usb_max_current_enable=1` to `/boot/firmware/config.txt`.
3. **Check the polarity** of every 5.5 × 2.1 lead and the terminal wires before switching on.

## Links
- Jeff Geerling's Project MINI RACK: https://mini-rack.jeffgeerling.com/
- Older interactive 3D view (v7.2, private): https://claude.ai/artifact/9pqgvvRfigWwcD8ecrPeBo
