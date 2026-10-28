# rework-01: what was fixed, and what's left to do (27 Oct 2026)

`rework-01/` is a working copy of the project (v7.2) where the paperwork has been corrected. **The printed parts (every STL and STEP) are unchanged.** The originals in the project root are untouched, so you can compare the two.

---

## 1. Fixed: the folder itself

The first copy of `rework-01` went wrong. The project was copied into itself, so `rework-01` held `rework-01/rework-01/…` **102 levels deep**, 21 GB of duplicates, until the path got too long for macOS. `rework-01.tar.xz` in the root (442 MB) was an archive of that copy, stopped part-way. xz reports "Unexpected end of input", so it can't be fully extracted.

- Checked first: all 42,421 nested files matched the top level by path and size. Nothing unique was in them.
- **Moved to the Trash, not deleted:**
  - `~/.Trash/rework-01_recursive-copy_nested_2026-10-27`
  - `~/.Trash/rework-01_truncated_2026-10-27.tar.xz`
- `rework-01/` is now one clean copy (258 MB).
- [ ] **Empty the Trash when you're happy.** It gives back about 21.5 GB.
- **Next time you copy:** run it from the parent folder, so the copy doesn't land inside what it's copying:
  `ditto "Pi 5 HomeLab 1" "Pi 5 HomeLab 1 - rework-02"`
  To archive, wait until the copy has finished, then run:
  `tar -cJf rework-02.tar.xz "Pi 5 HomeLab 1 - rework-02"`

## 2. Fixed: the design files (in `Pi5-MiniRack_v7.2_ALL-FILES_2026-10-27/` here)

| Problem found | Fix |
|---|---|
| **The BOM had none of the Pi unit's screws.** They were only in its README, so the BOM bought 10 M3 × 8 countersunk where 16 are needed, and no M3 × 12 or M2.5 screws at all. | The Hardware tab has a new **Pi unit** column. The BOM has new rows for M3 × 12 countersunk (buy 5), M2.5 × 8 (buy 10) and M2.5 × 10 (buy 10). M3 × 8 countersunk is now 16 needed (buy 20), and M3 inserts 18 needed. |
| **M5 inserts:** the BOM pointed to the Probots "M5/M6 90 pcs" kit. It's **mixed M5 + M6 in various lengths**, and its M5 hole guide is **6.8–7.2 mm**. The rack's 48 holes are **Ø6.4 × 10 mm**. | The BOM, START_HERE and the rack README now say: buy 50+ M5 only, made for a Ø6.4 mm hole, 8–10 mm long. The print plan says what to change (`INS_D`) if your inserts need a different hole. |
| **Flat HDMI 0.5 m is too short.** From the adapter's HDMI at the back of the Pi unit to the screen's side socket is ~45–52 cm, which is the same route that already made the screen's USB cable 1 m. | 1 m flat HDMI in the BOM, START_HERE and the screen README. |
| **Cat6 0.5 m is too short.** From the gateway's rear ports at the top down to the Pi's 2.5G port is ~45 cm. | A 1 m slim Cat6 in the BOM and START_HERE. |
| A BOM note said the screen gets its own 5 V 2 A supply. That's wrong since it moved to a Pi USB port. | Replaced: the screen and B1 run from the Pi's USB, so **set `usb_max_current_enable=1`**. The Pi is fed through the adapter (F), so it limits its USB ports to 600 mA in total. This is now in the screen and Pi unit READMEs too. |
| Other stale BOM text: | All updated: |
| – a driver board and screen tray that no longer exist | – foam tape and zip ties: what they're really for |
| – "PETG: skip if the Pi unit is already printed", though the UCG shelf needs PETG | – the PETG line now says ~0.1 kg is still needed for the UCG shelf |
| – an old NVMe price | – the NVMe note uses your cart price |
| – the HDMI-socket question for the old screen | – the screen note describes the (C) type |
| – "≈ g each (PETG)" on a mostly PLA list | – the column header just says "≈ g each" |
| – ~40 h of printing, against the plan's 45 h | – both say ~45 h |
| – washers "buy 25" while the docs said 20 | – washers: 16 needed, buy 20, matching the docs |
| Screen README: | Screen README: |
| – it still said it "replaces" the module "from the v7 bundle" | – the intro describes this module as the current one |
| – it pointed at an old **8U** rack check | – it points to the current 39-PASS check |
| – that old 8U check file sat next to the current ones | – the file is moved to `3_Display_7in_3U/docs/OLD_v7.1-8U_…` |
| Pi unit README: the UGREEN HDMI extender steps read as required, but the BOM buys none (it's only for a second screen). | The steps are marked optional. |
| Rack README: "plates 1–7 and 12" (plate 12 is the UCG shelf). | "Plates 1–7". |

**Money:**
- Still to spend is now **₹47,142** (was ₹47,022).
- Build hardware is ₹2,034 (was ₹1,964).
- DIY ≈ ₹5,400 and paid ≈ ₹16,800, as before.

**Checks re-run on the files in this folder:**
- rack: **39 PASS**
- UCG shelf: **15 PASS**
- B1 dock: **24 PASS**
- screen: **23 PASS**
- 0 FAIL in all four, with output identical to the shipped `VERIFICATION_*.txt`

The zip in this folder was rebuilt from the corrected files.

---

## 3. To do

### Orders: before you order on Wed 28 Oct
- [ ] **Fix the Amazon cart:**
  - **Remove:** the Tobo USB-C→DC 20 V cable (never connect it to the UPS), the 5×20 fuse holders, the blade-fuse kit and the 16 AWG wire.
  - **Swap:** the 0.5 m flat HDMI pack → a **1 m flat HDMI** cable.
  - **Add:** the 12 V ≥ 3 A plug-in adapter (5.5 × 2.1, centre +; e.g. Mean Well GST60A12-P1J), a 1 m USB-A → micro-USB cable and a 32 GB microSD card.
- [ ] **Cancel only the Mean Well LRS-150-12 line on order #3781408.** Don't press the whole-order "Cancel Order". If you can't cancel the line, return it when it arrives.
- [ ] **Order the rest from the BOM** (the "Have it?" column shows what's left):
  - the UCG-Ultra (₹17,949, B0D8PSW2BZ) + a **1 m slim Cat6**
  - **50+ M5 heat-set inserts for a Ø6.4 mm hole, 8–10 mm long.** Check the listing states the hole size.
  - 55 × M5 × 12 button head, 20 × M5 washers
  - M3 inserts (25), M3 × 8 countersunk (20), M3 × 8 button head (10)
  - **new:** M3 × 12 countersunk (5), M2.5 × 8 (10), M2.5 × 10 (10)
  - rubber feet, 1 mm double-sided foam tape
  - filament: 2 × PLA, 1 × PETG
- [ ] Check the 12 V adapter price. ₹2,477 is from earlier research, not a live listing.
- [ ] Your Google Calendar "Pi rack: …" reminders still list the 0.5 m HDMI cable and the M5/M6 kit. Update them if you rely on them.

### Decisions only you can make
- [ ] **The rack tips forward too easily at the top.**
  - About **5 N** pushed on the back of the UCG-Ultra tips the loaded rack forward, and an RJ45 plug can take up to 20 N to seat.
  - This is the one real design weakness left; the docs only work around it ("plug in before racking").
  - Options, with figures from the rack check's own tipping calculation:
    - **A. Fix the rack to the desk** (two screws or a hook-and-loop strip under the rear foot pads). It can't tip at all, there's no reprint, and it costs almost nothing.
    - **B. A ballast tray** hung between the middle and rear base bars, holding ~2 kg of steel (e.g. flat bar or washers).
      - ~**11–12 N** to tip at the gateway (about 2.5× today) and ~26 N for a label pull. It can't reach 20 N without ~4 kg.
      - Needs a small new printed part and a re-run of `verify_rack_t0.py`.
    - **C. Leave it.** Always plug the gateway in with its shelf out, or with a hand on the rack.
  - *Recommendation:* A if your desk allows it; otherwise B. Tell me which, and B can be designed and checked in `rework-01`.
- [x] **12 V cable at the front: solved 27 Oct with a new print.**
  - The brick goes inside the rack, in a cradle in the empty bay right of the Pi unit: `PRINT_THIS/13_PETG_12V-brick-cradle/`. It drops onto the middle and rear base bars with no screws. Its mains cord goes out the back.
  - The 12 V lead goes out through a notch in the bottom edge of the Pi faceplate, `PRINT_THIS/11_…/Plate11_WITH-DC-notch.3mf`, then ~2 cm across into the DC-IN window.
  - Checks: 42 PASS for the cradle (against v7.2 and the dock v5 here), and 39 PASS on the full rack check with the notched faceplate.
  - [ ] When promoting to v7.3: put `13_PETG_12V-brick-cradle/source/` into the bundle (the cradle and the notched faceplate). Then add plate 13 to `PRINT_PLAN_P1S.md` and the BOM: 2 hook-and-loop straps, ~0.08 kg PETG.
- [ ] **Fri 30 Oct: decide what the 5 × WeAct e-paper + 5 × ESP32-C3 are for.** They aren't part of the rack yet.

### Measure
- [x] ~~Wed 28 Oct: the NIIMBOT B1's thickness.~~ **Settled 27 Oct:** the official manual gives 132 × 91 × 62 mm. Dock v5 (in `2_B1_Dock_3U/` here) is built around the real B1 from the user's photos, with no spacers: 22 PASS dock, 38 PASS rack. **The dock is now a printable change in rework-01, so promote it as v7.3.**
- [ ] **When the inserts arrive:** print plate 3 first and set one M5 insert in a rail hole and a joint boss.
  - If it's loose or bulges the wall, change `INS_D` in `1_Rack_9U_T0-look/source/rack_t0.py` and re-export before printing the rest.
- [ ] **Wed 4 Nov, when the screen arrives:** before printing its module, measure the four numbers in `3_Display_7in_3U/README.md`:
  - 165 wide
  - 124.2 over the tabs
  - 8.0 deep
  - the tab size

### Print (P1S, `PRINT_PLAN_P1S.md`)
- [ ] Plate 3 first (insert test), then plates 1, 2 and 4–7 (rack, PLA, lid open).
- [ ] Plate 12: UCG shelf (PETG, enclosure closed, add a brim if the plate is worn).
- [ ] Plates 10–11: Pi unit (PETG).
- [ ] Plate 8: B1 dock v5.
- [ ] Plate 9: screen module, after measuring the screen.

### Build
- [ ] Inserts, then the sides (2U base, 3U, 3U, 1U top), the base bars, the cap, the handles and the feet.
- [ ] **Pi unit** (`4_Pi_Unit_2U/README.md`):
  - [ ] Check by eye where the adapter (F)'s 12 V screw terminal sits; it isn't in the 3D model.
  - [ ] **Check polarity** on the UPS OUT → terminal lead before switching on.
  - [ ] Feed the adapter from the UPS **or** PoE, not both. The UCG-Ultra's ports don't supply PoE, so the Cat6 to it is safe.
- [ ] Dock (B1 open slide on top, lid end on the right) and screen module.
- [ ] Rack the units bottom-up: Pi, B1 dock, screen, UCG shelf.
  - **Plug the gateway's cables in before racking its shelf** (or do option A or B above first).

### First power-up (software)
- [ ] Boot from the microSD (the adapter (F) isn't a HAT+), enable NVMe/PCIe boot, then copy the OS to the NVMe.
- [ ] Add `usb_max_current_enable=1` to `/boot/firmware/config.txt`, so the screen and the charging B1 get enough USB current.
- [ ] Check the screen's touch, the B1 over USB (niimprint), and the 2.5G link to the UCG-Ultra.

### Finish the rework
- [ ] When you're happy with `rework-01`:
  - move the root's current v7.2 folder and zip into `_Old_versions/`
  - move `rework-01`'s folder and zip up to the root (rename them v7.3 if anything printable changes, e.g. a ballast tray)
  - copy `rework-01/START_HERE.md` over the root one
- [ ] If option B is chosen: design the tray, re-run the four checks, update the print plan, the BOM, `VISUALS/` and the 3D page (https://claude.ai/artifact/9pqgvvRfigWwcD8ecrPeBo).

---

## Known limits (already accepted, nothing to do unless you want them)
- **HATs:** no HAT fits under the Pi unit's lid with the Armor Lite fitted. A 5–10 mm lid riser would fix it, and the rack has 14 mm of headroom.
- **UGREEN extender:** whether its micro-HDMI plug reaches the Pi's free port with the adapter fitted is unverified. It only matters if you add a second display.
- **Checks:** every check is a calculation on 3D models, not a physical test. The tipping figures especially depend on the assumed unit weights.
