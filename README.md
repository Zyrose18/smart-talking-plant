# Smart Talking Plant 🌱

A completely unnecessary but fun hardware project based on the Raspberry Pi Pico. 

Basically, this plant monitors its own soil moisture. If it drops below a certain threshold (around 20%), the plant starts complaining loudly through a speaker. The best part? The warning sounds are recorded voice memos from my coworkers, playing in a specific loop.

Right now, it's a fully working breadboard prototype. The code is stable and doing exactly what it should.

## The Hardware
- **MCU:** Raspberry Pi Pico (RP2040)
- **Audio:** MAX98357A I2S Amplifier breakout + a generic small speaker
- **Storage:** Standard MicroSD card module (SPI)
- **Sensor:** Capacitive Soil Moisture Sensor v2.0 (Analog)

## Wiring & Quirks
If you want to recreate this, pay attention to the voltages. It's a mix of 5V and 3.3V logic.

**MicroSD Module (SPI) - 5V!**
- Powered via VBUS (5V) and GND
- CS -> GP13
- MISO -> GP12
- MOSI -> GP11
- SCK -> GP10

**MAX98357A Amp (I2S) - 3.3V**
- Powered via 3V3 OUT and GND
- BCLK -> GP4
- LRC -> GP3
- DIN -> GP2
- *Important:* I tied the **GAIN pin directly to GND**. This drops the gain to -9dB and prevents awful audio clipping. Don't skip this or your ears will bleed.

**Moisture Sensor - 3.3V**
- Powered via 3V3 OUT and GND (needs to be 3.3V, don't use 5V here)
- AOUT -> GP26 (A0)

## Software details
The whole thing runs on **CircuitPython**. 

- **Audio setup:** It plays 16-bit PCM WAV files (mono) loaded from `/sd/sounds/`. 
- **The Loop:** It doesn't just play random files. It loops through my coworkers in a fixed order (Steven -> Eybruh -> Minh -> Eddy, Josef, Umar, Zau) so everyone gets their turn to yell at me.
- **Sensor Calibration:** Analog raw values are mapped to percentages. (Dry = roughly 52000, Wet = 25000).
- **Hissing fix:** I2S amps tend to hiss when idle. To fix this, the code explicitly calls `i2s.stop()` and `mixer.deinit()` right after a sound finishes. Dead silent during pauses.

## What's next? (To-Do)
- [x] Breadboard prototype & software logic
- [ ] Design a carrier PCB in EasyEDA to finally get rid of the jumper wire mess.
- [ ] 3D print a proper custom enclosure for the electronics (will need some help with the CAD design to make room for the USB port and speaker grill).

---

## ⚖️ Copyright & License
© 2026 [Dein Name]. All rights reserved. 

This repository and its contents are public for portfolio and demonstration purposes only. You are welcome to read the code and get inspired, but copying, modifying, distributing, or using this project commercially without explicit permission is strictly prohibited.
