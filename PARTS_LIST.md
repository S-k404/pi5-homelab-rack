# Pi 5 HomeLab Mini Rack: Final Bill of Materials & Hardware Verification

> **Build:** 9U rack, Pi 5 in the **Argon Poly+ 5** + adapter (F) holder, 12-ALT2 UCG mount, plate 13 brick cradle, clean faceplate (the brick's lead stays behind it, 28 Oct).  
> **What to print:** `01_PRINT_FILES/` (checked 28 Oct). The adapter (F) holder waits for a fit test with the real Poly+ 5 (see that README); the totals below include the step-down + UGREEN you'd need if it fails. **Corrected 28 Oct:** totals, the Poly+ 5 price, the Poly+ 5 hardware, and the false "rocker switch / invisible cable slit" notes.  
> **Checked again 28 Oct (ultrareview):** prices now match the Robu hardware cart (`01_PRINT_FILES/ROBU_HARDWARE_CART_TO_RESTORE.md`), the Cat6 is 1 m (the route to LAN 1 needs ≈ 61 cm), every cable length is checked on the model (`03_CHECKS/VERIFICATION_wiring_all-cables_28Oct.txt`), and the fastener counts were re-counted from the CAD. What changed and why: `ULTRAREVIEW/README.md`.

---

## 1. Electronics & Compute

| Item | Specification / Function | Qty | Unit Price (₹) | Total (₹) | Procurement Status & Source |
|---|---|:---:|:---:|:---:|---|
| **Raspberry Pi 5 (8 GB)** | Quad-core Arm Cortex-A76 @ 2.4 GHz, 8 GB LPDDR4X | 1 | 19,999 | 19,999 | **Ordered** (Order #3781408, 27 Oct) |
| **Waveshare Pi5 Connector Adapter (F)** | PCIe Gen3/2 to 2.5G PoE ETH, M.2 NVMe, 7–24 V screw terminal | 1 | 4,949 | 4,949 | **Ordered** (Order #3781408, 27 Oct) |
| **Argon Poly+ 5 Case & THRML 30mm Cooler** | Case with the THRML 30 mm cooler inside | 1 | 4,254 | 4,254 | **Purchased** (₹4,254 is the 27 Oct cart price; ₹859 here before was the Armor Lite's Robu price. Order number not recorded). Sits on the Poly+ 5 tray (W1) |
| **EVM 512 GB 2230 NVMe SSD** | PCIe Gen3 x4 M.2 2230 NVMe solid-state storage | 1 | 9,999 | 9,999 | **In Cart / To Order** (Amazon.in) |
| **Cuzor Mini UPS PRO (12V 3A)** | 3 × 2900 mAh cells, 12 V 3 A. Its switch, LED and OUT face the rack **rear**; DC-IN faces the faceplate | 1 | 2,199 | 2,199 | **To Order**: Robu ₹2,199 (hardware cart); Amazon ₹1,998 (27 Oct cart). **It's in both carts: buy it once** |
| **Waveshare 7" 1024×600 HDMI IPS Low-Power Touch (C)** | 1024×600 capacitive IPS touch (Waveshare / REES52 branded) | 1 | 4,389 | 4,389 | **To Order**: Robu ₹4,389 (hardware cart); Amazon ₹5,691 (27 Oct cart). **It's in both carts: buy it once** |
| **UniFi Cloud Gateway Ultra (UCG-Ultra)** | Cloud gateway router with 1 GbE LAN ports, multi-WAN | 1 | 17,949 | 17,949 | **In Cart / To Order** (Amazon.in B0D8PSW2BZ) |
| **NIIMBOT B1 Label Printer** | 20–50 mm thermal label printer docked in 3U body | 1 | 0 | 0 | **Already Owned** |

---

## 2. Power Supplies, Adapters & Cables

| Item | Specification / Function | Qty | Est. Price (₹) | Procurement & Route Notes |
|---|---|:---:|:---:|---|
| **12 V 5 A (60 W) DC Power Brick** | 5.5 × 2.1 mm center positive plug; 110 × 50 × 30 mm | 1 | 425 | **Robu Standard 12V 5A** (or Mean Well GST60A12). Mounts inside rack in Plate 13 cradle. Check it comes **with a mains cord** (C13 or C7 to an Indian plug). Its DC lead only needs ≈ 20 cm: coil the rest on top of the brick |
| **Right-Angle 5.5 × 2.1 mm male → straight female extension, ~30 cm** | UPS DC-IN → the brick's own plug, behind the faceplate (28 Oct: shelf floor → gusset arch → the cradle's front; it spans ~14 cm) | 1 | ≈150 | Amazon.in ("DC 5.5 × 2.1 90° extension"). Not priced yet; check the angle is 90° on the **male** end |
| **Right-Angle 5.5 × 2.1 mm DC Pigtail, bare ends, ≥ 30 cm** | UPS OUT (rack rear) → the adapter (F)'s screw terminal (route ≈ 24 cm, checked 28 Oct) | 1 | 151 | Amazon.in (SHOKITECH): check its length. Check polarity |
| **12 V → 5 V 5 A USB-C step-down** | **Only if the fit test fails** (the adapter can't plug into the Pi through the Poly+ 5's side cut-outs): powers the Pi from the UPS | 1 | ≈199 | **Not sourced yet.** Robu leads: XY-3606 (₹139) or a 25 W module (₹199). Check it really has a USB-C output. Zip-ties to the tray's 2 anchors |
| **UGREEN 20134 micro-HDMI extender** | **Only if the fit test fails**: Pi micro-HDMI 0 → the shelf's HDMI tower | 1 | ≈500 | Amazon.in (estimate) |
| **Flat Thin HDMI Cable (1 m)** | Full-size HDMI male to male | 1 | 567 | Amazon.in. Fit test passes: adapter (F)'s HDMI-A (rack rear) → screen: needs ≈ 62 cm with slack. Fails: the UGREEN socket in the shelf tower → screen. Plug mouldings up to 22 mm wide fit the holder (widened 28 Oct) |
| **USB-A to Micro-USB Cable (1 m)** | Power + capacitive touch data for 7" display | 1 | 59 | Robu cart. Pi 5 rear USB 2.0 port → 7" screen side micro-USB port (~0.5 A). Needs ≈ 70 cm with slack |
| **USB-A to USB-C Cable (50 cm)** | Power charging + USB serial printing for NIIMBOT B1 | 1 | 150 | Pi 5 rear USB 2.0 port → NIIMBOT B1 printer dock: ≤ 34 cm wherever the B1's port is. Screen + B1 charging use ~1.3–1.5 A of the Pi's 1.6 A USB budget |
| **Slim Cat6 Patch Cable (1 m)** | Gigabit / 2.5 GbE network patch | 1 | 200 | UCG-Ultra LAN port → the adapter (F)'s 2.5G port (or the Pi's own port if the fit test fails). Needs ≈ 61 cm with slack into LAN 1, so **1 m, not 0.5 m**. The UCG's LAN ports are 1 GbE, so the link runs at 1 G |
| **MicroSD Card (32 GB)** | High-speed Class 10 / A1 card | 1 | 1,629 | Robu cart line (SanDisk Ultra GO 32 GB). Any A1 32 GB card (≈ ₹350) does the same job. Initial Pi OS boot & PCIe NVMe bootloader configuration. |
| **UCG-Ultra power** | its USB-C adapter | — | — | **In the box** (Ubiquiti: "5V DC, 3A USB-C adapter included"). It needs its own wall socket: **the gateway isn't on the UPS** (only the Pi side is) |

---

## 3. Fasteners & Mechanical Hardware

| Fastener / Hardware | Required Qty | Buy Qty | Specification | Application in Rack |
|---|:---:|:---:|---|---|
| **M5 Heat-Set Brass Inserts** | **48** | 50+ | Ø6.4 mm OD × 8–10 mm length | 18 frame joints + 4 cap + 4 handle feet + 6 base bars + 16 rack rail holes (only the 16 the units use: the list is in `FINAL_TODO/FINAL_TODO.md`). Robu's "M5-M6 90 pcs" pack mixes M5 and M6: **count the M5s**; under 50, buy more |
| **M3 Heat-Set Brass Inserts** | **18** | 25 | Ø4.0 mm OD × 5–6 mm length | 4 in B1 dock ears, 8 in screen module (4 ears + 4 clips), 6 in Pi shelf posts |
| **M5 × 12 mm Button-Head Screws** | **28** | 30 | ISO 7380, A2 Stainless / Black Oxide | 18 module joints, 4 top cap, 6 bottom base tie rods |
| **M5 × 12 mm Button-Head (or Thumbscrews)** | **20** | 25 | ISO 7380 / M5 knurled thumb screws | 4 for top handles, 16 for unit ears (Pi, Dock, Screen, UCG) |
| **M5 Washers** | **16** | 20 | M5 flat washers (black or stainless) | Placed under unit-ear mounting screws to protect 3D prints |
| **M3 × 8 mm Button-Head Screws** | **4** | 10 | ISO 7380 M3 | Secures 4 screen corner clamping clips |
| **M3 × 8 mm Countersunk Screws** | **14** | 20 | DIN 7991 M3 countersunk | 4 for B1 dock ears, 4 for screen ears, 6 for faceplate to shelf (no v3 lid in this build) |
| **M3 × 12 mm Countersunk Screws** | **3** | 5 | DIN 7991 M3 countersunk | Poly+ 5 tray to the UPS tray. Fit them before the case: two end up under it. No inserts: they cut their own thread in the UPS tray's 2.5 mm pilots |
| **M2.5 × 25 mm Pan-Head Screws** (if the holder passes the fit test) | **4** | 10 | Pan or button head (not countersunk) | Adapter (F) holder: lid + board onto the posts (self-tap into 2.1 mm pilots). Replaces the M2.5 × 8 / × 10 + shims of the bare-board case |
| **Stick-On Rubber Feet (10–15 mm)** | **4** | 4 | Adhesive neoprene / silicone pads | Placed under the 4 bottom corner feet of 2U base |
| **1 mm Double-Sided Foam Tape** | 1 roll | 1 roll | 10–15 mm wide, 1 mm thick | Damps Cuzor UPS on tray floor ribs; pads screen corner tabs |
| **Zip Ties / Hook-and-Loop Straps** | 4 | 1 pack | 150 mm cable ties / velcro straps | Secures 12V brick in Plate 13 cradle; manages internal wiring |

---

## 4. 3D Printing Filament Requirements (Bambu Lab P1S)

| Material | Net Print Weight | Slicing & Waste Margin | Total Required | Spools to Buy | Recommended Color / Finish |
|---|:---:|:---:|:---:|:---:|---|
| **PLA** | ~1,260 g (1,189 now + 71 screen body later) | slicer waste on top | **≈1.3 kg** | **2 Spools** (1 kg each) | Silver (as in the Robu order). The Robu hardware cart has Sunlu APLA **grey** ×2: change the colour if you print yourself and want silver |
| **PETG** | ~514 g (293 now + 126 after the UPS check + 95 after measuring / the fit test) | slicer waste on top | **≈0.55 kg** | **1 Spool** (1 kg) | Black. The Robu hardware cart has Pro-Range PETG **grey** |

---

## 5. Financial Summary (All Figures in INR ₹)

| Category | Total Value | Already Owned / Ordered | Remaining to Spend |
|---|:---:|:---:|:---:|
| **Electronics & Compute** | ₹63,738 | ₹29,202 (Pi 5 + Adapter F + Argon Poly+ 5 & THRML) | **₹34,536** |
| **Power Supplies, Cables, Step-down, UGREEN** | ₹3,880 | ₹0 | **₹3,880** (₹699 of it only if the fit test fails) |
| **Fasteners & Small Hardware** (Robu cart lines) | ₹2,997 | ₹0 | **₹2,997** + the unpriced bits below |
| **3D Printing Filament** (skip if Robu prints) | ₹2,866 | ₹0 | **₹2,866** |
| **Grand Total** | **₹73,481** | **₹29,202** | **₹44,279** |

Re-summed 28 Oct (ultrareview) from the Robu hardware cart: UPS ₹2,199 and screen ₹4,389 (Robu, not the Amazon prices), microSD ₹1,629 and micro-USB ₹59 (the cart lines), fasteners = M5 inserts 959 + 3 × M5×12 packs 501 + washers 89 + M3×8 button 239 + M3 inserts 1,129 + zip ties 80, filament = 2 × 899 + 1,068. **Not priced yet:** M3 × 8 and M3 × 12 countersunk, M2.5 × 25 pan-head, rubber feet, 1 mm foam tape (none on Robu), and the right-angle DC extension (≈ ₹150, not in the totals).

Earlier (28 Oct morning): sums checked. The old table summed the electronics to ₹60,484 instead of ₹61,444 (₹960 short), with the Poly+ 5 at ₹859; at ₹4,254 the electronics come to ₹64,839. Not included: the Robu print-service order (₹6,702 on 27 Oct, before the cart changes in `01_PRINT_FILES/README.md`).

*(Procurement Notes: The build uses the user's purchased **Argon Poly+ 5 case** with integrated **Argon THRML 30mm PWM cooler** mounted on the Plate 11B tray with the Waveshare Adapter (F) in the 11B-SIDE holder. Using the Robu Standard 12V 5A power brick saved ₹2,052 vs. the industrial Mean Well unit. Not needed in this build: the Active Cooler, the Armor Lite, the shims, the switch extender and accent filament).*
