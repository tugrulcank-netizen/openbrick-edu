# OpenBrick EDU -- Sprint Plan

## Phase 1: Core Loop
**Goal:** Hub + IMU + 1 motor + BLE + basic block IDE (full stack end-to-end)
**Duration:** 2 weeks (pending PCB delivery)
**Start:** 2026-03-06

---

## Week 1: Firmware Core

### Day 1 -- MPU6050 IMU Driver
- [ ] Write failing tests for IMU driver (test_imu.py)
- [ ] Implement IMU driver (firmware/drivers/imu.py)
- [ ] Verify: pytest firmware/tests/ all green
- [ ] Commit: feat(firmware): add MPU6050 IMU driver with tests

### Day 2 -- N20 Motor Driver
- [ ] Write failing tests for motor driver (test_motor_n20.py)
- [ ] Implement N20 driver with encoder reading (firmware/drivers/motor_n20.py)
- [ ] Verify: pytest firmware/tests/ all green
- [ ] Commit: feat(firmware): add N20 motor driver with encoder

### Day 3 -- PID Controller
- [ ] Write failing tests for PID controller (test_pid.py)
- [ ] Implement PID controller (firmware/hal/pid.py)
- [ ] Wire PID into motor driver
- [ ] Verify: pytest firmware/tests/ all green
- [ ] Commit: feat(firmware): add PID controller for motor positioning

### Day 4 -- BLE GATT Service
- [ ] Write failing tests for BLE service stub (test_ble.py)
- [ ] Implement BLE GATT service definitions (firmware/ble/service.py)
- [ ] Implement BLE protocol handler stub (firmware/ble/protocol.py)
- [ ] Verify: pytest firmware/tests/ all green
- [ ] Commit: feat(firmware): add BLE GATT service and protocol stub

### Day 5 -- Firmware Integration + Buffer
- [ ] Wire boot -> BLE -> HAL -> drivers together
- [ ] Write integration test: boot sequence with mocked hardware
- [ ] Run full firmware test suite + coverage check (target: 80%)
- [ ] Fix any failing tests or coverage gaps
- [ ] Commit: feat(firmware): integrate boot, BLE, HAL, drivers

---

## Week 2: IDE Core + Integration

### Day 6 -- Web Bluetooth Manager
- [ ] Write failing tests for BLE manager (ide/src/ble/)
- [ ] Implement BLE manager: scan, connect, disconnect
- [ ] Verify: npm test all green
- [ ] Commit: feat(ide): add Web Bluetooth manager

### Day 7 -- Basic Blockly Workspace
- [ ] Write failing tests for Blockly code generator
- [ ] Implement core block categories: Hub, Motors, Sensors
- [ ] Verify generated MicroPython output matches expected
- [ ] Commit: feat(ide): add core Blockly blocks and Python generators

### Day 8 -- Connect + Run + Stop Flow
- [ ] Implement connect button, run button, stop button in IDE
- [ ] Wire BLE manager to Blockly code generator output
- [ ] Write Playwright E2E test: connect -> run -> stop
- [ ] Commit: feat(ide): add connect/run/stop flow

### Day 9 -- Hardware-in-the-Loop (requires PCB)
- [ ] Flash firmware to ESP32-S3-WROOM-1-N8R2
- [ ] Connect MPU6050 on breadboard, verify IMU readings over BLE
- [ ] Connect N20 motor, verify motor control over BLE
- [ ] Log results in docs/validation-log.md
- [ ] Commit: test(hardware): hardware-in-the-loop validation results

### Day 10 -- End-to-End + Phase 1 Review
- [ ] Full end-to-end test: IDE block program -> BLE -> motor moves
- [ ] LEGO fit test with printed calibration jig, log offset
- [ ] Run full test suite: firmware + IDE
- [ ] Phase 1 review: what shipped vs plan
- [ ] Write Phase 2 sprint plan
- [ ] Commit: docs: Phase 1 complete, update validation log and plan

---

## Decisions Needed
- [ ] ADR-003: BLE GATT service UUID scheme
- [ ] ADR-004: BLE framed binary protocol format

## Handoff Notes
_Updated at end of each session._

## Metrics (update daily)
| Metric | Target | Current |
|--------|--------|---------|
| Firmware test coverage | >= 80% | ~60% (18 tests, stubs only) |
| IDE test coverage | >= 75% | 0% (scaffold only) |
| CI pass rate | > 95% | 100% |
| Commits | >= 1/day | on track |
| Open tech debt | < 15 | 0 |
