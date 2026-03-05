# ADR-001: Sensor/Motor Port Connector Type

| Field  | Value |
|--------|-------|
| **ID** | ADR-001 |
| **Date** | 2026-03 |
| **Status** | Accepted |
| **Origin** | Human |

## Context

OpenBrick EDU requires a physical connector for the 6 sensor/motor ports on
the hub. The connector must:

- Be available from Turkish domestic suppliers (Robotistan, Trendyol)
- Support 4 signal lines (power, ground, data+, data−) at minimum
- Fit inside a LEGO Technic-compatible housing (constrained by 8mm grid)
- Be robust enough for repeated classroom connect/disconnect cycles
- Be low-cost (target < $0.50 per port pair)
- Not require soldering for end-user assembly

## Decision

Use **RJ11 (6P4C)** connectors for all sensor and motor ports.

## Alternatives Considered

| Option | Reason Rejected |
|--------|----------------|
| JST-PH 4-pin | Harder to source domestically; smaller size makes classroom handling fiddly for ages 10–14 |
| USB-C | Overkill for sensor lines; adds cost; occupies the dedicated USB-C port slot |
| LEGO LPF2 (proprietary) | Requires reverse-engineering; legal risk; not available as off-the-shelf component |
| 3.5mm audio jack (TRRS) | Only 4 contacts; no locking mechanism; not designed for repeated I2C/PWM signals |
| Dupont/pin header | Not robust; pins bend; not suitable for student use |

## Consequences

- **Positive:** RJ11 is widely stocked in Turkey; cheap; sturdy locking tab; 6P4C gives 4 usable conductors (power, ground, data+, data−); familiar to makers.
- **Positive:** Stranded telephone cable can be used for custom sensor extensions.
- **Negative:** RJ11 is not the smallest connector; sensor housings must accommodate it within the LEGO Technic grid.
- **Negative:** Not compatible with LEGO LPF2 motors/sensors natively — an optional adapter board is planned post-MVP.
- **Neutral:** Pin assignment (power/ground/SDA/SCL or PWM) must be documented and enforced consistently across all port types. See `docs/bom.md` for wiring standard.
