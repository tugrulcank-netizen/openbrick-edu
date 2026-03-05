# OpenBrick EDU -- Session State Document

**Last updated:** 2026-03-06 (end of session 5)
**Purpose:** Carry context between Claude conversations. Paste this at the start of a new chat.

## Project Summary

- Hardware: ESP32-S3-WROOM-1-N8R2 (8MB flash, 2MB PSRAM)
- Software: Web IDE (React/TypeScript/Blockly) + MicroPython firmware
- Target users: Ages 10-14, Turkish schools
- BOM target: Under $60 USD (Robotistan, Trendyol)
- GitHub: https://github.com/tugrulcank-netizen/openbrick-edu
- Local path: C:\Users\tugru\openbrick-edu

## Current Phase

Phase 1: Core Loop -- Day 1 starts next session.

## Phase 0 Status: COMPLETE (8/9)

All deliverables done. Only open item: hardware not yet ordered.

## Completed (Sessions 1-5)

- GitHub repo, CLAUDE.md hierarchy, 5 skill files, CI (3 workflows, green)
- ADR-001 (RJ11), ADR-002 (N20 motor + encoder)
- docs/architecture.md, lego-specs.md v1.1, bom.md v1.2
- Firmware dev env: esptool, mpremote, pytest, ruff, mypy
- IDE scaffold: Vite + React + TS + Blockly + Jest + Playwright + ESLint
- Calibration jig: 7 pin holes (4.7-5.3mm), STL exported, print ordered
- Firmware folders: boot, ble, hal, drivers, executor, matrix, audio, storage, tests
- HAL base classes: sensor.py, motor.py
- Boot manager: boot/manager.py
- 18 passing unit tests (12 HAL + 6 boot)
- Phase 1 sprint plan: docs/plan.md (10 days)
- 24 commits on main, CI green

## Phase 1 Tasks

- [ ] Day 1: MPU6050 IMU driver (TDD)
- [ ] Day 2: N20 motor driver with encoder (TDD)
- [ ] Day 3: PID controller (TDD)
- [ ] Day 4: BLE GATT service stub (TDD)
- [ ] Day 5: Firmware integration
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

## Decisions Needed

- ADR-003: BLE GATT service UUID scheme
- ADR-004: BLE framed binary protocol format

## Dev Environment

- Python 3.14.3 -- use py not python
- Firmware venv: source .venv-firmware/Scripts/activate
- Node.js 24.14.0
- OpenSCAD 2021.01

## Session Start Checklist

cd /c/Users/tugru/openbrick-edu
git pull
source .venv-firmware/Scripts/activate
pytest firmware/tests/ -v

## Session Wrap-up Checklist

- [ ] git add + commit + push
- [ ] Update docs/changelog.md
- [ ] Update docs/plan.md
- [ ] Update session-state.md
- [ ] Verify CI green on GitHub
