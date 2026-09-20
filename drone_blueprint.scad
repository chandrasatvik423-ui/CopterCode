// COPTERCODE AUTO-GENERATED FRAME
// MISSION: quadcopter
// TOPOLOGY: 4 ARMS
// STATUS: PASSED

difference() {
    union() {
        // Central hub — height matches arm_height for joint continuity
        cube([39.5, 39.5, 6.0], center=true);
        rotate([0, 0, 45.0]) translate([62.5, 0, 0]) cube([125.0, 36.0, 6.0], center=true);
        rotate([0, 0, 45.0]) translate([125.0, 0, 0]) cylinder(h=6.0, d=32, center=true, $fn=50);
        rotate([0, 0, 135.0]) translate([62.5, 0, 0]) cube([125.0, 36.0, 6.0], center=true);
        rotate([0, 0, 135.0]) translate([125.0, 0, 0]) cylinder(h=6.0, d=32, center=true, $fn=50);
        rotate([0, 0, 225.0]) translate([62.5, 0, 0]) cube([125.0, 36.0, 6.0], center=true);
        rotate([0, 0, 225.0]) translate([125.0, 0, 0]) cylinder(h=6.0, d=32, center=true, $fn=50);
        rotate([0, 0, 315.0]) translate([62.5, 0, 0]) cube([125.0, 36.0, 6.0], center=true);
        rotate([0, 0, 315.0]) translate([125.0, 0, 0]) cylinder(h=6.0, d=32, center=true, $fn=50);

    }
    union() {
        // FC standoffs, battery slots
        translate([-15.25, -15.25, 0]) cylinder(h=8.0, d=3.0, center=true, $fn=20);
        translate([15.25, -15.25, 0]) cylinder(h=8.0, d=3.0, center=true, $fn=20);
        translate([15.25, 15.25, 0]) cylinder(h=8.0, d=3.0, center=true, $fn=20);
        translate([-15.25, 15.25, 0]) cylinder(h=8.0, d=3.0, center=true, $fn=20);
        translate([-12.0, 0.0, 0]) cube([3.0, 20.0, 8.0], center=true);
        translate([12.0, 0.0, 0]) cube([3.0, 20.0, 8.0], center=true);

        // Motor mount holes
        rotate([0, 0, 45.0]) translate([125.0, 0, 0]) {
            cylinder(h=8.0, d=11.200000000000001, center=true, $fn=30);
            translate([-8.0, -8.0, 0]) cylinder(h=8.0, d=3.0, center=true, $fn=20);
            translate([8.0, -8.0, 0]) cylinder(h=8.0, d=3.0, center=true, $fn=20);
            translate([8.0, 8.0, 0]) cylinder(h=8.0, d=3.0, center=true, $fn=20);
            translate([-8.0, 8.0, 0]) cylinder(h=8.0, d=3.0, center=true, $fn=20);
        }
        rotate([0, 0, 135.0]) translate([125.0, 0, 0]) {
            cylinder(h=8.0, d=11.200000000000001, center=true, $fn=30);
            translate([-8.0, -8.0, 0]) cylinder(h=8.0, d=3.0, center=true, $fn=20);
            translate([8.0, -8.0, 0]) cylinder(h=8.0, d=3.0, center=true, $fn=20);
            translate([8.0, 8.0, 0]) cylinder(h=8.0, d=3.0, center=true, $fn=20);
            translate([-8.0, 8.0, 0]) cylinder(h=8.0, d=3.0, center=true, $fn=20);
        }
        rotate([0, 0, 225.0]) translate([125.0, 0, 0]) {
            cylinder(h=8.0, d=11.200000000000001, center=true, $fn=30);
            translate([-8.0, -8.0, 0]) cylinder(h=8.0, d=3.0, center=true, $fn=20);
            translate([8.0, -8.0, 0]) cylinder(h=8.0, d=3.0, center=true, $fn=20);
            translate([8.0, 8.0, 0]) cylinder(h=8.0, d=3.0, center=true, $fn=20);
            translate([-8.0, 8.0, 0]) cylinder(h=8.0, d=3.0, center=true, $fn=20);
        }
        rotate([0, 0, 315.0]) translate([125.0, 0, 0]) {
            cylinder(h=8.0, d=11.200000000000001, center=true, $fn=30);
            translate([-8.0, -8.0, 0]) cylinder(h=8.0, d=3.0, center=true, $fn=20);
            translate([8.0, -8.0, 0]) cylinder(h=8.0, d=3.0, center=true, $fn=20);
            translate([8.0, 8.0, 0]) cylinder(h=8.0, d=3.0, center=true, $fn=20);
            translate([-8.0, 8.0, 0]) cylinder(h=8.0, d=3.0, center=true, $fn=20);
        }

    }
}
