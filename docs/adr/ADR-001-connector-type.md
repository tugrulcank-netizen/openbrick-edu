# ADR-001: I/O Port Connector Type

**Date:** 2026-03-05
**Status:** Accepted
**Origin:** Human

## Context

The OpenBrick EDU hub needs 6 I/O ports for connecting sensors and motors. We need a standard connector that is durable, kid-friendly (ages 10–14), affordable, and available from Turkish domestic suppliers. The connector must carry 4 signals: VCC (3.3V), GND, and 2 data lines (I2C SDA/SCL or GPIO).

LEGO's proprietary LPF2 connector is not an option — it is not available as a standalone part and replicating it would add cost and complexity.

## Decision

**Use RJ11 (6P4C) connectors for all sensor and motor I/O ports.**

## Alternatives Considered

### RJ11 (6P4C) — CHOSEN
- 6-position, 4-conductor telephone-style jack
- Very robust — rated for thousands of insertions, withstands cable yanking by children
- Familiar form factor (phone cable) — easy for kids to plug and unplug
- Standard phone cables are cheap and widely available (~$0.50–1.00 per cable)
- Connectors cost ~$0.10–0.20 each
- Available from Robotistan, local electronics shops, and AliExpress
- Disadvantage: larger footprint than JST-PH, takes more PCB and housing space

### JST-PH (4-pin)
- Compact connector, saves PCB and housing space
- Cheap (~$0.05–0.10 per connector)
- Disadvantage: fragile locking tabs — can snap with rough handling by children
- Disadvantage: small size makes alignment difficult for ages 10–14
- Disadvantage: requires custom cables (not off-the-shelf)

### JST-XH (4-pin)
- Slightly larger than JST-PH, more robust
- Still requires custom cables
- Less kid-friendly than RJ11

## Consequences

- All hub housings must accommodate the larger RJ11 jack footprint (~14mm × 10mm per port)
- Standard 6P4C phone cables can be used — no custom cable manufacturing needed
- The PCB layout needs 6 × RJ11 jacks; this will influence minimum hub size
- Sensor and motor housings each need an RJ11 jack with strain relief
- Pin assignment standard (documented in docs/lego-specs.md):
  - Pin 1: VCC (3.3V)
  - Pin 2: SDA / GPIO1
  - Pin 3: SCL / GPIO2
  - Pin 4: GND
- An optional LPF2 adapter board can be designed post-MVP for users who own LEGO sensors/motors
