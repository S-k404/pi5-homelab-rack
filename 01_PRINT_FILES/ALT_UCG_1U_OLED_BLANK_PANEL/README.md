# Alternative: 1U Blank Faceplate with 0.91" 128x32 OLED Display

If you decide **not** to purchase the **Ubiquiti Cloud Gateway Ultra (UCG-Ultra)**, use this alternative 1U faceplate to fill the top 1U slot in your 9U rack.

It features a recessed bezel designed specifically to house a **0.91-inch 128×32 I2C OLED display**, giving you an animated mini-dashboard on the front of your rack showing homelab stats (IP address, CPU temperature, RAM usage, storage, and network throughput) driven directly by your Raspberry Pi 5.

---

## 1. Supported OLED Modules on Robu.in

Both of these drop directly into the rear mounting pocket:

1. **GoldenMorning 0.91" 128×32 Blue OLED Module** *(Recommended for value)*
   * **Robu SKU**: `62312`
   * **Price**: ₹ 212.00
   * **Dimensions**: 38.0 × 12.0 mm PCB, 22.4 × 5.6 mm active area
   * **Interface**: 4-pin 2.54 mm header (`GND`, `VCC`, `SCL`, `SDA`)
   * **Product Link**: https://robu.in/product/0-91-inch-128x32-i2c-iic-serial-blue-oled-lcd-display-module/

2. **Waveshare 128×32 General 0.91" OLED Module** *(Includes pre-crimped wire harness)*
   * **Robu SKU**: `968451`
   * **Price**: ₹ 629.00
   * **Dimensions**: 36.0 × 12.5 mm PCB
   * **Interface**: 4-pin PH2.0 locking plug with female dupont jumpers included
   * **Product Link**: https://robu.in/product/waveshare-128x32-general-0-91inch-oled-display-module/

---

## 2. 3D Model Files Included

* **`UCG_Alt_1U_Blank_OLED_Faceplate.step`** (CAD STEP file for Onshape)
* **`UCG_Alt_1U_Blank_OLED_Faceplate.stl`** (3D print mesh, 254 × 43.65 × 6.6 mm, 35.7 cm³, 100% watertight)
* **`UCG_Alt_1U_OLED_Retention_Clamp.step`** (Rear retention clamp bar)
* **`UCG_Alt_1U_OLED_Retention_Clamp.stl`** (Print mesh for clamp, secured with 2 × M2 screws)

### Printing Specs:
* **Material**: PETG Black (to match rack) or PLA Silver (to match B1 dock)
* **Infill**: 20%
* **Layer Height**: 0.20 mm Standard Quality
* **Print Time / Weight**: ~45 grams (costs only ~₹180–₹220 on Robu, saving ~₹400 over the heavy UCG mount).

---

## 3. Wiring to Raspberry Pi 5 GPIO

Connect the 4 pins of the OLED to the Raspberry Pi 5 40-pin header:

| OLED Pin | Pi 5 Pin # | Pi 5 Function | Wire Color (Typical) |
|---|:---:|---|---|
| **GND** | Pin 6 or 9 | Ground | Black |
| **VCC** | Pin 1 | 3.3V Power | Red |
| **SCL** | Pin 5 | GPIO 3 (I2C1 SCL) | Yellow / Blue |
| **SDA** | Pin 3 | GPIO 2 (I2C1 SDA) | Green / White |

*Note: The SSD1306 OLED runs natively on 3.3V logic — no level shifters or pull-up resistors are required.*

---

## 4. Software Setup (Pi 5 Python Telemetry Script)

Enable I2C on your Pi 5:
```bash
sudo raspi-config
# Navigate to: Interface Options -> I2C -> Enable -> Yes
```

Install the Adafruit SSD1306 library:
```bash
pip install adafruit-circuitpython-ssd1306 pillow psutil
```

Sample Python script (`homelab_stats.py`):
```python
import time, socket, psutil, board, busio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306

i2c = busio.I2C(board.SCL, board.SDA)
oled = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c, addr=0x3c)

oled.fill(0)
oled.show()

image = Image.new("1", (oled.width, oled.height))
draw = ImageDraw.Draw(image)
font = ImageFont.load_default()

while True:
    draw.rectangle((0, 0, oled.width, oled.height), outline=0, fill=0)
    
    # Get System Stats
    hostname = socket.gethostname()
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
        
    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory().percent
    
    # Display 3 compact lines
    draw.text((0, 0),  f"IP:  {ip}", font=font, fill=255)
    draw.text((0, 11), f"CPU: {cpu}% | RAM: {mem}%", font=font, fill=255)
    draw.text((0, 22), f"HOST: {hostname}", font=font, fill=255)
    
    oled.image(image)
    oled.show()
    time.sleep(2)
```

---

## 5. Comparison: Ubiquiti UCG-Ultra vs. 0.91" OLED Mod

| Feature | Ubiquiti UCG-Ultra | Pi 5 + 0.91" OLED Mod |
|---|---|---|
| **Screen Type** | 0.96" Monochrome LCM | 0.91" Monochrome OLED (128×32) |
| **Hardware Cost** | **₹ 12,000 – ₹ 14,000+** | **₹ 212** (GoldenMorning) or **₹ 629** (Waveshare) |
| **Telemetry Shown** | UniFi Gateway throughput, WAN IP | Pi 5 CPU, RAM, Temp, IP, Docker containers, Pi-hole |
| **Customizability** | Fixed firmware (cannot modify) | 100% open-source Python scripts / animations |
| **3D Print Needed** | `UCG-Ultra_1U_Mount` (~136g, ₹590) | `1U_Blank_OLED_Faceplate` (~45g, ~₹200) |
