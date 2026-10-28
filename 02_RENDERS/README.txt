FINAL BUILD renders (28 Oct 2026): what ../01_PRINT_FILES builds. RE-RENDERED 28 Oct evening (ultrareview) on this Mac
(Blender 5.2.3, Cycles on the GPU), from the honest scene:
- the adapter (F) holder base with its new HDMI plug relief (W2, 28 Oct)
- THE CLEAN FRONT (second pass, 28 Oct): the faceplate has no DC-IN window and no notch. The brick's 12 V lead stays behind it:
  right-angle extension plug in the UPS DC-IN, along the shelf floor, through the arch in the shelf's right gusset, into the
  brick cradle's open front, where it joins the brick's plug; the brick's spare lead is coiled beside the join (08, 16).
  The UPS OUT lead goes over the UPS edge at the joint post as before: the routes the checks pass.
- the cable riser runs tight against the right-hand side (x -110), behind the dock's and screen's ears; straight on (03)
  no cable shows
- the UCG-Ultra's display is drawn where Ubiquiti's front view has it (18.5 mm up, under the mount's window; it was drawn
  3.5 mm too low before) The 16 renders made before this by another tool showed a
  'hidden' route that runs through the UPS tray, and a right-angle DC-IN plug the brick doesn't have (old ones in ../ULTRAREVIEW/before/)
- NEW: every other cable (group 'rack_cables' from ../04_DESIGN_SOURCE/9_scripts_28Oct/verify_wiring_all.py): flat HDMI and
  micro-USB to the screen, USB-C to the B1, Cat6 (blue) to the UCG-Ultra, the UCG's USB-C power. 17 = side panel off, 18 = from the back
- 00_HOMELAB_RACK_ENGINEERING_SCHEMATIC.png: View C redrawn with measured depths (the brick cradle doesn't fit the 140 mm rack)
- The turntable / exploded GIF + MP4 were made by another tool from its own scene before the review: they show its lead route
  and the old holder; not re-made.


Colours: PLA parts silver (rack, handles, cap, base bars, B1 dock + ears, screen module + clips), PETG parts black
(Pi shelf, UPS tray, DC-notch faceplate, Poly+ 5 tray, adapter (F) holder, brick cradle + 8 mm spacer, UCG mount).

What's new against the 27 Oct renders:
- the DC-notch faceplate (8 x 9 mm notch in its bottom edge)
- the plate 13 cradle with the Robu 12 V brick (110 x 50 x 30), its C13 mains plug and cord out of the back
- the brick's 12 V lead: along the cradle, out through the notch, into the UPS DC-IN window
- the right-angle plug in the UPS OUT (rack rear) and its 4 mm lead to the adapter (F)'s screw terminal
  (right channel, over the UPS's edge at the joint post, front pocket, the tray's lead hole, the holder's front notch:
  the route checked in ../03_CHECKS/VERIFICATION_pi-unit_power-path+side-ports_28Oct.txt)
- 15: the plug in the UPS OUT, seen from the rear (tray, case, holder lid and faceplate hidden)
- 16: the same cutaway from above the front: the whole lead route

Seen from the front, the brick bay is on the LEFT of the Pi unit.
The adapter holder is drawn in place, but it only gets printed if the fit test passes (see ../01_PRINT_FILES/README.md).

Stand-ins, not measurements: the Argon Poly+ 5 (seller size), the adapter (F)'s parts other than the PCB, holes,
RJ45 and HDMI-A, the cables, and the UPS's jacks. The brick's plug is drawn at the centre of the DC-IN window, where the
tray and faceplate windows expect the jack. The UPS CAD model has its DC-IN elsewhere; check the real unit.

01-04 whole rack · 05-09 Pi unit (09 = holder lid off) · 10-11 B1 dock · 12 screen · 13-14 UCG-Ultra mount ·
15-16 power path · 17-18 wiring. FINAL_sheet.png = all of them on one page. Pi5_MiniRack_FINAL_studio.blend = the scene.

Rebuild (source/): export_final.py <rack source> <4_Pi_Unit_2U> <scene out> <UCG mesh dir> <Argon folder>
                   <brick_cradle.py dir> <DC-notch faceplate STEP>
                   then (wiring) python verify_wiring_all.py <scene out> <rack source> <report> <wired scene>
                   copy screen_ui.png + ucg_ui.png into the wired scene folder
                   then blender -b --python build_final.py -- <wired scene> <render out> final
                   then python make_sheet_final.py <render out>
