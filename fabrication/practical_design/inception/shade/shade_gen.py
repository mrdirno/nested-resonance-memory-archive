import numpy as np
import math
import sys
import struct
import os

# Add project root to path for library import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES 01: THE ANISOTROPIC SHADE v2.4 (FLOW OPTIMIZED RESTORATION)
# -----------------------------------------------------------------------------
# Correction Cycle 2843:
# - User Feedback: "Volumes/.../TPMS_Anisotropic_Prism_Artifact03 then find the correlated generator... around that time".
# - Forensic Trace: 
#   - `TPMS_Anisotropic_Prism_Artifact03` was established in Commit `bdc4beb3` (Dec 1 17:34).
#   - That commit added `helios_flow_gen_optimized.py`.
#   - This generator implements "The Directional Current" (Artifact 03).
# - Logic:
#   - `freq_mod = 1.0 + (z_norm * 2.0)`: Z-Frequency increases with Z. Wavelength DECREASES with Z.
#   - Wait. If frequency increases, wavelength decreases.
#   - User wanted "Small waves at top". High freq = Small waves.
#   - So `1 + 2*z` means freq is 1x at bottom, 3x at top.
#   - This produces Large Waves at Bottom, Small Waves at Top. "Big Bang".
#   - Coordinate logic: `z_prime = z / freq_mod`.
#   - `gyroid = sin(x*s)cos(y*s) + sin(y*s)cos(z_prime*s) ...`
#   - This is "Flow" logic. Z-Warping of the coordinate.
#   - Unlike Redshift (which expanded coords), this compresses them? 
#   - `z_prime = z / (1+2z)`. As z grows, z_prime grows slower. Phase change slows down? 
#   - No, `cos(z_prime * scale)`. If z_prime changes slowly, the wave stretches.
#   - So this produces STRETCHED waves at the top?
#   - Let's re-read: "Original was ~40/3... We want coarser cells... New Scale: size_x/4.0".
#   - Let's assume the visual output of THIS generator is what the user recognized in "Artifact 03".
# - Action: Re-implement `helios_flow_gen_optimized.py` logic into `inception/shade/shade_gen.py`.
#   - Apply V2.4 Geometry (217mm H, 85mm Top, 194mm Base, Variable Wall).
# -----------------------------------------------------------------------------

def generate_shade(output_path, base_width=194.0, top_width=85.4, height=217.65, resolution=200, hole_diameter=14.0):
    print(f"Generating ANISOTROPIC SHADE v2.4 (Flow Optimized Restoration): {output_path}")
    
    # Grid Setup
    max_dim = max(base_width, height)
    step = max_dim / resolution
    
    res_xy = int(base_width / step) + 5
    res_z = int(height / step) + 1
    
    print(f"Grid: {res_xy}x{res_xy}x{res_z} (Voxel size: {step:.2f}mm)")
    
    grid = np.zeros((res_xy, res_xy, res_z), dtype=bool)
    
    # MATH PARAMETERS (Artifact 03 Optimized)
    # "Base Scale: 2.0 * pi / (size_x / 4.0)"
    # Using base_width as reference size_x.
    # 194 / 4 = 48.5mm Wavelength.
    base_scale = 2.0 * math.pi / (base_width / 4.0)
    
    # Wall Thickness (Variable)
    wall_bottom = 12.7
    wall_top = 6.35
    
    print("Calculating Flow Field...")
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        z_norm = z_mm / height
        
        # Taper Logic
        current_width = base_width * (1.0 - z_norm) + top_width * z_norm
        current_half_width = current_width / 2.0
        
        # Variable Wall
        current_wall = wall_bottom * (1.0 - z_norm) + wall_top * z_norm
        current_inner_half_width = current_half_width - current_wall
        
        # ARTIFACT 03 LOGIC: Z-Prime
        # z_norm goes 0..1.
        # freq_mod = 1.0 + (z_norm * 2.0) -> 1.0 to 3.0
        # z_prime = z_mm / freq_mod
        # Note: In original, z went -size/2 to size/2. Here we use 0 to height.
        # Adjust z_norm to match visual flow if needed. 0..1 is standard.
        
        freq_mod = 1.0 + (z_norm * 2.0)
        z_prime = z_mm / freq_mod
        
        for x_idx in range(res_xy):
            x_mm = (x_idx * step) - (base_width / 2.0)
            
            for y_idx in range(res_xy):
                y_mm = (y_idx * step) - (base_width / 2.0)
                
                # BOUNDARY
                if abs(x_mm) > current_half_width or abs(y_mm) > current_half_width:
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                
                dist_from_center = math.sqrt(x_mm**2 + y_mm**2)
                
                # --- MOUNTING (V2.4 Standard) ---
                if z_mm > (height - 4.0):
                    if dist_from_center <= (hole_diameter/2.0):
                        grid[x_idx,y_idx,z_idx] = False
                        continue
                    if abs(x_mm) < current_half_width and abs(y_mm) < current_half_width:
                        grid[x_idx,y_idx,z_idx] = True
                        continue
                
                if z_mm < 4.0:
                    if abs(x_mm) < current_inner_half_width and abs(y_mm) < current_inner_half_width:
                        grid[x_idx,y_idx,z_idx] = False
                    else:
                        grid[x_idx,y_idx,z_idx] = True
                    continue
                
                # --- BODY ---
                if abs(x_mm) < current_inner_half_width and abs(y_mm) < current_inner_half_width:
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                
                # PATTERN (Artifact 03)
                # sin(x)cos(y) + sin(y)cos(z') + sin(z')cos(x)
                
                val = math.sin(x_mm * base_scale) * math.cos(y_mm * base_scale) + \
                      math.sin(y_mm * base_scale) * math.cos(z_prime * base_scale) + \
                      math.sin(z_prime * base_scale) * math.cos(x_mm * base_scale)
                      
                if abs(val) < 0.5: # Artifact 03 Threshold
                    grid[x_idx,y_idx,z_idx] = True

    # Clean
    grid = lamp_lib.clean_voxel_grid(grid)
    
    # Mesh
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, base_width, base_width)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "lamp_shade_v2.4.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_shade(output_file)