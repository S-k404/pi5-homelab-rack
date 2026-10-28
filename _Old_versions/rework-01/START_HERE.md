# Pi 5 HomeLab: start here (27 Oct 2026)

> **This is the rework-01 copy.** Its BOM and docs are corrected (the printed parts are unchanged). **`REWORK-01_TODO.md`** lists what was fixed and everything still to do.

**The current design is v7.2:** `Pi5-MiniRack_v7.2_ALL-FILES_2026-10-27/`. Open its `START_HERE.md`. Everything you need to print, buy and build is in that folder, and `Pi5-MiniRack_v7.2_ALL-FILES_2026-10-27.zip` is the same folder zipped.

v7.2 is a 9U rack. From the bottom: Pi 5 + UPS (2U), NIIMBOT B1 dock (3U), 7" touch screen (3U), and a UniFi UCG-Ultra shelf (1U) on top.

| You want | Open |
|---|---|
| What to print, plate by plate, on the P1S | `Pi5-MiniRack_v7.2_ALL-FILES_2026-10-27/PRINT_PLAN_P1S.md` |
| Print files | `STL_for_printing/` inside each unit folder (`1_Rack…`, `2_B1_Dock…`, `3_Display…`, `4_Pi_Unit…`, `5_UCG-Ultra…`) |
| What to buy, with prices | `Pi5-MiniRack_v7.2_ALL-FILES_2026-10-27/BOM_Pi5-MiniRack_v7.2.xlsx` (₹47,142 still to spend, of which ₹17,949 is the UCG-Ultra) |
| Interactive 3D view | https://claude.ai/artifact/9pqgvvRfigWwcD8ecrPeBo (private to your claude.ai account) |
| Older versions | `_Old_versions/`. Don't print from these. |

**Printing at a glance (Bambu P1S):**
- 12 plates.
- PLA ≈ 1.29 kg (buy 2 spools); PETG ≈ 0.41 kg (1 spool).
- Cost doing it yourself ≈ ₹5,400; paying an experienced person ≈ ₹16,800.

## Decided (27 Oct)
- **12 V power: a plug-in adapter instead of the Mean Well LRS-150-12.**
  - **What to get:** 12 V, **3 A or more** (5 A preferred), 5.5 × 2.1 mm plug, centre positive. For example the Mean Well GST60A12-P1J (12 V 5 A). It takes a standard PC-style (IEC C13) mains cord with an Indian plug.
  - **How it connects:** it plugs straight into the UPS DC-IN, so there's no mains wiring, no fuse kit and no rear panel.
- **No power strip in the rack.** The 12 V adapter (UPS) and the UCG-Ultra's own power adapter go to wall sockets; the screen and the B1 run off the Pi's USB ports.
- **Cancel or return the LRS-150-12.** Order #3781408 only has a whole-order "Cancel Order" button, which would also cancel the Pi 5 and the adapter. Ask the seller to cancel just that line, or return it when it arrives.

## To do
The dated items are also on your Google Calendar as all-day "Pi rack: …" reminders.

**Orders**
- [ ] **Tue 27 Oct: fix the Amazon cart before ordering.**
  - **Remove:** the Tobo USB-C→DC adapter (20 V, never connect it to the UPS), the ERH 5×20 PCB fuse holders, the CoolShef blade-fuse kit and the 16 AWG wire. The Pi 27 W supply and the Portronics charger are optional.
  - **Keep:** the 90° DC pigtails. You only need one (UPS OUT → adapter); the second is a spare, because the seller's minimum is 2.
  - **Swap:** the 0.5 m flat HDMI pack for a **1 m** flat HDMI cable (the route to the screen is ~45–52 cm).
  - **Add:** the plug-in 12 V adapter (see "Decided" above), a 1 m USB-A to micro-USB cable and a 32 GB microSD card.
- [ ] **Wed 28 Oct: cancel ONLY the Mean Well LRS-150-12 on order #3781408.** Don't press "Cancel Order", which cancels the whole order. Ask the seller to cancel that line, or return it when it arrives.
- [ ] **Wed 28 Oct: order what isn't in the cart yet** (the BOM's "Have it?" column shows what's left):
  - UniFi UCG-Ultra, ₹17,949 (Amazon.in B0D8PSW2BZ) + a **1 m** slim Cat6 patch cable
  - **50+ M5 heat-set inserts made for a Ø6.4 mm hole, 8–10 mm long** (not the Probots mixed M5/M6 kit), 55 × M5 × 12 button-head screws, 20 × M5 washers, plus the M3 inserts and the M3 / M2.5 screws on the BOM's Hardware tab (it now includes the Pi unit's screws)
  - filament: 2 × 1 kg PLA (silver or grey; black for the cap if you want two-tone) and 1 × 1 kg PETG

**Measure**
- [ ] **Wed 28 Oct: measure the NIIMBOT B1's thickness.** At about 62 mm, also print the two 5 mm spacers; at about 67 mm, print the dock as it is.
- [ ] **Wed 4 Nov, when the screen arrives:** before printing its module, measure the four numbers in `3_Display_7in_3U/README.md`: 165 wide, 124.2 over the corner tabs, 8.0 deep, and the tab size.

**Print (P1S, see `PRINT_PLAN_P1S.md`)**
- [ ] **From Sun 1 Nov, when the filament arrives:** print the rack plates (1–7) and the UCG shelf (plate 12, PETG). These don't depend on any measurements.
- [ ] Plates 10–11: the Pi unit (PETG).
- [ ] Plate 8: the B1 dock, after measuring the B1.
- [ ] Plate 9: the screen module, after measuring the screen on 4 Nov.

**Build**
- [ ] Heat-set inserts, then stack and screw the sides (2U base, 3U, 3U, 1U top), the base bars, the cap and the handles.
- [ ] Build the Pi unit (`4_Pi_Unit_2U/README.md`), the dock and the screen module.
- [ ] Rack the units bottom-up: Pi, B1 dock, screen, then the UCG shelf. **Plug the gateway's cables in before you rack its shelf:** about 5 N on its back tips the rack forward.

**Later**
- [ ] **Fri 30 Oct: decide what the 5 × WeAct e-paper + 5 × ESP32-C3 are for.** They're not part of the rack yet; say what they're for and they can be designed in.
