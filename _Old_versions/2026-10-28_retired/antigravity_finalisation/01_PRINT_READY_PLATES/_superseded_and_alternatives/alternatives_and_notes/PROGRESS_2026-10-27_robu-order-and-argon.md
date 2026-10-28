# Progress: Robu print order + Argon Poly+ 5 change (27 Oct 2026)

**Taking over? Start with `HANDOFF_FOR_NEXT_AGENT.md` (next steps, Robu automation tips, file map).** Status when saved: the print order is in the Robu cart (17 lines, ₹6,702), not checked out; the user answered "Not yet" to re-adding the hardware.

Saved mid-session. **Nothing has been checked out or paid for.** Everything below is in the Robu cart only.

## 1. Robu print-service cart: current state (audited from the cart page)
Robu's print service can't share a cart with normal items, so the cart was cleared and holds print jobs only. **17 lines, 32 units, ₹6,702** (the 15 lines below at ₹6,421, plus the Waveshare holder base ₹192 and lid ₹89 added later the same day). Every line was checked from the cart page for file, material, infill, qty and price (unit × qty = line total on all 17; the sum matches the subtotal).

| Part | Qty | Setup | Unit ₹ | Line ₹ |
|---|---|---|---|---|
| Rack_SideModule_2U_Base | 2 | PLA silver, 15% | 352 | 704 |
| Rack_SideModule_3U | 4 | PLA silver, 15% | 377 | 1,508 |
| Rack_SideModule_1U_Top | 2 | PLA silver, 15% | 206 | 412 |
| Rack_CapHalf | 2 | PLA silver, 15% | 412 | 824 |
| Rack_Handle | 2 | PLA silver, 20% | 113 | 226 |
| Rack_BaseBar | 3 | PLA silver, 15% | 73 | 219 |
| B1_Dock_3U_Ear | 4 | PLA silver, 15% | 34 | 136 |
| Display7C_Clip | 4 | PLA silver, 30% | 30 | 120 |
| B1_Dock_3U_Body (v5, `08_PLA_B1-dock/`) | 1 | PLA silver, 15% | 601 | 601 |
| Pi5_UPS_v3_ups_tray_pinned | 1 | PETG black, 20% | 296 | 296 |
| Rack_Shelf_pinned | 1 | PETG black, 20% | 384 | 384 |
| Rack_Faceplate_2U_10in | 1 | PETG black, 20% | 222 | 222 |
| Pi5_UPS_v3_shims | 1 | PETG black, 90% | 30 | 30 |
| **UCG-Ultra 1U mount, 3 keystones** (ALT2, Printables 942972) | 1 | PETG black, 15% | 587 | 587 |
| **Pi5_ArgonPoly5_tray** (plate 11B) | 1 | PETG black, 20% | 152 | 152 |
| **Waveshare_F_holder_base** (11B-SIDE) | 1 | PETG black, 20% | 192 | 192 |
| **Waveshare_F_holder_lid** (11B-SIDE) | 1 | PETG black, 20% | 89 | 89 |

Changes made today after the first audit (₹6,578, 16 lines):
- **UCG shelf swapped** (user's choice): plate 12 shelf (₹472) removed; the ready-made ALT2 mount (₹587) added at the user's 15% infill (its SETTINGS.txt says 20%). Its file note says "for your own printing only: don't re-share the file".
- **Argon Poly+ 5 change**: the standard board tray (₹302) and lid (₹122) removed; the Argon Poly+ 5 tray (₹152) added. The faceplate is the same file in both designs, so it stays.

Not in the order on purpose: the screen module body (`Display7C_3U_Body`, waits for the screen to arrive 4 Nov), the old B1 dock and spacers (obsolete), plate 13 (no STL yet).

Mistakes caught on the way: (a) 3U modules, 1U tops and cap halves were first added at 70% infill (wrong option code), then removed and re-added at 15%; (b) the cart tab froze on a native "delete?" dialog once, so the first UCG delete never happened; it was redone with the dialog stubbed.

## 2. Argon Poly+ 5 (user bought it: black, THRML heatsink/fan inside)
Per `ALT_Pi-unit_Argon-cases+coolers/README.md`, the Pi unit is **plate 10 + plate 11B instead of plate 11**.
- **WARNING: plate 11B is marked "WAIT: measure the case first".** The tray fits a case up to 96.0 × 66.5 mm; the listed size is 93.5 × 64 × 30 mm and sellers warn of 0–1 cm error. It is in the cart, but **don't check out the Argon tray line until the case has arrived and been measured.** If the case is bigger than 96 × 66.5, the pocket has to be widened.
- **Adapter (F) can't be used inside this case.** That loses the NVMe SSD, the 2.5G PoE port and the 12 V screw terminal. Boot from microSD or a USB SSD; use the Pi's own 1G Ethernet.
- **Power:** UPS 12 V OUT → right-angle DC pigtail → 12 V → 5 V 5 A USB-C step-down converter → Pi USB-C (keeps battery backup), or the official 27 W supply (no backup).
- **Screen HDMI:** the UGREEN 20134 micro-HDMI extender is now **required** (Amazon).
- **Cooler:** not needed; the Armor Lite V5 (₹859) and the Official Active Cooler (₹519) are dropped from the lists.
- Affected purchases outside this cart: the EVM 512 GB 2230 NVMe (₹9,999, Amazon cart) and the Waveshare adapter (F) (already ordered, #3781408) have no place in the Poly+ 5 build as designed.

## 3. Hardware list to re-add after the print order is checked out
`ROBU_HARDWARE_CART_TO_RESTORE.md`: updated, 13 lines, ₹15,083 (Armor Lite V5 dropped). Still to source: a 12 V → 5 V 5 A **USB-C** step-down (not confirmed on Robu).

## 4. Waveshare adapter (F) holder beside the Poly+ 5: DONE, in the Robu print cart (base ₹192 + lid ₹89, PETG black 20%, qty 1 each; not checked out)
Robu's configurator measured the uploaded files at 10.26 × 5.60 × 2.58 cm (base) and 10.26 × 5.60 × 1.73 cm (lid), which match the STLs. Estimated print time 2 h 06 min (base) and 57 min (lid).
The user confirmed: a standalone holder, styled like the Poly+ 5 (black, grooved lid, vent window), NVMe / 2.5G / HDMI 0 / 12 V terminal reachable at the rear.
- Files: `ALT_Pi-unit_Argon-cases+coolers/11B-SIDE_PETG_Waveshare-F-holder_beside-Poly+5/` (`Waveshare_F_holder_base.stl`, `Waveshare_F_holder_lid.stl`, SETTINGS.txt, README.md, three renders). STEP in `STEP_for_Onshape/`, source in `source/waveshare_f_holder.py`, checks in `checks/VERIFICATION_waveshare_f_holder.txt` (25 PASS, 0 FAIL).
- Built from Waveshare's dimension drawing (PCB 85 × 52.5, holes 58 × 46.5, port centres). Everything else on the board (M.2, FFC, terminal, plugs, tall parts) was read off the drawing image and is an estimate.
- It sits on the Argon tray's free left area, straddling the tray's rims; 56 × 102.6 mm, top at z 65.7. PETG ≈ 19 g + 12 g. Hardware: 4 × M2.5 × 25 pan-head screws (new; they replace the 4 × M2.5 × 10 + shims).
- **Things that don't match what the user asked for** (told to the user; they are facts about the board and case):
  - The 12 V terminal is at the **front** end of the board and faces forward, not the rear. The lead enters the front notch.
  - The adapter's plugs (5.5 mm) can't reach the Pi's ports through the case wall (1.2 mm short of a 64 mm case), so HDMI 0 and Pi power don't work through it. Use the UGREEN extender and the 12 V → 5 V converter.
  - NVMe + 2.5G run over the 16-pin FFC; how the FFC leaves the Poly+ 5 is unknown until the case arrives.
- Not printed or fitted anywhere; no prototype.

## 5. Next steps
1. ~~Add the holder (base + lid) to the Robu print cart~~ done (see section 4). Remove those two lines if you'd rather print the holder on the P1S.
2. After the user checks out the print order, re-add the hardware from `ROBU_HARDWARE_CART_TO_RESTORE.md` (that file now lists the 4 × M2.5 × 25 screws for the holder).
3. When the Poly+ 5 and the adapter arrive: measure the case (plate 11B waits on it), the side wall, port heights and the adapter's real layout; compare with the holder's README.
4. Update the main READMEs / BOM for the Poly+ 5 build (they still describe the bare-board design).
