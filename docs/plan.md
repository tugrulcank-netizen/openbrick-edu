# OpenBrick EDU — Sprint Plan

Updated: 2026-03-04

## Current Phase

**Phase 0: Setup (Month 1)**
Goal: Development environment, CI/CD, documentation scaffolding, BOM procurement, architecture decisions locked.

---

## This Week (Week 1: Mar 4–10)

### Completed
- [x] Create GitHub repository with README, LICENSE (MIT), .gitignore
- [x] Create root CLAUDE.md with project instructions
- [x] Create subdirectory CLAUDE.md files (firmware/, ide/, hardware/)
- [x] Create 5 skill files in .claude/skills/

### In Progress
- [ ] Create docs/ scaffolding (this file, changelog, nfr-status, safety-checklist, validation-log, metrics)
- [ ] Create initial ADRs: ADR-001 connector type (RJ11 vs JST-PH), ADR-002 motor selection (Geekservo vs N20)

### Up Next
- [ ] Set up GitHub Actions CI pipeline (lint + type-check placeholder)
- [ ] Initialize firmware repo structure (folders, __init__.py, HAL base classes)
- [ ] Initialize IDE repo structure (Vite + React + TypeScript scaffold)

---

## Week 2 (Mar 11–17)

- [ ] Define firmware architecture diagram (docs/architecture.md)
- [ ] Define IDE architecture diagram
- [ ] Create LEGO dimensional spec file (docs/lego-specs.md) from skill file data
- [ ] Create BOM spreadsheet with Turkish supplier links and prices (docs/bom.md)
- [ ] Order first batch of components (ESP32-S3, MPU6050, Geekservo motors)

---

## Week 3 (Mar 18–24)

- [ ] Design calibration test jig in OpenSCAD/FreeCAD
- [ ] 3D print calibration test jig — test with genuine LEGO Technic parts
- [ ] Set up firmware dev environment (MicroPython, esptool, pytest)
- [ ] Set up IDE dev environment (Node.js, Vite, React, Blockly, Jest, Playwright)
- [ ] Write first ADR for BLE protocol framing decisions

---

## Week 4 (Mar 25–31)

- [ ] Breadboard prototype: ESP32-S3 + MPU6050 + 1 Geekservo motor
- [ ] First firmware boot: LED matrix splash screen + BLE advertisement
- [ ] Log calibration jig fit test results in docs/validation-log.md
- [ ] Phase 0 review: all setup tasks complete, ready for Phase 1
- [ ] Write Phase 1 sprint plan

---

## Backlog (Future Phases)

### Phase 1: Core Loop (Months 2–4)
- Hub PCB design in KiCad
- 3D-printable hub enclosure (LEGO compatible)
- Firmware: boot sequence, HAL, BLE GATT, IMU driver, motor PID
- IDE: Blockly workspace, core blocks, Web Bluetooth connect + upload
- LEGO fit validation (≥95% pass rate)

### Phase 2: Sensors (Months 5–6)
- Color, distance, force sensor drivers
- Sensor housings (3D printed, LEGO compatible)
- Blockly blocks + Python generators for all sensors
- Live sensor dashboard (Recharts)

### Phase 3: Polish (Months 7–8)
- MicroPython text editor (Monaco)
- Project save/load
- Turkish + English i18n
- Playwright E2E tests
- Performance optimization

### Phase 4: Content (Months 9–10)
- 10 STEAM lesson plans (TR + EN)
- Assembly guides, video tutorials
- Usability testing with ages 10–14

### Phase 5: Launch (Months 11–12)
- Public release, docs site, community setup

---

## Decisions Needed

- [ ] RJ11 vs JST-PH connectors — need to compare availability in Turkey, durability, ease of use for kids
- [ ] Geekservo vs N20 motors — Geekservo is LEGO-native but open-loop; N20 needs custom mount but has encoder
- [ ] VL53L0X vs HC-SR04 distance sensor — ToF is more accurate but costs more

## Handoff Notes

_Write notes here at the end of each session so the next session has context._

- **2026-03-04:** Repository created. CLAUDE.md hierarchy and all 5 skill files committed. Next task: create docs/ scaffolding files.
