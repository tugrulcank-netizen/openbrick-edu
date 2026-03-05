# OpenBrick EDU -- Session State Document

**Last updated:** 2026-03-06 (end of session 6)
**Purpose:** Carry context between Claude conversations. Paste this at the start of a new chat.

## Project Summary

- Hardware: ESP32-S3-WROOM-1-N8R2 (8MB flash, 2MB PSRAM)
- Software: Web IDE (React/TypeScript/Blockly) + MicroPython firmware
- Target users: Ages 10-14, Turkish schools
- BOM target: Under $60 USD (Robotistan, Trendyol)
- GitHub: https://github.com/tugrulcank-netizen/openbrick-edu
- Local path: C:\Users\tugru\openbrick-edu

## Current Phase

Phase 1: Core Loop — Day 5 (Firmware Integration) is next.

## Phase 0 Status: COMPLETE (8/9)

All deliverables done. Only open item: hardware not yet ordered.

## Completed (Sessions 1–6)

- GitHub repo, CLAUDE.md hierarchy, 5 skill files, CI (3 workflows, green)
- ADR-001 (RJ11), ADR-002 (N20 motor + encoder) — updated with Origin field
- ADR-003 (BLE GATT UUID scheme), ADR-004 (BLE framed binary protocol)
- ADR-005 (I2C bus injection pattern for sensor drivers)
- docs/architecture.md, lego-specs.md v1.1, bom.md v1.2
- Firmware dev env: esptool, mpremote, pytest, ruff, mypy
- IDE scaffold: Vite + React + TS + Blockly + Jest + Playwright + ESLint
- Calibration jig: 7 pin holes (4.7–5.3mm), STL exported, print ordered
- Firmware folders: boot, ble, hal, drivers, executor, matrix, audio, storage, tests
- HAL base classes: sensor.py, motor.py
- Boot manager: boot/manager.py
- MPU6050 IMU driver: firmware/drivers/mpu6050.py (24 unit tests)
- N20 motor driver: firmware/drivers/motor_n20.py (32 unit tests)
- PID controller: firmware/drivers/pid.py (27 unit tests) — lives in drivers/, not hal/
- MotorN20.run_to_angle() wired to PID
- BLE service UUIDs: firmware/ble/service.py (ADR-003)
- BLE protocol encoder/decoder + CRC-16: firmware/ble/protocol.py (ADR-004, 30 unit tests)
- **Total firmware tests: 113/113 passing**

## Phase 1 Tasks

- [x] Day 1: MPU6050 IMU driver (TDD) ✅
- [x] Day 2: N20 motor driver with encoder (TDD) ✅
- [x] Day 3: PID controller (TDD) ✅
- [x] Day 4: BLE GATT service + protocol (TDD) ✅
- [ ] Day 5: Firmware integration (boot → BLE → HAL → drivers)
- [ ] Day 6: Web Bluetooth manager (IDE)
- [ ] Day 7: Basic Blockly workspace
- [ ] Day 8: Connect + run + stop flow
- [ ] Day 9: Hardware-in-the-loop (requires PCB)
- [ ] Day 10: End-to-end + Phase 1 review

## Pending Hardware

- ESP32-S3-WROOM-1-N8R2 -- not yet ordered
- MPU6050 breakout -- not yet ordered
- N20 motor + encoder -- not yet ordered
- Calibration jig print -- ordered (craftcloud3d.com, PETG)

## Important Notes

- PID lives at firmware/drivers/pid.py (not hal/ — pure math, no hardware dependency)
- Encoder IRQ direction logic: channel A rising reads channel B state. If motor counts backwards on real hardware, swap enc_a and enc_b in HAL port manager — do NOT touch the driver
- PID has internal state (integral). Call motor._pid.reset() before re-engaging after a stop to avoid windup carryover
- BLE CRC polynomial: 0x1021, init 0xFFFF (must match ide/src/ble/protocol.ts)

## Decisions Needed

_None. All ADRs current._

## Dev Environment

- Python 3.14.3 -- use `py` not `python`
- Firmware venv: source .venv-firmware/Scripts/activate
- Node.js 24.14.0
- OpenSCAD 2021.01

## Session Start Checklist

```bash
cd /c/Users/tugru/openbrick-edu
git pull
source .venv-firmware/Scripts/activate
pytest firmware/tests/ -v
```

## Session Wrap-up Checklist

- [ ] git add + commit + push
- [ ] Update docs/changelog.md
- [ ] Update docs/plan.md
- [ ] Update session-state.md
- [ ] Verify CI green on GitHub
