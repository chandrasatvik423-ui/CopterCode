// COPTERCODE AUTO-GENERATED FRAME
// MISSION: Test Drone
// TOPOLOGY: 4 ARMS
// STATUS: PASSED

difference() {
    union() {
        // Central hub — height matches arm_height for joint continuity
        cube([36.0, 36.0, 5.0], center=true);
        rotate([0, 0, 45.0]) translate([55.0, 0, 0]) cube([110.0, 30.0, 5.0], center=true);
        rotate([0, 0, 45.0]) translate([110.0, 0, 0]) cylinder(h=5.0, d=32.0, center=true, $fn=50);
        rotate([0, 0, 135.0]) translate([55.0, 0, 0]) cube([110.0, 30.0, 5.0], center=true);
        rotate([0, 0, 135.0]) translate([110.0, 0, 0]) cylinder(h=5.0, d=32.0, center=true, $fn=50);
        rotate([0, 0, 225.0]) translate([55.0, 0, 0]) cube([110.0, 30.0, 5.0], center=true);
        rotate([0, 0, 225.0]) translate([110.0, 0, 0]) cylinder(h=5.0, d=32.0, center=true, $fn=50);
        rotate([0, 0, 315.0]) translate([55.0, 0, 0]) cube([110.0, 30.0, 5.0], center=true);
        rotate([0, 0, 315.0]) translate([110.0, 0, 0]) cylinder(h=5.0, d=32.0, center=true, $fn=50);

    }
    union() {
        // FC standoffs, battery slots

        // Motor mount holes
        rotate([0, 0, 45.0]) translate([110.0, 0, 0]) {
            cylinder(h=7.0, d=11.200000000000001, center=true, $fn=30);
            translate([-8.0, -8.0, 0]) cylinder(h=7.0, d=3.0, center=true, $fn=20);
            translate([8.0, -8.0, 0]) cylinder(h=7.0, d=3.0, center=true, $fn=20);
            translate([8.0, 8.0, 0]) cylinder(h=7.0, d=3.0, center=true, $fn=20);
            translate([-8.0, 8.0, 0]) cylinder(h=7.0, d=3.0, center=true, $fn=20);
        }
        rotate([0, 0, 135.0]) translate([110.0, 0, 0]) {
            cylinder(h=7.0, d=11.200000000000001, center=true, $fn=30);
            translate([-8.0, -8.0, 0]) cylinder(h=7.0, d=3.0, center=true, $fn=20);
            translate([8.0, -8.0, 0]) cylinder(h=7.0, d=3.0, center=true, $fn=20);
            translate([8.0, 8.0, 0]) cylinder(h=7.0, d=3.0, center=true, $fn=20);
            translate([-8.0, 8.0, 0]) cylinder(h=7.0, d=3.0, center=true, $fn=20);
        }
        rotate([0, 0, 225.0]) translate([110.0, 0, 0]) {
            cylinder(h=7.0, d=11.200000000000001, center=true, $fn=30);
            translate([-8.0, -8.0, 0]) cylinder(h=7.0, d=3.0, center=true, $fn=20);
            translate([8.0, -8.0, 0]) cylinder(h=7.0, d=3.0, center=true, $fn=20);
            translate([8.0, 8.0, 0]) cylinder(h=7.0, d=3.0, center=true, $fn=20);
            translate([-8.0, 8.0, 0]) cylinder(h=7.0, d=3.0, center=true, $fn=20);
        }
        rotate([0, 0, 315.0]) translate([110.0, 0, 0]) {
            cylinder(h=7.0, d=11.200000000000001, center=true, $fn=30);
            translate([-8.0, -8.0, 0]) cylinder(h=7.0, d=3.0, center=true, $fn=20);
            translate([8.0, -8.0, 0]) cylinder(h=7.0, d=3.0, center=true, $fn=20);
            translate([8.0, 8.0, 0]) cylinder(h=7.0, d=3.0, center=true, $fn=20);
            translate([-8.0, 8.0, 0]) cylinder(h=7.0, d=3.0, center=true, $fn=20);
        }

    }
}
