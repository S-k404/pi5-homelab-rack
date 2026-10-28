# Pi 5 HomeLab: the final to-do list (28 Oct 2026, after the ultrareview)

This is the **one** to-do list. `START_HERE.md` points here; the print list is `01_PRINT_FILES/README.md`; the buy list is `PARTS_LIST.md`; what the review found and changed is `ULTRAREVIEW/README.md`.

**The build:** 9U T0-look rack · B1 dock v5 · 7" screen module · Pi 5 in the Argon Poly+ 5 with the adapter (F) in its holder beside it (fit test first) · Cuzor UPS · 12 V brick in the plate 13 cradle · **clean faceplate** (no window, no notch: the brick's lead stays behind it) · Printables 942972 UCG-Ultra mount.
**Left / right:** seen from the **front**, the brick bay is on the **left** of the Pi unit, and the cables run up the back on the **right**.

---

## 0. Before you check out anything
- [ ] **Robu print cart** (17 lines, ₹6,702 on 27 Oct):
  - replace `Rack_Faceplate_2U_10in` with **`C2_Pi_Faceplate_2U_clean`** (28 Oct: no DC-IN window, no notch)
  - **re-upload the Pi shelf** from `01_PRINT_FILES/1_PRINT-NOW/10_Pi_Rack_Shelf_pinned…`. It changed on 28 Oct: there's now an arch in the right gusset for the 12 V lead
  - remove `Pi5_UPS_v3_shims`
  - add `11_Brick_Cradle_12V` + `12_Brick_Spacer_8mm` (PETG black, 20 %)
  - **new (28 Oct):** re-upload the adapter (F) holder **base** from `01_PRINT_FILES/3_WAIT/W2_…`. The file in the cart has an 18.6 mm HDMI notch, which stops a 20–22 mm HDMI plug 2.4 mm short. The lid didn't change.
  - check out the UPS tray only after the UPS check (§2), the Poly+ 5 tray after measuring the case, and the holder after the fit test. The faceplate doesn't wait any more
- [ ] **Leave `01_PRINT_FILES/5_SLIM_CARGO_…` out of the order.** It's an *alternative* 140 mm rack frame, not extra parts, and the 12 V brick and its cradle don't fit it.
- [ ] **The screen and the Cuzor UPS are in two carts** (Amazon on 27 Oct, and the Robu hardware list). Buy each once: Robu ₹4,389 / ₹2,199, Amazon ₹5,691 / ₹1,998.
- [ ] **Buy a 1 m Cat6, not 0.5 m.** From the adapter to the gateway's LAN 1 needs ≈ 61 cm.
- [ ] If they're still in the Amazon cart from the 27 Oct check, these aren't needed: the 52Pi Armor Lite V5 (the THRML cooler is inside the Poly+ 5), the second flat HDMI cable, and the Tobo USB-C → DC "laptop" adapter. That one is probably 20 V: **never plug it into the UPS.**

## 1. Orders
- [ ] **Robu hardware** (after the print order): `01_PRINT_FILES/ROBU_HARDWARE_CART_TO_RESTORE.md`, 13 lines, **₹14,564** (the file said ₹15,083, which still counted the dropped Active Cooler).
  - **M5 inserts:** the "M5-M6 90 pcs" pack mixes sizes. Count the M5s; you need **48**. If the pack has fewer than about 50, add more M5.
- [ ] **Not on Robu: find these elsewhere.**
  - M3 × 8 countersunk × 14
  - M3 × 12 countersunk × 3
  - right-angle 5.5 × 2.1 pigtail with bare ends, **≥ 30 cm** (Amazon SHOKITECH ≈ ₹151)
  - **right-angle 5.5 × 2.1 male → straight female extension, ~30 cm** (UPS DC-IN → the brick's plug, all behind the faceplate; it needs ~14 cm)
  - 4 × stick-on rubber feet
  - 1 mm double-sided foam tape
  - only if the holder passes the fit test: M2.5 × 25 pan-head × 4
- [ ] **Amazon:**
  - UCG-Ultra (B0D8PSW2BZ)
  - EVM 512 GB 2230 NVMe
  - 1 m slim Cat6
  - 1 m flat HDMI
  - 50 cm USB-A → USB-C (for the B1)
  - only if the fit test fails: the UGREEN 20134 micro-HDMI extender and a 12 V → 5 V 5 A USB-C step-down (check it really has a USB-C output)
- [ ] **Order #3781408:** cancel or return ONLY the Mean Well LRS-150-12 line. Don't press "Cancel Order".

## 2. When things arrive: measure and test
- [ ] **Cuzor UPS** (a photo is enough):
  - switch, LED and OUT on one end
  - DC-IN on the other end, at the end that lines up with the faceplate's DC-IN window
  - length ≤ 101 mm

  Then order or print `2_CHECK-UPS-FIRST` (C1 + C2).
- [ ] **Argon Poly+ 5:**
  - the case is ≤ 96.0 × 66.5
  - **fit test** (`01_PRINT_FILES/README.md`): the adapter's USB-C and micro-HDMI both click fully home through the case's side cut-outs, with the adapter level
  - the 16-pin FFC can leave the case

  Pass: print W1 + W2 + W3. Fail: print W1 only, and use the step-down + UGREEN.
- [ ] **Screen (Wed 4 Nov):**
  - 164.9 wide
  - 124.2 over the corner tabs
  - 8.0 from glass to board back
  - **tab holes 157.0 mm apart across, ~115 mm up** (they're short slots, 112.8–117.0). Corrected 28 Oct: the plate settings said ~159 × ~114.

  Then print W4 (`Plate09`).
- [ ] **12 V brick:**
  - its thickness picks the spacer (29–30.5 mm: the 8 mm one)
  - the plug is 5.5 × 2.1, centre-positive
  - a mains cord comes with it
  - note how long its DC lead is: it only needs ≈ 20 cm, and the rest gets coiled (§4)
- [ ] **UCG-Ultra in the printed mount**, before racking: plug in a patch cable (LAN 1) and its USB-C.
  - On Ubiquiti's rear view they clear the mount's 10 mm rear lip (RJ45 by ~1.4 mm, USB-C by ~3.9 mm) and the corner post (4.5 mm). That's measured on a picture, ±1 mm, so confirm it here.
  - If a plug does touch the lip, trim the lip to ~5 mm with flush cutters; the posts still stop the gateway.
  - The reset pinhole is behind the corner post: slide the gateway out to press it.
  - The 5 V 3 A USB-C adapter comes in the box (Ubiquiti).
- [ ] **NIIMBOT B1:**
  - Where's its USB-C? The 50 cm cable reaches anywhere on the printer: ≤ 34 cm needed.
  - Where does the lid hinge? The dock works with both guesses (85° or 120° of swing).
- [ ] **Heat-set insert test:** print plate 03 first and set one M5 insert in a Ø6.4 hole.

## 3. Print
- [ ] Plate 03 (insert test), then the rest of `01_PRINT_FILES/1_PRINT-NOW/`
- [ ] `2_CHECK-UPS-FIRST/` after the UPS check
- [ ] `3_WAIT/` after measuring or testing; delete from `Plate11W` whatever you don't print
- [ ] Filament if you print yourself: ≈ 1.3 kg PLA + 0.55 kg PETG. The Robu hardware cart has **grey** filament, but the renders and the Robu print order are silver PLA / black PETG.

## 4. Build
- [ ] **M5 inserts: 48, and only these:**
  - 18 in the top ribs of the 2U base and both 3U modules (3 per side each)
  - 4 in the 1U tops' top ribs, front and rear holes only (the cap screws; the middle holes stay empty)
  - 4 in the cap columns (handles)
  - 6 in the base-bar ends (2 each)
  - **16 in the front rail holes the units use:** holes **1, 6, 7, 15, 16, 24, 25, 27** counted from the bottom, on both front posts (Pi 1 + 6, dock 7 + 15, screen 16 + 24, UCG 25 + 27). The rear rail holes stay empty.
- [ ] **M3 inserts: 18:** 4 in the dock body (ears), 4 + 4 in the screen module (ears + clip bosses), 6 in the Pi shelf (faceplate).
- [ ] **Rack:** stack and screw it: the 2U base, 3U, 3U, the 1U tops, the base bars, the cap and the handles. That's 48 × M5 × 12, with washers on the 16 unit-ear screws.
- [ ] **Pi unit:**
  1. UPS on foam tape in the UPS tray, tray onto the shelf pins.
  2. Poly+ 5 tray on with 3 × M3 × 12 countersunk. Fit them before the case: two end up under it, and they cut their own thread.
  3. Case on foam tape. If the fit test passed: the holder, the adapter (4 × M2.5 × 25), the FFC.
  4. The UPS OUT lead (§5, line 3).
  5. **The 12 V extension (§5, line 1):**
     - push its right-angle plug into the UPS DC-IN, through the tray's DC-IN window, with the cable pointing left (seen from the front)
     - lay the cable down on the shelf floor, along the front and under the OUT lead
     - thread it through the arch at the foot of the right post's gusset
  6. The faceplate (6 × M3 × 8 countersunk). Nothing passes through it.
- [ ] **Brick:**
  - strap it in the cradle with the 8 mm spacer
  - bring the extension's socket into the cradle's open front (over the strap rib) and push the brick's own plug into it
  - coil the brick's spare lead beside the join (a ~50 × 20 mm loop holds ~0.6 m), and any more on top of the brick (110 × 38 × 40 mm under the dock). Zip-tie the coil; don't wrap it round the brick.
- [ ] **Rack the units bottom-up:** Pi, dock, screen, then the UCG mount (plugged in first).
- [ ] **Fix the rack to the desk.** It tips forward at ~5.8 N pushed on the gateway's back.

## 5. Wiring (checked on the models: `03_CHECKS/VERIFICATION_wiring_all-cables_28Oct.txt`, render 17–18)
| # | Cable | From → to | Route | Bought / needed |
|---|---|---|---|---|
| 1 | Brick 12 V lead + right-angle extension | brick → join in the cradle's front → UPS DC-IN | **all behind the faceplate:** shelf floor → gusset arch → cradle front (render 08, 16) | extension 30 cm / ~15 cm; coil the brick's spare beside the join |
| 2 | Mains cord | wall → brick | out of the rack's back | comes with the brick? |
| 3 | Right-angle pigtail, bare ends | UPS OUT (rack rear) → adapter (F) screw terminal | right channel → **over the UPS's top edge at the joint post** → front window → tray lead hole → holder front notch | ≥ 30 cm / ≈ 24 cm |
| 4 | Flat HDMI | adapter (F) HDMI-A → screen HDMI | out of the Pi's rear, down to 50 mm, across to the **right side** (seen from the front) and up the riser tight against it (the ears hide it), to the screen's socket edge; the flat cable folds back behind the screen | 1 m / ≈ 62 cm |
| 5 | USB-A → micro-USB | Pi USB 2.0 → screen micro-USB | same riser | 1 m / ≈ 70 cm |
| 6 | USB-A → USB-C | Pi USB 2.0 → NIIMBOT B1 | into the back of the dock | 50 cm / ≤ 34 cm |
| 7 | Slim Cat6 | adapter (F) 2.5G (or the Pi's own port) → UCG-Ultra LAN | same riser up to 362 mm, across behind the gateway (below the mount's open keystone hole), up into LAN 1 | **1 m** / ≈ 61 cm |
| 8 | USB-C | UCG-Ultra → its own adapter → wall socket | down the back | it's **not on the UPS** |
| 9 | Patch cable | ISP router → UCG-Ultra WAN | | yours |

- [ ] Zip-tie the riser bundle (4, 5, 7, 8) tight against the inside of the right-hand side modules (seen from the front), one cable behind the other. Seen straight on, nothing should show (render 03).
- [ ] **Polarity:** check the brick plug and the pigtail's bare ends with a meter before the first switch-on. Centre-positive: + goes to the terminal's + screw.

## 6. First power-up
- [ ] Boot from the microSD. Add `usb_max_current_enable=1` to `/boot/firmware/config.txt`.
- [ ] USB budget: the screen (~0.4 A) and the B1 charging (~1 A) share the Pi's 1.6 A. If the Pi logs USB over-current, unplug the B1 once it's charged (it prints over Bluetooth too).
- [ ] If the FFC route works: move the OS to the NVMe.
- [ ] UPS: ~32 Wh is roughly 1 h at full load, 2–3 h idle. Only the Pi side is on it.

## 7. Later / decisions
- [ ] What the 5 × WeAct e-paper + 5 × ESP32-C3 are for.
- [ ] Do you want the gateway on the UPS too? It isn't now: it has its own USB-C adapter.
- [ ] **Slim Cargo rack:** only if you want the travel version. The brick would have to live outside, or it needs a new short cradle. It now has print plates (`SlimPlate01–07`, replacing Plate01–07) and a weight estimate (frame ≈ 1.24 kg PETG with the ears and clips), but nothing has been printed or test-fitted.
- [x] Onshape: the master STEP assemblies were regenerated on 28 Oct (clean faceplate, shelf with the arch, holder base with the HDMI relief). One thing is still a stand-in: unit 4 is the unused custom UCG shelf, because the Printables 942972 mount only exists as a mesh. Rebuild with `04_DESIGN_SOURCE/ONSHAPE_PROJECT/build_onshape_project.py`.
- [ ] Git: the first commit holds 433 MB of STL/STEP/PNG, so `/ultrareview` can't run on this repo (no remote, too large). See `ULTRAREVIEW/README.md`.
