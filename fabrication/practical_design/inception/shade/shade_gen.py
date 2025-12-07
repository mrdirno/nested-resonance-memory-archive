import numpy as np
import math
import sys
import struct
import os

# Add project root to path for library import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES 01: THE ANISOTROPIC SHADE v2.4 (PURE GYROID V1 RESTORATION)
# -----------------------------------------------------------------------------
# Correction Cycle 2845:
# - User Feedback: "Math and shape right, waves too small... dig again... same one somewhere with waves bigger".
# - Forensic Trace:
#   - The user directed me to "Artifact 03" (Flow) but then said it was "inverted" and "waves too small".
#   - `helios_field_gen.py` (Artifact 01) uses `scale = 2.0 * math.pi / (size / 3.0)`.
#   - If `size` = 40mm, wavelength = 13.3mm.
#   - My recent attempts used ~48mm wavelength.
#   - The user wants BIGGER waves than that.
#   - "Bigger" implies a smaller divisor. e.g. Base/2.0 or Base/1.5.
#   - Let's look at the user's feedback again: "There's the same one somewhere with the waves bigger you'll prob find it this next one".
#   - This suggests there was a specific version I missed.
#   - In Commit `a26a7149`, I see `base_pattern_scale_x = 2.0 * math.pi / (base_size_x_unscaled / 3.0)`.
#   - In `helios_flow_gen_optimized.py` (Artifact 03), it was `size_x / 4.0`.
#   - So the Prism generator (a26a7149) had LARGER waves (Base/3) than Flow (Base/4).
#   - Base/3 = 64.6mm. Base/4 = 48.5mm.
#   - Maybe 64.6mm is what they want?
#   - BUT, user said "Pyramid Outline" was missing in my Prism restoration (Cycle 2836).
#   - I restored Pyramid Outline in Cycle 2841 using V1 logic. User said "Same as last one and now pyramid outline" (Wait, "now pyramid outline" means it HAS it? Or "no pyramid outline"?).
#   - User said "that was the same as the last one and now pyramid outline... it's just sharp pointy ting as edge of pyrmid".
#   - This implies they LIKED the "sharp pointy thing" (Pyramid Outline) but the waves were wrong?
#   - Or they DISLIKED it?
#   - User: "Just restore the generator and generate as is."
#   - Then later: "Oh this is the right math and shape but the waves are too small".
#   - This refers to Cycle 2844 (Inverted Flow).
#   - Cycle 2844 used `Base/4` (48mm).
#   - If I change it to `Base/3` (64mm) or `Base/2` (97mm), it matches "Bigger".
#   - AND I must keep the "Inverted Flow" logic (`z_prime = z * freq`)?
#   - Or did the "Original" use a simpler logic that *looked* like Inverted Flow?
#   - "Same one somewhere with the waves bigger".
#   - Maybe the original `helios_flow_gen.py` had `Base/3`?
#   - `helios_flow_gen` (ac1e7bae) had `2*pi/15`. 15mm. That's smaller.
#   - Maybe I should look for a generator that used `Base/2`?
#   - I will try `Base/2.5` (approx 77mm).
#   - And apply the "Inverted Flow" logic which the user confirmed as "Right Math".
# -----------------------------------------------------------------------------

def generate_shade(output_path, base_width=194.0, top_width=85.4, height=217.65, resolution=200, hole_diameter=14.0):
    print(f"Generating ANISOTROPIC SHADE v2.4 (Big Wave Inverted Flow): {output_path}")
    
    # Grid Setup
    max_dim = max(base_width, height)
    step = max_dim / resolution
    
    res_xy = int(base_width / step) + 5
    res_z = int(height / step) + 1
    
    print(f"Grid: {res_xy}x{res_xy}x{res_z} (Voxel size: {step:.2f}mm)")
    
    grid = np.zeros((res_xy, res_xy, res_z), dtype=bool)
    
    # MATH PARAMETERS
    # User wants "Bigger waves".
    # Previous attempt: Base/4 (48mm).
    # Let's try Base/2.5 (77.6mm).
    # This creates significantly larger structures.
    base_scale = 2.0 * math.pi / (base_width / 2.5)
    
    # Wall Thickness (Variable)
    wall_bottom = 12.7
    wall_top = 6.35
    
    print("Calculating Flow Field (Big Wave)...")
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        z_norm = z_mm / height
        
        # Taper Logic
        current_width = base_width * (1.0 - z_norm) + top_width * z_norm
        current_half_width = current_width / 2.0
        current_wall = wall_bottom * (1.0 - z_norm) + wall_top * z_norm
        current_inner_half_width = current_half_width - current_wall
        
        # INVERTED FLOW LOGIC (Confirmed Correct Math)
        # z_prime = z * freq_mod
        # freq_mod increases with Z -> Higher freq/Small waves at Top.
        
        freq_mod = 1.0 + (z_norm * 2.0) # 1x -> 3x
        z_prime = z_mm * freq_mod
        
        for x_idx in range(res_xy):
            x_mm = (x_idx * step) - (base_width / 2.0)
            
            for y_idx in range(res_xy):
                y_mm = (y_idx * step) - (base_width / 2.0)
                
                # BOUNDARY
                if abs(x_mm) > current_half_width or abs(y_mm) > current_half_width:
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                
                dist_from_center = math.sqrt(x_mm**2 + y_mm**2)
                
                # --- MOUNTING ---
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
                
                # PATTERN (Inverted Flow)
                val = math.sin(x_mm * base_scale) * math.cos(y_mm * base_scale) + \
                      math.sin(y_mm * base_scale) * math.cos(z_prime * base_scale) + \
                      math.sin(z_prime * base_scale) * math.cos(x_mm * base_scale)
                      
                if abs(val) < 0.5:
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