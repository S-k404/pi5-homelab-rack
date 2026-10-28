# Check reports (28 Oct 2026; ultrareview additions in the evening)

All of these are calculations on the 3D models, not physical tests. The print files they cover are in `../01_PRINT_FILES/`; the scripts are in `../04_DESIGN_SOURCE/`.

| Report | What it checks | Result |
|---|---|---|
| `VERIFICATION_wiring_all-cables_28Oct.txt` | **Every cable** in the rack: HDMI, micro-USB, USB-C to the B1, Cat6, the gateway's power and its plugs vs the mount (port positions from Ubiquiti's rear view), **the brick's 12 V lead behind the faceplate** (right-angle DC-IN plug, extension through the shelf's gusset arch, the join and coil in the cradle; nothing in front of the faceplate), the USB and UPS power budgets | 26 PASS, 1 FAIL (a 0.5 m Cat6 would be too short: buy 1 m), 2 WARN (a 5.5 mm lead would be tight in the gusset arch, the real one is 4 mm; USB budget ~1.3–1.5 A of 1.6 A) |
| `VERIFICATION_slim-cargo_fit_28Oct.txt` | The 28 Oct build in the Slim Cargo 140 mm rack: depth, collisions, what the Pi shelf and the brick cradle stand on | 5 PASS, 3 FAIL: **the 12 V brick cradle doesn't fit** (187 mm long, hits the slim bars). The four units fit |
| `VERIFICATION_pi-unit_power-path+side-ports_28Oct.txt` | The right-angle plug in the UPS OUT, the lead to the adapter (F) terminal, the brick plug, and the Pi's side ports with the F holder in place | Plug + 4 mm lead fit. Notes: 0.5 mm under the plug; lift the lead over the UPS edge at the joint post. **The holder blocks the side ports** (hence the fit test). The UPS model's DC-IN position doesn't match the windows (check the real UPS) |
| `VERIFICATION_brick-cradle_with_Poly5-build_42PASS.txt` | Brick cradle, spacers, six brick sizes, mains plug, 12 V lead route through the faceplate notch, tipping, against this Pi unit | 42 PASS. **Its 12 V lead section is for the notch faceplate, replaced on 28 Oct** by the clean front: the lead now stays behind the faceplate (checked in the wiring report) |
| `VERIFICATION_rack_with_Poly5-tray+DC-notch-faceplate_38PASS.txt` | Whole rack with every unit: collisions, ear slots, cap clearance, panel stiffness, tipping | 38 PASS |
| `VERIFICATION_waveshare_F_holder_26PASS.txt` | Adapter (F) holder: the board, notches, tray fit, and (new 28 Oct) the HDMI and RJ45 **plugs** pushed home | 26 PASS (the old holder failed the HDMI plug test: 147 mm³; its rear wall now has a 23 mm relief) |
| `VERIFICATION_UCG-mount_12-ALT2_8PASS-1WARN_27Oct.txt` | Printables 942972 UCG mount in the rack | 8 PASS, 1 WARN (rear plugs) |
| `VERIFICATION_Argon-trays_27Oct.txt` | Poly+ 5 / NEO 5 trays | 29 PASS |
| `VERIFICATION_B1-dock-v5_27Oct.txt` | B1 dock v5 | 22 PASS |
| `VERIFICATION_screen-module_27Oct.txt` | Display7C screen module | 23 PASS |
| `MEASUREMENTS_every_part.md` | Every print file: size, one watertight body, flat on the bed, fits the bed, weight, byte-identical to its checked source | all pass |
| `PLATES_3MF_audit.txt` | Every P1S plate read back: parts identified, on the bed, quantities match the list | all pass |
| `AUDIT_antigravity-faceplate_why-it-was-dropped.txt` | Why the "v7.3 final" switch-window faceplate and switch extender were retired | broken |

**28 Oct, ultrareview:** the power-path script in `04_DESIGN_SOURCE/9_scripts_28Oct/` had been edited by another tool after this report (a 9 × 9 × 6 mm "compact" plug and a lead route "hidden under the tray"). That version fails its own check: the 3.5 mm lead runs 18 mm³ into the UPS tray and 9 mm³ into the brick's plug. The original script was put back; re-run, it gives this report line for line. Details: `../ULTRAREVIEW/README.md`.
