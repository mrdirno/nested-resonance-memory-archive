import numpy as np
import math
import sys
import struct

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES 01: THE EVENT HORIZON (SHADE) - V4 FIX (PRACTICALITY)
# -----------------------------------------------------------------------------
# Logic: 
# 1. Schwarz D Pattern (Z-Scaled).
# 2. Shell Masking (Hollow).
# 3. **Cylindrical Core Void**: Force 90mm dia clearance for hand/bulb.
# 4. Top Plate overrides everything.
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

def generate_shade(output_path, diameter=160.0, height=140.0, resolution=100, hole_diameter=42.0):
    print(f"Generating EVENT HORIZON SHADE (V4 PRACTICALITY FIX): {output_path}")
    
    # Mount Parameters
    mount_hole_radius = hole_diameter / 2.0 # 21mm
    mount_plate_radius = mount_hole_radius + 8.0 # 29mm
    solid_rim_height = 4.0 
    
    # Shell Parameters
    # We want a thin shell for the pattern
    shell_thickness = 5.0 
    
    # Practicality Parameters (The Fix)
    # Hand access needs ~80-90mm diameter.
    # Bulb needs ~60mm.
    # Let's enforce a Cylindrical Keep-Out of Radius 45mm (Diam 90mm).
    # BUT, the top plate hole is 42mm (Radius 21).
    # So the void must taper or step?
    # No, the void is for the HAND to reach up.
    # The void stops at the Top Plate.
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
    
    # Frequency Setup
    base_scale = 2.0 * math.pi / (diameter / 5.0) 
    max_scale_factor = 1.5 # Conservative clamp to ensure holes stay open
    
    print("Calculating Field...")
    
    radius = diameter / 2.0
    sphere_z_center = height - radius
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        
        # Z-Scaling
        z_norm = z_mm / height
        current_scale_factor = 1.0 + (1.0 * z_norm)
        if current_scale_factor > max_scale_factor:
            current_scale_factor = max_scale_factor
        current_scale = base_scale * current_scale_factor
        
        for x_idx in range(res_x):
            x_mm = (x_idx * step) - (diameter / 2.0)
            
            for y_idx in range(res_y):
                y_mm = (y_idx * step) - (diameter / 2.0)
                
                dist_from_center_xy = math.sqrt(x_mm**2 + y_mm**2)
                dist_sq = x_mm**2 + y_mm**2 + (z_mm - sphere_z_center)**2
                dist_spherical = math.sqrt(dist_sq)
                
                # --- LOGIC STACK ---
                is_solid = False
                
                # 1. Shell Masking
                in_outer_shell = dist_spherical <= radius
                in_inner_void = dist_spherical < (radius - shell_thickness)
                
                # 2. Hand Access Void (Override Inner Void)
                # If we are inside the hand access cylinder, we are definitely void.
                # Unless we are at the Top Plate.
                in_hand_void = dist_from_center_xy < hand_access_radius
                
                # Combined Void Logic:
                # Void if (Spherical Inner Void) OR (Hand Access Cylinder)
                is_void = in_inner_void or in_hand_void
                
                if in_outer_shell and not is_void:
                     # 3. Pattern Generation
                     lx = x_mm * current_scale
                     ly = y_mm * current_scale
                     lz = z_mm * current_scale
                     
                     sx, sy, sz = math.sin(lx), math.sin(ly), math.sin(lz)
                     cx, cy, cz = math.cos(lx), math.cos(ly), math.cos(lz)
                     
                     val = sx*sy*sz + sx*cy*cz + cx*sy*cz + cx*cy*sz
                     
                     if abs(val) < 0.35: 
                         is_solid = True
                
                # 4. Structural Overrides
                
                # A. Top Plate (Mounting) - SUPREME AUTHORITY
                if z_mm > (height - solid_rim_height):
                    if dist_from_center_xy < mount_plate_radius:
                        is_solid = True
                        
                # B. Bottom Rim
                if z_mm < solid_rim_height:
                    # Make sure the rim extends inwards enough to meet the pattern
                    # But respects the Hand Void? 
                    # No, the rim can be slightly tighter if needed, but 90mm is wide.
                    # Let's trust the hand void.
                    if dist_from_center_xy < radius and not in_hand_void:
                        is_solid = True
                        
                # 5. Hardware Subtracts
                
                # A. Mounting Hole
                if z_mm > (height - solid_rim_height):
                    if dist_from_center_xy < mount_hole_radius:
                        is_solid = False
                        
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