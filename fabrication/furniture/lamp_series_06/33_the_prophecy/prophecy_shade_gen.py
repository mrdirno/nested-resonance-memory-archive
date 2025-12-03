import numpy as np
import math
import sys
import struct
import os

# Add project root to path for library import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES 06: THE PROPHECY (SHADE)
# -----------------------------------------------------------------------------
# Logic: The All-Seeing Eye (Cyclopean).
# Method: Large central aperture (Iris) with radiating mechanical iris blades.
# Standard: V7 (Spider Fitter, 14mm Hole, 25.4mm Wall).
# -----------------------------------------------------------------------------

def generate_shade(output_path, diameter=200.0, height=180.0, resolution=120, hole_diameter=14.0):
    print(f"Generating THE PROPHECY SHADE: {output_path}")
    
    # Mount Parameters
    mount_hole_radius = hole_diameter / 2.0 
    hub_radius = 20.0 
    spoke_width = 8.0 
    top_plate_height = 4.0
    bottom_rim_height = 4.0
    
    # Shell Parameters
    wall_thickness = 25.4 
    hand_access_radius = 45.0 
    
    # Grid Setup
    max_dim = max(diameter, height)
    step = max_dim / resolution
    
    res_x = int(diameter / step) + 5
    res_y = int(diameter / step) + 5
    res_z = int(height / step) + 1
    
    print(f"Grid: {res_x}x{res_y}x{res_z} (Voxel size: {step:.2f}mm)")
    
    grid = np.zeros((res_x, res_y, res_z), dtype=bool)
    
    # Eye Logic
    # A spherical shell with a large hole in the front? 
    # Lamps shade usually open at bottom and top.
    # Let's make the "Pupil" the side feature?
    # Or implies the whole shade is the eye.
    
    # Mechanical Iris Pattern
    # Overlapping blades spiraling into a center.
    # Center of iris is the top mount? No, that's standard.
    # Let's make the iris pattern visible on the walls.
    
    # "Cyclopean Geometry"
    # A large lens-like structure on one side?
    # No, symmetry is better for lamps usually (spinning).
    # Let's do a "Panopticon" - Eyes everywhere?
    # Or one big eye looking UP (towards the light source).
    
    # Plan: Mechanical Iris Aperture look.
    # Spiraling blades from bottom to top.
    
    num_blades = 12
    twist = math.pi / 2.0 # 90 degrees twist
    
    print("Foreseeing the Future...")
    
    radius = diameter / 2.0
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        z_norm = z_mm / height
        
        # Taper: Spherical / Eyeball shape
        # z from 0 to height.
        # Center at height/2
        z_rel = (z_mm - height/2.0) / (height/2.0) # -1 to 1
        
        # Sphere radius profile
        # r = sqrt(1 - z^2)
        # Squashed sphere
        sphere_profile = math.sqrt(max(0.0, 1.0 - z_rel*z_rel))
        current_radius = radius * sphere_profile
        
        # Ensure minimum radius at top/bottom for fitting/access
        min_r = 50.0
        if current_radius < min_r: current_radius = min_r
        
        # Twist for blades
        angle_offset = z_norm * twist
        
        for x_idx in range(res_x):
            x_mm = (x_idx * step) - (diameter / 2.0)
            
            for y_idx in range(res_y):
                y_mm = (y_idx * step) - (diameter / 2.0)
                
                dist_xy = math.sqrt(x_mm**2 + y_mm**2)
                angle = math.atan2(y_mm, x_mm)
                
                # --- PRIORITY 1: SPIDER FITTER ---
                fitter_override = lamp_lib.apply_spider_fitter(
                    x_mm, y_mm, z_mm, dist_xy,
                    mount_z_start=(height - top_plate_height),
                    mount_hole_radius=mount_hole_radius,
                    hub_radius=hub_radius,
                    spoke_width=spoke_width,
                    outer_radius=radius
                )
                
                if fitter_override is not None:
                    grid[x_idx,y_idx,z_idx] = fitter_override
                    continue

                # --- PRIORITY 2: BOTTOM RIM ---
                if z_mm < bottom_rim_height:
                    if dist_xy < radius and dist_xy > hand_access_radius:
                         grid[x_idx,y_idx,z_idx] = True
                         continue

                # --- PRIORITY 3: PROPHECY SHELL ---
                
                if dist_xy > radius:
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                    
                if dist_xy < (radius - wall_thickness):
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                    
                # Iris Blade Pattern
                # Sawtooth wave around the circumference
                
                local_angle = angle + angle_offset
                
                # Blade function
                # 0 to 1 ramp repeated
                blade_phase = (local_angle * num_blades / (2*math.pi)) % 1.0
                
                # Overlap blades?
                # Solid if phase < 0.8 (gap of 0.2)
                
                is_solid = False
                if blade_phase < 0.85:
                    is_solid = True
                    
                # Constrain to the spherical envelope
                if dist_xy > current_radius: is_solid = False
                if dist_xy < (current_radius - 10.0): is_solid = False # Shell thickness
                
                # Hand access override
                if dist_xy < hand_access_radius: is_solid = False
                
                # Add a "Pupil" ring in the middle?
                # Horizontal ring at equator
                if abs(z_mm - height/2.0) < 5.0:
                    if dist_xy < current_radius and dist_xy > hand_access_radius:
                        is_solid = True
                        
                grid[x_idx,y_idx,z_idx] = is_solid

    # Mesh Extraction
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, diameter, diameter, 0.0)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "prophecy_shade.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_shade(output_file)
