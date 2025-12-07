import numpy as np
import math
import sys
import struct
import os

# Add project root to path for library import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES 01: THE ANISOTROPIC SHADE v2.4 (V4 QA RESTORATION)
# -----------------------------------------------------------------------------
# Correction Cycle 2839:
# - User Feedback: "Go one more forward".
# - Forensic Trace: Commit `36552a77` (Dec 1 18:47) modified `helios_lamp_shade_v4_gen.py`.
# - Logic: This version includes "SOLID TRANSITION FIX" (ensuring solidity below mount) and Triskelion Spokes (3-way).
# - It retains the `px_ref` (Reference Coordinate) logic for the "Big Bang" effect.
# - Action: Re-implement EXACTLY this logic (Triskelion + Solid Transition + Ref Coords).
# - Geometry: V2.4 (217.65mm H, 85.4mm Top, 194mm Base, Variable Wall).
# -----------------------------------------------------------------------------

def generate_shade(output_path, base_width=194.0, top_width=85.4, height=217.65, resolution=200, hole_diameter=14.0):
    print(f"Generating ANISOTROPIC SHADE v2.4 (V4 QA Restoration): {output_path}")
    
    # V4 Params
    size_x = top_width
    size_y = top_width
    size_z = height
    
    # Calculate k_expansion
    # Width_Bottom = Width_Top * (1 + k)
    k_expansion = (base_width / top_width) - 1.0
    
    # Mount Params (V4 QA)
    hub_diam = 40.0
    spoke_width = 8.0
    top_mount_height = 15.0
    
    # Wall Thickness (Variable)
    wall_bottom = 12.7 # 1/2 inch
    wall_top = 6.35    # 1/4 inch
    
    # Grid Setup
    res_x = resolution
    res_y = resolution
    step_ref = size_x / resolution
    res_z = int(size_z / step_ref)
    
    step_x = size_x / res_x
    step_y = size_y / res_y
    step_z = size_z / res_z
    
    print(f"Grid: {res_x}x{res_y}x{res_z} (Voxel: ~{step_x:.2f}mm)")
    
    grid = np.zeros((res_x, res_y, res_z), dtype=bool)
    
    # MATH PARAMETERS (V4 QA)
    base_scale_xy = 2.0 * math.pi / (size_x / 3.0)
    
    print("Calculating Field (V4 QA Logic)...")
    
    for z_idx in range(res_z):
        pz = z_idx * step_z
        z_norm = pz / size_z
        
        expansion_factor = 1.0 + k_expansion * (1.0 - z_norm)
        
        current_width = size_x * expansion_factor
        
        # Variable Wall
        current_wall = wall_bottom * (1.0 - z_norm) + wall_top * z_norm
        current_outer_half_width = current_width / 2.0
        current_inner_half_width = current_outer_half_width - current_wall
        
        # Z Modulation (V4)
        base_wavelength_z = size_z / 4.0
        base_scale_z_val = 2.0 * math.pi / base_wavelength_z
        # V4 used modulated_scale_z with k_mod=0.01. Effectively constant.
        current_scale_z = base_scale_z_val
        
        # Mount Logic Zones
        is_top_mount = (pz > (size_z - top_mount_height))
        dist_from_top = size_z - pz
        is_transition_zone = dist_from_top < (top_mount_height + 10.0)
        
        for x_idx in range(res_x):
            px_ref = (x_idx * step_x) - (size_x/2)
            for y_idx in range(res_y):
                py_ref = (y_idx * step_y) - (size_y/2)
                
                px_phys = px_ref * expansion_factor
                py_phys = py_ref * expansion_factor
                
                # GLOBAL BOUNDARY
                if abs(px_phys) > current_outer_half_width or abs(py_phys) > current_outer_half_width:
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                
                r_phys = math.sqrt(px_phys**2 + py_phys**2)
                
                # 1. TOP MOUNT (Spider Fitter)
                if is_top_mount:
                    # A. Hole
                    if r_phys < (hole_diameter / 2.0):
                        grid[x_idx,y_idx,z_idx] = False
                        continue
                    # B. Hub
                    if r_phys < (hub_diam / 2.0):
                        grid[x_idx,y_idx,z_idx] = True
                        continue
                    # C. Spokes (Triskelion 120 deg)
                    spoke_half = spoke_width / 2.0
                    d1 = abs(py_phys)
                    d2 = abs(-math.sqrt(3)*px_phys - py_phys) / 2.0
                    d3 = abs(math.sqrt(3)*px_phys - py_phys) / 2.0
                    
                    if (d1 < spoke_half) or (d2 < spoke_half) or (d3 < spoke_half):
                        grid[x_idx,y_idx,z_idx] = True
                        continue
                    
                    # D. Rim Merge
                    dx = current_outer_half_width - abs(px_phys)
                    dy = current_outer_half_width - abs(py_phys)
                    if min(dx, dy) < current_wall: # V4 used constant wall, we use current
                        grid[x_idx,y_idx,z_idx] = True
                        continue
                        
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                
                # 2. SOLID TRANSITION (Below Mount)
                # "Ensure the shell is SOLID just below the top mount"
                # But only within the SHELL thickness? V4 logic says:
                # "if dist_from_top < ... : grid = True"
                # This was placed AFTER shell mask check in V4.
                
                # 3. BODY
                
                # Shell Mask
                dx = current_outer_half_width - abs(px_phys)
                dy = current_outer_half_width - abs(py_phys)
                dist_to_edge = min(dx, dy)
                
                if dist_to_edge > current_wall:
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                
                # SOLID TRANSITION CHECK (After Shell Mask, so applies to shell only)
                if is_transition_zone:
                    grid[x_idx,y_idx,z_idx] = True
                    continue
                
                # 4. BOTTOM RIM
                if pz < 4.0:
                    grid[x_idx,y_idx,z_idx] = True
                    continue
                
                # 5. GYROID PATTERN
                val = math.sin(px_ref * base_scale_xy) * math.cos(py_ref * base_scale_xy) + \
                      math.sin(py_ref * base_scale_xy) * math.cos(pz * current_scale_z) + \
                      math.sin(pz * current_scale_z) * math.cos(px_ref * base_scale_xy)
                      
                if abs(val) < 0.55: # V4 used 0.4, increasing for variable wall robustness
                    grid[x_idx,y_idx,z_idx] = True

    # Meshing (V4)
    print("Extracting Isosurface...")
    vertices = []
    faces = []
    
    def add_quad(v1, v2, v3, v4):
        idx = len(vertices)
        vertices.extend([v1, v2, v3, v4])
        faces.append((idx, idx+1, idx+2))
        faces.append((idx, idx+2, idx+3))

    for z_idx in range(res_z):
        pz = z_idx * step_z
        z_norm = pz / size_z
        expansion_factor = 1.0 + k_expansion * (1.0 - z_norm)
        
        for x_idx in range(res_x):
            for y_idx in range(res_y):
                if not grid[x_idx,y_idx,z_idx]: continue
                
                px_ref = (x_idx * step_x) - (size_x/2)
                py_ref = (y_idx * step_y) - (size_y/2)
                
                vx = px_ref * expansion_factor
                vy = py_ref * expansion_factor
                vz = pz
                
                s2x = (step_x * expansion_factor) / 2
                s2y = (step_y * expansion_factor) / 2
                s2z = step_z / 2
                
                if x_idx == res_x-1 or not grid[x_idx+1,y_idx,z_idx]:
                    add_quad((vx+s2x, vy-s2y, vz-s2z), (vx+s2x, vy+s2y, vz-s2z), (vx+s2x, vy+s2y, vz+s2z), (vx+s2x, vy-s2y, vz+s2z))
                if x_idx == 0 or not grid[x_idx-1,y_idx,z_idx]:
                    add_quad((vx-s2x, vy-s2y, vz+s2z), (vx-s2x, vy+s2y, vz+s2z), (vx-s2x, vy+s2y, vz-s2z), (vx-s2x, vy-s2y, vz-s2z))
                if y_idx == res_y-1 or not grid[x_idx,y_idx+1,z_idx]:
                    add_quad((vx+s2x, vy+s2y, vz-s2z), (vx-s2x, vy+s2y, vz-s2z), (vx-s2x, vy+s2y, vz+s2z), (vx+s2x, vy+s2y, vz+s2z))
                if y_idx == 0 or not grid[x_idx,y_idx-1,z_idx]:
                    add_quad((vx-s2x, vy-s2y, vz-s2z), (vx+s2x, vy-s2y, vz-s2z), (vx+s2x, vy-s2y, vz+s2z), (vx-s2x, vy-s2y, vz+s2z))
                if z_idx == res_z-1 or not grid[x_idx,y_idx,z_idx+1]:
                    add_quad((vx+s2x, vy-s2y, vz+s2z), (vx+s2x, vy+s2y, vz+s2z), (vx-s2x, vy+s2y, vz+s2z), (vx+s2x, vy-s2y, vz+s2z))
                if z_idx == 0 or not grid[x_idx,y_idx,z_idx-1]:
                    add_quad((vx-s2x, vy-s2y, vz-s2z), (vx-s2x, vy+s2y, vz-s2z), (vx+s2x, vy+s2y, vz-s2z), (vx+s2x, vy-s2y, vz-s2z))

    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "lamp_shade_v2.4.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_shade(output_file)