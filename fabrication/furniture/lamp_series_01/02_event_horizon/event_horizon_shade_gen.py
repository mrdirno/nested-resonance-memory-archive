import numpy as np
import math
import sys
import struct

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES 01: THE EVENT HORIZON (SHADE) - V6 FIX (1-INCH WALL + ROBUST MOUNT)
# -----------------------------------------------------------------------------
# Logic: 
# 1. 1-Inch Thick Wall (Robustness).
# 2. 200mm Diameter (Max Print Area).
# 3. Spider Fitter: Solid Hub (40mm) + Spokes Merging with Shell.
# 4. Scale: Matches Redshift Baseline.
# -----------------------------------------------------------------------------

def write_binary_stl(filename, vertices, faces):
    def normal(v1, v2, v3):
        u = v2 - v1
        w = v3 - v1
        nx = u[1]*w[2] - u[2]*w[1]
        ny = u[2]*w[0] - u[0]*w[2]
        nz = u[0]*w[1] - u[1]*w[0]
        n = np.array([nx, ny, nz])
        norm = np.linalg.norm(n)
        return n / norm if norm > 0 else np.array([0, 0, 1])

    num_triangles = len(faces)
    print(f"Writing Binary STL ({num_triangles} triangles)...")

    with open(filename, 'wb') as f:
        f.write(b'\0' * 80)
        f.write(struct.pack('<I', num_triangles))
        for face in faces:
            v1 = np.array(vertices[face[0]])
            v2 = np.array(vertices[face[1]])
            v3 = np.array(vertices[face[2]])
            n = normal(v1, v2, v3)
            data = struct.pack('<3f3f3f3f', n[0], n[1], n[2], v1[0], v1[1], v1[2], v2[0], v2[1], v2[2], v3[0], v3[1], v3[2])
            f.write(data)
            f.write(struct.pack('<H', 0))

def generate_shade(output_path, diameter=200.0, height=140.0, resolution=100, hole_diameter=12.5):
    print(f"Generating EVENT HORIZON SHADE (V6 ROBUST FIX): {output_path}")
    
    # Mount Parameters (Robust Spider Fitter)
    mount_hole_radius = hole_diameter / 2.0 # 6.25mm
    hub_radius = 20.0 # 40mm Solid Disk
    spoke_width = 8.0 # Thicker spokes for 1-inch wall
    solid_rim_height = 5.0 # Thicker Top Plate
    
    # Shell Parameters (The 1-Inch Rule)
    wall_thickness = 25.4 
    
    # Hand Access (Still needed, but works with 1-inch wall?)
    # Radius 100mm. Inner Wall at 75mm. 
    # Void needs to be at least ~90mm diam (45 radius).
    # 75mm > 45mm, so the hollow core is naturally large enough.
    # We just need to ensure no "internal debris" blocks it.
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
    
    # Frequency Setup (Redshift Match)
    # Redshift Base Period ~48.5mm.
    target_period = 48.5
    
    # Z-Scaling: Start Larger (60) -> Target (48.5)
    start_scale = 2.0 * math.pi / 60.0
    end_scale = 2.0 * math.pi / target_period
    
    print("Calculating Field...")
    
    radius = diameter / 2.0
    sphere_z_center = height - radius
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        z_norm = z_mm / height
        
        # Scale
        current_scale = start_scale * (1.0 - z_norm) + end_scale * z_norm
        
        for x_idx in range(res_x):
            x_mm = (x_idx * step) - (diameter / 2.0)
            
            for y_idx in range(res_y):
                y_mm = (y_idx * step) - (diameter / 2.0)
                
                dist_from_center_xy = math.sqrt(x_mm**2 + y_mm**2)
                dist_sq = x_mm**2 + y_mm**2 + (z_mm - sphere_z_center)**2
                dist_spherical = math.sqrt(dist_sq)
                
                # --- PRIORITY 1: TOP SPIDER FITTER (THE MOUNT) ---
                if z_mm > (height - solid_rim_height):
                    # 1. Hole
                    if dist_from_center_xy < mount_hole_radius:
                        grid[x_idx,y_idx,z_idx] = False
                        continue
                        
                    # 2. Hub (Solid Disk)
                    if dist_from_center_xy < hub_radius:
                        grid[x_idx,y_idx,z_idx] = True
                        continue
                        
                    # 3. Spokes (Connecting Hub to Inner Wall)
                    # We need spokes to cross the "Void" between Hub (20mm) and Wall (Starts at Radius - 25.4mm = 74.6mm)
                    # So spokes run from 20mm to ~75mm.
                    if dist_from_center_xy < (radius - wall_thickness + 2.0): # Overlap slightly with wall
                         if abs(x_mm) < (spoke_width/2) or abs(y_mm) < (spoke_width/2):
                             grid[x_idx,y_idx,z_idx] = True
                             continue
                    
                    # 4. The Rest (Shell Top)
                    # The shell logic below will handle the rim, but we can force solid rim here to be safe.
                    if dist_from_center_xy < radius and dist_from_center_xy > (radius - wall_thickness):
                        grid[x_idx,y_idx,z_idx] = True
                    continue
                    
                # --- PRIORITY 2: SHELL & PATTERN ---
                
                is_solid = False
                
                # 1. Shell Definition (1-Inch Thick)
                in_outer_shell = dist_spherical <= radius
                in_inner_void = dist_spherical < (radius - wall_thickness)
                
                # 2. Hand Access (Redundant here usually, but keeps core clear)
                in_hand_void = dist_from_center_xy < hand_access_radius
                is_void = in_inner_void or in_hand_void
                
                if in_outer_shell and not is_void:
                    # Pattern
                    lx = x_mm * current_scale
                    ly = y_mm * current_scale
                    lz = z_mm * current_scale
                     
                    sx, sy, sz = math.sin(lx), math.sin(ly), math.sin(lz)
                    cx, cy, cz = math.cos(lx), math.cos(ly), math.cos(lz)
                     
                    val = sx*sy*sz + sx*cy*cz + cx*sy*cz + cx*cy*sz
                    
                    # Threshold tuned for 1-inch wall to be robust but not solid
                    # With thicker wall, we can afford a lower threshold (thinner lattice members) 
                    # OR higher threshold (denser).
                    # Let's keep it standard 0.35 to ensure connectivity.
                    if abs(val) < 0.35: 
                        is_solid = True
                        
                # --- PRIORITY 3: BOTTOM RIM ---
                if z_mm < solid_rim_height:
                    if dist_from_center_xy < radius and not in_hand_void:
                         is_solid = True
                         
                grid[x_idx,y_idx,z_idx] = is_solid

    print("Extracting Mesh...")
    def add_quad(v1, v2, v3, v4):
        idx = len(vertices)
        vertices.extend([v1, v2, v3, v4])
        faces.append((idx, idx+1, idx+2))
        faces.append((idx, idx+2, idx+3))

    for z in range(res_z):
        z_mm = z * step
        for x in range(res_x):
            x_mm = (x * step) - (diameter/2)
            for y in range(res_y):
                y_mm = (y * step) - (diameter/2)
                
                if not grid[x,y,z]: continue
                s2 = step/2
                
                if x==res_x-1 or not grid[x+1,y,z]: add_quad((x_mm+s2, y_mm-s2, z_mm-s2), (x_mm+s2, y_mm+s2, z_mm-s2), (x_mm+s2, y_mm+s2, z_mm+s2), (x_mm+s2, y_mm-s2, z_mm+s2))
                if x==0 or not grid[x-1,y,z]: add_quad((x_mm-s2, y_mm-s2, z_mm+s2), (x_mm-s2, y_mm+s2, z_mm+s2), (x_mm-s2, y_mm+s2, z_mm-s2), (x_mm-s2, y_mm-s2, z_mm-s2))
                if y==res_y-1 or not grid[x,y+1,z]: add_quad((x_mm+s2, y_mm+s2, z_mm-s2), (x_mm-s2, y_mm+s2, z_mm-s2), (x_mm-s2, y_mm+s2, z_mm+s2), (x_mm+s2, y_mm+s2, z_mm+s2))
                if y==0 or not grid[x,y-1,z]: add_quad((x_mm-s2, y_mm-s2, z_mm-s2), (x_mm+s2, y_mm-s2, z_mm-s2), (x_mm+s2, y_mm+s2, z_mm-s2), (x_mm-s2, y_mm-s2, z_mm-s2))
                if z==res_z-1 or not grid[x,y,z+1]: add_quad((x_mm+s2, y_mm-s2, z_mm+s2), (x_mm+s2, y_mm+s2, z_mm+s2), (x_mm-s2, y_mm+s2, z_mm+s2), (x_mm-s2, y_mm-s2, z_mm+s2))
                if z==0 or not grid[x,y,z-1]: add_quad((x_mm-s2, y_mm-s2, z_mm-s2), (x_mm+s2, y_mm-s2, z_mm-s2), (x_mm+s2, y_mm+s2, z_mm-s2), (x_mm-s2, y_mm-s2, z_mm-s2))

    write_binary_stl(output_path, vertices, faces)
    print(f"Saved: {output_path}")

if __name__ == "__main__":
    output_file = "fabrication/furniture/lamp_series_01/02_event_horizon/event_horizon_shade.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_shade(output_file)