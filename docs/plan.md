# OpenBrick EDU — Sprint Plan

**Last updated:** 2026-03-05 (end of Session 4)
**Current phase:** Phase 0: Setup (Month 1)
**Current week:** Week 4

---

## Week 3 — COMPLETED ✅

| Task | Status |
|------|--------|
| Firmware dev environment (esptool, mpremote, pytest, ruff, mypy) | ✅ |
| IDE dev environment (Node.js, Vite, React, TypeScript, Blockly, ESLint, Prettier) | ✅ |
| Calibration test jig design in OpenSCAD → STL exported | ✅ |

---

## Week 4 — IN PROGRESS

| Task | Status | Notes |
|------|--------|-------|
| Order calibration jig print from craftcloud3d.com | ⬜ | PETG, 0.2mm, 3 walls, 20% infill, no supports |
| Breadboard prototype: ESP32-S3 + MPU6050 + 1 N20 motor | ⬜ | Waiting for components from Robotistan |
| First firmware boot: LED matrix splash + BLE advertisement | ⬜ | Depends on breadboard |
| Phase 0 review + write Phase 1 sprint plan | ⬜ | End of week |

---

## Decisions Needed

- Confirm calibration offset after jig arrives → log in docs/validation-log.md
- Choose print orientation for hub enclosure (pending jig results)

---

## Handoff Notes

- Python command is `py` (not `python`) on this machine
- Firmware venv: `source .venv-firmware/Scripts/activate`
- IDE: `cd ide && npm install` after fresh pull
- OpenSCAD added to PATH in ~/.bashrc — works in Git Bash
- git config core.autocrlf true — set to avoid LF/CRLF warnings
