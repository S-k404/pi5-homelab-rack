# Robu 3D Printing Service - Slim Cargo Upload Guide

This folder contains the print files for the **Slim Cargo 9U (140 mm)** build, renamed with their exact **Quantity**, **Material**, and **Infill** settings.

---

### Option A: Updating Your Existing Robu Cart (Recommended)
If you already have Quotation #005065 in your cart, you only need to swap out the changed parts:

1. **Delete from your cart:**
   - Lines 1–6 (the old 200 mm standard rack modules)
   - `Rack_Shelf_pinned` (the old shelf)
   - `Rack_Faceplate_2U_10in` (the old faceplate)
   - `Waveshare_F_holder_base` (the old holder base with narrow HDMI notch)
   - `Pi5_UPS_v3_shims` (shims are not used)
2. **Open folder:** `01_NEW_AND_REPLACED_PARTS/`
3. **Upload the 9 files below** to [robu.in/product/3d-printing-service1/](https://robu.in/product/3d-printing-service1/):

| File Name | Qty | Material | Quality | Infill |
|---|:---:|---|---|:---:|
| `01_[QTY_2]_[PETG_Black_25%]_SlimCargo_SideModule_2U_Base.stl` | **2** | PETG - Black | 0.2 mm Standard | **25%** |
| `02_[QTY_4]_[PETG_Black_25%]_SlimCargo_SideModule_3U.stl` | **4** | PETG - Black | 0.2 mm Standard | **25%** |
| `03_[QTY_2]_[PETG_Black_25%]_SlimCargo_SideModule_1U_Top.stl` | **2** | PETG - Black | 0.2 mm Standard | **25%** |
| `04_[QTY_2]_[PETG_Black_20%]_SlimCargo_CapHalf.stl` | **2** | PETG - Black | 0.2 mm Standard | **20%** |
| `05_[QTY_2]_[PETG_Black_35%]_SlimCargo_LowProfile_Handle.stl` | **2** | PETG - Black | 0.2 mm Standard | **35%** |
| `06_[QTY_3]_[PETG_Black_30%]_SlimCargo_BaseBar.stl` | **3** | PETG - Black | 0.2 mm Standard | **30%** |
| `07_[QTY_1]_[PETG_Black_20%]_REPLACE_SHELF_10_Pi_Rack_Shelf_pinned.stl` | **1** | PETG - Black | 0.2 mm Standard | **20%** |
| `08_[QTY_1]_[PETG_Black_20%]_REPLACE_FACEPLATE_C2_Pi_Faceplate_2U_clean.stl` | **1** | PETG - Black | 0.2 mm Standard | **20%** |
| `09_[QTY_1]_[PETG_Black_20%]_REPLACE_HOLDER_BASE_W2_Waveshare_F_Holder_Base.stl` | **1** | PETG - Black | 0.2 mm Standard | **20%** |

---

### Option B: Fresh Order from Scratch
If your cart is empty or you want to start fresh, open `02_ALL_PARTS_FRESH_ORDER/` and upload all 17 files according to the labels in their filenames.

---

> **Note on 12V Power Brick:** The 12V cradle (`11_Brick_Cradle_12V`) is omitted on purpose because it does not fit the 140 mm travel frame. The brick operates externally on your desk.
