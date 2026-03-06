# OpenBrick EDU — Session State Document

**Last updated:** 2026-03-07 (end of Day 6)
**Purpose:** Carry context between Claude conversations. Paste this at the start of a new chat.

## Project Summary

- Hardware: ESP32-S3-WROOM-1-N8R2 (8MB flash, 2MB PSRAM)
- Software: Web IDE (React/TypeScript/Blockly) + MicroPython firmware
- Target users: Ages 10-14, Turkish schools
- BOM target: Under $60 USD (Robotistan, Trendyol)
- GitHub: https://github.com/tugrulcank-netizen/openbrick-edu
- Local path: C:\Users\tugru\openbrick-edu

## Current Phase

Phase 1: Core Loop — Day 7 (Basic Blockly workspace) is next.

## Phase 0 Status: COMPLETE

All deliverables done. Only open item: hardware not yet ordered.

## Completed Work

### Firmware (Days 1–5) — 134/134 tests passing, 98% coverage
- HAL base classes: sensor.py, motor.py
- Boot manager: boot/manager.py
- MPU6050 IMU driver: firmware/drivers/mpu6050.py (24 tests)
- N20 motor driver with encoder: firmware/drivers/motor_n20.py (32 tests)
- PID controller: firmware/drivers/pid.py (27 tests)
- BLE GATT service UUIDs: firmware/ble/service.py (ADR-003)
- BLE protocol encoder/decoder + CRC-16: firmware/ble/protocol.py (30 tests)
- PortManager: firmware/hal/port_manager.py (21 integration tests)

### IDE (Day 6) — 36/36 tests passing, 91% coverage, CI green
- `ide/src/ble/types.ts` — CMD constants, GATT UUIDs, BleFrame interface, callback types
- `ide/src/ble/protocol.ts` — CRC-16/CCITT-FALSE (poly 0x1021, init 0xFFFF), encodeFrame(), decodeFrame()
- `ide/src/ble/BleManager.ts` — Web Bluetooth state machine
- `ide/src/ble/index.ts` — barrel export
- `ide/jest.config.js` — jsdom environment, collectCoverageFrom scoped to ble/
- `ide/jest.setup.ts` — TextEncoder/TextDecoder polyfill for jsdom
- `ide/tsconfig.app.json` — added jest and web-bluetooth types, excludes __tests__
- `ide/tsconfig.jest.json` — dedicated tsconfig for Jest with esModuleInterop

### ADRs
- ADR-001: RJ11 connector
- ADR-002: N20 motor with encoder
- ADR-003: BLE GATT UUID scheme
- ADR-004: BLE framed binary protocol
- ADR-005: I2C bus injection pattern

## Phase 1 Tasks

- [x] Day 1: MPU6050 IMU driver ✅
- [x] Day 2: N20 motor driver with encoder ✅
- [x] Day 3: PID controller ✅
- [x] Day 4: BLE GATT service + protocol ✅
- [x] Day 5: Firmware integration ✅
- [x] Day 6: Web Bluetooth manager (IDE) ✅
- [ ] Day 7: Basic Blockly workspace
- [ ] Day 8: Connect + run + stop flow
- [ ] Day 9: Hardware-in-the-loop (requires PCB)
- [ ] Day 10: End-to-end + Phase 1 review

## Pending Hardware

- ESP32-S3-WROOM-1-N8R2 — not yet ordered
- MPU6050 breakout — not yet ordered
- N20 motor + encoder — not yet ordered
- Calibration jig print — ordered (craftcloud3d.com, PETG)

## Important Notes

- PID lives at firmware/drivers/pid.py (not hal/ — pure math, no hardware dependency)
- Encoder IRQ direction: channel A rising reads channel B state. If motor counts backwards on real hardware, swap enc_a and enc_b in HAL port manager — do NOT touch the driver
- PID windup: call motor._pid.reset() before re-engaging after a stop
- BLE CRC: poly 0x1021, init 0xFFFF (CRC-16/CCITT-FALSE) — must match between firmware/ble/protocol.py and ide/src/ble/protocol.ts — confirmed matching
- CRC reference vectors: empty→0xFFFF, [0x00]→0xE1F0, "123456789"→0x29B1, "OpenBrick"→0x064D
- BleManager state machine: disconnected → connecting → connected → disconnecting → disconnected
- BleManager.sendFrame() throws 'Not connected' if called outside connected state
- Unexpected hub disconnect fires onError callbacks, resets to disconnected
- Jest environment: jsdom with TextEncoder polyfill (jest.setup.ts) — required for CI
- Coverage scoped to src/ble/** only — App.tsx and main.tsx excluded

## Dev Environment

- Python 3.14.3 — use `py` not `python`
- Firmware venv: source .venv-firmware/Scripts/activate
- Node.js 24.14.0
- OpenSCAD 2021.01

## Session Start Checklist

```bash
cd /c/Users/tugru/openbrick-edu
git pull
source .venv-firmware/Scripts/activate
pytest firmware/tests/ -v
npm --prefix ide test
```

## Session Wrap-up Checklist

- [ ] git add + commit + push
- [ ] Update docs/changelog.md
- [ ] Update session-state.md
- [ ] Verify CI green on GitHub
