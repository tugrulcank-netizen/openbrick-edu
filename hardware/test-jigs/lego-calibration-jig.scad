// OpenBrick EDU -- LEGO Technic Calibration Test Jig
// Purpose: Measure printer offset for pin holes and axle holes
// Print in PETG, 0.2mm layer height, 3 walls, 20% infill, no supports
// After printing: test fit with real LEGO Technic pin and axle
// Log results in docs/validation-log.md

// Nominal LEGO dimensions (from docs/lego-specs.md)
STUD_PITCH     = 8.0;
PIN_HOLE_NOM   = 4.9;
AXLE_HOLE_NOM  = 5.6;
WALL_MIN       = 1.6;

// Test matrix: 7 pin holes, nominal +/-0.2mm + full FDM-adjusted range (5.1-5.3mm)
PIN_SIZES = [4.7, 4.8, 4.9, 5.0, 5.1, 5.2, 5.3];

// Plate dimensions
COLS    = 7;
ROWS    = 2;
PLATE_W = COLS * STUD_PITCH * 2;
PLATE_H = ROWS * STUD_PITCH * 3;
PLATE_T = 4.8;

// Main plate
difference() {
    cube([PLATE_W, PLATE_H, PLATE_T]);

    // Row 0: Pin holes (round) -- 7 sizes
    for (i = [0:6]) {
        translate([STUD_PITCH + i * STUD_PITCH * 2, STUD_PITCH * 1.5, -0.1])
        cylinder(h = PLATE_T + 0.2, d = PIN_SIZES[i], $fn = 64);
    }

    // Row 1: Axle holes (cross shape) -- fixed nominal size
    for (i = [0:6]) {
        translate([STUD_PITCH + i * STUD_PITCH * 2, STUD_PITCH * 4.5, -0.1]) {
            cube([AXLE_HOLE_NOM, 1.8, PLATE_T + 0.2], center = true);
            cube([1.8, AXLE_HOLE_NOM, PLATE_T + 0.2], center = true);
        }
    }
}

// Labels (raised text)
for (i = [0:6]) {
    translate([STUD_PITCH + i * STUD_PITCH * 2 - 2.5, STUD_PITCH * 0.3, PLATE_T])
    linear_extrude(0.6)
    text(str(PIN_SIZES[i]), size = 2.5, font = "Liberation Sans");}
