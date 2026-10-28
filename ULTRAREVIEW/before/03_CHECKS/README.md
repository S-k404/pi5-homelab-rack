# Check reports (28 Oct 2026)

All of these are calculations on the 3D models, not physical tests. The print files they cover are in `../01_PRINT_FILES/`; the scripts are in `../04_DESIGN_SOURCE/`.

| Report | What it checks | Result |
|---|---|---|
| `VERIFICATION_pi-unit_power-path+side-ports_28Oct.txt` | The right-angle plug in the UPS OUT, the lead to the adapter (F) terminal, the brick plug, and the Pi's side ports with the F holder in place | Plug + 4 mm lead fit. Notes: 0.5 mm under the plug; lift the lead over the UPS edge at the joint post. **The holder blocks the side ports** (hence the fit test). The UPS model's DC-IN position doesn't match the windows (check the real UPS) |
| `VERIFICATION_brick-cradle_with_Poly5-build_42PASS.txt` | Brick cradle, spacers, six brick sizes, mains plug, 12 V lead route through the faceplate notch, tipping, against this Pi unit | 42 PASS |
| `VERIFICATION_rack_with_Poly5-tray+DC-notch-faceplate_38PASS.txt` | Whole rack with every unit: collisions, ear slots, cap clearance, panel stiffness, tipping | 38 PASS |
| `VERIFICATION_waveshare_F_holder_25PASS.txt` | Adapter (F) holder: the board, notches, tray fit | 25 PASS |
| `VERIFICATION_UCG-mount_12-ALT2_8PASS-1WARN_27Oct.txt` | Printables 942972 UCG mount in the rack | 8 PASS, 1 WARN (rear plugs) |
| `VERIFICATION_Argon-trays_27Oct.txt` | Poly+ 5 / NEO 5 trays | 29 PASS |
| `VERIFICATION_B1-dock-v5_27Oct.txt` | B1 dock v5 | 22 PASS |
| `VERIFICATION_screen-module_27Oct.txt` | Display7C screen module | 23 PASS |
| `MEASUREMENTS_every_part.md` | Every print file: size, one watertight body, flat on the bed, fits the bed, weight, byte-identical to its checked source | all pass |
| `PLATES_3MF_audit.txt` | Every P1S plate read back: parts identified, on the bed, quantities match the list | all pass |
| `AUDIT_antigravity-faceplate_why-it-was-dropped.txt` | Why the "v7.3 final" switch-window faceplate and switch extender were retired | broken |
