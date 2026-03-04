# Skill: LEGO Compatibility Validation

Load this skill when working on any 3D-printable housing, mechanical design, or fit testing for OpenBrick EDU.

---

## Complete LEGO Technic Dimensional Specification

### Primary Dimensions

| Parameter                    | Nominal (mm) | Tolerance (mm) | Notes                                    |
|-----------------------------|-------------|----------------|------------------------------------------|
| Stud pitch (center-to-center)| 8.000       | ±0.05          | Foundational grid — everything derives from this |
| Technic pin hole diameter    | 4.900       | ±0.10          | For injection-molded ABS; adjust for 3D print |
| Technic axle cross-hole width| 5.600       | ±0.10          | Cross-shaped; measure across flat faces   |
| Beam width (studless)        | 7.800       | ±0.10          | External width of a 1-wide Technic beam   |
| Plate height                 | 3.200       | ±0.05          | 1 plate unit                             |
| Brick height                 | 9.600       | ±0.10          | = 3 plates                               |
| Stud diameter                | 4.800       | ±0.05          | Top of brick/plate                       |
| Stud height                  | 1.700       | ±0.10          | Above top surface                        |
| Anti-stud (tube) inner dia   | 4.800       | ±0.05          | Bottom of brick                          |
| Anti-stud (tube) outer dia   | 6.310       | ±0.10          | Bottom of brick                          |
| Technic pin diameter         | 4.800       | ±0.05          | The pin itself (not the hole)            |
| Technic pin friction ridge   | 5.000       | ±0.05          | Raised section for friction fit          |
| Technic axle width (across flats) | 4.800  | ±0.05          | Measured across the flat faces           |
| Technic axle width (across points)| 5.600  | ±0.10          | Measured across the cross points         |
| Pin hole center height       | 5.800       | ±0.10          | From bottom of beam to hole center       |
| Half-stud offset             | 4.000       | ±0.05          | Half of stud pitch, used in offset grids |

### Derived Dimensions

| Parameter                          | Value (mm)    | Derivation                          |
|-----------------------------------|--------------|-------------------------------------|
| 2-wide beam width                  | 16.000       | 2 × stud pitch                     |
| Pin hole spacing (along beam)      | 8.000        | = stud pitch                        |
| Cross-axle to pin hole center      | 0.000        | Coaxial — same center point         |
| Beam end to first hole center      | 4.000        | = half stud pitch                   |
| Minimum housing length (2-hole)    | 16.000       | 2 × stud pitch (includes margins)   |
| Minimum housing width (1-wide)     | 7.800        | = beam width                        |

---

## 3D Print Tolerance Adjustment

### Why Adjustment Is Needed

Injection-molded ABS (LEGO's process) produces parts with ±0.02mm accuracy. FDM 3D printing typically achieves ±0.1–0.3mm depending on printer calibration, material, and feature orientation. Holes tend to print smaller than designed due to:
- First-layer squish reducing bottom opening
- Filament dragging at layer seams
- Thermal contraction during cooling

### Adjustment Formulas

**Pin holes (circular):**
```
Adjusted diameter = Nominal (4.9mm) + Printer Offset
```

| Printer Type / Quality  | Typical Offset | Adjusted Diameter |
|------------------------|---------------|-------------------|
| Well-calibrated FDM     | +0.1 to +0.2  | 5.0–5.1 mm       |
| Average FDM             | +0.2 to +0.4  | 5.1–5.3 mm       |
| SLA/MSLA resin          | +0.0 to +0.1  | 4.9–5.0 mm       |

**Axle holes (cross-shaped):**
```
Adjusted cross width = Nominal (5.6mm) + Printer Offset
```

| Printer Type / Quality  | Typical Offset | Adjusted Width |
|------------------------|---------------|----------------|
| Well-calibrated FDM     | +0.1          | 5.7 mm         |
| Average FDM             | +0.2 to +0.3  | 5.8–5.9 mm    |
| SLA/MSLA resin          | +0.0 to +0.1  | 5.6–5.7 mm    |

**Stud pitch:** No adjustment needed — this is a center-to-center distance, not a feature size.

### Calibration Procedure

1. Print the calibration test jig: `hardware/test-jigs/calibration-board.stl`
2. Using genuine LEGO Technic pins, test each hole diameter (4.8 to 5.7mm in 0.1mm steps)
3. Record the hole that gives a snug friction fit:
   - Too tight = pin won't insert or requires significant force
   - Correct = pin inserts with moderate pressure and holds when inverted
   - Too loose = pin falls out under gravity
4. Record the axle hole that gives correct fit for a standard Technic axle
5. Update `config/print_profile.json` with your values:
   ```json
   {
     "printer": "Ender 3 V2",
     "material": "PETG",
     "layer_height_mm": 0.2,
     "pin_hole_diameter_mm": 5.2,
     "axle_cross_width_mm": 5.8,
     "calibration_date": "2026-03-15",
     "notes": "Holes #4 and #5 both acceptable; chose 5.2 for slightly tighter fit"
   }
   ```
6. Re-run calibration whenever you change material, nozzle, or printer

---

## Fit Test Checklist

Run this checklist after every housing design change. Log results in `docs/validation-log.md`.

### Pin Hole Tests (test each hole on the housing)

- [ ] Standard LEGO Technic pin (black, with friction ridges) inserts and holds
- [ ] Standard LEGO Technic pin (grey/beige, frictionless) inserts smoothly
- [ ] 3L Technic pin inserts fully without binding
- [ ] Pin stays in place when housing is inverted (gravity test)
- [ ] Pin can be removed without tools (but requires intentional pull)
- [ ] Two housings connect via shared pin — alignment is correct
- [ ] Housing connects to a genuine LEGO Technic beam via pin — grid aligns

### Axle Hole Tests (test each axle hole)

- [ ] Standard LEGO Technic axle (length 2–4) inserts and rotates freely
- [ ] Axle does not wobble excessively (< 0.5mm lateral play)
- [ ] Axle with a bush/collar holds position

### Beam Compatibility Tests

- [ ] Housing width matches beam width (7.8mm) — fits in beam-width slots
- [ ] Pin holes on housing align with pin holes on adjacent LEGO beams
- [ ] Housing attaches securely to a standard LEGO Technic frame structure
- [ ] Multiple housings can be combined in a LEGO construction without interference

### Structural Tests

- [ ] Housing does not flex visibly under normal handling
- [ ] Snap-fit closure holds during vigorous use (shake test)
- [ ] Cable exits cleanly through connector opening without pinching
- [ ] PCB fits internally without interference with pin holes or mounting features
- [ ] No sharp edges — all external fillets ≥ 0.5mm (run finger along all edges)

### Grid Alignment Test

- [ ] Place housing on a LEGO Technic 15×1 beam — all pin holes align ±0.2mm
- [ ] Place housing between two parallel beams — width allows proper spacing
- [ ] Build a simple frame using only LEGO + the housing — structure is stable

---

## Validation Script Templates

### OpenSCAD Dimension Validator

Use this script to validate that a parametric model's dimensions are within tolerance:

```openscad
// lego_dimension_check.scad
// Run with: openscad -o /dev/null -D "check=true" lego_dimension_check.scad

// Nominal values
STUD_PITCH = 8.0;
PIN_HOLE_DIA = 4.9;       // Adjust for your printer profile
AXLE_CROSS = 5.6;         // Adjust for your printer profile
BEAM_WIDTH = 7.8;
BRICK_HEIGHT = 9.6;
PLATE_HEIGHT = 3.2;

// Tolerance bounds
PITCH_TOL = 0.05;
HOLE_TOL = 0.1;
AXLE_TOL = 0.1;
WIDTH_TOL = 0.1;

module check_dimension(name, actual, nominal, tolerance) {
    if (abs(actual - nominal) > tolerance) {
        echo(str("FAIL: ", name, " = ", actual, "mm (expected ", nominal, " ±", tolerance, "mm)"));
    } else {
        echo(str("PASS: ", name, " = ", actual, "mm"));
    }
}

// Example usage — call with your model's actual values:
// check_dimension("Pin hole 1 diameter", 5.15, PIN_HOLE_DIA, HOLE_TOL);
// check_dimension("Hole 1-2 pitch", 8.02, STUD_PITCH, PITCH_TOL);
```

### Python Measurement Validator

For post-print measurement verification using calipers:

```python
"""
lego_fit_validator.py
Record caliper measurements and validate against LEGO spec.
Usage: python lego_fit_validator.py measurements.json
"""
import json
import sys
from dataclasses import dataclass

@dataclass
class DimensionSpec:
    name: str
    nominal_mm: float
    tolerance_mm: float

LEGO_SPECS = [
    DimensionSpec("stud_pitch", 8.0, 0.05),
    DimensionSpec("pin_hole_dia", 4.9, 0.1),       # Use your printer-adjusted value
    DimensionSpec("axle_cross_width", 5.6, 0.1),    # Use your printer-adjusted value
    DimensionSpec("beam_width", 7.8, 0.1),
    DimensionSpec("brick_height", 9.6, 0.1),
    DimensionSpec("plate_height", 3.2, 0.05),
]

def validate(measurements: dict[str, float]) -> list[dict]:
    results = []
    for spec in LEGO_SPECS:
        if spec.name in measurements:
            actual = measurements[spec.name]
            deviation = abs(actual - spec.nominal_mm)
            passed = deviation <= spec.tolerance_mm
            results.append({
                "name": spec.name,
                "nominal": spec.nominal_mm,
                "actual": actual,
                "deviation": round(deviation, 3),
                "tolerance": spec.tolerance_mm,
                "status": "PASS" if passed else "FAIL",
            })
    return results

if __name__ == "__main__":
    with open(sys.argv[1]) as f:
        measurements = json.load(f)
    results = validate(measurements)
    for r in results:
        status = "✓" if r["status"] == "PASS" else "✗"
        print(f"  {status} {r['name']}: {r['actual']}mm (target {r['nominal']}±{r['tolerance']}mm, dev {r['deviation']}mm)")
    failures = [r for r in results if r["status"] == "FAIL"]
    if failures:
        print(f"\n{len(failures)} FAILED — adjust printer profile or model dimensions.")
        sys.exit(1)
    else:
        print(f"\nAll {len(results)} checks PASSED.")
```

---

## Common Fit Problems and Solutions

| Problem                           | Likely Cause                        | Fix                                        |
|----------------------------------|-------------------------------------|---------------------------------------------|
| Pins won't insert                | Hole too small                      | Increase PIN_HOLE_DIA_3DP by 0.1mm; re-calibrate |
| Pins fall out                    | Hole too large                      | Decrease PIN_HOLE_DIA_3DP by 0.1mm         |
| Axle won't rotate               | Cross-hole too tight                | Increase AXLE_CROSS by 0.1mm               |
| Axle wobbles excessively         | Cross-hole too large                | Decrease AXLE_CROSS by 0.1mm               |
| Holes misalign with LEGO beam   | Pitch error or rounding             | Check that hole spacing is exact multiples of 8.0mm |
| Housing too wide for LEGO frame | Beam width exceeded                 | Verify outer width ≤ 7.8mm per unit width  |
| Layer separation at pin holes   | Weak inter-layer adhesion           | Increase print temperature; use PETG; orient holes perpendicular to layers |
| Snap-fit too loose after use    | Material creep (PLA)                | Switch to PETG for snap-fit features       |
