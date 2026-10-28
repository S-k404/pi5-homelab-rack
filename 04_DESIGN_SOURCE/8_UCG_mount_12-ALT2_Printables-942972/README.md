# Ready-made prints from Jeff Geerling's mini-rack list (27 Oct 2026)

These are community designs, from [mini-rack.jeffgeerling.com](https://mini-rack.jeffgeerling.com/) or found while checking it. A design gets into this folder only if it suits **your** rack: one Pi 5 with the adapter (F) and the UPS, the B1, the Waveshare 7" (C) and the UCG-Ultra, in the 9U T0-look frame.

**Status (27 Oct): one file downloaded, checked and filed as `12-ALT2`.** The other candidate was skipped because it wasn't downloaded. Your original download stays untouched in `_downloads/`. To add another design, drop it into `_downloads/` and Claude will check and file it the same way.

## Worth printing (alternatives to plate 12)
Both hold the UCG-Ultra in the top 1U slot, in place of your own `12_PETG_UCG-Ultra-shelf`. Pick one, or keep plate 12. Yours has only been checked on the computer, while these have been printed by many people.

| Folder | Design | Download from | Status |
|---|---|---|---|
| **`12-ALT2_PETG_UCG-Ultra-1U-3-keystones_Printables-942972`** | UniFi Cloud Gateway Ultra 10" rackmount, 1U, with 3 keystone slots | [printables.com/model/942972](https://www.printables.com/model/942972-unifi-cloud-gateway-ultra-10-rackmount) | **Checked, ready to print:** 8 PASS, 0 FAIL, 1 WARN (see below) |
| `12-ALT1_PETG_UCG-Ultra-1U_MakerWorld-783611` | Unofficial 10-inch mount for UCG-Ultra / UCG-Max / UXG-Max (V2, Nov 2024; 4.9★ from 92 ratings) | [makerworld.com/models/783611](https://makerworld.com/models/783611) | **Skipped:** not downloaded |

### 12-ALT2: check results (`12-ALT2_…/checks/VERIFICATION_ucg_option2.txt`)
- **Ear slots:** they sit on your M5 rail inserts, within 0.26 mm of the EIA positions. Fix it with 4 × M5 × 12 + washers, like plate 12.
- **Fit in the rack:** no collisions with the rack, the screen module below or the cap. The tray ends 133 mm behind the rails, so the cables have room.
- **Gateway fit:** the UCG-Ultra fits with 0.75 mm each side. The floor, the panel, the side walls and a rear stop locate it (2.2 mm of play). The display window is centred across the gateway's face.
- **One change made for your rack:**
  - As downloaded, the panel is a full 44.45 mm and **touches the cap (0.00 mm gap)**.
  - The print file has **0.8 mm taken off the top**, so it's a standard 43.65 mm 1U panel with 0.8 mm under the cap. The ear slots haven't moved.
  - The 3 keystone holders (separate pieces in the download) are joined to the panel, and 2 junk surfaces were removed.
- **WARN, check the rear plugs on the real gateway:**
  - A 3 mm lip runs across the back, 10 mm above the floor, 2 mm behind the gateway.
  - A corner post covers the last 14 mm of the gateway's back on the right (seen from the front).
  - Plug the RJ45 and USB-C cables in before racking. If one hits, ask Claude to cut that part down.
- **Print:** PETG, panel face down, 136 mm tall, about 120 g, supports off. It's placed at 45° on the plate so a brim fits. Details are in `SETTINGS.txt`.

**Licence:** these files are for your own printing. Don't re-share them, and keep them out of the project zip if you send that to anyone.

## Looked at and left out
| Design | Why not |
|---|---|
| Printable rack frames: Lab Rax, HomeRacker, Mod10, MiniRax, bwees, rackstack… | You chose the T0 look, and every unit is built for that frame. The Pi unit's shelf also rests on your rack's base bars, so another frame would need a new support for it. |
| DeskPi 2 × Pi 5 tray, Pi Slice Rack, other Pi 5 mounts | Bare boards only: no room for the adapter (F) or the Cuzor UPS. You have one Pi, already in plates 10–11. |
| Argon NEO 5 1U mounts ([MakerWorld 2889139](https://makerworld.com/en/models/2889139-10-1u-rack-mount-for-raspberry-argon-neo-5), [Printables 1463834](https://www.printables.com/model/1463834-neo5x2-and-neo5-nvme-10-rack-mount)) | They need a 10th U and have no room for the UPS. If you do use a NEO 5, use `../ALT_Pi-unit_Argon-cases+coolers/` (11A) instead. |
| Printables 1658909 (UCG-Ultra/Max, split in 3 parts) | Split for small beds and needs M3 inserts. The P1S prints the one-piece mounts above. |
| Lab Rax UCG-Max 1U mount (MakerWorld 2113543) | Made for the Lab Rax frame. |
| DeskPi 7" touch-screen case (Model 19), the 19-inch 3U panel for the 7" (C) | Wrong screen, or wrong rack width. Keep plate 09. |
| Anything for the NIIMBOT B1 | There's no 10-inch rack mount for it. Keep plate 08. |
| Blanking or vent panels, cable combs | All 9U are used, and the back is open. |
