# FINAL PRINTS (28 Oct 2026): everything you need to print, and nothing else

**This folder is the print list.** It's for the build you chose on 28 Oct:
- the v7.2 9U rack
- B1 dock v5
- the 7" screen module
- the Pi in the **Argon Poly+ 5**, with the **Waveshare adapter (F) holder** beside it (**the holder waits for a fit test**, see below)
- the **Printables 942972 UCG-Ultra mount (12-ALT2)**
- the **12 V brick cradle (plate 13)**
- the **DC-notch faceplate**

Every file is a copy of the one the checks ran on (md5 compared). See `checks/`.

**Each STL holds ONE part.** The `__x4__` in a name means "print or order 4 of this file". Material: PLA = silver, PETG = black, as in your Robu order.

**Which side is which:** seen from the **front**, the brick bay is on the **left** of the Pi unit, and the Poly+ 5 sits left of the adapter holder. The older notes say "right of the Pi unit": that's the Pi unit's own frame, which faces the rack rear.

## 1. Order or print now (`1_ORDER-NOW/`, 15 files, 30 parts)
| # | File | Qty | Material · infill (Robu) | Size on the bed, mm | ≈ g each | What it is |
|---|---|---|---|---|---|---|
| 01 | `01_Rack_SideModule_2U_Base__x2__PLA.stl` | 2 | PLA silver · 15 % | 200 × 108.9 × 40 | 93 | rack: bottom side modules |
| 02 | `02_Rack_SideModule_3U__x4__PLA.stl` | 4 | PLA silver · 15 % | 200 × 136.4 × 28 | 104 | rack: 3U side modules |
| 03 | `03_Rack_SideModule_1U_Top__x2__PLA.stl` | 2 | PLA silver · 15 % | 200 × 47.5 × 28 | 50 | rack: 1U top side modules |
| 04 | `04_Rack_CapHalf__x2__PLA.stl` | 2 | PLA silver · 15 % | 147.8 × 200 × 30 | 96 | rack: vented cap halves |
| 05 | `05_Rack_Handle__x2__PLA.stl` | 2 | PLA silver · 20 % | 172 × 45 × 14 | 36 | rack: U handles |
| 06 | `06_Rack_BaseBar__x3__PLA.stl` | 3 | PLA silver · 15 % | 165.7 × 165.7 × 11 | 21 | rack: base bars |
| 07 | `07_Unit_Ear_3U__x4__PLA.stl` | 4 | PLA silver · 15 % | 28 × 132.6 × 3 | 10 | ears: 2 for the dock + 2 for the screen module |
| 08 | `08_Display7C_Clip__x4__PLA.stl` | 4 | PLA silver · 30 % | 20 × 9 × 3 | 1 | screen-module corner clips |
| 09 | `09_B1_Dock_v5_Body__x1__PLA.stl` | 1 | PLA silver · 15 % | 214 × 95 × 130 | 120 | B1 dock v5 (real B1, 132 × 91 × 62) |
| 10 | `10_Pi_Rack_Shelf_pinned__x1__PETG.stl` | 1 | PETG black · 20 % | 170.1 × 116.7 × 68 | 96 | Pi unit: shelf |
| 11 | `11_Pi_UPS_Tray_pinned__x1__PETG.stl` | 1 | PETG black · 20 % | 118.3 × 91.4 × 36.5 | 62 | Pi unit: Cuzor UPS tray (see "UPS jacks" below) |
| 12 | `12_Pi_Faceplate_2U_DC-notch__x1__PETG.stl` | 1 | PETG black · 20 % | 254 × 88.1 × 4 | 64 | Pi unit: faceplate, 8 × 9 mm notch for the brick's 12 V lead |
| 13 | `13_Brick_Cradle_12V__x1__PETG.stl` | 1 | PETG black · 20 % | 43.3 × 187.4 × 35.4 | 63 | 12 V brick cradle, in the bay beside the Pi unit |
| 14 | `14_Brick_Spacer_8mm__x1__PETG.stl` | 1 | PETG black · 20 % | 110 × 31.6 × 10.4 | 17 | spacer for Robu's 30 mm thick brick |
| 15 | `15_UCG-Ultra_1U_Mount_Printables-942972__x1__PETG.stl` | 1 | PETG black · 15 % | 254 × 43.7 × 136 (panel face down) | 117 | UCG-Ultra mount, 3 keystones. For your own use only: don't re-share this file |

## 2. Wait (`2_WAIT_measure-first/`)
| File | Qty | Material | ≈ g | Wait for |
|---|---|---|---|---|
| `W1_Argon_Poly5_Tray__x1__PETG__WAIT-measure-case.stl` | 1 | PETG black · 20 % | 43 | **The Poly+ 5 case.** The tray takes up to **96.0 long × 66.5 wide**; listings say 93.5 × 64 × 30 (± 1 cm). Bigger: don't print |
| `W3_Waveshare_F_Holder_Base__x1__PETG__WAIT-test-fit.stl` | 1 | PETG black · 20 % | 35 | **The fit test below** (the case and the adapter in hand) |
| `W4_Waveshare_F_Holder_Lid__x1__PETG__WAIT-test-fit.stl` | 1 | PETG black · 20 % | 17 | same |
| `W2_Display7C_3U_Body__x1__PLA__WAIT-measure-screen.stl` | 1 | PLA silver · 15 % | 71 | **The screen (4 Nov).** Check 164.9 wide, 124.2 over the corner tabs, 8.0 deep, and the tab size |

### Why the holder waits: the fit test
The holder puts the adapter (F)'s own USB-C and micro-HDMI plugs in line with the Pi's side ports, 3–5 mm from the case. **Nothing else fits in that gap**, so the step-down converter's USB-C and the UGREEN micro-HDMI plug can't go in while the holder is there. The check shows ~740–1,170 mm³ of holder inside each port's 32 mm plug space.

So the holder only works if the adapter plugs **straight into the Pi through the Poly+ 5's side cut-outs**.
- **Test:**
  1. Put the Pi in the Poly+ 5 and close it.
  2. Hold the adapter flat beside it, plug edge towards the case, and push its USB-C and micro-HDMI into the cut-outs.
  3. Both must click fully home (≈ 6 mm in) with the adapter level.
  4. Also check that the 16-pin FFC can leave the case.
- **Passes:**
  - print W3 + W4
  - power everything through the UPS OUT → adapter terminal lead (below)
  - you don't need the step-down converter or the UGREEN extender
  - NVMe, 2.5G and the adapter's HDMI all work
- **Fails:** don't print the holder. Power the Pi with a 12 V → 5 V 5 A USB-C step-down from the UPS OUT, and use the UGREEN extender for HDMI.
  - The side ports then have 32 mm free (checked 27 Oct).
  - You lose the NVMe and the 2.5G port.

## 3. Optional (`3_OPTIONAL/`)
The cradle needs one spacer that suits the brick's thickness. The 8 mm one is for 29–30.5 mm. Print one of these instead **only if your brick measures** 30.5–32.5 (6 mm), 32.5–34.5 (4 mm) or 34.5–36.5 (2 mm). 36.5–38.2 mm needs no spacer.

## Pi unit power: UPS OUT plug and the lead to the Waveshare terminal (checked 28 Oct)
The Waveshare adapter (F) takes 12 V on a **screw terminal**, so the lead is a right-angle 5.5 × 2.1 **plug** in the UPS OUT with bare wires at the other end. See `checks/VERIFICATION_pi-unit_power-path+side-ports_28Oct.txt`, and renders 15 and 16.

| Check | Result |
|---|---|
| **Right-angle plug** (11 × 12 overmould, 16 mm deep) in the UPS OUT, through the UPS tray's rear window | **fits**, 17.9 mm each side. Only **0.5 mm** under it, for a jack at the model's height: if yours sits lower or the plug is fatter, file the window's bottom edge |
| **Plug + strain relief**, cable out sideways | touches nothing; sticks out 13 mm behind the case into the open rack rear |
| **Route:** OUT (rear) → the right-hand channel beside the UPS → front window → pocket behind the faceplate, under the tray → the tray's 12 × 8 lead hole → the holder's front notch → terminal | **a 4 mm lead fits (≈ 24 cm, so get a 30 cm pigtail)**. A 5.5 mm lead just touches the holder notch's edge |
| **Pinch** in the channel at the M3 joint post (x 107.7, y 40) | only 2.95 mm either side. **Lift the lead over the UPS's top edge there**, into the 5.5 mm air gap under the tray floor |
| **The brick's plug** in DC-IN | the lead clears it |
| **Tray lead hole** | takes two 4 mm leads (terminal + converter) |
| **Terminal** | wire entries face the holder's front notch; screws on top, so lid off to wire it. **Check polarity** (+ to + on the terminal) |

**UPS jacks: check yours before plates 10 and 11** (the UPS tray and the faceplate):
- **Cuzor publish no drawing.** Their page gives 10 × 8 × 2.8 cm (the tray takes up to 101 × 81 × 28.5), a **slide** switch (0/1, not a rocker) and IN/OUT 5.5 × 2.1 jacks.
- **The tray and faceplate windows assume** the switch, LED and OUT on the face towards the **rack rear** (window x 58–110), and **DC-IN at the right-hand end of the face towards the faceplate** (window x 80–112).
- **The CAD model of the UPS has its DC-IN at the other end** (x 14.6), behind solid wall.
- **One marketplace listing says 10.2 cm long:** 1 mm too long for the tray.

Look at a photo of the real unit (or the unit itself) before the UPS tray and faceplate go to print.

## Robu print cart: what to change (vs the 27 Oct audit: 17 lines, ₹6,702)
I haven't looked at the cart today. These changes are against the 27 Oct audit in `PRINT_THIS/_superseded_and_alternatives/alternatives_and_notes/HANDOFF_FOR_NEXT_AGENT.md`.

| Cart line | Change |
|---|---|
| `Rack_Faceplate_2U_10in` (plain, ₹222) | **Replace** with `12_Pi_Faceplate_2U_DC-notch`. The plain faceplate blocks the brick's 12 V lead |
| `Pi5_UPS_v3_shims` (₹30) | **Remove**: the F holder doesn't use them |
| — | **Add** `13_Brick_Cradle_12V` + `14_Brick_Spacer_8mm` (PETG black, 20 %) |
| `Pi5_ArgonPoly5_tray` (₹152) | Keep, but **check out only once the case is measured** |
| `Waveshare_F_holder_base` (₹192) + `_lid` (₹89) | Keep, but **check out only after the fit test passes**. If it fails, remove them |
| `Pi5_UPS_v3_ups_tray_pinned`, `Rack_Faceplate…` | Check the UPS jack positions first (above) |
| the other 11 lines | correct as they are |
| later | `W2_Display7C_3U_Body` after 4 Nov |

## Printing it yourself on the P1S (`4_P1S_plates_3MF/`)
Every part is already placed on the 256 × 256 bed. Open the `.3mf`, load geometry only if asked, then slice. Each plate has its `_SETTINGS.txt` beside it.

| Plate | Contents | Material |
|---|---|---|
| 03 **first** | 3U module + 2 handles. Heat-set one M5 insert (Ø6.4 × 10 hole) before the other rack plates | PLA 0.24 |
| 01, 02, 04, 05, 06, 07 | rack sides, base bars, 1U tops, cap halves, 4 ears, 4 clips | PLA 0.24 |
| 08 | B1 dock v5 | PLA 0.20 |
| 10 | Pi shelf + UPS tray (no shims) | PETG 0.20 |
| 11 | DC-notch faceplate. **Brim off** (254 mm on a 256 mm bed) | PETG 0.20 |
| 12-ALT2 | UCG-Ultra mount, 45° on the plate | PETG 0.20 |
| 13 | cradle + all 4 spacers (delete the ones you don't need) | PETG 0.20 |
| 11W | **Wait:** Poly+ 5 tray (measure the case) + F holder base and lid (fit test) | PETG 0.20 |
| 09 | **Wait:** screen module body | PLA 0.20 |

**Filament:** PLA ≈ 1.19 kg now + 0.07 kg later, so 2 spools. PETG ≈ 0.42 kg now + 0.10 kg later (+ 0.04 kg for spare spacers), so 1 spool.

## Renders (28 Oct): `renders/`
**Re-rendered for this build:**
- DC-notch faceplate
- plate 13 cradle with the 110 × 50 × 30 brick, its mains plug and lead
- the right-angle plug in the UPS OUT and its lead to the terminal
- Poly+ 5 + holder
- 12-ALT2

**Two new shots:**
- **15:** from the rear, the plug in the UPS OUT
- **16:** a cutaway (tray, case and holder lid hidden) showing the whole lead route

**Earlier renders that are wrong:** the Antigravity renders (`../Pi 5 Mini Rack Renders/`, `../antigravity_finalisation/03_BLENDER_RENDERS/`).
- They show the broken switch-window faceplate, a "rocker switch", and a UPS moved 29.9 mm forward.
- They show no brick-lead notch.

**Stand-ins:** the Poly+ 5, the adapter's parts and the UPS jacks are modelled from listings, drawings and the CAD model, not measured.

## What was checked (28 Oct, on the 3D models, not a physical test)
| Check | Result | File in `checks/` |
|---|---|---|
| **Pi power path:** UPS OUT plug, lead to the terminal, side-port space | plug and 4 mm lead fit (with the over-the-UPS step at the joint post). **Side ports blocked by the holder** (hence the fit test) | `VERIFICATION_pi-unit_power-path+side-ports_28Oct.txt` |
| **Brick cradle** + spacers + lead route against this Pi unit (Poly+ 5 tray and case at max size, DC-notch faceplate) | **42 PASS** | `VERIFICATION_brick-cradle_with_Poly5-build_42PASS.txt` |
| **Full rack** with the Poly+ 5 tray + case + DC-notch faceplate | **38 PASS** | `VERIFICATION_rack_with_Poly5-tray+DC-notch-faceplate_38PASS.txt` |
| **Adapter (F) holder** (its own fit: board, notches, tray) | **25 PASS** | `VERIFICATION_waveshare_F_holder_25PASS.txt` |
| **UCG mount 12-ALT2** (27 Oct; same file) | 8 PASS, 1 WARN (rear plugs) | `VERIFICATION_UCG-mount_12-ALT2_8PASS-1WARN_27Oct.txt` |
| **Poly+ 5 tray, B1 dock v5, screen module** (27 Oct; same files) | 29, 22, 23 PASS | `VERIFICATION_Argon-trays…`, `…B1-dock-v5…`, `…screen-module…` |
| **Rebuilt from source today:** cradle, spacers, DC-notch faceplate, Poly+ 5 tray, F holder | byte-identical | (`source/`) |
| **Every STL:** one watertight body, flat, fits the bed, size, weight | all pass | `MEASUREMENTS_every_part.md` |
| **Every 3MF read back:** parts identified, on the bed, quantities match the list | 0 fail | `PLATES_3MF_audit.txt` |
| **The Antigravity faceplate and switch extender** | **broken, dropped** | `AUDIT_antigravity-faceplate_why-it-was-dropped.txt` |

**Key sizes, checked against the CAD:**
- **Rack:** 280 W × 200 D, 9U (400.05 mm), rail holes 236.525 apart, 224 mm clear, M5 insert holes Ø6.4 × 10.
- **Fitted units:**
  - B1: 132 × 91 × 62
  - UCG-Ultra: 141.8 × 127.6 × 30
  - Robu brick: 110 × 50 × 30
  - Poly+ 5 pocket: 96.0 × 66.5
  - Cuzor UPS: 100 × 80 × 28

## Bugs found and fixed on 28 Oct
1. **Antigravity's "v7.3 final" faceplate didn't work.**
   - **Switch window:** it has a window for the UPS switch on the front, but the Cuzor's switch, LED and OUT face the **rack rear**. Behind the window is the UPS tray's solid wall.
   - **Switch extender (plate 14):** it can't reach anything.
   - **"Hidden cable slit":** this cut only a 9 × 7 mm groove.
   - **Notch:** it also lost the brick-lead notch. Back to the checked DC-notch faceplate.
2. **The F holder blocks the Pi's side ports** in the Poly+ 5 build. The side-port check passed on 27 Oct before the holder existed, and was never re-run with it. The holder now waits for the fit test above.
3. **The old route for the UPS OUT lead ("through the right channel") was never modelled.**
   - The joint post in that channel leaves only 2.95 mm. The lead has to go over the UPS's edge there.
   - The OUT plug has only 0.5 mm under it in the window.
   - The UPS CAD model puts DC-IN where the windows don't expect it.
4. **The Antigravity docs** described the wrong Pi unit at first, the wrong UCG part, a rocker switch, and an "invisible" 12 V route.
5. **Wrong counts and weights:**
   - "x4" 3U modules per plate: it's 1 per plate, 4 in all.
   - "x2" ears on plates 06/07: it's 1 each.
   - Plate 04 ≈ 128 g, not 144.
   - F holder ≈ 35 + 17 g, not 19 + 12.

## Hardware this build needs
- **Not needed:**
  - Active Cooler, Armor Lite (the Poly+ 5 has the THRML)
  - 4 × M2.5 × 8 and 4 × M2.5 × 10 + shims (old board tray)
  - 2 of the 16 M3 × 8 countersunk (old lid), so **14**
- **Needed:**
  - **a 30 cm right-angle 5.5 × 2.1 pigtail with bare ends** (UPS OUT → terminal)
  - **4 × M2.5 × 25 pan-head** (if the holder passes)
  - 2 straps or zip ties for the brick
  - 3 × M3 × 12 countersunk (Poly+ 5 tray onto the UPS tray; fit them before the case, two end up under it)
  - the M5 hardware, M3 inserts and 6 faceplate screws as before
- **Only if the fit test fails:**
  - a 12 V → 5 V 5 A **USB-C** step-down (check it really has USB-C out)
  - the UGREEN 20134 micro-HDMI extender

## Check by hand when the parts arrive
- **Poly+ 5:**
  - its outline (≤ 96.0 × 66.5)
  - the **fit test** above
  - the FFC exit
- **UPS:**
  - which faces the IN and OUT jacks and the switch are on, and where along each face
  - its length (≤ 101)
- **UCG-Ultra:** plug its RJ45 and USB-C in, in the 12-ALT2 mount, before racking.
- **Tipping:** the rack tips forward at ~5.8 N on the back of the gateway. Fix it to the desk, or plug the gateway in before racking it.

## Rebuild
- **This folder:** `source/build_final.py <project root> <rework-01 v7.2 bundle> <new folder>`
- **The power-path check:** `source/verify_pi_power_path.py <v7.2 bundle> <Argon folder> <DC-notch faceplate STEP> <report>`. Run it from the Argon `source/` folder.
- **Renders:** `renders/source/`. See its README.
