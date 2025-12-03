import numpy as np
import math
import sys
import struct
import os

# Add project root to path for library import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES 03: THE MOBIUS (SHADE)
# -----------------------------------------------------------------------------
# Logic: Mobius Strip (Infinite Loop).
# Method: Parametric Mobius Strip equation.
# Standard: V7 (Spider Fitter, 14mm Hole, 25.4mm Wall).
# -----------------------------------------------------------------------------

def generate_shade(output_path, diameter=200.0, height=180.0, resolution=120, hole_diameter=14.0):
    print(f"Generating THE MOBIUS SHADE: {output_path}")
    
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
    
    # Mobius Logic
    # We need a Mobius strip that fits in a cylinder.
    # x = (R + v*cos(t/2)) * cos(t)
    # y = (R + v*cos(t/2)) * sin(t)
    # z = v * sin(t/2)
    
    # But we want it vertical.
    # Let's twist a ribbon 180 degrees as it goes up?
    # That's just a twisted plane.
    
    # Let's approximate a "Mobius Cylinder"
    # It looks like a cylinder but the wall twists from inside to outside.
    # r(theta, z) = R_avg + A * sin(theta/2 + z_factor)
    
    # But theta/2 is discontinuous at 2pi.
    # True Mobius must self-intersect or be in 4D to be non-intersecting.
    # In 3D, it's a twisted loop.
    
    # Let's create a "Twisted Ribbon" structure.
    # N ribbons that twist 180 degrees.
    
    num_ribbons = 3
    twist_total = math.pi # 180 deg
    
    print("Twisting Infinity...")
    
    radius = diameter / 2.0
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        z_norm = z_mm / height
        
        current_twist = z_norm * twist_total
        
        for x_idx in range(res_x):
            x_mm = (x_idx * step) - (diameter / 2.0)
            
            for y_idx in range(res_y):
                y_mm = (y_idx * step) - (diameter / 2.0)
                
                dist_xy = math.sqrt(x_mm**2 + y_mm**2)
                angle = math.atan2(y_mm, x_mm)
                
                # --- PRIORITY 1: SPIDER FITTER (Dynamic) ---
                current_shell_radius = radius 
                fitter_override = lamp_lib.apply_spider_fitter(
                    x_mm, y_mm, z_mm, dist_xy,
                    mount_z_start=(height - top_plate_height),
                    mount_hole_radius=mount_hole_radius,
                    hub_radius=hub_radius,
                    spoke_width=spoke_width,
                    outer_radius=current_shell_radius
                )
                
                if fitter_override is not None:
                    grid[x_idx,y_idx,z_idx] = fitter_override
                    continue

                # --- PRIORITY 2: BOTTOM RIM ---
                if z_mm < bottom_rim_height:
                    if dist_xy < radius and dist_xy > hand_access_radius:
                         grid[x_idx,y_idx,z_idx] = True
                         continue

                # --- PRIORITY 3: MOBIUS SHELL ---
                
                if dist_xy > radius:
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                    
                if dist_xy < (radius - wall_thickness):
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                    
                # Twisted Ribbon Logic (Anisotropic)
                
                # Anisotropy: Twist rate increases with Z (Acceleration)
                local_twist = z_norm**1.5 * twist_total # Non-linear
                
                val = math.sin(num_ribbons * angle + local_twist)
                
                # Connector strands (Z-Stretched)
                # stretch Z frequency
                connect = math.sin(z_mm * 0.1) # Low freq = Stretched Z
                
                if abs(val) > 0.5: # Ribbons
                    grid[x_idx,y_idx,z_idx] = True
                elif connect > 0.85: # Connectors
                    grid[x_idx,y_idx,z_idx] = True
                else:
                    grid[x_idx,y_idx,z_idx] = False

    # Clean Dust (QA)
    grid = lamp_lib.clean_voxel_grid(grid)

    # Mesh Extraction
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, diameter, diameter, 0.0)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "mobius_shade.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_shade(output_file)
