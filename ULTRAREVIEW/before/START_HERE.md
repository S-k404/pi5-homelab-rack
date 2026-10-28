# Pi 5 HomeLab: start here (28 Oct 2026)

**Print / order list: `01_PRINT_FILES/README.md`.** Overview and folder map: `README.md`. Buy list: `PARTS_LIST.md`.

The build:
- the 9U rack
- B1 dock v5
- the 7" screen module
- the Pi 5 in the **Argon Poly+ 5** with the adapter (F) holder
- the **12-ALT2** UCG-Ultra mount
- the 12 V brick cradle (plate 13)
- the **DC-notch** faceplate

Print only from `01_PRINT_FILES/`. Everything older (including the broken "hidden-slit / switch" faceplate) is in `_Old_versions/`.

## To do
**Orders**
- [ ] **Robu print cart** (not checked out on 27 Oct):
  - replace `Rack_Faceplate_2U_10in` with `C2_Pi_Faceplate_2U_DC-notch`; check it and the UPS tray line out only after the **UPS check**
  - remove `Pi5_UPS_v3_shims`
  - add `11_Brick_Cradle_12V` + `12_Brick_Spacer_8mm` (PETG black, 20 %)
  - keep the Poly+ 5 tray line, but only check it out once the case is measured
  - keep the F holder base + lid lines, but only check them out after the **fit test** (`01_PRINT_FILES/README.md`)
- [ ] **Robu hardware** (after the print order): the list in `01_PRINT_FILES/ROBU_HARDWARE_CART_TO_RESTORE.md`, plus:
  - a right-angle 5.5 × 2.1 pigtail with bare ends, **at least 30 cm** (UPS OUT → adapter terminal)
  - 4 × M2.5 × 25 pan-head (if the holder passes the fit test)
  - only if the fit test fails: a 12 V → 5 V 5 A USB-C step-down (check it has a USB-C output)
- [ ] **Amazon:**
  - UCG-Ultra (B0D8PSW2BZ)
  - EVM 512 GB 2230 NVMe
  - UGREEN 20134 micro-HDMI extender (only if the fit test fails)
  - 1 m slim Cat6
  - 1 m flat HDMI
  - 50 cm USB-C cable for the B1
- [ ] **Order #3781408:** cancel or return ONLY the Mean Well LRS-150-12 line (don't press "Cancel Order").

**Measure**
- [ ] **Argon Poly+ 5, when it arrives:**
  - length and width (the tray takes ≤ 96.0 × 66.5)
  - the **holder fit test**: do the adapter's USB-C + micro-HDMI plug fully into the Pi through the case's side cut-outs?
  - whether the adapter's 16-pin FFC can leave the case
- [ ] **Cuzor UPS:** which faces the IN / OUT jacks and the switch are on, and length ≤ 101 mm (before the UPS tray + faceplate print)
- [ ] **Screen, Wed 4 Nov:**
  - 164.9 wide
  - 124.2 over the corner tabs
  - 8.0 deep
  - the tab size

**Print**
- [ ] Plate 03 first: test one M5 insert in a Ø6.4 hole.
- [ ] Then the rest of `01_PRINT_FILES/1_PRINT-NOW/`; `2_CHECK-UPS-FIRST/` once the UPS checks out; `3_WAIT/` once measured / tested.

**Build**
- [ ] **Rack:** heat-set the inserts, then stack and screw the sides (2U base, 3U, 3U, 1U top), the base bars, the cap and the handles.
- [ ] **Pi unit:**
  1. Fit the UPS tray on the shelf.
  2. Screw the Poly+ 5 tray on with 3 × M3 × 12 (before the case).
  3. Fit the case and the F holder; run the UPS OUT lead through the right channel (over the UPS's edge at the joint post) and up the tray's lead hole to the terminal; fit the faceplate.
- [ ] **Brick:** strap it in the cradle with the 8 mm spacer. Lead out through the faceplate notch into the UPS DC-IN.
- [ ] **Rack the units bottom-up:** Pi, dock, screen, then the UCG mount. Plug the gateway in before racking it.

**Later**
- [ ] Decide what the 5 × WeAct e-paper + 5 × ESP32-C3 are for.
