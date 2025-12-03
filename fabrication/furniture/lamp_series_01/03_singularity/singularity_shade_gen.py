import numpy as np
import math
import sys
import struct
import os

# Add project root to path for library import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES 01: THE SINGULARITY (SHADE) - THE VOID REVISION
# -----------------------------------------------------------------------------
# Logic: 
# 1. 1-Inch Thick Wall (Robustness).
# 2. 200mm Diameter (Max Print Area).
# 3. Mount: SPIDER FITTER (Hub + Spokes), Hand Access.
# 4. Math: Gyroid with Radial Torsion (Vortex Effect).
# -----------------------------------------------------------------------------

def generate_shade(output_path, diameter=200.0, height=140.0, resolution=100, hole_diameter=14.0):
    print(f"Generating SINGULARITY SHADE (VORTEX LATTICE): {output_path}")
    
    # Mount Parameters (Spider Fitter)
    mount_hole_radius = hole_diameter / 2.0 
    hub_radius = 20.0 # 40mm Hub
    spoke_width = 8.0 
    top_plate_height = 4.0 
    bottom_rim_height = 4.0 
    
    # Shell Parameters
    wall_thickness = 25.4 # 1 Inch
    hand_access_radius = 45.0 
    
    # Grid Setup
    max_dim = max(diameter, height)
    step = max_dim / resolution
    
    res_x = int(diameter / step) + 5
    res_y = int(diameter / step) + 5
    res_z = int(height / step) + 1
    
    print(f"Grid: {res_x}x{res_y}x{res_z} (Voxel size: {step:.2f}mm)")
    
    vertices = []
    faces = []
    grid = np.zeros((res_x, res_y, res_z), dtype=bool)
    
    # Vortex Parameters
    base_scale = 2.0 * math.pi / 40.0 # 40mm period
    twist_factor = 0.05 # Twist per mm radius
    
    print("Calculating Vortex Field...")
    
    radius = diameter / 2.0
    sphere_z_center = height - radius
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        
        for x_idx in range(res_x):
            x_mm = (x_idx * step) - (diameter / 2.0)
            
            for y_idx in range(res_y):
                y_mm = (y_idx * step) - (diameter / 2.0)
                
                dist_from_center_xy = math.sqrt(x_mm**2 + y_mm**2)
                
                # Effective Z for Connection Guarantee
                effective_z = z_mm
                if z_mm > (height - 10.0):
                    effective_z = height - 10.0
                
                dist_sq = x_mm**2 + y_mm**2 + (effective_z - sphere_z_center)**2
                dist_spherical = math.sqrt(dist_sq)
                
                # Calculate current shell outer radius at this Z for Dynamic Constraint
                dz = effective_z - sphere_z_center
                term = radius**2 - dz**2
                if term < 0: term = 0
                current_shell_radius = math.sqrt(term)
                
                # --- PRIORITY 1: SPIDER FITTER (Library Call) ---
                fitter_override = lamp_lib.apply_spider_fitter(
                    x_mm, y_mm, z_mm, dist_from_center_xy,
                    mount_z_start=(height - top_plate_height),
                    mount_hole_radius=mount_hole_radius,
                    hub_radius=hub_radius,
                    spoke_width=spoke_width,
                    outer_radius=current_shell_radius # DYNAMIC CONSTRAINT
                )
                
                if fitter_override is not None:
                    grid[x_idx,y_idx,z_idx] = fitter_override
                    continue

                # --- PRIORITY 2: BOTTOM RIM ---
                if z_mm < bottom_rim_height:
                    if dist_from_center_xy < radius and dist_from_center_xy > hand_access_radius:
                         grid[x_idx,y_idx,z_idx] = True
                         continue

                # --- PRIORITY 3: SHELL & VORTEX PATTERN ---
                is_solid = False
                in_outer_shell = dist_spherical <= radius
                in_inner_void = dist_spherical < (radius - wall_thickness)
                in_hand_void = dist_from_center_xy < hand_access_radius
                is_void = in_inner_void or in_hand_void
                
                if in_outer_shell and not is_void:
                    # AGPH SINGULARITY SHADE: The Jet
                    
                    # P: Prismatic a(z) - Spherical
                    
                    # Define z_norm locally
                    z_norm = z_mm / height
                    
                    # H: Helix R(z) - Vortex Twist
                    twist = z_norm * 4.0 * math.pi
                    ca = math.cos(twist)
                    sa = math.sin(twist)
                    tx = x_mm * ca - y_mm * sa
                    ty = x_mm * sa + y_mm * ca
                    
                    # A: Anisotropy A(z) - Radial Expansion (The Jet)
                    # Stretch OUTWARDS from Z-axis
                    radial_stretch = 1.0 + (dist_from_center_xy / radius) * 2.0
                    
                    # Scale
                    freq = 2.0 * math.pi / 35.0
                    lx = tx * freq * (1.0/radial_stretch)
                    ly = ty * freq * (1.0/radial_stretch)
                    lz = z_mm * freq 
                    
                    # G: Gyroid
                    val = math.sin(lx)*math.cos(ly) + math.sin(ly)*math.cos(lz) + math.sin(lz)*math.cos(lx)
                    
                    if abs(val) < 0.35: 
                        is_solid = True
                        
                grid[x_idx,y_idx,z_idx] = is_solid

    # Clean Dust (Strict QA)
    grid = lamp_lib.clean_voxel_grid(grid)

    print("Extracting Mesh...")
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, diameter, diameter)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "singularity_shade.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_shade(output_file)