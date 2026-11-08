# 10-inch 9U Slim Cargo Mini Rack (140 mm Depth)
### Suitcase-Ready & Ruggedized for Airline Cargo Transport

This prototype is a specialized **140 mm depth, high-strength travel variant** of the 10-inch 9U Homelab Mini Rack. It is engineered specifically to pack inside standard international carry-on luggage (cabin bags) or checked baggage with room for shock-absorbing foam or clothing padding.

---

## 1. Why 140 mm Depth?

| Specification | Standard Desktop Rack (v7.2) | Slim Cargo Travel Prototype | Advantage for Travel |
|---|---|---|---|
| **Depth** | $200.0\text{ mm}$ ($7.87"$) | **$140.0\text{ mm}$ ($5.51"$)** | **$-60\text{ mm}$ / 30% slimmer.** Easily fits into one half of a clamshell suitcase (which has $100\text{--}120\text{ mm}$ internal depth per shell). |
| **Total Height** | $495.1\text{ mm}$ (with handles and plinth) | **$458.1\text{ mm}$ (with handles and plinth)** | **$-37\text{ mm}$ shorter** (it said 445 mm and −50 mm; measured on the models, 28 Oct). The handles rise 18 mm, not 45, so they don't catch on suitcase zippers. |
| **Outer Wall Skin** | $1.2\text{ mm}$ (lightweight PLA) | **$2.4\text{ mm}$ (heavy-duty cargo skin)** | Double thickness for impact, crush, and puncture resistance. |
| **Corner Posts** | $12.0\text{ mm}$ | **$14.0\text{ mm}$** | Beefier anchor around M5 heat-set inserts. |
| **Anti-Racking** | Plain thin vents | **Integrated diagonal shear trusses** | Prevents diagonal parallelogram distortion when luggage is dropped or tossed. |
| **Print Material** | PLA (brittle, cracks in cold cargo holds) | **PETG, ABS/ASA, or PETG-CF** | High impact strength, ductile under shock, cold-temperature resistant. |

---

> **Corrected 28 Oct (ultrareview).** Section 2 used to list made-up depths ("brick cradle 120 mm, fits with 20 mm"; "12 V 3 A"). Measured on the models (`../../03_CHECKS/VERIFICATION_slim-cargo_fit_28Oct.txt`), the four units fit but the 12 V brick cradle doesn't, and the fastener count is 48, not 38.

## 2. The 4 units fit inside the 140 mm envelope; the 12 V brick cradle doesn't

All four units in the homelab mount to standard 10-inch EIA-310 rails ($236.5\text{ mm}$ hole pitch, $224\text{ mm}$ clear opening) and fit comfortably within the 140 mm depth:

Measured on the models (rack frame, z back from the front rails):

| Unit | Ends at z | In 140 mm |
|---|---|---|
| 1U UCG-Ultra mount (Printables 942972) + gateway (127.6) | 133.0 | fits; the gateway's rear plugs stick out ~20 mm behind |
| 2U Pi unit: shelf, trays, Poly+ 5, adapter (F) holder | 117.1 | fits; the right-angle plug in the UPS OUT ends at 127.9 |
| **12 V 5 A brick in the plate 13 cradle** | **201.4** | **doesn't fit**: the cradle is 187 mm long and hits the slim middle and rear bars (z 63–77, 126–139) |
| 3U NIIMBOT B1 dock | 92.0 | fits |
| 3U 7" screen module | 30.0 | fits |

The Pi shelf rests on the slim front and middle bars (z 1–14, 63–77), so the Pi unit itself is supported.

---

## 3. Hardware & Fasteners (Uniform One-Size System)

* **Screws:** 48 × M5 × 12 mm button head (ISO 7380): 18 module joints + 4 cap + 4 handles + 6 base bars + 16 unit ears (counted from `slim_rack.py`, 28 Oct; it was given as 38).
* **Inserts:** 48 × M5 brass heat-set inserts (Ø6.4 × 10 mm holes).
* **Tool:** $3\text{ mm}$ Allen hex key.

---

## 4. CAD & Manufacturing Files

* **Onshape-Ready 3D Assembly STEP:**  
  [`STEP_for_Onshape/SlimCargo_Rack_9U_140mm_ASSEMBLY.step`](STEP_for_Onshape/SlimCargo_Rack_9U_140mm_ASSEMBLY.step)
* **Print-Ready STLs (fit standard $220\times 220\text{ mm}$ and Bambu $256\times 256\text{ mm}$ beds):**
  * `SlimCargo_SideModule_2U_Base_x2.stl`
  * `SlimCargo_SideModule_3U_x4.stl`
  * `SlimCargo_SideModule_1U_Top_x2.stl`
  * `SlimCargo_CapHalf_x2.stl`
  * `SlimCargo_LowProfile_Handle_x2.stl`
  * `SlimCargo_BaseBar_x3.stl`
* **Print plates, overhang check and filament estimate (28 Oct):** `source/build_slim_plates.py <project root>` writes the seven P1S plates into `../../01_PRINT_FILES/5_SLIM_CARGO_140mm_TRAVEL_PROTOTYPE/P1S_plates/` and the report `../../03_CHECKS/VERIFICATION_slim-cargo_plates_28Oct.txt` (frame ≈ 1,193 g PETG). The earlier "no supports, all overhangs ≤ 45°" is not true; see that report.
* **Studio Renders:**  
  Located in [`02_RENDERS/SLIM_CARGO_PROTOTYPE/`](../../02_RENDERS/SLIM_CARGO_PROTOTYPE).

