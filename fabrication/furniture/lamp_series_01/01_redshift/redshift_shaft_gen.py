import numpy as np
import math
import sys
import struct
import os

# Add project root to path for library import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES 01: THE REDSHIFT (SHAFT) v2.0
# -----------------------------------------------------------------------------
# REFINEMENT v2.0: Double Helix Gyroid, Library Integration.
# Logic: Arterial Helix (Twisted vein structure).
# Features: V4 QA (Solid Core, End Caps, 14mm Clearance).
# -----------------------------------------------------------------------------

def generate_shaft(output_path, 
                   height=200.0,
                   diam_base=55.0,
                   diam_top=40.0,
                   resolution=100):
    
    print(f"Generating Redshift Shaft (v2.0): {output_path}")
    
    # Internal Core Params (Clearance for 1/8 IP Rod)
    hole_radius = 7.0 # 14mm Diam
    solid_core_radius = 9.0 # 18mm Diam (2mm solid wall around rod)
    
    # Twist Params
    total_rotation = 2.0 * math.pi # 360 degree twist over the height
    
    # Grid
    res_x = resolution
    res_y = resolution
    # Step based on max diameter
    step_ref = diam_base / resolution
    res_z = int(height / step_ref)
    
    step_x = diam_base / res_x
    step_y = diam_base / res_y
    step_z = height / res_z
    
    print(f"Grid: {res_x}x{res_y}x{res_z} (Voxel: ~{step_ref:.2f}mm)")
    
    grid = np.zeros((res_x, res_y, res_z), dtype=bool)
    
    # Pattern Scale
    scale = 2.0 * math.pi / 20.0 # 20mm wavelength
    
    print("Calculating Field (v2.0)...")
    
    for z_idx in range(res_z):
        pz = z_idx * step_z
        z_norm = pz / height
        
        # Taper Logic (Linear Interpolation)
        current_diam = diam_base * (1.0 - z_norm) + diam_top * z_norm
        current_radius = current_diam / 2.0
        
        # Rotation Angle at this Z
        theta = total_rotation * z_norm
        cos_t = math.cos(theta)
        sin_t = math.sin(theta)
        
        for x_idx in range(res_x):
            px_raw = (x_idx * step_x) - (diam_base/2)
            
            for y_idx in range(res_y):
                py_raw = (y_idx * step_y) - (diam_base/2)
                
                # 1. GLOBAL BOUNDARY CHECK (Tapered Cylinder)
                r_raw = math.sqrt(px_raw**2 + py_raw**2)
                
                if r_raw > current_radius:
                    continue # Outside the shaft
                
                # 2. INTERNAL CORE (Negative Space for Rod)
                if r_raw < hole_radius:
                    grid[x_idx, y_idx, z_idx] = False
                    continue
                
                # 3. SOLID CORE (Structural Integrity)
                if r_raw < solid_core_radius:
                    grid[x_idx, y_idx, z_idx] = True
                    continue
                
                # 4. END CAPS (Solid mating surfaces)
                # Bottom 2mm and Top 2mm
                if (pz < 2.0) or (pz > height - 2.0):
                    grid[x_idx, y_idx, z_idx] = True
                    continue
                
                # 5. TWISTED COORDINATE SYSTEM
                # Rotate (px, py) by theta
                px_rot = px_raw * cos_t - py_raw * sin_t
                py_rot = px_raw * sin_t + py_raw * cos_t
                
                # 6. GYROID GENERATION (Arterial Helix v2.0)
                # Intertwined veins: Gyroid + Phase shifted Gyroid?
                # Or simply thicken the Gyroid walls to merge veins
                
                # Standard Gyroid
                val = math.sin(px_rot * scale) * math.cos(py_rot * scale) + \
                      math.sin(py_rot * scale) * math.cos(pz * scale) + \
                      math.sin(pz * scale) * math.cos(px_rot * scale)
                
                # Double Helix Illusion: Threshold band?
                # abs(val - 0.5) < 0.2 ?
                
                if abs(val) < 0.5: # Thicker veins for v2.0
                    grid[x_idx, y_idx, z_idx] = True
                else:
                    grid[x_idx, y_idx, z_idx] = False

    # Clean Dust (Strict QA)
    grid = lamp_lib.clean_voxel_grid(grid)

    # Mesh Extraction (Library)
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step_x, diam_base, diam_base)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "redshift_shaft.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_shaft(output_file)