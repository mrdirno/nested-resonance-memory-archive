import numpy as np
import math
import sys
import struct
import os

# Add project root to path for library import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES 05: THE AETHER (BASE)
# -----------------------------------------------------------------------------
# Logic: Floating Ring (Levitation Illusion).
# Features: Wire Channel, Feet Recesses (V4 Std).
# Pattern: Void center with minimal supports.
# -----------------------------------------------------------------------------

def generate_base(output_path, diameter=140.0, height=30.0, resolution=100):
    print(f"Generating AETHER BASE: {output_path}")
    
    radius = diameter / 2.0
    
    # V4 QA Params
    rod_radius = 7.0 # 14mm
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
    
    # Ring Geometry
    # Donut shape hovering?
    # Cannot truly hover. Must have central stem.
    # Make central stem minimal (hidden in shadow).
    
    stem_radius = 25.0
    
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
                
                # Base Body
                if dist <= radius:
                    # "Floating" Ring
                    # Thick outer ring
                    # Thin central stem
                    
                    is_solid = False
                    
                    # Central Stem
                    if dist < stem_radius:
                        is_solid = True
                        
                    # Bottom Plate (Stability)
                    if z_mm < 5.0:
                        is_solid = True
                        
                    # Outer Ring (Levitating)
                    # Torus profile
                    ring_r = radius * 0.8
                    ring_thickness = 10.0
                    
                    # Dist to ring center
                    d_ring = math.sqrt((dist - ring_r)**2 + (z_mm - height/2)**2)
                    if d_ring < ring_thickness:
                        is_solid = True
                        
                    # Connectors (Thin spokes)
                    # 3 spokes connecting stem to ring
                    # if abs(sin(3*angle)) < width
                    
                    if dist >= stem_radius and dist <= (ring_r - ring_thickness):
                        # Spoke check
                        spoke_w = 4.0
                        # Distance to 3 lines
                        # Rotate so one is on X axis
                        
                        in_spoke = False
                        for i in range(3):
                            sa = i * 2*math.pi/3
                            # distance from point to line
                            # normal vector (-sin, cos)
                            d_line = abs(x_mm * -math.sin(sa) + y_mm * math.cos(sa))
                            if d_line < (spoke_w/2.0):
                                # Vertical bounds for spoke
                                if abs(z_mm - height/2) < (spoke_w/2.0):
                                    in_spoke = True
                        
                        if in_spoke: is_solid = True
                        
                    if is_solid:
                        grid[x_idx,y_idx,z_idx] = True
                    else:
                        grid[x_idx,y_idx,z_idx] = False
                else:
                    grid[x_idx,y_idx,z_idx] = False

    # Mesh Extraction
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, diameter, diameter)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "aether_base.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_base(output_file)
