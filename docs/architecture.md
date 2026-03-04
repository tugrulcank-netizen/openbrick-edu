# OpenBrick EDU — System Architecture

**Version:** 1.0  
**Date:** 2026-03-05  
**Status:** Living document — update when architecture decisions change  
**Related ADRs:** ADR-001 (connectors), ADR-002 (motors)

---

## 1. System Overview

OpenBrick EDU is a three-layer system. The layers communicate over BLE (wireless) or USB serial (wired fallback). No backend server is required — the Web IDE is a static application that talks directly to the hub.

```
┌─────────────────────────────────────────────────────────┐
│                    LAYER 1: WEB IDE                     │
│         Browser (Chrome / Edge) — Static App            │
│   React + TypeScript + Blockly + Monaco + Recharts      │
└───────────────────┬─────────────────────────────────────┘
                    │  BLE (Web Bluetooth API)
                    │  USB Serial (WebSerial API — fallback)
                    │  Protocol: framed binary, CRC-16
┌───────────────────▼─────────────────────────────────────┐
│               LAYER 2: BLE / USB TRANSPORT              │
│          Bidirectional framed binary protocol           │
│   Messages: program upload │ run/stop │ telemetry       │
│             sensor stream  │ motor cmd │ hub status     │
└───────────────────┬─────────────────────────────────────┘
                    │  GATT characteristics (BLE)
                    │  USB serial @ 115200 baud (fallback)
┌───────────────────▼─────────────────────────────────────┐
│             LAYER 3: ESP32-S3 HUB FIRMWARE              │
│         MicroPython runtime + C extensions (HAL)        │
│   Sensors │ Motors │ LED Matrix │ IMU │ Speaker │ BMS   │
└─────────────────────────────────────────────────────────┘
```

---

## 2. Firmware Architecture

### 2.1 Module Dependency Graph

```
                        ┌─────────┐
                        │  boot/  │  Startup, hardware init,
                        │         │  LED splash, battery check
                        └────┬────┘
                             │ initializes
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
        ┌──────────┐  ┌──────────┐  ┌──────────┐
        │   ble/   │  │   usb/   │  │ storage/ │
        │  GATT    │  │  REPL +  │  │ Program  │
        │ service  │  │ protocol │  │  slots   │
        └────┬─────┘  └────┬─────┘  └──────────┘
             │              │
             └──────┬───────┘
                    ▼
             ┌────────────┐
             │ executor/  │  Sandboxed MicroPython runner
             │            │  Watchdog timer (5s reset)
             └─────┬──────┘
                   │ calls
         ┌─────────┴──────────┐
         ▼                    ▼
   ┌──────────┐        ┌──────────────┐
   │   hal/   │        │   matrix/    │
   │ Port     │        │  5×5 WS2812B │
   │ Sensor   │        │  animation   │
   │ Motor    │        └──────────────┘
   │ (base    │
   │ classes) │        ┌──────────────┐
   └─────┬────┘        │   audio/     │
         │             │  Piezo tones │
         │ implements  └──────────────┘
         ▼
   ┌──────────────────────────────────┐
   │           drivers/               │
   │  color.py   (TCS34725)           │
   │  distance.py (VL53L0X / HC-SR04) │
   │  force.py   (HX711 + load cell)  │
   │  imu.py     (MPU6050 — in hub)   │
   │  motor.py   (N20 + encoder)      │
   └──────────────────────────────────┘
```

### 2.2 Firmware Module Descriptions

| Module | Language | Responsibility |
|--------|----------|----------------|
| `boot/` | MicroPython | Hardware init, LED splash, battery level check, BLE/USB service start |
| `ble/` | MicroPython + C | GATT service definitions, connection management, framed binary protocol handler |
| `usb/` | MicroPython | USB serial REPL and protocol handler (fallback transport) |
| `hal/` | MicroPython | Abstract base classes: `Port`, `Sensor`, `Motor` — defines contracts for all drivers |
| `drivers/` | MicroPython | Concrete sensor and motor drivers implementing HAL interfaces |
| `executor/` | MicroPython | Sandboxed user program runner with watchdog timer; prevents user code from bricking hub |
| `matrix/` | MicroPython + C | 5×5 WS2812B LED animation engine; pixel API, scroll text, animations |
| `audio/` | MicroPython | Piezo buzzer tone and melody API |
| `storage/` | MicroPython | Flash program slot manager; stores up to 20 user programs |
| `ota/` | MicroPython | WiFi OTA update handler with rollback — **deferred to post-MVP** |

### 2.3 HAL Interface Contracts

All sensor drivers inherit from `hal.Sensor`. All motor drivers inherit from `hal.Motor`. This contract is what allows the IDE to treat all sensors/motors uniformly.

```python
# hal/sensor.py — abstract contract (do not implement here)
class Sensor:
    def init(self, port: Port) -> None: ...      # initialize hardware
    def read(self) -> dict: ...                   # return {value, unit, raw}
    def calibrate(self) -> None: ...              # run calibration routine
    def sensor_type(self) -> str: ...             # return type string for IDE

# hal/motor.py — abstract contract
class Motor:
    def init(self, port: Port) -> None: ...
    def set_speed(self, speed: int) -> None: ...  # -100 to +100
    def set_angle(self, degrees: int) -> None: ... # absolute, uses PID
    def get_angle(self) -> int: ...               # reads encoder
    def stop(self, mode: str = 'brake') -> None: ...
```

### 2.4 BLE GATT Service Structure

```
OpenBrick EDU Service (UUID: defined in .claude/skills/ble-protocol.md)
│
├── Program Upload Characteristic   (WRITE, chunked binary)
├── Run/Stop Characteristic         (WRITE, single-byte command)
├── Telemetry Characteristic        (NOTIFY, 20-byte frames at 50Hz)
├── Sensor Stream Characteristic    (NOTIFY, per-port values)
├── Motor Command Characteristic    (WRITE, speed + angle commands)
└── Hub Status Characteristic       (READ + NOTIFY, battery, errors)
```

### 2.5 Port Connector Wiring

Per ADR-001, all ports use RJ11 connectors. Pin assignments differ by port type:

```
Sensor Port (6P4C — 4 pins used):
  Pin 1: VCC (3.3V, 100mA max)
  Pin 2: SDA / GPIO signal 1
  Pin 3: SCL / GPIO signal 2
  Pin 4: GND

Motor Port (6P6C — all 6 pins used):
  Pin 1: Motor+ (DRV8833 output A1)
  Pin 2: Motor- (DRV8833 output A2)
  Pin 3: Encoder A (GPIO input, interrupt)
  Pin 4: Encoder B (GPIO input, interrupt)
  Pin 5: VCC (3.3V encoder power)
  Pin 6: GND
```

---

## 3. IDE Architecture

### 3.1 Module Dependency Graph

```
┌──────────────────────────────────────────────────────────┐
│                    src/App.tsx                           │
│              Root component, routing, state              │
└──┬───────────┬───────────┬──────────────┬───────────────┘
   │           │           │              │
   ▼           ▼           ▼              ▼
┌──────┐  ┌────────┐  ┌─────────┐  ┌──────────┐
│block │  │editor/ │  │dashboard│  │projects/ │
│ly/   │  │Monaco  │  │Recharts │  │save/load │
│Block │  │editor  │  │sensor   │  │export/   │
│editor│  │Python  │  │charts   │  │import    │
└──┬───┘  └────┬───┘  └────┬────┘  └──────────┘
   │           │            │
   └─────┬─────┘            │
         ▼                  │
   ┌──────────┐             │
   │   ble/   │◄────────────┘  (dashboard subscribes to BLE stream)
   │  Web     │
   │Bluetooth │
   │ manager  │
   └────┬─────┘
        │
        ▼
   ┌──────────┐
   │  i18n/   │  Loaded by all UI components
   │ TR / EN  │
   └──────────┘
```

### 3.2 IDE Module Descriptions

| Module | Stack | Responsibility |
|--------|-------|----------------|
| `src/blockly/` | TypeScript + Blockly | Custom block definitions (JSON), toolbox categories, MicroPython code generators |
| `src/editor/` | TypeScript + Monaco | MicroPython text editor, syntax highlighting, autocomplete, error underlining |
| `src/ble/` | TypeScript | Web Bluetooth manager, protocol encoder/decoder, connection state machine |
| `src/dashboard/` | React + Recharts | Real-time sensor value visualization, numeric displays, live graphs |
| `src/simulator/` | TypeScript | Virtual hub and sensor emulation — **deferred to post-MVP** |
| `src/i18n/` | JSON | Turkish (tr.json) and English (en.json) string tables |
| `src/projects/` | TypeScript | Save/load to localStorage, export/import as .json files |
| `src/tutorials/` | React | Guided tutorial engine with step highlighting — **deferred to post-MVP** |

### 3.3 BLE Connection State Machine

```
         ┌──────────┐
         │  IDLE    │  No hub connected
         └────┬─────┘
              │ user clicks "Connect"
              ▼
         ┌──────────┐
         │SCANNING  │  navigator.bluetooth.requestDevice()
         └────┬─────┘
              │ device selected
              ▼
         ┌──────────┐
         │CONNECTING│  gatt.connect()
         └────┬─────┘
              │ GATT connected
              ▼
         ┌──────────┐
         │  READY   │  All characteristics discovered
         └────┬─────┘
         ▲    │ user uploads program
         │    ▼
         │  ┌──────────┐
         │  │UPLOADING │  Chunked binary write
         │  └────┬─────┘
         │       │ upload complete
         │       ▼
         │  ┌──────────┐
         │  │ RUNNING  │  Hub executing user program
         │  └────┬─────┘
         │       │ stop command / program ends
         └───────┘
              │ disconnect / error
              ▼
         ┌──────────┐
         │  ERROR   │  Show error message, retry option
         └──────────┘
```

### 3.4 Blockly Block Structure

Each custom block consists of three files:

```
src/blockly/
├── blocks/
│   └── [category]/
│       └── [block_name].json       # Block definition (shape, inputs, colors)
├── generators/
│   └── python/
│       └── [category]/
│           └── [block_name].ts     # MicroPython code generator
└── toolbox.ts                      # Registers all blocks into toolbox categories
```

Block categories map to hub capabilities:
- `hub/` — LED matrix, speaker, battery, buttons
- `motors/` — set speed, set angle, get angle, stop
- `sensors/` — color read, distance read, force read, IMU read
- `control/` — loops, conditionals, wait (standard Blockly)
- `variables/` — variables (standard Blockly)

---

## 4. Communication Protocol

### 4.1 Frame Format

All messages over BLE and USB use the same framed binary format:

```
┌────────┬────────┬────────────┬──────────────────┬────────┐
│  SOF   │  TYPE  │   LENGTH   │     PAYLOAD      │ CRC-16 │
│ 1 byte │ 1 byte │  2 bytes   │  0–512 bytes     │ 2 bytes│
│  0xAA  │        │ big-endian │                  │        │
└────────┴────────┴────────────┴──────────────────┴────────┘
```

Message types: `0x01` = program chunk, `0x02` = run, `0x03` = stop, `0x04` = telemetry, `0x05` = sensor data, `0x06` = motor command, `0x07` = hub status.

Full protocol specification: `@.claude/skills/ble-protocol.md`

### 4.2 Program Upload Sequence

```
IDE                                    HUB
 │                                      │
 │── UPLOAD_START (program size) ──────►│
 │                                      │ allocates slot
 │◄── ACK ──────────────────────────────│
 │                                      │
 │── CHUNK_0 (512 bytes max) ──────────►│
 │◄── ACK ──────────────────────────────│
 │                                      │
 │── CHUNK_N ... ──────────────────────►│
 │◄── ACK ──────────────────────────────│
 │                                      │
 │── UPLOAD_END (CRC-16 of full prog) ─►│
 │                                      │ verifies CRC
 │◄── READY or ERROR ───────────────────│
```

---

## 5. Hardware Block Diagram

```
                    ┌─────────────────────────────────┐
                    │          ESP32-S3 HUB PCB        │
                    │                                  │
  USB-C ───────────►│ USB                  BLE 5.0     │◄──── Web IDE
                    │                                  │
  Li-Ion 18650 ────►│ BMS + TP4056                     │
                    │                                  │
                    │ ESP32-S3-WROOM-1                 │
                    │   ├── I2C bus ──► MPU6050 (IMU)  │
                    │   ├── SPI/I2C ──► 5×5 WS2812B   │
                    │   ├── GPIO ─────► Piezo buzzer   │
                    │   │                              │
                    │   ├── Port 1 (RJ11) ──► Sensor   │
                    │   ├── Port 2 (RJ11) ──► Sensor   │
                    │   ├── Port 3 (RJ11) ──► Sensor   │
                    │   ├── Port 4 (RJ11) ──► Sensor   │
                    │   │                              │
                    │   ├── Port 5 (RJ11) ──► Motor    │
                    │   │     └── DRV8833 H-bridge      │
                    │   └── Port 6 (RJ11) ──► Motor    │
                    │         └── DRV8833 H-bridge      │
                    └─────────────────────────────────┘
```

---

## 6. Key Constraints (Non-Negotiable)

| Constraint | Value | Source |
|-----------|-------|--------|
| Stud pitch | 8.0mm ±0.05mm | LEGO Technic spec |
| Pin hole (3D print) | 5.1–5.3mm | Calibrated per printer |
| Axle cross-hole | 5.6mm ±0.1mm | LEGO Technic spec |
| SRAM budget (ESP32-S3) | ~520KB total | Allocate: firmware ~200KB, user prog ~100KB, heap ~220KB |
| IDE bundle size | <500KB gzipped | NFR-P04 |
| Hub boot time | <3 seconds | NFR-P01 |
| Sensor poll rate | ≥50 Hz | NFR-P02 |
| BOM target | <$60 USD | Project constraint |

---

## 7. Technology Stack Summary

| Layer | Technology | Version | Notes |
|-------|-----------|---------|-------|
| Firmware runtime | MicroPython | Latest stable | ESP32-S3 port |
| Firmware C extensions | ESP-IDF / C | Latest stable | HAL performance-critical paths only |
| IDE framework | React | 18+ | Functional components + hooks only |
| IDE language | TypeScript | Strict mode | No `any` without `// JUSTIFIED:` |
| Block editor | Google Blockly | Latest | Custom blocks via JSON + TS generators |
| Code editor | Monaco Editor | Latest | MicroPython syntax highlighting |
| Charts | Recharts | Latest | Sensor dashboard |
| IDE build | Vite | Latest | Fast HMR, bundle analysis |
| IDE test (unit) | Jest | Latest | |
| IDE test (E2E) | Playwright | Latest | Critical user flows |
| Firmware lint | ruff | Latest | Zero warnings |
| Firmware types | mypy strict | Latest | All modules typed |
| IDE lint | ESLint strict | Latest | |
| PCB design | KiCad | 8+ | |
| 3D design | FreeCAD / OpenSCAD | Latest | Parametric models only |
| CI/CD | GitHub Actions | — | 3 workflows active |

---

*Update this document when a new ADR changes the architecture. Add the ADR number and link in the relevant section.*
