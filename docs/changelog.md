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
