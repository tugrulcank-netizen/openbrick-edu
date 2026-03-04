# OpenBrick EDU — Safety Checklist

Complete at the end of every hardware phase. Photograph results and commit to the repo.

---

## Mechanical Safety (NFR-R04)

| Check | Pass? | Notes | Photo? |
|---|---|---|---|
| No sharp edges on any housing | ☐ | Run finger along all edges | ☐ |
| All external fillets ≥ 0.5mm | ☐ | Measure with calipers | ☐ |
| No detachable parts smaller than 3cm | ☐ | Small parts = choking hazard | ☐ |
| Snap-fit closures hold under vigorous use | ☐ | Shake test | ☐ |
| No pinch points in moving parts | ☐ | Check motor mounts, hinges | ☐ |
| Cable strain relief prevents wire exposure | ☐ | Pull test on connectors | ☐ |

## Electrical Safety (NFR-R03)

| Check | Pass? | Notes | Photo? |
|---|---|---|---|
| All I/O ports limited to 3.3V | ☐ | Multimeter verification | ☐ |
| All I/O ports limited to 500mA | ☐ | Current limit test | ☐ |
| Short-circuit protection on all ports | ☐ | Short each port, verify no damage | ☐ |
| USB-C wiring correct (CC resistors present) | ☐ | Schematic review + multimeter | ☐ |
| No exposed conductors accessible from outside | ☐ | Visual inspection | ☐ |

## Battery Safety (NFR-R02)

| Check | Pass? | Notes | Photo? |
|---|---|---|---|
| BMS low-voltage cutoff at 2.8V | ☐ | Discharge test with logging | ☐ |
| BMS charge cutoff at 4.2V | ☐ | Charge test with logging | ☐ |
| Thermal cutoff at 60°C | ☐ | Heat test (use heat gun near sensor) | ☐ |
| Battery housing prevents cell puncture | ☐ | Drop test from 1m | ☐ |
| Charging auto-stops when full | ☐ | Leave on charge overnight, check voltage | ☐ |
| TP4056 module securely mounted | ☐ | Shake test | ☐ |

---

## Sign-Off

| Phase | Date | All Checks Pass? | Signed |
|---|---|---|---|
| Phase 1: Core Loop | | ☐ | |
| Phase 2: Sensors | | ☐ | |
| Phase 3: Polish | | ☐ | |
| Pre-Launch | | ☐ | |
