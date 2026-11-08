# Wall frame for the Waveshare Pi5 Connector Adapter (F) (8 Nov 2026)

A standalone frame that hangs on the wall like a picture. Hang it landscape, with the plug edge down. It is two prints: a box (the back plate and walls) and a front frame.

| | |
|---|---|
| Size | 103.6 × 72.1 mm, 30.6 mm deep when assembled |
| Print | PETG, 0.20 mm, 3 walls, 20 % gyroid, **no supports**. Print both parts flat side down, as the STLs are saved. Both fit on one plate. About 45 g + 13 g. |
| Board | 4 × M2.5 screws, 5–10 mm long (the ones in the adapter's box). They self-tap into 2.1 mm pilots. |
| Front frame | 4 × **M3 × 12 countersunk** (the OnlyScrews pack). They self-tap into 2.5 mm pilots in the corner columns. |
| Wall | 2 keyholes **28.0 mm apart**, on one level line. Screw shank ≤ 4.2 mm, head ≤ 9 mm across and ≤ 3 mm tall. Leave the head standing **2.5–3 mm** off the wall, hook the frame over both heads, then let it drop 8 mm. |

## Openings
- **Left side (ports end):** HDMI, RJ45 and the PWR rod. The jack faces sit about 0.7 mm proud of the wall. The opening also takes an HDMI plug moulding if the jack turns out to sit 1 mm back.
- **Bottom slot (x 27–80):** the 16-pin FFC cable to the Pi, the micro-HDMI and USB-C plugs, and the 3-pin socket. The cable is 100 mm long, so the Pi has to sit within about 8 cm below the frame.
- **Right side notch:** the 7–24 V wires. The green plug-in terminal slides out through this notch, so you can unplug it without opening the frame. Its screws are under the front frame, so wire it before you fit the front.
- **Top wall:** vent slots. Air comes in at the bottom slot and leaves at the top and through the window.

The adapter isn't plugged into the Pi here, so its USB-C and micro-HDMI plugs aren't connected to anything. Power the Pi on its own, and use the Pi's own micro-HDMI port for the screen.

## Not checked
- All board dimensions come from Waveshare's drawing (`source/waveshare_F_drawing.png`). Several part heights are estimates: the RJ45 at 13.5 mm and the terminal at about 12 mm. There's 15 mm of clearance above the board.
- The full collision and overhang checks used for the old holder weren't run on this frame, and no test print has been made. Check the board fits the box before you fit the front frame.

Rebuild: `uv run --python 3.12 --with cadquery python source/waveshare_f_wall_frame.py <out>`
