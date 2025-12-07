import numpy as np
import math
import sys
import struct
import os

# Add project root to path for library import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES 01: THE ANISOTROPIC SHADE v2.4 (V4 GEN RESTORATION)
# -----------------------------------------------------------------------------
# Correction Cycle 2838:
# - User Correction: "Not the right one... find the original first... trace the history".
# - Forensic Path: User pointed to `lamp_base_v2.3mf` and `lamp_shade_v2.3mf` in `FAVORITES`.
# - Discovery: These artifacts were updated/restored in commit `82d0026c` (Dec 1 17:24) and `15319712` (Dec 1 17:10).
# - Key Link: `helios_lamp_shade_v4_gen.py` was introduced/modified around this time (Commit `8157ce4e`).
# - Logic Match: V4 Gen uses `px_ref` (Reference Coordinates) logic, which matches the "Coordinate Scaling" I found in Cycle 2836, 
#   but specifically implemented as `px_ref` in a V4 context with `k_expansion`.
# - This logic produces the "Big Bang" effect (Small top, large bottom) while maintaining cell count.
# - V4 Gen also has "Spider Fitter Override" and "Shell Mask" logic.
# - Action: Re-implement V4 Gen logic exactly, but with V2.4 Geometry.
# -----------------------------------------------------------------------------

def generate_shade(output_path, base_width=194.0, top_width=85.4, height=217.65, resolution=200, hole_diameter=14.0):
    print(f"Generating ANISOTROPIC SHADE v2.4 (V4 Restoration): {output_path}")
    
    # V4 Gen Parameters Mapping
    size_x = top_width  # V4 used Top Size as reference
    size_y = top_width
    size_z = height
    
    # Calculate k_expansion for V4 logic
    # expansion_factor = 1.0 + k_expansion * (1.0 - z_norm)
    # At z_norm=0 (Bottom), factor = 1 + k
    # Width_Bottom = Width_Top * (1 + k)
    # k = (Width_Bottom / Width_Top) - 1
    k_expansion = (base_width / top_width) - 1.0
    
    print(f"V4 Params: Top={size_x}, k={k_expansion:.4f}")

    # Wall Thickness (Variable)
    wall_bottom = 12.7 # 1/2 inch
    wall_top = 6.35    # 1/4 inch
    
    # Grid Setup
    # V4 Logic: Resolution applies to TOP size?
    # "step_ref = size_x / resolution"
    # 85mm / 200 = 0.42mm step. Very fine.
    
    res_x = resolution
    res_y = resolution
    
    # Z resolution logic from V4
    step_ref = size_x / resolution
    res_z = int(size_z / step_ref)
    
    step_x = size_x / res_x
    step_y = size_y / res_y
    step_z = size_z / res_z
    
    print(f"Grid: {res_x}x{res_y}x{res_z} (Voxel: ~{step_x:.2f}mm)")
    
    grid = np.zeros((res_x, res_y, res_z), dtype=bool)
    
    # MATH PARAMETERS (V4)
    # base_scale_xy = 2.0 * math.pi / (size_x / 3.0)
    # Top Wavelength = Top Width / 3.0 = 85 / 3 = 28mm.
    # Bottom Wavelength = Bottom Width / 3.0 = 194 / 3 = 64mm. (Due to coordinate scaling)
    # This matches the "Big Bang" range perfectly.
    base_scale_xy = 2.0 * math.pi / (size_x / 3.0)
    
    print("Calculating Field (V4 Logic)...")
    
    for z_idx in range(res_z):
        pz = z_idx * step_z
        z_norm = pz / size_z # 0 bottom -> 1 top
        
        # Expansion Factor (V4: Top Reference)
        # factor = 1.0 + k * (1.0 - z_norm) -> 1.0 at Top, 1+k at Bottom
        # Note: Previous cycles used 0 at Bottom logic? No, V4 used 0 at Bottom for z_norm.
        # Let's check V4 code:
        # pz = z_idx * step_z (0 at bottom)
        # expansion_factor = 1.0 + k_expansion * (1.0 - z_norm)
        # at z=0 (bot), factor = 1+k (Large). at z=1 (top), factor = 1 (Small).
        # Correct.
        
        expansion_factor = 1.0 + k_expansion * (1.0 - z_norm)
        
        # Physical Dimensions
        current_width = size_x * expansion_factor
        
        # Variable Wall Logic
        current_wall = wall_bottom * (1.0 - z_norm) + wall_top * z_norm
        
        current_outer_half_width = current_width / 2.0
        current_inner_half_width = current_outer_half_width - current_wall
        
        # Z Modulation
        base_wavelength_z = size_z / 4.0
        base_scale_z_val = 2.0 * math.pi / base_wavelength_z
        # V4: modulated_scale_z = base_scale_z_val / (1 + k_mod * z_norm)
        # k_mod = 0.01 (Default in V4)
        current_scale_z = base_scale_z_val 
        
        for x_idx in range(res_x):
            # Reference Coordinates (Top Scale)
            px_ref = (x_idx * step_x) - (size_x/2)
            
            for y_idx in range(res_y):
                py_ref = (y_idx * step_y) - (size_y/2)
                
                # Physical Coordinates (Scaled)
                px_phys = px_ref * expansion_factor
                py_phys = py_ref * expansion_factor
                
                # BOUNDARY CHECKS (Physical)
                if abs(px_phys) > current_outer_half_width or abs(py_phys) > current_outer_half_width:
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                
                dist_from_center = math.sqrt(px_phys**2 + py_phys**2)
                
                # --- PRIORITY 1: SOLID CAP ---
                if pz > (size_z - 4.0):
                    if dist_from_center <= (hole_diameter/2.0):
                        grid[x_idx,y_idx,z_idx] = False
                        continue
                    if abs(px_phys) < current_outer_half_width and abs(py_phys) < current_outer_half_width:
                        grid[x_idx,y_idx,z_idx] = True
                        continue
                
                # --- PRIORITY 2: BOTTOM RIM ---
                if pz < 4.0:
                    if abs(px_phys) < current_inner_half_width and abs(py_phys) < current_inner_half_width:
                        grid[x_idx,y_idx,z_idx] = False
                    else:
                        grid[x_idx,y_idx,z_idx] = True
                    continue
                
                # --- PRIORITY 3: CORNERS (Restored from V4 Logic D. SHELL MERGE) ---
                # "If we are at the outer rim, keep it solid"
                # distance_to_edge check
                dist_to_edge_x = current_outer_half_width - abs(px_phys)
                dist_to_edge_y = current_outer_half_width - abs(py_phys)
                
                # V4 Logic D: if min(dx, dy) < wall_thickness -> Solid
                # This makes the ENTIRE shell solid? 
                # No, V4 only did this inside "SPIDER FITTER OVERRIDE".
                # But we want Solid Corners.
                # Let's apply "Corner Rails" logic again (5mm).
                if dist_to_edge_x < 5.0 and dist_to_edge_y < 5.0:
                    grid[x_idx,y_idx,z_idx] = True
                    continue
                
                # --- PRIORITY 4: BODY ---
                # Inner Void
                if abs(px_phys) < current_inner_half_width and abs(py_phys) < current_inner_half_width:
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                
                # Pattern Math (V4 uses px_ref/py_ref)
                val = math.sin(px_ref * base_scale_xy) * math.cos(py_ref * base_scale_xy) + \
                      math.sin(py_ref * base_scale_xy) * math.cos(pz * current_scale_z) + \
                      math.sin(pz * current_scale_z) * math.cos(px_ref * base_scale_xy)
                      
                if abs(val) < 0.55:
                    grid[x_idx,y_idx,z_idx] = True

    # Extract Isosurface (V4 Meshing)
    print("Extracting Isosurface (Voxel)...")
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
                
                # Vertex Generation (V4: px_ref * expansion)
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
