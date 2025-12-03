import numpy as np
import math
import sys
import struct
import random
import os

# Add project root to path for library import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES 01: THE SUPERNOVA (SHADE) - THE VOID REVISION
# -----------------------------------------------------------------------------
# Logic: 
# 1. Concept: Explosive Expansion (Nebula).
# 2. Math: Interference Noise (Superposition of random sine waves).
# 3. Standard: 1-Inch Wall, SPIDER FITTER (Hub + Spokes), Hand Access.
# -----------------------------------------------------------------------------

def generate_shade(output_path, diameter=200.0, height=140.0, resolution=100, hole_diameter=14.0):
    print(f"Generating SUPERNOVA SHADE (CHAOS LATTICE): {output_path}")
    
    # Mount Parameters (Spider Fitter)
    mount_hole_radius = hole_diameter / 2.0 
    hub_radius = 20.0 # 40mm Hub
    spoke_width = 8.0 
    top_plate_height = 4.0 
    bottom_rim_height = 4.0 
    
    # Shell Parameters
    wall_thickness = 25.4 # 1 Inch
    
    # Calculate hand_access_radius to GUARANTEE 1 inch rim at bottom
    # Rim extends from radius (100) to hand_access_radius
    # Width = radius - hand_access_radius
    # Width must be 25.4
    hand_access_radius = (diameter / 2.0) - 25.4
    
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
    
    # Interference Noise Setup
    num_waves = 7
    waves = []
    random.seed(42)
    base_freq = 2.0 * math.pi / 40.0 
    
    for i in range(num_waves):
        theta = random.uniform(0, 2*math.pi)
        phi = random.uniform(0, math.pi)
        dx = math.sin(phi) * math.cos(theta)
        dy = math.sin(phi) * math.sin(theta)
        dz = math.cos(phi)
        freq = base_freq * random.uniform(0.8, 1.2)
        phase = random.uniform(0, 2*math.pi)
        waves.append((dx, dy, dz, freq, phase))
    
    print("Calculating Chaos Field...")
    
    radius = diameter / 2.0
    sphere_z_center = height - radius
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        
        for x_idx in range(res_x):
            x_mm = (x_idx * step) - (diameter / 2.0)
            
            for y_idx in range(res_y):
                y_mm = (y_idx * step) - (diameter / 2.0)
                
                dist_from_center_xy = math.sqrt(x_mm**2 + y_mm**2)
                
                effective_z = z_mm
                if z_mm > (height - 10.0):
                    effective_z = height - 10.0
                
                # Calculate dist_spherical HERE
                dist_sq = x_mm**2 + y_mm**2 + (effective_z - sphere_z_center)**2
                dist_spherical = math.sqrt(dist_sq)
                
                # Calculate current shell outer radius at this Z for Dynamic Constraint
                dz = effective_z - sphere_z_center
                term = radius**2 - dz**2
                if term < 0: term = 0
                current_shell_radius = math.sqrt(term)
                
                # --- PRIORITY 1: MOUNT (Cantilever Bar/Ring) ---
                # The user wants a ring/disk with a hole.
                # This must exist even if chaos erodes it.
                
                if z_mm > (height - 6.0): # Top 6mm
                    # Central Hub (Solid)
                    if dist_from_center_xy < 22.0 and dist_from_center_xy > 7.0:
                        grid[x_idx,y_idx,z_idx] = True
                        continue
                    # Hole
                    if dist_from_center_xy <= 7.0:
                        grid[x_idx,y_idx,z_idx] = False
                        continue
                        
                    # Cantilever Bars (Spokes)
                    # 3 Spokes
                    spoke_angle = math.atan2(y_mm, x_mm)
                    # Check alignment with 0, 120, 240
                    # cos(3*angle) > threshold
                    if math.cos(3.0 * spoke_angle) > 0.9: # Narrow bars
                         if dist_from_center_xy < current_shell_radius:
                             grid[x_idx,y_idx,z_idx] = True
                             continue

                # --- PRIORITY 2: BOTTOM RIM ---
                if z_mm < bottom_rim_height:
                    if dist_from_center_xy < radius and dist_from_center_xy > hand_access_radius:
                         grid[x_idx,y_idx,z_idx] = True
                         continue

                # --- PRIORITY 3: SHELL & CHAOS PATTERN ---
                is_solid = False
                in_outer_shell = dist_spherical <= radius
                in_inner_void = dist_spherical < (radius - wall_thickness)
                in_hand_void = dist_from_center_xy < hand_access_radius
                is_void = in_inner_void or in_hand_void
                
                if in_outer_shell and not is_void:
                    # Sum Sine Waves
                    val = 0.0
                    for w in waves:
                        dx, dy, dz, freq, phase = w
                        proj = x_mm*dx + y_mm*dy + z_mm*dz
                        val += math.sin(proj * freq + phase)
                    
                    if abs(val) < 1.4: # Thickened (was 1.2)
                        is_solid = True
                    
                    # CONNECTIVITY SHARDS (Ribs)
                    # Radial Spikes
                    angle = math.atan2(y_mm, x_mm)
                    
                    # 6 Spikes
                    spike = math.cos(6.0 * angle)
                    if spike > 0.8:
                        is_solid = True
                        
                grid[x_idx,y_idx,z_idx] = is_solid

    # Clean Dust (Strict QA)
    grid = lamp_lib.clean_voxel_grid(grid)

    print("Extracting Mesh...")
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, diameter, diameter)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "supernova_shade.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_shade(output_file)
