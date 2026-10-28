# Pi 5 build — STEP models for Onshape

All units mm. Shared origin: Pi 5 PCB corner (USB-C/HDMI edge = Y0, GPIO edge = +Y, USB/Ethernet end = +X, PCB underside = Z0).

| File | Size (X × Y × Z) | Source / confidence |
|---|---|---|
| RaspberryPi5_8GB.step | 85 × 56 board; 89.1 × 57.2 × 18.8 overall | Board, holes, port centres: **Raspberry Pi drawing**. Connector bodies/heights: estimated |
| GeeekPi_ArmorLite_V5.step | 58 × 40 × 11 | Envelope: **52Pi listing**. Fin layout and 2 screw-hole positions: estimated |
| EVM_256GB_M2_2242_SATA.step | 42 × 22 × 3.85 | Envelope: **EVM spec**. PCB 0.8 (M.2 standard). Key notch positions: approximate |
| Cuzor_MiniUPS_Pro_12V3A.step | 100 × 80 × 28 | Envelope: **Cuzor Labs product page**. Jack/switch placement: estimated |
| Waveshare_Pi5_Connector_Adapter_F_PLACEHOLDER.step | 87.5 × 63.5 × 15.1 | **PLACEHOLDER.** Only the plug X-positions (they match the Pi's ports) are reliable |
| Pi5_build_layout_ASSEMBLY.step | everything positioned | Reference layout |

## Exact Pi 5 features (from the official drawing)
- Mounting holes Ø2.7 at (3.5, 3.5), (61.5, 3.5), (3.5, 52.5), (61.5, 52.5) — 58 × 49 pattern
- Bottom edge port centres: USB-C X=11.2, micro-HDMI0 X=25.8, micro-HDMI1 X=39.2
- Right edge port centres: Ethernet Y=10.2, USB Y=29.1 and Y=47.0
- GPIO 2×20 header centred at (32.5, 52.5)

## ⚠ Compatibility
The EVM drive is **M.2 SATA**. The Waveshare adapter supports **NVMe only**. Replace it with a 2230/2242 **NVMe** SSD (e.g. EVM EVMNV42/256GB). The model geometry is the same 42 × 22 envelope.

## Onshape
1. Document → Import → choose the `.step` files. Each file comes in as named parts (PCB, USB3 stack, …), coloured.
2. STEP carries no sketches or constraints — parts arrive fixed. In an Assembly, place **Mate connectors on the hole cylinders** (Pi Ø2.7 holes) and port faces, then Fasten/Revolute mate.
3. For enclosure work on the Pi, the official Raspberry Pi 5 STEP (pip.raspberrypi.com → Raspberry Pi 5 → "RaspberryPi5-step") is exact and preferred.

## Updating the Waveshare adapter
Open `build.py`, edit the `[E]` values in `waveshare_adapter_f()` from Waveshare's outline drawing (docs.waveshare.com/Pi5-Connector-Adapter-F → Dimensions), then run `python3 build.py`.
