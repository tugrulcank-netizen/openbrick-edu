## [Unreleased]

### 2026-03-06
- feat(firmware): MPU6050 IMU driver (`firmware/drivers/mpu6050.py`) — 24 unit tests, all green
- docs(adr): ADR-001 and ADR-002 updated with Origin field
- docs(adr): ADR-003 added — BLE GATT UUID scheme
- docs(adr): ADR-004 added — BLE framed binary protocol format
- docs(adr): ADR-005 added — I2C bus injection pattern for sensor drivers

## Session 5 -- 2026-03-06

### Added

- hardware/test-jigs: expanded calibration jig to 7 pin holes (4.7-5.3mm), re-exported STL
- firmware/: full module folder structure (boot, ble, hal, drivers, executor, matrix, audio, storage, tests)
- firmware/hal/sensor.py: Sensor base class
- firmware/hal/motor.py: Motor base class
- firmware/boot/manager.py: BootManager class
- firmware/tests/test_hal.py: 12 unit tests for HAL base classes
- firmware/tests/test_boot.py: 6 unit tests for BootManager
- docs/plan.md: Phase 1 sprint plan (10 days)

### Tests
- Firmware: 18/18 passing

# OpenBrick EDU — Changelog

All notable changes to this project are documented here.

---

## 2026-03-04

### Added
- GitHub repository with MIT license
- Root CLAUDE.md with project instructions
- Subdirectory CLAUDE.md files: firmware/, ide/, hardware/
- Skill files: lego-compatibility-validation, ble-protocol, blockly-block-creation, sensor-driver-pattern, motor-control
- docs/plan.md sprint plan
- docs/ scaffolding (changelog, nfr-status, metrics, validation-log, safety-checklist)
- Create initial ADRs: ADR-001 connector type (RJ11 vs JST-PH), ADR-002 motor selection (Geekservo vs N20)

## 2026-03-05
### Added
- docs/architecture.md — 3-layer system architecture (Web IDE → BLE/USB → ESP32-S3)
- docs/lego-specs.md v1.1 — LEGO Technic dimensional specifications, external print service calibration workflow
- docs/bom.md v1.2 — Bill of materials with Turkish supplier links, Robotistan PCB as primary PCB supplier, print service budget
- firmware/requirements-dev.txt — firmware dev environment (esptool, mpremote, pytest, ruff, mypy)
- ide/ — Vite + React + TypeScript scaffold with Blockly, Jest, Playwright, ESLint, Prettier
- hardware/test-jigs/lego-calibration-jig.scad — OpenSCAD calibration jig (5 pin hole sizes + axle holes)
- hardware/test-jigs/lego-calibration-jig.stl — Exported STL ready for print service order
