> **⚠ 28 Oct 2026, read first:** the print list for your build (Argon Poly+ 5 + F holder, 12-ALT2 UCG mount, plate 13, DC-notch faceplate) is **`FINAL_PRINTS_2026-10-28/`** in the project root, re-checked today. The "v7.3 final" hidden-slit / switch faceplate and the switch extender (plate 14) **do not work** (the Cuzor switch faces the rack rear; the brick-lead notch was lost). They were moved to `_superseded_and_alternatives/BROKEN_antigravity-faceplate+switch-extender_2026-10-28/`, and plates 11 / 11B use the DC-notch faceplate again. Plate counts below: one 3U module per plate (4 in all), one ear on plates 06 and 07 (4 in all); plate 04 is ≈128 g.

# Pi 5 HomeLab Mini Rack: Complete Documentation (v7.3 Antigravity Final)

A custom **10-inch 9U desktop mini rack** engineered in the DeskPi RackMate T0 aesthetic, inspired by Jeff Geerling's Mini Rack project. It fits on a Bambu Lab P1S (256 × 256 mm bed).

---

## 1. Specifications & Rack Layout

- **Width:** 280 mm overall (standard 10-inch EIA-310 spacing: 236.525 mm hole pitch, 224 mm clear width)
- **Depth:** 200 mm
- **Height:** 9U (approx. 430 mm with cap and feet)

```
+------------------------------------------+  Top Cap & Handles
|  1U: UniFi Cloud Gateway Ultra (UCG)     |  Mount with 3 Keystone RJ45 slots
+------------------------------------------+
|  3U: 7" Capacitive Touch HDMI Display    |  Waveshare / REES52 7" (C) module
+------------------------------------------+
|  3U: NIIMBOT B1 Label Printer Dock       |  Dock v5 (swings open to load paper)
+------------------------------------------+
|  2U: Pi 5 Server + UPS Unit              |  Pi 5 8GB, Active Cooler, Waveshare (F),
|                                          |  NVMe SSD, Cuzor UPS, Hidden Cable Slit
+------------------------------------------+  Plinth & Rubber Feet
```

---

## 2. Power Architecture & Cable Management

- **Power In:** Plug-in **12 V ≥ 3 A** AC/DC power brick (5.5 × 2.1 mm center-positive barrel plug).
- **Internal Brick Placement:** The brick sits securely inside the empty right bay on the bottom plinth in the **Plate 13 Cradle**, with its mains cord exiting the rear of the rack.
- **Hidden UPS-to-Board Cable Slit:**
  - The 12 V power lead from the UPS OUT barrel plug routes directly into an internal channel on the rear of the faceplate (`x = 97..106 mm`, `z = 4..38 mm`, 2.5 mm depth).
  - The cable travels up inside the channel behind the solid 1.5 mm faceplate wall and passes straight into the board tray floor hole directly to the Waveshare 7–24 V screw terminal.
  - **Zero visible wire on the front panel!**
- **Front-Panel UPS ON/OFF Switch Access:**
  - Dedicated beveled opening on the faceplate (`16 × 11 mm` with 2.5 mm radius) aligned with the Cuzor switch at `x = 62.6 mm, z = 13.0 mm`.
  - Includes a custom 3D-printed **Switch Extender** that snaps over the switch nub and slides smoothly between ON and OFF with tactile front grip ridges.
- **Peripherals:**
  - The 7" touch display and NIIMBOT B1 printer run directly off the Raspberry Pi 5 USB ports.
  - Set `usb_max_current_enable=1` in `/boot/firmware/config.txt` to unlock full 1.6 A USB current.

---

## 3. Assembly Sequence

1. **Insert Heat-Set Nuts:**
   - Press M5 inserts (Ø6.4 mm) into rack side modules and base bar corners.
   - Press M3 inserts (Ø4.0 mm) into the Pi shelf posts and front lip.
2. **Assemble Frame:**
   - Stack side modules (2U base → 3U → 3U → 1U top) and screw together with base bars, rear stops, and top cap.
3. **Pi Unit Assembly:**
   - Apply foam tape to the UPS tray ribs, set the Cuzor UPS in place.
   - Snap the switch extender onto the UPS switch lever.
   - Fasten board tray to UPS tray using 3 × M3 × 12 mm countersunk screws from inside.
   - Install Raspberry Pi 5 with Active Cooler, attach Waveshare Adapter (F) and NVMe SSD.
   - Plug the right-angle DC lead into UPS OUT, route cable up through the hidden internal slit, and fasten to the Waveshare 7–24 V screw terminal.
   - Fasten lid with 2 × M3 × 8 mm screws.
   - Secure the unit onto the shelf standoffs (pins locate the bottom holes).
   - Fasten the front faceplate with 6 × M3 × 8 mm screws, guiding the switch extender into its front bezel.
4. **Dock, Display & Gateway:**
   - Slide NIIMBOT B1 into Dock v5.
   - Mount 7" display in Display7C frame with 4 clips.
   - Place UCG-Ultra into the 1U mount.
   - Mount all units into rack rails with M5 × 12 mm screws and washers.

