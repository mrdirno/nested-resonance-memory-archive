import numpy as np
import math
import sys
import struct

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES 01: THE EVENT HORIZON (SHADE) - V3 FIX (HOLLOW + Z-SCALE)
# -----------------------------------------------------------------------------
# Logic: 
# 1. Schwarz D (Diamond) Pattern
# 2. Shell Logic: Pattern only generates between Inner Radius and Outer Radius.
# 3. Z-Scaling: Frequency increases with Z (Wavelength shrinks).
# 4. Top Plate overrides Spherical Boundary.
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
    print(f"Generating EVENT HORIZON SHADE (V3 FIX): {output_path}")
    
    # Mount Parameters
    mount_hole_radius = hole_diameter / 2.0 # 21mm
    mount_plate_radius = mount_hole_radius + 8.0 # 29mm outer radius for plate
    solid_rim_height = 4.0 
    
    # Shell Parameters
    shell_thickness = 4.0 # Actual shell thickness for the pattern region
    
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
    
    # Frequency Setup (Schwarz D)
    # Base Scale (Bottom)
    base_scale = 2.0 * math.pi / (diameter / 5.0) 
    
    # Max Frequency Constraint (Smallest wave limit)
    # "Never go smaller than the smallest wave" -> Interpretation:
    # Let's assume the user liked the top of a previous design or wants a safety limit.
    # Let's limit the scale factor to 2.0x base (Half wavelength).
    max_scale_factor = 2.0 
    
    print("Calculating Field (Schwarz D with Z-Scaling)...")
    
    radius = diameter / 2.0
    sphere_z_center = height - radius
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        
        # Z-Norm for scaling
        z_norm = z_mm / height
        
        # Scale Modulation: Linear ramp up
        # Scale = Base * (1 + k*z)
        # At z=0, Scale = Base.
        # At z=H, Scale = Base * (1 + k).
        # Let k=1.0 (Doubles frequency at top).
        current_scale_factor = 1.0 + (1.0 * z_norm)
        
        # Clamp (Safety limit)
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
                
                # --- BOOLEAN LOGIC STACK ---
                is_solid = False
                
                # 1. Shell Masking (The "Hollow" Fix)
                # Check if voxel is within the spherical shell volume
                in_outer_shell = dist_spherical <= radius
                in_inner_void = dist_spherical < (radius - shell_thickness)
                
                if in_outer_shell and not in_inner_void:
                     # 2. Pattern Generation
                     lx = x_mm * current_scale
                     ly = y_mm * current_scale
                     lz = z_mm * current_scale
                     
                     sx, sy, sz = math.sin(lx), math.sin(ly), math.sin(lz)
                     cx, cy, cz = math.cos(lx), math.cos(ly), math.cos(lz)
                     
                     val = sx*sy*sz + sx*cy*cz + cx*sy*cz + cx*cy*sz
                     
                     if abs(val) < 0.4: # Slightly thicker walls for printability
                         is_solid = True
                
                # 3. Structural Overrides
                
                # A. Top Plate (Mounting)
                if z_mm > (height - solid_rim_height):
                    if dist_from_center_xy < mount_plate_radius:
                        is_solid = True
                        
                # B. Bottom Rim
                if z_mm < solid_rim_height:
                    if dist_from_center_xy < radius and dist_from_center_xy > (radius - shell_thickness - 2.0):
                        is_solid = True
                        
                # 4. Hardware Subtracts
                
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
