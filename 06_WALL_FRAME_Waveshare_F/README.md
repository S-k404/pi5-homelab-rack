# Wall frame for the Waveshare Pi5 Connector Adapter (F) (8 Nov 2026)

A standalone frame that hangs on the wall like a picture. Hang it landscape, with the plug edge down. It is two prints: a box (the back plate and walls) and a front frame.

| | |
|---|---|
| Size | 104.3 × 72.5 mm, 30.6 mm deep when assembled |
| Print | PETG, 0.20 mm (Bambu "0.20mm Standard"), 3 walls, 20 % gyroid, **no supports**, textured PEI. Print both parts flat side down, as the STLs are saved: the box on its back, the front on its underside. Both fit on one plate. About 30 g + 10 g. |
| Board | 4 × M2.5 screws, 5–10 mm long (the ones in the adapter's box). They self-tap into 2.1 mm pilots. |
| Front frame | 4 × **M3 × 12 countersunk** (the OnlyScrews pack). They self-tap into 2.5 mm pilots in the corner columns. |
| Wall | 2 keyholes **28.0 mm apart**, on one level line. Screw shank ≤ 4.0 mm, head ≤ 9 mm across and ≤ 2.8 mm tall. Leave the underside of each head **2–3 mm** off the wall (anything from 1.8 to 3.2 mm works), hook the frame over both heads, then let it drop 8 mm. |

## Openings
- **Left side (ports end):** HDMI, RJ45 and the PWR rod. The jack faces sit about 0.5 mm proud of the wall. The opening also takes an HDMI plug moulding if the jack turns out to sit 1 mm back.
- **Bottom slot (x 27–80):** the 16-pin FFC cable to the Pi, the micro-HDMI and USB-C plugs, and the 3-pin socket. The cable is 100 mm long, so the Pi has to sit within about 8 cm below the frame.
- **Right side notch:** the 7–24 V wires. The green plug-in terminal slides out through this notch, so you can unplug it without opening the frame. Its screws are under the front frame, so wire it before you fit the front.
- **Top wall:** vent slots. Air comes in at the bottom slot and leaves at the top and through the window.

The adapter isn't plugged into the Pi here, so its USB-C and micro-HDMI plugs aren't connected to anything. Power the Pi on its own, and use the Pi's own micro-HDMI port for the screen.

![On the wall](renders/1_on_the_wall.png)

![Exploded](renders/4_exploded.png)

The renders are made in Blender. They show the board as simple shapes in the drawing's positions and colours, not Waveshare's real model. `renders/` also has the ports side, the terminal side and the back with the keyholes. To turn it round yourself, open `WallFrame_F_scene.blend` in Blender.

## Fit order
1. Plug the FFC into the adapter. If you're using an SSD, fit it now too.
2. Lower the board into the box, jacks first into the side opening. Fix it with the 4 M2.5 screws.
3. Wire the green terminal plug and push it home. Feed the FFC down through the bottom slot.
4. Fit the front frame with the 4 M3 × 12 countersunk screws.
5. Fit two wall screws 28.0 mm apart, level, with the head undersides 2–3 mm off the wall. Hang the frame and let it drop.

## Files
- `STL_for_printing/`: the two STLs to print. Next to them are **STEP files of the same two parts in the same print position**. These are exported from the exact CAD model, not converted from the mesh, so holes and fillets are true curves. `checks/STEP_vs_STL.txt` confirms the STL vertices lie within 0.001 mm of the STEP surface, with the same volume.
- `STEP_for_Onshape/`: the same two parts in their assembled position.

## Clearance check of the STEP files (8 Nov)
`checks/CLEARANCES_from_STEP.txt`: **41 PASS, 0 FAIL**.
- The delivered STEP files are read back from disk and moved into place. Moved, they are the identical solid to the assembled STEPs (0.0000 mm³ difference).
- They're then measured with exact OpenCASCADE distances against every board part, all the screws and the cable plug and lead spaces.
- The tightest real gaps:
  - Board edge to the left wall stub: 0.40 mm.
  - Terminal to the right wall: 1.12 mm.
  - USB-C plug to the bottom wall: 1.28 mm.
  - RJ45 top to the front frame: 1.50 mm.
  - Estimated pin tails under the board to a post: 0.30 mm.

`checks/CLEARANCE_SCHEMATIC.pdf` (and `.png`) is a dimensioned drawing with gaps in red:
- **A:** the front view, laid over Waveshare's own drawing and registered on the hole centres.
- **B–F:** five sections through the STEP files, at the RJ45, the HDMI and terminal, the USB-C plug and bottom slot, a keyhole with its wall screw, and the front screws.

**Fix that came out of this check:** the head pocket behind each keyhole was only 3.2 mm deep. That only took a head standing 1.8–2.2 mm off the wall, not the 2.5–3 mm this README used to say. It's now 4.2 mm deep, and the neck is 4.6 mm wide.

## Checks (8 Nov, on the CAD models, not a physical test)
`checks/VERIFICATION_wall_frame.txt`: **29 PASS, 0 FAIL**. It covers:
- The board, all its parts, the plugs and the pin tails underneath: none of them touch the box or the front.
- The RJ45 and HDMI cable plugs fit whether the jack faces stand 3.3 mm (as drawn) or only 1.0 mm past the board.
- The terminal plug slides out through the right notch.
- The FFC and leads have a clear path out of the bottom slot.
- The screws' grip in their pilots, and the keyhole fit.
- Both STLs are watertight, sit flat on the bed and need no supports. The widest bridge is 9.6 mm, the roof over each keyhole.
- Measured off the STL files themselves: board posts 58.01 × 46.50, keyholes 28.00 apart, and the front's screw holes within 0.01 mm of the box's pilots.

The first check run caught an HDMI plug moulding catching the side opening by 0.2 mm, so the opening was widened 0.6 mm.

## Board dimensions (checked 8 Nov)
`checks/DIMENSIONS_adapter_F.txt` has the details.
- The drawing (`source/waveshare_F_drawing.png`) was measured by pixel analysis relative to the four hole centres.
- It was cross-checked against waveshare.com's 86.0 × 52.5 mm and against the Raspberry Pi 5 mechanical drawing (`source/raspberry-pi-5-mechanical-drawing.pdf`). The adapter's plugs have to land on the Pi's USB-C and micro-HDMI 0, which are 14.6 mm apart.
- The drawing is good to about ±0.3 mm. The holes are Ø2.8–3.0, so they take M2.5 screws, not M2.
- The check moved four numbers: the terminal end (97.6 → 97.9), the HDMI span, the plug tips (−6.2 → −6.4) and the jack faces (3.5 → 3.3). The frame was given more room at the terminal end and the plug edge, and grew 0.7 × 0.4 mm.

## Not verified (needs the real board)
- Part heights. The drawing is a top view, so the RJ45 at 13.5 mm and the terminal at about 12 mm are estimates. There's 15 mm of clearance above the board.
- What the PWR rod is for, and its height.
- How it prints: no test print has been made. Check the board fits the box before you fit the front frame.

## Rebuilding
From `source/`:
1. `uv run --python 3.12 --with cadquery --with trimesh --with numpy --with scipy python waveshare_f_wall_frame.py <out>`
2. `uv run --python 3.12 --with cadquery --with trimesh --with numpy --with scipy --with networkx --with shapely --with rtree python verify_wall_frame.py <out> <report.txt>`
3. Renders: `uv run --python 3.12 --with cadquery python export_render_meshes.py <out>`, then `/Applications/Blender.app/Contents/MacOS/Blender -b -P render_wall_frame.py -- <out>`. This writes `<out>/renders/` and the `.blend`.
4. Print-position STEPs and their match with the STLs: `python export_print_step.py <out>/STL_for_printing <report.txt>` (same `uv run --with ...` as step 2).
5. Clearance check and schematic: `python step_clearance_check.py <out>/STL_for_printing <out>/STEP_for_Onshape waveshare_F_drawing.png <dir>` (add `--with matplotlib --with pillow`).

All the sizes are knobs at the top of `waveshare_f_wall_frame.py`. For example, `JACK_FACE_X` if your jacks sit differently, `BORDER` for the frame width, `KEY_X` for the keyhole spacing, and `LABEL` (an empty string drops the engraving).
