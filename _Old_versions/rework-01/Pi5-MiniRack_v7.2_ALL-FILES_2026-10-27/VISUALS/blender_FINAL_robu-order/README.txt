FINAL BUILD renders (27 Oct 2026): what the Robu print order (17 lines, Rs 6,702) builds.

Colours as ordered: every PLA part silver (rack, handles, cap, base bars, B1 dock body + ears, screen clips),
every PETG part black (Pi shelf, UPS tray, faceplate, Argon Poly+ 5 tray, adapter (F) holder base + lid,
UCG-Ultra mount from Printables 942972). The screen module body is shown in PLA silver too; it isn't ordered yet
(it waits for the screen, due 4 Nov).

Not in the picture: the 12 V brick (no plate 13 cradle or DC-notch faceplate in the order, so it sits outside),
the UPS shims (ordered, but the holder doesn't use them), the 12 V -> 5 V USB-C converter and all cables.

Stand-ins, not measurements: the Argon Poly+ 5 (seller size 93.5 x 64 x 30, ports placed from the Pi 5 drawing,
top styled like the holder), and the adapter (F)'s parts other than the PCB, holes, RJ45 and HDMI-A.

01-04 whole rack · 05-09 Pi unit (09 = holder lid off) · 10-11 B1 dock · 12 screen · 13-14 UCG-Ultra mount
FINAL_sheet.png = all of them on one page. Pi5_MiniRack_FINAL_studio.blend = the scene, one camera per shot.

Rebuild: source/export_final.py <rack source> <4_Pi_Unit_2U> <scene out> <UCG mesh dir> <PRINT_THIS/ALT_Pi-unit_Argon-cases+coolers>
         then blender -b --python source/build_final.py -- <scene out> <render out> final
