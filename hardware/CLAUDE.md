# OpenBrick EDU — Hardware Instructions

3D-printable LEGO Technic-compatible housings and PCB design.

## Design Tools

- **3D Modeling:** FreeCAD or OpenSCAD (parametric models required)
- **PCB Design:** KiCad 8+
- **Slicer:** PrusaSlicer or Cura (provide recommended profiles)
- **Validation:** Physical fit test with genuine LEGO Technic elements

## LEGO Dimensional Constants

ALL dimensions are defined as named constants in parametric models. NEVER use magic numbers.

```
STUD_PITCH         = 8.0      # mm, center-to-center (±0.05)
PIN_HOLE_DIA       = 4.9      # mm, standard Technic pin hole (±0.1)
PIN_HOLE_DIA_3DP   = 5.1–5.3  # mm, adjusted for 3D print shrinkage (CALIBRATE PER PRINTER)
AXLE_CROSS_WIDTH   = 5.6      # mm, cross-section width (±0.1)
BEAM_WIDTH         = 7.8      # mm, studless beam width (±0.1)
PLATE_HEIGHT       = 3.2      # mm (±0.05)
BRICK_HEIGHT       = 9.6      # mm = 3 plates (±0.1)
STUD_DIA           = 4.8      # mm (±0.05)
BEARING_HOLE_CTR_H = 5.8      # mm from base (±0.1)
```

**Full specification with tolerance adjustment formulas:** load skill `@.claude/skills/lego-compatibility-validation.md`

## 3D Printing Rules

| Rule                          | Value / Guideline                                     |
|------------------------------|-------------------------------------------------------|
| Minimum wall thickness       | 1.6 mm (matches LEGO unit dimension)                  |
| Structural material          | PETG or ABS (required for load-bearing housings)      |
| Non-structural material      | PLA acceptable (covers, decorative elements)          |
| Print orientation            | MUST be specified per STL to maximize pin hole accuracy|
| Support material              | Minimize — design for supportless printing where possible |
| Pin holes orientation        | Print perpendicular to build plate when possible       |
| Infill (structural)          | ≥ 40% for mounting points, ≥ 20% elsewhere            |
| Layer height (dimensional)   | 0.15–0.20 mm for Technic features                     |

## Housing Design Requirements

Every housing MUST include:

1. **≥ 4 Technic pin holes on ≥ 2 faces** — for versatile mounting to LEGO structures
2. **Pin holes on the 8mm grid** — center-to-center distance is always a multiple of 8.0mm
3. **Connector opening** — sized for RJ11 (6P4C) or JST-PH cable exit with strain relief
4. **Internal PCB mounting bosses** — M2 or M2.5 screw posts or snap-fit rails
5. **Fillet on ALL external edges** — minimum 0.5mm radius (child safety, NFR-R04)
6. **Snap-fit or screw closure** — tool-free assembly preferred (NFR-U04)

## Calibration Test Jig

The calibration test jig (`hardware/test-jigs/calibration-board.stl`) is the first thing users print. It contains:

- 10 pin holes at standard diameter (4.9mm target)
- 10 pin holes at adjusted diameters (4.8, 4.9, 5.0, 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7mm)
- 4 axle cross-holes at standard and ±0.1mm variations
- Stud pitch verification grid (4×4)
- Beam width slot
- Measurement reference marks with dimension labels

Users test with genuine LEGO Technic pins and axles, identify which hole size gives the best fit, and adjust the `PIN_HOLE_DIA_3DP` constant in their parametric model accordingly.

## PCB Design Conventions (KiCad)

- **Schematic:** Hierarchical sheets — one per subsystem (power, MCU, I/O ports, LEDs, audio)
- **Net naming:** Use descriptive names: `ESP_SDA1`, `PORT3_SCL`, `VBAT_SENSE`, `MOTOR_PWM_A`
- **Decoupling:** 100nF ceramic cap within 5mm of every IC power pin
- **USB-C:** CC resistors (5.1kΩ to GND) for proper device detection
- **BLE antenna:** Keep 10mm copper-free zone around ESP32-S3 antenna area
- **I/O protection:** TVS diodes or series resistors on all external-facing I/O pins
- **Connector footprints:** Verify 3D model alignment with housing STL before ordering PCB

## Connector Strategy

| Connector   | Use Case            | Pin Count | Notes                              |
|------------|---------------------|-----------|-------------------------------------|
| RJ11 (6P4C)| Sensor/motor ports  | 4 (of 6)  | Power + I2C/GPIO; easy to source    |
| JST-PH     | Alt: sensor ports   | 4         | Smaller footprint; less robust      |
| USB-C      | Programming/charge  | —         | Data + 5V charging                  |
| JST-XH     | Battery connection  | 2         | Internal only; keyed, no reverse    |

**Decision recorded in:** `docs/adr/ADR-001-connector-type.md`

## Part Naming Convention

```
openbrick_{component}_{variant}_v{version}.stl
```

Examples:
- `openbrick_hub_top_v1.stl`
- `openbrick_hub_bottom_v1.stl`
- `openbrick_sensor_color_housing_v2.stl`
- `openbrick_motor_mount_geekservo_v1.stl`
- `openbrick_battery_housing_v1.stl`
- `openbrick_test_jig_calibration_v1.stl`

## Fit Testing Protocol

After every housing design change:

1. Print on at least one FDM printer at 0.2mm layer height, PETG
2. Test ALL pin holes with genuine LEGO Technic pins (friction fit, not loose, not impossible)
3. Test ALL axle holes with genuine LEGO Technic axles
4. Test beam-width slots with genuine LEGO Technic beams
5. Attach to a real LEGO Technic structure — verify it holds under gentle load
6. Log results in `docs/validation-log.md` with date, printer model, material, pass/fail per feature
7. Photograph and commit photos to `docs/validation-photos/`

**Target: ≥ 95% fit test pass rate** (NFR requirement)

## AI Agent Limitations for Hardware

- **3D modeling:** The agent CANNOT create or edit 3D models directly. It CAN review parametric dimension tables, generate OpenSCAD scripts, and validate that dimensions match the LEGO spec.
- **PCB design:** The agent CANNOT use KiCad interactively. It CAN review netlists, check pin assignments, generate schematic review checklists, and write KiCad scripting plugins.
- **Physical testing:** The agent has NO access to physical results. Always log results in `docs/validation-log.md` so the agent has context in future sessions.

## Critical Rules

- NEVER use magic numbers for LEGO dimensions — always reference named constants
- NEVER skip the calibration jig step when changing print settings or printers
- NEVER finalize a housing without physical fit testing with genuine LEGO parts
- ALWAYS specify print orientation in the STL metadata or README
- ALWAYS maintain ≥ 0.5mm fillets on all external edges (child safety)
- ALWAYS update `docs/validation-log.md` after every hardware test
- When working on any housing design, load `@.claude/skills/lego-compatibility-validation.md`
