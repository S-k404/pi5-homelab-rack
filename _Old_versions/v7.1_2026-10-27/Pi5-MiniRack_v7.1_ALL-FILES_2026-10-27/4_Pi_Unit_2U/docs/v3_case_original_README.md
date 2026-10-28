# Pi 5 + Waveshare Adapter (F) + Cuzor MiniUPS PRO — v3 (stacked, compact)

The case is 118 × 114 × 71 mm. The old v2 was 211 × 114 × 39 mm. Every part fits a 120 × 120 mm bed.

## Print (PETG, 0.2 mm, 3 walls, 20 % infill, no supports)
| File | Orientation |
|---|---|
| `Pi5_UPS_v3_ups_tray.stl` | Floor down |
| `Pi5_UPS_v3_board_tray.stl` | Floor down |
| `Pi5_UPS_v3_lid.stl` | Upside down (top face on bed) |
| `Pi5_UPS_v3_shims.stl` | 4 each of 0.5, 1 and 2 mm |

## Airflow
- A **5.5 mm gap** separates the top of the UPS from the board tray. Air enters it from slots in the left wall and from the open front and back. This keeps Pi heat away from the battery cells.
- A **12 mm channel** on the right of the UPS has wall and floor slots, and also carries the 12 V lead.
- **Floor slots under the Pi and the adapter** connect to that gap, so air can rise past the boards.
- On top, there is a **hex grill over the fan**, slots over the SSD, and exhaust slots at the back. The side and back walls of the board tray have slots too.

## UPS
- Its switch, LED and OUT face the front window, so you can reach them.
- DC-IN is at the back, under the overhang. The adapter plug goes straight in.
- OUT uses a right-angle 5.5×2.1 plug. The lead goes into the right channel, out the back window, and up through the floor hole of the board tray. From there it follows the cable-tie anchors to the screw terminal.
- **Check polarity before connecting the terminal.**

## Hardware
- UPS tray to board tray: 3× M3×12 countersunk screws, driven down from inside the board tray. Fit these before the boards.
- Pi: 4× M2.5×8 screws, self-tapping into 2.2 mm pilots. Alternatively, drill the pilots to 3.6 mm and use M2.5 heat-set inserts.
- Adapter: 4× M2.5×10 screws and shims (see step 4).
- Lid: 2× M3×8 countersunk screws at the back. Two teeth at the front hook into pockets in the front wall.
- Double-sided foam tape under the UPS, on the ribs, to stop it rattling.

## Assembly
1. Stick foam tape on the ribs and put the UPS in the bottom tray with the switch end on the right. Switch it ON.
2. Set the board tray on top and fit the 3 joint screws.
3. Screw down the Pi, then fit the Armor Lite.
4. Adapter:
   - Plug it fully into the Pi.
   - Slide shims under each hole until each one just touches the board without lifting it (expect about 1–3 mm).
   - Mark each spot through the hole. Remove the adapter and drill a 2.0 mm pilot into the solid pad at each mark.
   - Refit the adapter and screw it down. The pads are solid, so wherever the plugs put the board you can drill.
5. Connect the FFC, the SSD and the 12 V lead.
6. Hook the lid's front teeth in, lower it and fit the 2 back screws.

## Checks run
- Pi 5 official STEP: 0 clashes with any part.
- Adapter: no clash across the full drill-pad area and shim range.
- UPS: fits up to 101 × 81 × 28.5 mm. A unit 1.5 mm larger than that does clash, which confirms the check works.
- Adapter plugs line up with the Pi sockets: HDMI 0.25 mm off, USB-C 0.05 mm off.

## Assumptions
- Positions of the UPS switch, LED, OUT and IN are taken from product photos, with large windows to cover any error.
- The Armor Lite is assumed to be 16.5 mm tall or less. The lid gives 3.7 mm of margin above that.
