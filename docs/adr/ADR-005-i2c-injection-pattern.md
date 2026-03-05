# ADR-005: I2C Bus Injection Pattern for Sensor Drivers

| Field  | Value |
|--------|-------|
| **ID** | ADR-005 |
| **Date** | 2026-03 |
| **Status** | Accepted |
| **Origin** | AI-Suggested & Human-Approved |

## Context

During Phase 1, Day 1 (MPU6050 IMU driver implementation), a decision was made
about how sensor drivers receive their I2C bus instance. This pattern will be
reused by every sensor driver in the project (color, distance, force, and any
future sensors), so it needs to be established as a standard early.

Two approaches were possible:

1. **Driver creates its own I2C bus** using `machine.I2C(...)` internally.
2. **I2C bus is injected** at driver construction time as a parameter.

The choice affects testability, resource sharing, and coupling to MicroPython's
`machine` module.

## Decision

**Inject the I2C bus at construction time.**

All sensor drivers accept an `i2c` parameter in `__init__`:

```python
class MPU6050(Sensor):
    def __init__(self, port: int, i2c):
        super().__init__(port)
        self._i2c = i2c
```

The hub firmware (HAL port manager) is responsible for creating and owning the
I2C bus instance, then passing it to each driver on the appropriate port.

## Alternatives Considered

| Option | Reason Rejected |
|--------|----------------|
| Driver creates its own I2C bus | Couples driver to `machine.I2C`; impossible to unit test without hardware; two drivers on the same I2C bus would create conflicting bus instances |
| Global I2C singleton | Hides dependency; makes test setup non-obvious; creates ordering issues during boot |
| I2C passed via `init()` method | Splits construction from dependency injection; driver is in an invalid state between `__init__` and `init()` |

## Consequences

- **Positive:** All 24 MPU6050 unit tests run without physical hardware or mocking `machine` — MockI2C is passed directly.
- **Positive:** Multiple sensors on the same I2C bus share one bus instance — no bus conflicts.
- **Positive:** Every future sensor driver follows the same pattern — new contributors (and AI agents) can reference `mpu6050.py` as the canonical example.
- **Negative:** Slightly more boilerplate in the HAL port manager (must create and pass I2C instances).
- **Neutral:** This pattern is standard in embedded Python (MicroPython community calls it "dependency injection by convention").

## Implementation Notes

- The I2C bus creation and port-to-bus mapping lives in `firmware/hal/port_manager.py` (to be implemented in Phase 1, Day 5).
- The mock I2C pattern for tests is established in `firmware/tests/drivers/test_mpu6050.py` — use `_make_mock_i2c()` as the template for all future driver tests.
- CLAUDE.md should reference this ADR when the agent implements new sensor drivers.
