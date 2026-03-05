# ADR-002: Motor Type for Angular Positioning

| Field  | Value |
|--------|-------|
| **ID** | ADR-002 |
| **Date** | 2026-03 |
| **Status** | Accepted |
| **Origin** | Human |

## Context

OpenBrick EDU requires at least one motor type capable of angular positioning
(target: ±2° repeatability per NFR). The motor must:

- Be sourceable from Robotistan (domestic Turkish supplier, confirmed stocked)
- Fit inside a LEGO Technic-compatible 3D-printed housing on the 8mm grid
- Support closed-loop position control (encoder feedback required)
- Operate at 3.3V–5V logic levels compatible with ESP32-S3 GPIO
- Cost under $6 USD per unit (BOM target)

## Decision

Use **N20 micro gear motor with magnetic Hall-effect encoder** as the primary
motor type for Phase 1 and Phase 2.

Sourced from: **Robotistan** (domestic, confirmed available).

## Alternatives Considered

| Option | Reason Rejected |
|--------|----------------|
| Geekservo LEGO-compatible servo | No encoder feedback; positioning relies on internal servo feedback only; less flexible for curriculum; higher cost |
| Standard RC servo (9g) | No continuous rotation without modification; no encoder; limited to 180° |
| LEGO LPF2 motor | Proprietary connector; not available as standalone component; legal ambiguity |
| Stepper motor (28BYJ-48) | Too large for LEGO-compatible housing; high current draw; slow; overkill for target age group |
| DC motor without encoder | No position feedback; cannot meet ±2° repeatability NFR |

## Consequences

- **Positive:** Magnetic encoder gives quadrature pulses for closed-loop PID control — meets ±2° repeatability NFR (NFR-P03).
- **Positive:** N20 form factor is compact; fits within LEGO Technic beam width (7.8mm) with a custom 3D-printed mount.
- **Positive:** Available from Robotistan; no import risk.
- **Negative:** Requires PID controller implementation in firmware (Day 3 of Phase 1 sprint).
- **Negative:** Encoder interrupt handling must be implemented carefully on ESP32-S3 to avoid missing pulses at high RPM.
- **Neutral:** Geekservo remains in the BOM alternatives table as a post-MVP option for simpler use cases where position precision is not required.

## Implementation Notes

- Encoder channels connect to ESP32-S3 GPIO with interrupt-driven pulse counting.
- PID controller tuning parameters live in `firmware/drivers/motor_n20.py`.
- Motor driver IC (L298N or DRV8833) required on hub PCB — see `docs/bom.md`.
