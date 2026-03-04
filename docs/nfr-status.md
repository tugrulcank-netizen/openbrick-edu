# OpenBrick EDU — NFR Status Dashboard

Updated: 2026-03-04

Track each non-functional requirement with current value, target, and status.
Update weekly during the reflection phase.

| ID | Requirement | Target | Current | Status |
|---|---|---|---|---|
| NFR-P01 | Hub boot time | < 3s | Not measured | 🔴 Not started |
| NFR-P02 | Sensor polling rate | ≥ 50 Hz | Not measured | 🔴 Not started |
| NFR-P03 | Motor control latency | < 20 ms | Not measured | 🔴 Not started |
| NFR-P04 | IDE page load | < 3s on 10 Mbps | Not measured | 🔴 Not started |
| NFR-P05 | BLE upload speed | < 5s for <10KB | Not measured | 🔴 Not started |
| NFR-R01 | Crash recovery | Watchdog < 5s | Not measured | 🔴 Not started |
| NFR-R02 | Battery safety | BMS 2.8V/4.2V/60°C | Not tested | 🔴 Not started |
| NFR-R03 | Electrical safety | 3.3V/500mA per port | Not tested | 🔴 Not started |
| NFR-R04 | Child safety | No sharp edges, ≥0.5mm fillet | Not tested | 🔴 Not started |
| NFR-U01 | First-time setup | ≤ 5 steps, age 10+ | Not tested | 🔴 Not started |
| NFR-U02 | Block coding learnability | < 15 min first project | Not tested | 🔴 Not started |
| NFR-U03 | Error messages | Human-readable, no stack traces | Not reviewed | 🔴 Not started |
| NFR-M01 | New sensor driver | < 200 LOC via HAL | Not measured | 🔴 Not started |
| NFR-M02 | New Blockly block | Single JSON + generator | Not measured | 🔴 Not started |

## Notes

- 🟢 Green = meets target
- 🟡 Amber = within 10% of target, needs attention
- 🔴 Red = not measured, not started, or failing

NFR checks will be automated in CI as they become measurable (Phase 1+).
