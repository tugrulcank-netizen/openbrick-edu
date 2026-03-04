# ADR-002: Motor Selection

**Date:** 2026-03-05
**Status:** Accepted
**Origin:** Human

## Context

The OpenBrick EDU platform needs motors for driving wheels, mechanisms, and robotic arms in educational projects. Requirements: 3.3–6V operation (battery powered), position feedback for angular control (±2° target), small enough to fit in a LEGO Technic-compatible 3D-printed housing, and available from Turkish domestic suppliers. The platform targets ages 10–14 and must support both continuous rotation (wheels) and angular positioning (arms).

AliExpress sourcing was ruled out due to long shipping times, customs unpredictability, and support difficulties — local Turkish suppliers are strongly preferred for all critical components.

## Decision

**Use N20 micro gear motors with 12 CPR magnetic encoders as the primary motor, sourced from Robotistan.**

A custom 3D-printed LEGO Technic-compatible housing with axle cross-hole output will be designed to mount the N20 motor and provide LEGO mechanical integration.

## Alternatives Considered

### N20 + Magnetic Encoder — CHOSEN
- GA12-N20 micro DC motor with metal gearbox (~100–300 RPM variants available)
- 12 CPR magnetic encoder board solders directly to motor back
- Precise closed-loop position control with PID: ±2° achievable
- Continuous 360° rotation for wheel drive applications
- 3.3–6V operating range matches hub power system
- Domestically available: Robotistan stocks both motor and encoder
- Cost: ~$3–5 total (motor + encoder)
- Disadvantage: not LEGO-native — requires custom 3D-printed mount with Technic axle adapter
- Disadvantage: 4+4 wires (motor + encoder) — more complex wiring than servo
- Disadvantage: requires H-bridge motor driver circuit on hub PCB (L298N or DRV8833)

### Geekservo LEGO-Compatible Motor
- Native LEGO Technic axle output — plug-and-play with LEGO builds
- Simple 2-wire connection (VCC + GND)
- PWM speed control
- Disadvantage: no position encoder — open-loop control only (±5° at best)
- Disadvantage: NOT available from Turkish domestic suppliers — AliExpress only
- Disadvantage: open-loop means no accurate angular positioning for robotics tasks
- Disadvantage: "jumping teeth" clutch protection limits torque applications

### Standard Micro Servo (SG90/MG90S)
- Very cheap (~$1–2), widely available at Robotistan
- Built-in position control (potentiometer feedback)
- 3-wire connection (simple)
- Disadvantage: limited to 180° rotation — cannot drive wheels
- Disadvantage: potentiometer feedback is less accurate than encoder (±5°)
- Disadvantage: not LEGO-compatible — needs custom mount
- Disadvantage: cannot do continuous rotation without modification

## Consequences

- Hub PCB must include H-bridge motor driver channels (DRV8833 or similar) for N20 motors
- Hub PCB must include encoder input pins (2 GPIO per motor for quadrature decoding)
- RJ11 connector pin assignment for motor ports needs 4+ signals — may need to use all 6 pins of RJ11:
  - Pin 1: Motor+ (H-bridge output)
  - Pin 2: Motor- (H-bridge output)
  - Pin 3: Encoder A
  - Pin 4: Encoder B
  - Pin 5: VCC (3.3V for encoder)
  - Pin 6: GND
  - **Note:** This means motor ports use 6P6C (full RJ11) while sensor ports use 6P4C — same physical jack, different wiring
- Firmware HAL Motor class must implement PID controller with encoder feedback
- A 3D-printed LEGO Technic-compatible motor housing must be designed with:
  - Technic pin holes on at least 2 faces for mounting
  - Axle cross-hole output shaft adapter (5.6mm ±0.1mm)
  - Strain relief for RJ11 cable entry
- Motor calibration procedure must be documented for initial PID tuning
- Geekservo support can be added post-MVP as an optional "simple motor" module if demand exists
