
// Astro-Forge Engineering Standard v7.0
// Status: FAILED - REJECTED FOR FLIGHT
$fn = 64;
diagonal = 180;
arm_width = 12.0;
arm_height = 5.0;
motor_diam = 28;
pcb_l = 36.0;
pcb_w = 36.0;
thick = arm_height; // Synchronized with arm_height for joint continuity

module center_body() {
    difference() {
        hull() {
            cylinder(d=max(pcb_l, pcb_w) + 20, h=thick, center=true);
            cube([pcb_l + 15, pcb_w + 15, thick], center=true);
        }
        for(angle = [45.0, 135.0, 225.0, 315.0]) {
            rotate([0, 0, angle])
            translate([diagonal/4, 0, 0])
            cylinder(d=3.2, h=thick + 2, center=true);
        }
    }
    translate([0, pcb_w/2 + 3, 1])
    linear_extrude(2)
    text("standard racing drone", size=3, halign="center", valign="center");
    
    translate([0, -pcb_w/2 - 3, 1])
    linear_extrude(2)
    text("[REJECTED]", size=3, halign="center", valign="center");
    
}

module arm(length, width, height) {
    difference() {
        hull() {
            cylinder(d=width + 6, h=height, center=true);
            translate([length, 0, 0])
            cylinder(d=motor_diam + 4, h=height, center=true);
        }
        translate([length * 0.4, 0, 0])
        cube([length * 0.5, width * 0.35, height + 2], center=true);
        
        translate([length + (-8.0), -8.0, 0]) cylinder(d=3.0, h=height + 2, center=true);
        translate([length + (8.0), -8.0, 0]) cylinder(d=3.0, h=height + 2, center=true);
        translate([length + (8.0), 8.0, 0]) cylinder(d=3.0, h=height + 2, center=true);
        translate([length + (-8.0), 8.0, 0]) cylinder(d=3.0, h=height + 2, center=true);

    }
}

// Assembly
center_body();
for(angle = [45.0, 135.0, 225.0, 315.0]) {
    rotate([0, 0, angle])
    arm(diagonal/2, arm_width, arm_height);
}
