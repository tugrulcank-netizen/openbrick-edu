# OpenBrick EDU — Bill of Materials (BOM)

**Version:** 1.1  
**Date:** 2026-03-05  
**Exchange Rate Used:** 1 USD ≈ 44 TL (serbest piyasa, 05 Mart 2026)  
**BOM Target:** < $60 USD per unit (component cost — excludes tools, print service costs amortized over multiple units)

---

## Sourcing Policy

| Tier | Supplier | Used For | Shipping |
|------|----------|----------|----------|
| 🥇 Primary | **Robotistan** — robotistan.com | All maker components: MCUs, sensors, motors, modules | Same-day dispatch; 1–3 day Turkey delivery |
| 🥈 Secondary | **Trendyol** — trendyol.com | Batteries, cables, filament, commodity hardware | 1–2 day delivery |
| 🥉 Tertiary | **Turkish PCB Houses** | Custom PCB fabrication — domestic only | 7–14 days |
| 📦 Community Alt. | **AliExpress** — aliexpress.com | Listed for international contributors only — **NOT for Turkish orders due to customs** | 2–4 weeks + customs risk |

> ⚠️ **AliExpress note for Turkish users:** Due to customs regulations, AliExpress orders frequently incur unpredictable duties, delays, or confiscation. All AliExpress links in this BOM are provided as reference for international project contributors only. Turkish builders should source exclusively from Robotistan and Trendyol.

> 💡 **Design priority:** This BOM prioritises build quality, functional reliability, and ease of use over minimum cost. The $60 target is a guideline, not a hard constraint for the reference build.

---

## Part 1: Microcontroller

| # | Component | Part / Spec | Qty | Est. TL | Est. USD | 🇹🇷 Turkish Supplier | 🌍 Community Alt. (AliExpress) | Notes |
|---|-----------|------------|-----|---------|---------|---------------------|-------------------------------|-------|
| 1 | ESP32-S3 Module | **ESP32-S3-WROOM-1-N8R2** (8MB Flash, 2MB PSRAM, BLE 5.0, PCB antenna) | 1 | ~600 TL | ~$14 | [Robotistan](https://www.robotistan.com/espressif-esp32-s3-wroom-1-n8r2-wifi-bt-50-module-en) | AliExpress: search "ESP32-S3-WROOM-1 N8R2" | **N8R2 variant is required.** PSRAM is needed for MicroPython heap with complex programs. Do not substitute N4 (no PSRAM) for the reference build. |

**Subtotal Part 1:** ~600 TL / ~$14

---

## Part 2: Sensors

| # | Component | Part / Spec | Qty | Est. TL | Est. USD | 🇹🇷 Turkish Supplier | 🌍 Community Alt. (AliExpress) | Notes |
|---|-----------|------------|-----|---------|---------|---------------------|-------------------------------|-------|
| 2 | IMU / Gyro | **MPU6050** 6-axis accelerometer + gyroscope breakout (I2C) | 1 | ~150 TL | ~$3.50 | [Robotistan](https://www.robotistan.com/mpu6050-6-axis-acceleration-and-gyro-sensor-6-dof-3-axis-accelerometer-and-gyros) | AliExpress: search "MPU6050 breakout GY-521" | Mounted inside hub PCB. I2C address 0x68. |
| 3 | Color Sensor | **TCS34725** RGB color sensing breakout (I2C, 3.3V) | 1 | ~150 TL | ~$3.50 | [Robotistan](https://www.robotistan.com/yuvali-renk-algilayici-sensor-tcs34725) | AliExpress: search "TCS34725 color sensor module" | I2C address 0x29. Needs IR blocking filter (included on most breakouts). |
| 4 | Distance Sensor | **VL53L0X** ToF laser distance sensor (I2C, up to 2m) | 1 | ~150 TL | ~$3.50 | [Robotistan](https://www.robotistan.com/vl53l0x-lazer-tof-sensor-modul-i2c-pwm-serial) | AliExpress: search "VL53L0X ToF module" | Preferred over HC-SR04: I2C, compact, 3.3V native, no GPIO timing issues. |
| 5 | Force Sensor (amplifier) | **HX711** 24-bit load cell amplifier breakout | 1 | ~70 TL | ~$1.60 | [Robotistan](https://www.robotistan.com/agirlik-sensor-kuvvetlendirici-load-cell-amplifier-hx711) | AliExpress: search "HX711 load cell amplifier" | SPI-like 2-wire protocol. Pairs with item 6. |
| 6 | Force Sensor (cell) | **1kg strain gauge load cell** (half-bridge, 4-wire) | 1 | ~70 TL | ~$1.60 | Robotistan / Trendyol | AliExpress: search "1kg load cell strain gauge" | Pairs with HX711. Mount in 3D-printed housing with fixed plate and measuring arm. |

**Subtotal Part 2:** ~590 TL / ~$14

---

## Part 3: Motors and Drivers

| # | Component | Part / Spec | Qty | Est. TL | Est. USD | 🇹🇷 Turkish Supplier | 🌍 Community Alt. (AliExpress) | Notes |
|---|-----------|------------|-----|---------|---------|---------------------|-------------------------------|-------|
| 7 | Motor + Encoder | **N20 DC micro gear motor 6V 100–300 RPM + 12 CPR magnetic encoder** (6-wire combo) | 2 | ~300 TL each | ~$7 each | [Robotistan](https://www.robotistan.com) — search "N20 enkoder motor" | AliExpress: search "N20 gear motor magnetic encoder 6V" | ADR-002 decision. Verify encoder is 6-wire (Motor+, Motor−, EncA, EncB, VCC, GND). 100 RPM recommended for controllability. |
| 8 | Motor Driver | **DRV8833** dual H-bridge motor driver module (1.5A per channel, 2.7–10.8V) | 2 | ~100 TL each | ~$2.30 each | Robotistan / Trendyol — search "DRV8833 modül" | AliExpress: search "DRV8833 dual motor driver module" | 2 modules needed (one per motor port). More efficient and compact than L298N. Sleep pin must be pulled HIGH. |

**Subtotal Part 3:** ~1,000 TL / ~$23

---

## Part 4: Power System

| # | Component | Part / Spec | Qty | Est. TL | Est. USD | 🇹🇷 Turkish Supplier | 🌍 Community Alt. (AliExpress) | Notes |
|---|-----------|------------|-----|---------|---------|---------------------|-------------------------------|-------|
| 9 | Battery Cell | **18650 Li-Ion 3.7V 2500–3000 mAh — protected cell** | 1 | ~120 TL | ~$2.75 | [Trendyol](https://www.trendyol.com) — search "18650 korumalı pil" | Local electronics shops | **Buy protected cell only** (built-in PCM). Unprotected cells risk over-discharge. NFR-R02 safety requirement. |
| 10 | Battery Charger | **TP4056 USB-C 1S Li-Ion charger module with protection** (2-chip board: TC4056A + DW01/FS8205) | 1 | ~25 TL | ~$0.60 | [Robotistan](https://www.robotistan.com) — search "TP4056 USB-C" | AliExpress: search "TP4056 Type-C charger module with protection" | **Buy the 2-chip version** with separate protection IC. Single-chip TP4056 has no over-discharge protection. |
| 11 | BMS Protection | **BMS 1S 3.7V 3A** over-charge / over-discharge / short circuit protection board | 1 | ~35 TL | ~$0.80 | Trendyol / Robotistan — search "1S BMS 3.7V" | AliExpress: search "1S BMS lithium protection board 3A" | Redundant protection layer. Required by NFR-R02 for child-facing product. |
| 12 | Battery Holder | **18650 single cell holder** with solder lugs or 20cm wire leads | 1 | ~25 TL | ~$0.60 | Robotistan / Trendyol | AliExpress: search "18650 battery holder single" | Mount inside 3D-printed battery bay in hub housing. |

**Subtotal Part 4:** ~205 TL / ~$5

---

## Part 5: Display and Audio

| # | Component | Part / Spec | Qty | Est. TL | Est. USD | 🇹🇷 Turkish Supplier | 🌍 Community Alt. (AliExpress) | Notes |
|---|-----------|------------|-----|---------|---------|---------------------|-------------------------------|-------|
| 13 | LED Matrix | **5×5 WS2812B addressable RGB LED panel** (25 LEDs, 3.3V signal compatible) | 1 | ~100 TL | ~$2.30 | Robotistan / Trendyol — search "WS2812B 5x5 matrix" | AliExpress: search "5x5 WS2812B NeoPixel matrix panel" | Use pre-assembled panel, not individual LEDs. Add 300–500Ω series resistor on data line and 100µF cap on power. |
| 14 | Piezo Buzzer | **Passive piezo buzzer 5V** (through-hole, 12mm diameter) | 1 | ~20 TL | ~$0.45 | [Robotistan](https://www.robotistan.com) — search "pasif buzzer" | AliExpress: search "passive piezo buzzer 5V 12mm" | **Passive** (not active) — required for tone generation via PWM. Active buzzers only beep at one fixed frequency. |

**Subtotal Part 5:** ~120 TL / ~$3

---

## Part 6: Connectors and PCB Hardware

| # | Component | Part / Spec | Qty | Est. TL | Est. USD | 🇹🇷 Turkish Supplier | 🌍 Community Alt. (AliExpress) | Notes |
|---|-----------|------------|-----|---------|---------|---------------------|-------------------------------|-------|
| 15 | Sensor Port Jacks | **RJ11 6P4C PCB-mount jack** (through-hole, right-angle) | 4 | ~20 TL each | ~$0.45 each | Robotistan / Trendyol — search "RJ11 PCB jack 6P4C" | AliExpress: search "RJ11 6P4C PCB mount jack through hole" | ADR-001. 4 sensor ports. Right-angle preferred for horizontal panel mounting. |
| 16 | Motor Port Jacks | **RJ11 6P6C PCB-mount jack** (through-hole, right-angle) | 2 | ~20 TL each | ~$0.45 each | Robotistan / Trendyol — search "RJ11 PCB jack 6P6C" | AliExpress: search "RJ11 6P6C PCB mount jack" | ADR-001. 2 motor ports. All 6 pins used (motor H-bridge + encoder). |
| 17 | USB-C Port | **USB-C female receptacle PCB-mount** (16-pin, USB 2.0) | 1 | ~25 TL | ~$0.60 | Robotistan / Trendyol | AliExpress: search "USB-C female PCB mount 16 pin" | Power input + USB serial. |
| 18 | Tactile Buttons | **6×6mm tactile push button** (through-hole, 4.3mm height) | 4 | ~5 TL each | ~$0.12 each | [Robotistan](https://www.robotistan.com) | AliExpress: search "6x6mm tactile push button through hole" | Hub buttons: Start, Stop, Menu, BLE Pair. |
| 19 | Power Switch | **SPDT slide switch** (through-hole, 2.5mm pitch) | 1 | ~10 TL | ~$0.23 | Robotistan | AliExpress: search "SPDT slide switch through hole PCB" | Main power on/off. |
| 20 | Sensor Cables | **RJ11 6P4C patch cable 30cm** (straight, 4-conductor) | 6 | ~30 TL each | ~$0.70 each | [Trendyol](https://www.trendyol.com) — search "RJ11 telefon kablosu" | AliExpress: search "RJ11 6P4C straight cable 30cm" | Buy a few extra for testing. Test fit with your RJ11 jacks before bulk ordering. |
| 21 | Voltage Regulator | **AMS1117-3.3 LDO** SOT-223 package | 2 | ~10 TL each | ~$0.23 each | Robotistan | AliExpress: search "AMS1117 3.3V LDO SOT-223" | 3.3V rail for ESP32-S3 and sensors. |
| 22 | Passive Components | Resistors (100Ω, 300Ω, 10kΩ assortment), capacitors (100µF, 100nF, 10µF assortment) | 1 set | ~80 TL | ~$1.80 | [Robotistan](https://www.robotistan.com) | AliExpress: search "resistor capacitor assortment kit" | Decoupling caps, pull-up resistors, LED data line resistor. Buy assortment kits. |

**Subtotal Part 6:** ~600 TL / ~$14

---

## Part 7: Custom PCB — Turkish Fabrication

The hub PCB is a custom 2-layer FR4 board designed in KiCad 8. Order from a Turkish PCB house — no customs risk, fast delivery, local support.

| # | Service | Spec | Qty | Est. Cost | Notes |
|---|---------|------|-----|-----------|-------|
| 23 | PCB Fabrication | 2-layer FR4, 1.6mm thickness, HASL finish, green solder mask, ~100×80mm board size | 5 pcs | ~400–800 TL / ~$9–18 | Order 5 minimum for iteration cycles. Export Gerber files from KiCad 8 in RS-274X format. |

### Turkish PCB Supplier Comparison

| Supplier | Location | Lead Time | Website | Status | Best For |
|----------|----------|-----------|---------|--------|----------|
| **Robotistan PCB Servisi** ⭐ | Turkey (online) | ~4 weeks | [robotistan.com/pcb-servisi](https://www.robotistan.com/pcb-servisi) | ✅ Active | **Recommended for OpenBrick EDU.** Same account as all other components — one order, one shipment. 1/2/4-layer FR-4, HASL/ENIG finish, IPC-A-600 standard, Gerber upload, stencil service. 5 pcs minimum. |
| **ERA PCB** | Ankara | 4–7 days | [erapcb.com](http://www.erapcb.com) | ✅ Active | Best for fast iteration — 4-day rush option. Use when you need a quick PCB respin after finding a design error. IPC-A-600 Class II. Call: +90 312 250 5014 |
| **Özde PCB** | Turkey | ~10 days | [ozdepcb.com](https://www.ozdepcb.com) | ✅ Active | Established 1995; solid backup option |
| **baskidevre.com.tr** | Turkey | ~10 days | [baskidevre.com.tr](https://www.baskidevre.com.tr) | ✅ Active | Established 1977 (42 years); IPC standards; solid backup option |
| ~~ERKAR Elektronik / İzmir PCB~~ | ~~İzmir~~ | — | [izmirnumunepcb.com](https://www.izmirnumunepcb.com) | ❌ **Production stopped** | Kept for reference — do not order |

> 💡 **Recommended workflow:** Order PCB from **Robotistan PCB Servisi** together with your components — one account, one shipment, no customs. Lead time is ~4 weeks so plan ahead: submit the PCB order as soon as your KiCad design is complete, then continue firmware development while it ships. If you need a fast respin after finding a bug, use **ERA PCB** for 4-day turnaround.

> 📋 **Robotistan PCB Servisi specs confirmed:**
> - Layers: 1, 2, or 4 ✅
> - Material: FR-4 standard ✅  
> - Thickness: 0.4–2.0mm (use 1.6mm standard) ✅
> - Surface finish: HASL, lead-free HASL, or ENIG (gold) ✅
> - Solder mask colours: green, red, blue, white, black, yellow, purple ✅
> - Silkscreen: white or black ✅
> - Stencil service: available ✅
> - Quality: IPC-A-600 standard ✅
> - Order format: Gerber ZIP/RAR upload, max 4MB ✅
> - Minimum quantity: 5 pieces ✅
> - SMD assembly: not yet available (coming soon)

**Subtotal Part 7:** ~400–800 TL / ~$9–18

---

## Part 8: 3D Printing — External Print Service

> 🖨️ **No in-house printer.** All 3D-printed parts are ordered from Turkish online print services. See `docs/lego-specs.md` Section 4 for the calibration workflow and print service recommendations.

| # | Item | Spec | Est. Qty | Est. TL | Est. USD | Service | Notes |
|---|------|------|----------|---------|---------|---------|-------|
| 24 | Calibration jig print | PETG, 0.2mm layers, 3 walls | 1× small part | ~50–100 TL | ~$1–2.50 | craftcloud3d.com / 3dyazici.com | **Order first, before any functional housing.** Determines your printer offset. |
| 25 | Hub enclosure prototype | PETG, 0.2mm layers | 1× set (~100g) | ~150–300 TL | ~$3.50–7 | Same service | Order after offset confirmed from jig |
| 26 | Sensor housings (×4) | PETG, 0.2mm layers | 4× parts (~50g each) | ~300–500 TL | ~$7–12 | Same service | Phase 2 — not needed yet |
| 27 | Motor mounts (×2) | PETG, 0.2mm layers | 2× parts (~40g each) | ~150–250 TL | ~$3.50–6 | Same service | Phase 2 — not needed yet |

**Subtotal Part 8:** ~160–240 TL / ~$4–5.50

---

## BOM Summary

| # | Category | Est. TL | Est. USD |
|---|----------|---------|---------|
| 1 | Microcontroller | ~600 | ~$14 |
| 2 | Sensors | ~590 | ~$14 |
| 3 | Motors & Drivers | ~1,000 | ~$23 |
| 4 | Power System | ~205 | ~$5 |
| 5 | Display & Audio | ~120 | ~$3 |
| 6 | Connectors & PCB Hardware | ~600 | ~$14 |
| 7 | Custom PCB (Turkish fab) | ~600 | ~$14 |
| 8 | 3D Printing (print service) | ~200–500 TL | ~$5–12 |
| | **TOTAL** | **~3,915–4,215 TL** | **~$92–100** |

> 📝 **Note on budget vs $60 target:** The $60 figure in the project plan assumed AliExpress pricing. The realistic Turkish domestic cost for a quality reference build is approximately $85–95 — still an 80%+ saving over SPIKE Prime at $400–455. The primary cost driver is motors with encoders (~$23 for two), which reflects fair domestic pricing for quality components. Cost is not the primary design constraint for this build.

---

## Phase 0 Order List — Buy Now

Only purchase what is needed for the Phase 1 breadboard prototype. Do not buy sensor modules, PCB, or cables yet. 3D prints are ordered from a print service — **not** included in this order.

| # | Component | Qty | Supplier | Est. TL | Est. USD | Priority |
|---|-----------|-----|----------|---------|---------|----------|
| 1 | ESP32-S3-WROOM-1-N8R2 | 1 | Robotistan | ~600 | ~$14 | 🔴 Critical |
| 2 | MPU6050 breakout | 1 | Robotistan | ~150 | ~$3.50 | 🔴 Critical |
| 7 | N20 motor + 12CPR encoder (6-wire) | 2 | Robotistan | ~600 | ~$14 | 🔴 Critical |
| 8 | DRV8833 motor driver module | 2 | Robotistan / Trendyol | ~200 | ~$4.60 | 🔴 Critical |
| 9 | 18650 Li-Ion protected cell | 1 | Trendyol | ~120 | ~$2.75 | 🔴 Critical |
| 10 | TP4056 USB-C charger (2-chip, with protection) | 1 | Robotistan | ~25 | ~$0.60 | 🔴 Critical |
| — | Breadboard (830 tie points) | 1 | Robotistan / Trendyol | ~80 | ~$1.80 | 🟡 Important |
| — | Jumper wire set (M-M + M-F) | 1 set | Robotistan / Trendyol | ~60 | ~$1.40 | 🟡 Important |
| — | USB-C cable (for programming) | 1 | Trendyol | ~50 | ~$1.15 | 🟡 Important |
| | **Phase 0 Total** | | | **~1,885 TL** | **~$44** | |

### Phase 1 Print Order — Order When KiCad Design is Ready

| # | Item | Qty | Service | Est. TL | Est. USD | When |
|---|------|-----|---------|---------|---------|------|
| P1 | Calibration jig | 1 | craftcloud3d.com / 3dyazici.com | ~50–100 | ~$1–2.50 | As soon as `hardware/test-jigs/lego-calibration-jig.stl` is ready |
| P2 | Hub enclosure prototype | 1 set | Same | ~150–300 | ~$3.50–7 | After jig result confirmed; KiCad done |
| | **Print Order Total** | | | **~200–400 TL** | **~$5–10** | |

---

## Pre-Approved Substitutes

These substitutions are approved without a new ADR. Document which substitute was used in `docs/validation-log.md`.

| Primary | Approved Substitute | When to Use | Trade-off |
|---------|---------------------|------------|-----------|
| VL53L0X | HC-SR04 ultrasonic | VL53L0X out of stock | Needs 2 GPIO pins (trigger + echo); less accurate; update driver |
| DRV8833 module | TB6612FNG module | DRV8833 unavailable | Higher current rating; minor wiring differences |
| AMS1117-3.3 | LD1117-3.3 SOT-223 | AMS1117 unavailable | Pin-compatible drop-in |
| PETG (print service) | PLA+ requested from service | Service doesn't offer PETG | Lower temp resistance; acceptable for prototype housings only |

---

## Change Log

| Date | Version | Change | Author |
|------|---------|--------|--------|
| 2026-03-05 | 1.0 | Initial BOM | AI-Assisted |
| 2026-03-05 | 1.1 | Turkish-only sourcing for reference build; AliExpress demoted to community-only reference; PCB moved to Turkish fab; quality-first selection; İzmir PCB house highlighted; cost target updated to reflect domestic pricing reality | AI-Assisted (Human-Approved) |

---

*Update this file when:*
- *Actual prices confirmed after visiting supplier sites*
- *A component is substituted (note reason)*
- *A component is ordered (add order date + actual TL paid)*
- *Exchange rate shifts more than 5%*
- *A new ADR affects component selection*
