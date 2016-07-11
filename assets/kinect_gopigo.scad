difference() {
    union() {
        import("kinect3C.stl");
        
        // For measurement
        //translate([0, -20, 0])
        //    cube(size=[110, 1, 20], center=true);
        //translate([-56, 0, 0])
        //    cube(size=[2, 40, 20], center=true);
        //translate([56, 0, 0])
        //    cube(size=[2, 40, 20], center=true);
        //translate([50, 0, 0])
        //    cube(size=[5, 40, 20], center=false);
        //translate([-50-5, -20, 5])
        //    cube(size=[5, 40, 20], center=false);
        //translate([-50, -15, 0])
        //    cube(size=[10, 4.5, 20], center=false);
        //translate([-50, 15-4.5, 0])
        //    cube(size=[10, 4.5, 20], center=false);
        //translate([-50, 2.5, 0])
        //    cube(size=[10, 3, 20], center=false);
        //translate([-50, -2.5-3, 0])
        //    cube(size=[10, 3, 20], center=false);
        
        // Extensions: original is 40mm, we want 55mm. The end of the original piece is rounded, so add 6mm overlap to compensate.
        extension_length = 55-40+6;
        translate([40-6,-15,0]) {
            cube(size=[extension_length, 30, 5], center=false);
        }
        translate([-(40-6)-extension_length,-15,0]) {
            cube(size=[extension_length, 30, 5], center=false);
        }
    }
    
    // Screw holes
    screw_radius = 2.5;
    screw_fn = 40;
    screw_x = 55-5-screw_radius;
    screw_y = screw_radius+3+screw_radius;
    translate([-screw_x, screw_y, 0], $fn=screw_fn) 
        cylinder(h=20, r=screw_radius, center=true);
    translate([-screw_x, 0, 0], $fn=screw_fn) 
        cylinder(h=20, r=screw_radius, center=true);
    translate([-screw_x, -screw_y, 0]) 
        cylinder(h=20, r=screw_radius, center=true, $fn=screw_fn);
    
    translate([screw_x, screw_y, 0], $fn=screw_fn) 
        cylinder(h=20, r=screw_radius, center=true);
    translate([screw_x, 0, 0], $fn=screw_fn) 
        cylinder(h=20, r=screw_radius, center=true);
    translate([screw_x, -screw_y, 0]) 
        cylinder(h=20, r=screw_radius, center=true, $fn=screw_fn);
}
