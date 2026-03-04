# OpenBrick EDU — LEGO Technic Dimensional Specifications

**Version:** 1.0  
**Date:** 2026-03-05  
**Status:** Authoritative reference — all hardware design MUST use these values  
**Authority:** This file is the single source of truth for all LEGO-compatible dimensions.  
**AI Agent Rule:** NEVER hardcode LEGO dimensions without referencing this file first.

---

## How to Use This File

1. **Before designing any 3D-printed part:** Read Section 2 (critical dimensions) and Section 4 (printer calibration).
2. **Before implementing any dimension in code or CAD:** Copy the value from the tables below — do not type from memory.
3. **After printing a part:** Run the fit tests in Section 6 and log results in `docs/validation-log.md`.
4. **When tolerances fail:** Consult Section 4 (printer adjustment) before changing the nominal values in this file.

> ⚠️ The nominal dimensions below are LEGO's actual specifications. The "3D print adjusted" values account for FDM shrinkage and over-extrusion. Always use the adjusted values for printed parts, not the nominal values.

---

## 1. LEGO Technic Grid System

LEGO Technic uses an **8mm modular grid**. Every hole, stud, and beam dimension is a multiple of 8mm (or a defined fraction of it). Understanding this grid is essential for all mechanical design.

```
    8mm      8mm      8mm
  ◄──────►◄──────►◄──────►
  ●        ●        ●        ●   ← Technic pin hole centers
  │        │        │        │
  ├────────┼────────┼────────┤   ← Beam top face
  │        │        │        │
  ├────────┼────────┼────────┤   ← Beam bottom face
     7.8mm beam width
```

All OpenBrick EDU housings must align their mounting holes to this 8mm grid so they interoperate with genuine LEGO Technic beams.

---

## 2. Critical Dimensions Table

This is the primary reference table. All values are in millimeters.

### 2.1 Core Grid Dimensions

| Parameter | Nominal (LEGO) | Tolerance | 3D Print Adjusted | Notes |
|-----------|---------------|-----------|-------------------|-------|
| Stud pitch (center-to-center) | 8.0 mm | ±0.05 mm | 8.0 mm | Grid unit — do not adjust |
| Plate height | 3.2 mm | ±0.05 mm | 3.2 mm | 1 plate = 3.2mm |
| Brick height (1 brick = 3 plates) | 9.6 mm | ±0.1 mm | 9.6 mm | |
| Beam width (studless Technic) | 7.8 mm | ±0.1 mm | 7.8 mm | Slightly under 8mm grid |

### 2.2 Technic Pin and Hole Dimensions

| Parameter | Nominal (LEGO) | Tolerance | 3D Print Adjusted | Notes |
|-----------|---------------|-----------|-------------------|-------|
| Technic pin hole diameter | 4.9 mm | ±0.1 mm | 5.1–5.3 mm | **Calibrate per printer — see Section 4** |
| Technic pin outer diameter | 4.8 mm | ±0.05 mm | N/A (not printed) | Reference only |
| Pin friction ridge diameter | 5.0 mm | ±0.05 mm | N/A | Creates friction fit |
| Pin length (short) | 15.8 mm | ±0.1 mm | N/A | Reference only |

> ⚠️ **Pin hole is the most critical dimension.** Too tight: pin won't insert. Too loose: pin falls out. Always run the calibration jig before printing functional parts. See Section 4.

### 2.3 Technic Axle Dimensions

| Parameter | Nominal (LEGO) | Tolerance | 3D Print Adjusted | Notes |
|-----------|---------------|-----------|-------------------|-------|
| Axle cross-hole width | 5.6 mm | ±0.1 mm | 5.8–6.0 mm | Cross-shaped hole, adjust per printer |
| Axle diameter (actual) | 5.5 mm | ±0.05 mm | N/A (not printed) | Reference only |
| Axle cross arm width | 1.8 mm | ±0.05 mm | N/A | Each arm of the cross |
| Axle cross arm height | 3.0 mm | ±0.05 mm | N/A | |

### 2.4 Stud Dimensions

| Parameter | Nominal (LEGO) | Tolerance | 3D Print Adjusted | Notes |
|-----------|---------------|-----------|-------------------|-------|
| Stud diameter | 4.8 mm | ±0.05 mm | 4.7 mm | Slightly smaller for fit |
| Stud height | 1.8 mm | ±0.05 mm | 1.8 mm | |
| Anti-stud (tube) inner diameter | 4.8 mm | ±0.05 mm | 5.0 mm | Inside bottom of bricks |
| Anti-stud (tube) outer diameter | 6.4 mm | ±0.1 mm | 6.4 mm | |

### 2.5 Technic Beam Dimensions

| Parameter | Nominal (LEGO) | Tolerance | Notes |
|-----------|---------------|-----------|-------|
| Beam height (1×N studless) | 7.8 mm | ±0.1 mm | Same as beam width |
| Beam length (N holes) | (N−1) × 8.0 + 7.8 mm | ±0.1 mm | e.g., 5-hole beam = 39.8mm |
| Hole center from beam edge | 3.9 mm | ±0.05 mm | Half of 7.8mm beam width |
| Hole spacing | 8.0 mm | ±0.05 mm | Grid pitch |
| Bearing hole center height | 5.8 mm from base | ±0.1 mm | For beams with lifting arms |

### 2.6 Connector and Housing Clearances

| Parameter | Value | Notes |
|-----------|-------|-------|
| Minimum wall thickness | 1.6 mm | Matches LEGO unit; structural minimum for FDM |
| Minimum fillet radius | 0.5 mm | NFR-R04 child safety requirement |
| RJ11 jack opening width | 13.0 mm | Allow ±0.3mm for insertion clearance |
| RJ11 jack opening height | 9.0 mm | Allow ±0.3mm |
| USB-C opening width | 9.5 mm | Allow ±0.3mm |
| USB-C opening height | 4.0 mm | Allow ±0.3mm |
| PCB standoff height | 3.0 mm | Between PCB and housing floor |
| PCB standoff M3 hole diameter | 3.2 mm | Clearance fit for M3 screw |

---

## 3. Minimum Mounting Requirements

Every OpenBrick EDU housing must meet these requirements to be LEGO-compatible:

| Requirement | Minimum | Notes |
|-------------|---------|-------|
| Technic pin holes per housing | 4 | Minimum for stable attachment |
| Faces with pin holes | 2 | Allows mounting from multiple directions |
| Pin hole grid alignment | 8.0mm grid | Holes must land exactly on 8mm grid |
| Part dimensions on grid | Yes | All outer dimensions should be multiples of 8mm where possible |

---

## 4. Printer Calibration Procedure

FDM printers vary significantly. The nominal LEGO dimensions will not work without calibration. **Always calibrate a new printer before printing functional parts.**

### 4.1 Calibration Jig

The calibration test jig is located at: `hardware/test-jigs/lego-calibration-jig.stl`

The jig contains a series of pin holes at 0.1mm increments from 4.7mm to 5.5mm, and axle cross-holes from 5.4mm to 6.2mm. Print the jig, then test genuine LEGO pins and axles in each hole.

### 4.2 Finding Your Printer's Offset

```
Step 1: Print the calibration jig at 0.2mm layer height, 3 walls, 20% infill.
Step 2: Test a genuine LEGO Technic pin in each pin hole row.
Step 3: Find the smallest hole where the pin inserts without force.
Step 4: Find the largest hole where the pin stays in without falling out.
Step 5: Your target hole diameter = midpoint of those two values.
Step 6: Calculate offset = target - 4.9mm (nominal).
Step 7: Apply this offset to all pin holes in your FreeCAD/OpenSCAD models.
Step 8: Repeat for axle cross-holes (nominal 5.6mm).
Step 9: Log your printer name and offsets in docs/validation-log.md.
```

### 4.3 Typical Offset Values by Printer Type

| Printer Type | Typical Pin Hole Offset | Typical Axle Hole Offset | Notes |
|-------------|------------------------|--------------------------|-------|
| Bambu Lab X1/P1 | +0.1 to +0.2 mm | +0.1 to +0.2 mm | Very consistent |
| Prusa MK3/MK4 | +0.1 to +0.3 mm | +0.2 to +0.3 mm | Consistent after calibration |
| Ender 3 (stock) | +0.2 to +0.4 mm | +0.3 to +0.4 mm | Higher variance; calibrate each print |
| Resin (MSLA) | −0.1 to +0.1 mm | −0.1 to +0.1 mm | Much tighter; use nominal values |

> These are starting estimates only. Always measure your specific printer.

### 4.4 Material Shrinkage Notes

| Material | Shrinkage | Recommendation |
|----------|-----------|----------------|
| PLA | ~0.3% | Acceptable for non-structural; limited temperature resistance |
| PETG | ~0.5% | **Recommended for structural housings** — good temp resistance, toughness |
| ABS | ~0.8% | Usable but warping risk; needs enclosure |
| ASA | ~0.6% | Good UV resistance; good for outdoor use |
| Resin | <0.1% | Excellent accuracy; brittle; not recommended for structural |

---

## 5. OpenSCAD / FreeCAD Parameter Names

When writing parametric CAD models, always use these exact variable names so models are consistent across the project.

```
// Core grid
STUD_PITCH          = 8.0;    // mm — never change
PLATE_HEIGHT        = 3.2;    // mm
BRICK_HEIGHT        = 9.6;    // mm
BEAM_WIDTH          = 7.8;    // mm

// Holes (nominal — override with printer offset in your slicer profile)
PIN_HOLE_NOMINAL    = 4.9;    // mm — LEGO spec
PIN_HOLE_PRINTED    = 5.2;    // mm — default FDM offset (+0.3); calibrate per printer
AXLE_HOLE_NOMINAL   = 5.6;    // mm — LEGO spec
AXLE_HOLE_PRINTED   = 5.9;    // mm — default FDM offset (+0.3); calibrate per printer

// Studs
STUD_DIAMETER       = 4.7;    // mm — slightly undersized for fit
STUD_HEIGHT         = 1.8;    // mm

// Safety
MIN_WALL            = 1.6;    // mm — minimum wall thickness
MIN_FILLET          = 0.5;    // mm — minimum fillet radius (child safety)

// Connectors
RJ11_WIDTH          = 13.0;   // mm — jack opening
RJ11_HEIGHT         = 9.0;    // mm — jack opening
USBC_WIDTH          = 9.5;    // mm — port opening
USBC_HEIGHT         = 4.0;    // mm — port opening
```

---

## 6. LEGO Fit Test Checklist

Run this checklist on every new 3D-printed housing before considering it complete. Log pass/fail results in `docs/validation-log.md` with photos.

### 6.1 Pin Hole Tests

| Test | Pass Criteria | Fail Action |
|------|--------------|-------------|
| Technic pin insertion (friction) | Inserts with light thumb pressure; holds without glue | Reprint with adjusted PIN_HOLE_PRINTED |
| Technic pin removal | Removable with fingers; does not require tools | Same as above |
| Technic pin (smooth) insertion | Inserts and spins freely | Increase PIN_HOLE_PRINTED by 0.1mm |
| Pin hole grid alignment | Pin holes align with genuine LEGO beam | Check STUD_PITCH = 8.0mm in model |
| Multi-hole beam alignment | 3-hole genuine beam mounts without stress | Check grid spacing accumulation |

### 6.2 Axle Tests

| Test | Pass Criteria | Fail Action |
|------|--------------|-------------|
| Axle insertion | Inserts with light pressure; no cracking | Increase AXLE_HOLE_PRINTED by 0.1mm |
| Axle rotation | Spins freely without wobble | Decrease AXLE_HOLE_PRINTED by 0.1mm |
| Axle retention | Does not slide out under gravity | Decrease AXLE_HOLE_PRINTED by 0.1mm |

### 6.3 Assembly Tests

| Test | Pass Criteria | Fail Action |
|------|--------------|-------------|
| Housing mounts to 5-hole beam | No visible gap; no stress whitening | Check beam width and grid alignment |
| Adjacent housing alignment | Two housings side-by-side align on 8mm grid | Check STUD_PITCH in model |
| Housing stackability | 1×3 beam sits flat on top of housing | Check BRICK_HEIGHT = 9.6mm |
| Flex/stress test | Housing does not crack at 2× expected load | Increase wall thickness; change to PETG |

### 6.4 Safety Tests

| Test | Pass Criteria | Fail Action |
|------|--------------|-------------|
| Edge sharpness | No sharp edges; all edges filleted ≥0.5mm | Add fillet in CAD; reprint |
| Small parts | No detachable parts smaller than 3cm | Redesign or add retention |
| Corner safety | All corners rounded ≥1.0mm | Add fillet |

---

## 7. Reference: Common LEGO Technic Part Dimensions

Quick reference for designing around common Technic parts:

| Part | Key Dimension | Notes |
|------|--------------|-------|
| Technic beam 1×5 | 39.8mm × 7.8mm × 7.8mm | 5 holes, 8mm pitch |
| Technic beam 1×9 | 71.8mm × 7.8mm × 7.8mm | 9 holes |
| Technic pin (friction) | Ø4.8mm × 15.8mm | Most common |
| Technic axle 3L | 24mm long | Ø5.5mm cross |
| Technic axle 5L | 40mm long | |
| Technic connector peg | Ø4.8mm × 15.8mm | Two-ended |
| Technic half-pin | Ø4.8mm × 7.8mm | Single stud end |
| Technic cross-axle connector | 15.8mm × 15.8mm | Joins two axles |

---

## 8. Change Log

| Date | Change | Author |
|------|--------|--------|
| 2026-03-05 | Initial version — all dimensions from project plan specs | AI-Assisted (Human-Approved) |

---

*This file is referenced by:*
- *`@.claude/skills/lego-compatibility-validation.md` — loaded during all hardware design sessions*
- *`@hardware/CLAUDE.md` — required reading for hardware subdirectory*
- *`@docs/architecture.md` — Section 6 (key constraints)*
- *All FreeCAD/OpenSCAD parametric models in `hardware/`*
