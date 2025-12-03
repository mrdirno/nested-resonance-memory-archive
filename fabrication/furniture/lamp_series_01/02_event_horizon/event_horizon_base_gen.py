import numpy as np
import math
import sys
import struct
import os

# Add project root to path for library import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES 01: THE EVENT HORIZON (BASE) v2.0
# -----------------------------------------------------------------------------
# REFINEMENT v2.0: Spiral Gravity Well Relief, Library Integration.
# Logic: Swirling Vortex Accretion Disk.
# Features: V4 QA (Wire Channel, Feet, Solid Core).
# -----------------------------------------------------------------------------

def generate_base(output_path, diameter=140.0, height=30.0, resolution=100):
    print(f"Generating EVENT HORIZON BASE (v2.0): {output_path}")
    
    radius = diameter / 2.0
    
    # V4 QA Params
    rod_radius = 7.0 
    foot_radius = 10.0
    foot_depth = 3.0
    foot_offset = 15.0
    channel_height = 8.0
    channel_width = 8.0
    
    step = diameter / resolution
    res_xy = int(diameter / step) + 2
    res_z = int(height / step) + 1
    
    print(f"Grid: {res_xy}x{res_xy}x{res_z}")
    
    grid = np.zeros((res_xy, res_xy, res_z), dtype=bool)
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        
        for x_idx in range(res_xy):
            x_mm = (x_idx * step) - radius
            for y_idx in range(res_xy):
                y_mm = (y_idx * step) - radius
                
                dist = math.sqrt(x_mm**2 + y_mm**2)
                angle = math.atan2(y_mm, x_mm)
                
                # V4 Features
                feature_check = lamp_lib.apply_base_v4_features(
                    x_mm, y_mm, z_mm, dist,
                    height=height,
                    hole_radius=rod_radius,
                    channel_height=channel_height,
                    channel_width=channel_width,
                    foot_depth=foot_depth,
                    foot_radius=foot_radius,
                    foot_offset=foot_offset,
                    radius=radius
                )
                
                if feature_check is not None:
                    grid[x_idx,y_idx,z_idx] = feature_check
                    continue
                
                # Base Body (The Naked Singularity)
                # NO SOLID CAP. See-through Lattice.
                
                if dist <= radius:
                    # 1. Lattice Logic (High Twist)
                    twist = (dist/radius) * 6.0 * math.pi # High spin
                    angle_twist = angle + twist
                    
                    # Anisotropic Lattice
                    # Stretch radially
                    base_k = 2.0 * math.pi / 20.0
                    
                    lx = dist * math.cos(angle_twist) * base_k
                    ly = dist * math.sin(angle_twist) * base_k
                    lz = z_mm * base_k
                    
                    val = math.sin(lx)*math.cos(ly) + math.sin(ly)*math.cos(lz) + math.sin(lz)*math.cos(lx)
                    
                    is_lattice = abs(val) < 0.4
                    
                    # 2. Structural Ribs (Integration)
                    # We need solid ribs for the feet and channel to exist within
                    # 4 Radial Ribs at 90 degrees
                    rib_angle_mod = abs(math.sin(2.0 * angle)) # Peaks at 45 deg? No, 2*angle peaks 4 times.
                    # Peaks at 45, 135... 
                    # Let's align with feet (45 degrees offset)
                    in_rib = rib_angle_mod > 0.9 # Thick ribs
                    
                    # 3. Feet/Channel Logic (Subtraction)
                    # We calculated feature_check earlier (False = Void)
                    # But now we need to ensure there is MATERIAL around the void
                    
                    # Rim
                    if dist > (radius - 4.0):
                        grid[x_idx,y_idx,z_idx] = True
                        continue
                        
                    # Core (Rod)
                    if dist < 12.0:
                        grid[x_idx,y_idx,z_idx] = True
                        continue
                        
                    # Combine Lattice + Ribs
                    if is_lattice or in_rib:
                        grid[x_idx,y_idx,z_idx] = True
                    else:
                        grid[x_idx,y_idx,z_idx] = False
                        
                else:
                    grid[x_idx,y_idx,z_idx] = False

    # Clean Dust (Strict QA)
    grid = lamp_lib.clean_voxel_grid(grid)

    # Mesh Extraction
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, diameter, diameter)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "event_horizon_base.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_base(output_file)
