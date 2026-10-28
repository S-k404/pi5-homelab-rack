# 10-inch 9U Slim Cargo Mini Rack (140 mm Depth)
### Suitcase-Ready & Ruggedized for Airline Cargo Transport

This prototype is a specialized **140 mm depth, high-strength travel variant** of the 10-inch 9U Homelab Mini Rack. It is engineered specifically to pack inside standard international carry-on luggage (cabin bags) or checked baggage with room for shock-absorbing foam or clothing padding.

---

## 1. Why 140 mm Depth?

| Specification | Standard Desktop Rack (v7.2) | Slim Cargo Travel Prototype | Advantage for Travel |
|---|---|---|---|
| **Depth** | $200.0\text{ mm}$ ($7.87"$) | **$140.0\text{ mm}$ ($5.51"$)** | **$-60\text{ mm}$ / 30% slimmer.** Easily fits into one half of a clamshell suitcase (which has $100\text{--}120\text{ mm}$ internal depth per shell). |
| **Total Height** | $495.0\text{ mm}$ (with handles) | **$445.0\text{ mm}$ (with handles)** | **$-50\text{ mm}$ shorter.** Eliminates tall snagging handles so it doesn't catch on suitcase zippers. |
| **Outer Wall Skin** | $1.2\text{ mm}$ (lightweight PLA) | **$2.4\text{ mm}$ (heavy-duty cargo skin)** | Double thickness for impact, crush, and puncture resistance. |
| **Corner Posts** | $12.0\text{ mm}$ | **$14.0\text{ mm}$** | Beefier anchor around M5 heat-set inserts. |
| **Anti-Racking** | Plain thin vents | **Integrated diagonal shear trusses** | Prevents diagonal parallelogram distortion when luggage is dropped or tossed. |
| **Print Material** | PLA (brittle, cracks in cold cargo holds) | **PETG, ABS/ASA, or PETG-CF** | High impact strength, ductile under shock, cold-temperature resistant. |

---

## 2. All 4 Subsystems Fit Inside the 140 mm Envelope

All four units in the homelab mount to standard 10-inch EIA-310 rails ($236.5\text{ mm}$ hole pitch, $224\text{ mm}$ clear opening) and fit comfortably within the 140 mm depth:

1. **1U: UniFi Cloud Gateway Ultra Shelf:** $135.0\text{ mm}$ deep (deepest unit in the rack; fits with $5.0\text{ mm}$ rear post clearance).
2. **2U: Raspberry Pi 5 Unit (Argon Poly+ 5 + Waveshare F):** $117.0\text{ mm}$ deep (fits with $23.0\text{ mm}$ clearance).
3. **12 V 3 A Power Brick in Cradle (Plate 13):** $120.0\text{ mm}$ deep (fits in the bottom bay with $20.0\text{ mm}$ clearance).
4. **3U: NIIMBOT B1 Face-Out Printer Dock:** $95.0\text{ mm}$ deep (fits with $45.0\text{ mm}$ clearance).
5. **3U: Waveshare 7-inch LCD (C) Touch Display:** $40.0\text{ mm}$ deep (ultra-slim profile; fits with $100.0\text{ mm}$ clearance).

---

## 3. Hardware & Fasteners (Uniform One-Size System)

* **Screws:** $38\times\text{ M5}\times 12\text{ mm}$ Button Head Socket Cap Screws (ISO 7380).
* **Inserts:** $38\times\text{ M5}$ Brass Heat-Set Threaded Inserts (outer $\varnothing 6.4\text{ mm}\times 10\text{ mm}$ depth).
* **Tool:** $3\text{ mm}$ Allen hex key.

---

## 4. CAD & Manufacturing Files

* **Onshape-Ready 3D Assembly STEP:**  
  [`STEP_for_Onshape/SlimCargo_Rack_9U_140mm_ASSEMBLY.step`](file://~/Downloads/Pi%205%20HomeLab%201/04_DESIGN_SOURCE/10_Slim_Cargo_Rack_140mm/STEP_for_Onshape/SlimCargo_Rack_9U_140mm_ASSEMBLY.step)
* **Print-Ready STLs (fit standard $220\times 220\text{ mm}$ and Bambu $256\times 256\text{ mm}$ beds):**
  * `SlimCargo_SideModule_2U_Base_x2.stl`
  * `SlimCargo_SideModule_3U_x4.stl`
  * `SlimCargo_SideModule_1U_Top_x2.stl`
  * `SlimCargo_CapHalf_x2.stl`
  * `SlimCargo_LowProfile_Handle_x2.stl`
  * `SlimCargo_BaseBar_x3.stl`
* **Studio Renders:**  
  Located in [`02_RENDERS/SLIM_CARGO_PROTOTYPE/`](file://~/Downloads/Pi%205%20HomeLab%201/02_RENDERS/SLIM_CARGO_PROTOTYPE/).

