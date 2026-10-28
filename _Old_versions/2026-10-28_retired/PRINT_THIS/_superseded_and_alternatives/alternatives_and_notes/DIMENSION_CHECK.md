# Dimension re-check (27 Oct 2026)

**Result: everything passes. Nothing printable needed changing.** These are calculations on the 3D models, not a physical test; the last section lists what only you can measure.

## 1. These are the right files
- The STLs in this folder are byte-for-byte copies of the v7.2 bundle's. Those are identical in the root `Pi5-MiniRack_v7.2_ALL-FILES_2026-10-27/` and in `rework-01/`: all 20 STLs match by SHA-256.
- **The 12 rack, dock, screen and UCG STLs were re-exported from the CadQuery source today, and all 12 came out byte-identical.** So the printed files are exactly the models the design checks below test.
- The Pi unit's 7 STLs match their STEP files: volume within 0.003%, size exact. The shims have no STEP; they're 12 small pieces by design.
- `checks/stl_vs_source.txt`

## 2. Design checks re-run: 101 PASS, 0 FAIL
| Check | Result | Same as the shipped file? |
|---|---|---|
| Rack (`verify_rack_t0.py`) | 39 PASS | identical |
| UCG-Ultra shelf | 15 PASS | identical |
| B1 dock | 24 PASS | identical (superseded 27 Oct evening: dock v5, 22 PASS, rack 38 PASS; see below) |
| Screen module (C type) | 23 PASS | identical |

## 3. Key dimensions
| What | Standard / real part | In the files |
|---|---|---|
| Rack hole spacing | EIA-310 10-inch: 236.525 mm | 236.525 mm; dock, screen, UCG and Pi slots all line up with the rail inserts |
| Hole pattern in each U | 6.35 / 22.225 / 38.1 mm | 27 holes per post, front and rear, unbroken across the module joints |
| Panel width | 10 in = 254 mm | 254.0 mm (Pi faceplate, dock and screen panels with ears, UCG panel) |
| 1U / 2U / 3U panel height | n × 44.45 − 0.8 mm clearance | 43.65 / 88.1 / 132.55 mm |
| Clear opening between posts | | 224 mm; the widest unit body is 214 mm |
| Outside size | DeskPi RackMate T0: 280 W × 200 D | 280 × 200 mm, 495 mm tall to the handle tops |
| UniFi UCG-Ultra | 141.8 × 127.6 × 30 mm (Ubiquiti) | fits with 0.6 mm all round; ports clear; 11.6 mm of air above it |
| NIIMBOT B1 | **132 × 91 × 62 mm** (official manual; another edition says 61.6) | dock v5 cradle for 62 mm + 1.5 mm, no spacers: 22 PASS |
| Waveshare 7" HDMI LCD (C) | 165 × 124.2 × 8 mm (Waveshare's 3D model) | located to within 0.5 mm; the 160 × 94 window shows the whole 154.2 × 85.9 active area |
| M5 heat-set insert holes | Ø6.4 × 10 mm | every rack part; ≥ 3.06 mm of wall round the rail inserts |
| M3 heat-set insert holes | Ø4 mm | in the dock and screen bodies; the checks confirm every ear and clip screw lines up with one |
| M5 clearance / counterbore | 5.5 / 10.5 mm | module joints, cap, handles, base-bar screws |
| Ear slots | M5 | 6.6 mm |
| Pi shelf on the base bars | | rests on the front and middle bars with no gap |
| UCG shelf vs. screen module | | 0.8 mm apart (355.2 vs 356.0 mm) |

M5 holes are cut at every rack position, front and rear, so units can go at any height. The 48 inserts on the BOM only go into the holes that are used: 18 joints, 4 cap, 4 cap columns, 6 base-bar ends and 16 rail holes. `checks/hole_census.txt`

## 4. Printable on the P1S
- **Every file is sound:** all 18 are watertight, each is one solid (the shims are 12 pieces by design), all lie flat on the bed, and the tallest is 137.2 mm (the UCG shelf). `checks/stl_measurements.txt`
- **Every plate fits:** all 13 plate files (12 plates, plus the spacer version of plate 04) fit the 256 × 256 bed with ≥ 1 mm to the edge and ≥ 2 mm between parts. That's 54 PASS. The 3MF files were read back after writing, and each part's position and volume matches. `checks/plate_layout_check.txt`
- **No supports needed.** The only faces pointing down off the bed are hole tops, 1 mm edge chamfers and short bridges. The biggest is the floor of the Pi shelf's HDMI tower, which bridges 24 mm in PETG. That was already known and is fine.

## 5. What a computer can't check: measure these
| What | When | Decides |
|---|---|---|
| ~~NIIMBOT B1 thickness~~ | settled 27 Oct: 62 mm per the official manual | nothing. Plate 04 is a single file, and plate 08 is dock v5 |
| The screen's four numbers (165 / 124.2 / 8.0 / tab size) | when it arrives, Wed 4 Nov | plate 09 |
| One M5 insert in a Ø6.4 hole | after plate 03 | whether the other rack plates can go ahead |

**The 3MF files** are written to the plain 3MF standard and checked by reading them back here. They haven't been opened in Bambu Studio, which isn't installed on this Mac. If any part lands off-centre, press **A** to arrange the plate.

## 6. Update, 27 Oct (evening): B1 dock v5
- **Sizing and layout:** the dock is now sized to the official B1, 132 × 91 × 62 mm. It's laid out from your photos: the open slide faces up, the lid end goes on your right, and the lip sits under the non-lid half only.
- **The lid opens in the rack:** the printer sits 20 mm off centre, so the lid can swing about 85° without hitting the dock.
- **Checks:**
  - dock: 22 PASS (`rework-01/.../2_B1_Dock_3U/VERIFICATION_dock.txt`)
  - rack: 38 PASS (the 62 mm-with-spacers check is gone along with the spacers)
  - plate layout: 44 PASS (12 plates, with no spacer variant)
- **Old files:** v4 is in `_obsolete_2026-10-27/`.
