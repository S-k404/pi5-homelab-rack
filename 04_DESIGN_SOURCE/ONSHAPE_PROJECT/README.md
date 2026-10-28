# Pi 5 HomeLab 10-Inch 9U Mini Rack · Master Onshape Project

This directory contains the official **Onshape Master CAD Project** and **Technical Engineering Schematics** for the 10-inch 9U Homelab Mini Rack.

Everything is provided in **standard AP214 STEP format (`.step` / `.stp`)**, which imports natively into **Onshape**, **SolidWorks**, **Autodesk Fusion 360**, **FreeCAD**, and **Rhino** with full solid geometry, individual named bodies, and color attribution preserved.

---

## 📦 Master Assembly Files

| File | Type | Depth | Description | Link |
| :--- | :--- | :--- | :--- | :--- |
| **`Pi5_HomeLab_9U_ALL_IN_ONE_COMBINED.step`** | **Master Combined 2-in-1** | **200 mm & 140 mm** | **Both Racks Side-by-Side in One File**: Standard 200 mm Desktop Edition on the left + Slim Cargo 140 mm Travel Edition on the right. Both with all 4 units loaded. Immediate visual comparison in Onshape! | [Download Combined STEP](file://~/Downloads/Pi%205%20HomeLab%201/04_DESIGN_SOURCE/ONSHAPE_PROJECT/Pi5_HomeLab_9U_ALL_IN_ONE_COMBINED.step) |
| **`Pi5_HomeLab_9U_Complete_ASSEMBLY.step`** | **Master STEP Assembly** | **200 mm** | **Complete Standard Homelab**: Full 9U rack frame (DeskPi T0 aesthetic) + all 4 units loaded in place (1U UCG-Ultra, 3U 7" Screen, 3U NIIMBOT B1 Dock, 2U Pi 5 + Cuzor UPS + 12V Brick Cradle + Spacers). | [Download STEP](file://~/Downloads/Pi%205%20HomeLab%201/04_DESIGN_SOURCE/ONSHAPE_PROJECT/Pi5_HomeLab_9U_Complete_ASSEMBLY.step) |
| **`SlimCargo_HomeLab_9U_Complete_ASSEMBLY.step`** | **Master STEP Assembly** | **140 mm** | **Complete Slim Cargo Edition**: 140 mm depth reinforced travel frame + low-profile flush handles + all 4 units fully verified inside the suitcase travel envelope. | [Download STEP](file://~/Downloads/Pi%205%20HomeLab%201/04_DESIGN_SOURCE/ONSHAPE_PROJECT/SlimCargo_HomeLab_9U_Complete_ASSEMBLY.step) |
| **`Pi5_HomeLab_9U_SingleBody_Compound_STUDIO.step`** | **Multi-Body Part Studio Compound** | **200 mm** | **Single Part Studio Model**: All 49 solid bodies united in place as a compound solid. Opens directly in an Onshape Part Studio tab without needing assembly mates! | [Download Compound STEP](file://~/Downloads/Pi%205%20HomeLab%201/04_DESIGN_SOURCE/ONSHAPE_PROJECT/Pi5_HomeLab_9U_SingleBody_Compound_STUDIO.step) |
| **`Pi5_HomeLab_9U_Onshape_Project_Package.zip`** | **Complete Project ZIP** | — | **One-Click Onshape Import**: Zip archive containing all master assemblies, 30 individual component STEPs, and full engineering schematics. | [Download ZIP](file://~/Downloads/Pi%205%20HomeLab%201/04_DESIGN_SOURCE/ONSHAPE_PROJECT/Pi5_HomeLab_9U_Onshape_Project_Package.zip) |

---

## 📐 Dimensioned Engineering Schematics

High-resolution engineering drawings showing all standard dimensions, EIA-310 10-inch mounting pitches, U-spacing, clearances, and fastener specifications:

- 📊 **[00_HOMELAB_RACK_ENGINEERING_SCHEMATIC.png](file://~/Downloads/Pi%205%20HomeLab%201/04_DESIGN_SOURCE/ONSHAPE_PROJECT/00_HOMELAB_RACK_ENGINEERING_SCHEMATIC.png)**:
  - **View A**: Front Elevation schematic with 10" EIA-310 standard spacing (236.525 mm hole pitch, 254 mm faceplates).
  - **View B**: Side Elevation comparison between 200 mm Desktop and 140 mm Slim Cargo profile.
  - **View C**: Component depth envelope bar chart (all units verified < 140 mm).
  - **View D**: Complete fastener, material, and manufacturing specifications.
- 📊 **[00_SLIM_CARGO_RACK_SCHEMATIC.png](file://~/Downloads/Pi%205%20HomeLab%201/04_DESIGN_SOURCE/ONSHAPE_PROJECT/00_SLIM_CARGO_RACK_SCHEMATIC.png)**: Dedicated schematic for the 140 mm Slim Cargo travel prototype.

---

## 🚀 How to Import into Onshape

### Method 1: Single Master Assembly (Recommended for Inspection & Visual Pairing)
1. Open [Onshape](https://cad.onshape.com) and create a new Document (e.g. `Pi5_HomeLab_9U_Master`).
2. Click the **`+` (Insert new tab)** button at the bottom-left of the window, or click **Import...** in the top Document menu.
3. Select either:
   - **`Pi5_HomeLab_9U_Complete_ASSEMBLY.step`** (for standard 200 mm rack), or
   - **`SlimCargo_HomeLab_9U_Complete_ASSEMBLY.step`** (for 140 mm slim cargo rack).
4. In the import options dialog:
   - **Import to this Document**: Checked.
   - **Default length unit**: Select **Millimeter (mm)**.
   - **Create a composite part**: Unchecked (keeps individual solid bodies distinct).
5. Click **OK**. Onshape creates an Assembly or Part Studio with all 35+ solid components loaded in their exact 3D coordinates!

### Method 2: One-Click Full Project Import
1. Drag and drop **`Pi5_HomeLab_9U_Onshape_Project_Package.zip`** directly into your Onshape Document or Documents page.
2. Onshape will unpack the archive and create organized folders with both master assemblies, component STEPs, and reference schematics.

### Method 3: Modular Assembly with Mate Connectors
If you want to create interactive kinematics (e.g., sliding the B1 printer in/out or opening the printer lid):
1. Import individual parts from the **[`INDIVIDUAL_STEP_PARTS/`](file://~/Downloads/Pi%205%20HomeLab%201/04_DESIGN_SOURCE/ONSHAPE_PROJECT/INDIVIDUAL_STEP_PARTS/)** directory.
2. In an Onshape **Assembly tab**:
   - Fix `Rack_SideModule_2U_Base_R` to the Origin.
   - Use **Fastened Mates** at the screw/insert centers for the side modules and base bars.
   - Use **Slider Mates** on the B1 dock cavity to simulate inserting/removing the printer.
   - Use **Revolute Mates** on the B1 printer lid hinge.

---

## 🌐 Coordinate Reference System

The assembly STEP files use the standard EIA-310 engineering coordinate system:

```
          +Y (Height)
           ▲
           │   [Cap & Handles] (Y = 400.05 to 475.05 mm)
           │   [Unit 4: 1U UCG-Ultra] (Y = 355.6 to 400.05 mm)
           │   [Unit 3: 3U 7" Waveshare Screen] (Y = 222.25 to 355.6 mm)
           │   [Unit 2: 3U NIIMBOT B1 Dock] (Y = 88.9 to 222.25 mm)
           │   [Unit 1: 2U Pi 5 + Cuzor UPS + Brick] (Y = 0.0 to 88.9 mm)
           ├────────────────────────► +Z (Depth, into rack)
          /│   [Plinth & Base Bars] (Y = -20.0 to 0.0 mm)
         / 
        ▼
       +X (Width across rack, -140 mm to +140 mm; Center X = 0)
```

- **Origin $(0, 0, 0)$**: Centerline of the rack at the bottom of the 9U rail space, flush with the front rail mounting face.
- **$X$ Axis**: Lateral width. Total rack width = $280.0\text{ mm}$ ($X \in [-140, +140]$). Rack ears mount at $X = \pm 118.2625\text{ mm}$ (EIA-310 $236.525\text{ mm} / 9.3125"$ pitch).
- **$Y$ Axis**: Vertical height. 9U total rack height = $400.05\text{ mm}$ ($9 \times 44.45\text{ mm}$). Cap adds $30.0\text{ mm}$, handles add $45.0\text{ mm}$ (or $18.0\text{ mm}$ low-profile).
- **$Z$ Axis**: Depth. $Z = 0$ is the front rail face. Units extend backward into $+Z$.
  - Standard 200 mm Rack: $Z \in [0, 200\text{ mm}]$.
  - Slim Cargo 140 mm Rack: $Z \in [0, 140\text{ mm}]$.

---

## 🗂️ Component & Body Hierarchy

The Master Assembly contains the following solid bodies, color-coded and named:

| Subsystem | Part Name in Onshape | Color / Material | Function / Specifications |
| :--- | :--- | :--- | :--- |
| **Rack Frame** | `Rack_side_0_2U_R` / `L` | Silver (`#C8CCD1`) | 2U Base side wall modules with plinth and foot pads. |
| | `Rack_side_1_3U_R` / `L` | Silver (`#C8CCD1`) | Lower 3U side module for NIIMBOT B1 Dock. |
| | `Rack_side_2_3U_R` / `L` | Silver (`#C8CCD1`) | Upper 3U side module for 7" Touch Screen. |
| | `Rack_side_3_1U_R` / `L` | Silver (`#C8CCD1`) | 1U Top side module for UCG-Ultra gateway. |
| | `Rack_bar_front` / `middle` / `rear` | Silver (`#C8CCD1`) | Base cross-bars providing structural lateral rigidity. |
| | `Rack_cap_R` / `L` | Silver (`#C8CCD1`) | Ventilated top cap halves with interlocking dovetail seam. |
| | `Rack_handle_R` / `L` | Silver (`#C8CCD1`) | Top grab handles for rack transport. |
| **Unit 4 (1U Top)** | `UCG_Ultra_1U_Shelf` | Dark Slate (`#333333`) | 1U tray with display window and rear corner stops. |
| | `UniFi_UCG_Ultra_Gateway` | White (`#F0F2F5`) | Solid dummy model of UniFi UCG-Ultra ($141.8 \times 127.6 \times 30\text{ mm}$). |
| **Unit 3 (3U)** | `Display7C_3U_Body` | Silver (`#C8CCD1`) | 3U front bezel and bracket for Waveshare 7" LCD (C type). |
| | `Display7C_Ear_R` / `L` | Silver (`#C8CCD1`) | Rack mounting ears with EIA-310 slotted mounting holes. |
| | `Waveshare_7in_LCD` | Glass Black (`#262B33`) | 7" 1024x600 IPS display glass, PCB, and connector envelope. |
| | `Display7C_Clip_1..4` | Silver (`#C8CCD1`) | Rear retention clips holding display against the front bezel. |
| **Unit 2 (3U)** | `B1_Dock_3U_Body` | Silver (`#C8CCD1`) | 3U dock cradle with thumb-access notch and cable channels. |
| | `B1_Dock_3U_Ear_R` / `L` | Silver (`#C8CCD1`) | Rack mounting ears for B1 dock. |
| | `NIIMBOT_B1_Body` | Cyan Slate (`#4A7A96`) | Detailed model of NIIMBOT B1 printer ($132 \times 91 \times 62\text{ mm}$). |
| | `NIIMBOT_B1_Lid` | Dark Slate (`#222222`) | Printer paper roll compartment lid. |
| | `NIIMBOT_B1_Slide` | White (`#F5F5F5`) | Printer paper exit and cut slide. |
| | `NIIMBOT_B1_Button` | Silver Grey (`#9AA0A6`) | Power / feed control button. |
| | `NIIMBOT_B1_LED` | Green (`#34D399`) | Status LED indicator. |
| **Unit 1 (2U Base)** | `Pi5_Rack_Shelf` | Dark Slate (`#333333`) | 2U main shelf with alignment pins for UPS & Argon trays. |
| | `Pi5_Faceplate_2U_DC_notch` | Dark Slate (`#333333`) | 2U faceplate with recessed window & DC power lead notch. |
| | `Pi5_UPS_Tray` | Dark Slate (`#333333`) | Retention tray for Cuzor 12V Mini UPS. |
| | `Cuzor_MiniUPS_Pro_12V3A` | Blue Slate (`#1E293B`) | Official 3D model of Cuzor 12V 3A Mini UPS Pro. |
| | `Pi5_ArgonPoly5_Tray` | Dark Slate (`#333333`) | Plate 11B tray for Argon Poly+ 5 case with foam tape datum. |
| | `Argon_Poly5_Shell` / `Top` | Dark Metal (`#1A1A1A`) | Stand-in model of Argon Poly+ 5 with fan louvres and ports. |
| | `Waveshare_F_Holder_Base` | Dark Slate (`#333333`) | Protective cradle for Waveshare PCIe-to-M.2 Adapter (F). |
| | `Waveshare_F_Holder_Lid` | Dark Slate (`#333333`) | Snap/screw lid for PCIe Adapter (F) holder. |
| | `Waveshare_Adapter_F_PCB` | Dark Blue (`#0D47A1`) | Adapter (F) PCB with 2.5G RJ45, HDMI-A, and terminal block. |
| | `EVM_512GB_NVMe_SSD` | Black (`#1A1A1A`) | M.2 2230 NVMe solid state drive in the M-key socket. |
| | `Brick_Cradle_12V` | Dark Slate (`#333333`) | Plate 13 cradle resting across middle & rear base bars. |
| | `Brick_Spacer_8mm` | Dark Slate (`#333333`) | 8 mm thickness adjustment spacer for the power brick. |
| | `Power_Brick_12V_5A` | Dark Slate (`#262626`) | 12V 5A Robu power brick ($110 \times 50 \times 30\text{ mm}$). |

---

## 🔩 Fasteners & Assembly BOM

All rack frame connections use a **single standardized screw and insert size**:

| Fastener | Quantity | Application |
| :--- | :--- | :--- |
| **M5 x 12 mm Button Head Socket Cap Screws** | **38 pcs** | Side module joints (18 pcs), cap attachment (8 pcs), handles (4 pcs), base bars (6 pcs), units to rack (16 pcs). |
| **M5 Brass Heat-Set Threaded Inserts** ($\varnothing 6.4\text{ mm} \times 10\text{ mm}$) | **38 pcs** | Embedded into top ribs of lower modules, cap columns, base bar ends, and rail posts. |
| **M2.5 x 6 mm Screws + Standoffs** | **8 pcs** | Waveshare Adapter (F) board mounting & Argon tray alignment. |
| **M3 x 8 mm Screws** | **4 pcs** | Display 7C rear retention clips. |

