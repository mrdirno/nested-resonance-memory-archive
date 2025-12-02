import numpy as np
import math
import sys
import struct

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES 01: THE SINGULARITY (SHAFT)
# -----------------------------------------------------------------------------
# Logic:
# 1. Shape: Hyperboloid of One Sheet (Spaghetification Look).
# 2. Core: 14mm Central Channel.
# 3. Ends: 10mm Holes for 1/8 IP Nipple.
# 4. Texture: Stretched Ribs.
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

def generate_shaft(output_path, height=160.0, resolution=120):
    print(f"Generating SINGULARITY SHAFT: {output_path}")
    
    # Dimensions
    waist_radius = 15.0
    base_radius = 35.0
    top_radius = 25.0
    
    # Core
    core_radius = 7.0 # 14mm Dia
    nipple_radius = 5.0 # 10mm Dia
    nipple_depth = 15.0 
    
    max_radius = max(base_radius, top_radius) + 5.0
    step = height / resolution
    
    res_x = int(2 * max_radius / step) + 2
    res_y = int(2 * max_radius / step) + 2
    res_z = int(height / step) + 1
    
    print(f"Grid: {res_x}x{res_y}x{res_z}")
    
    vertices = []
    faces = []
    grid = np.zeros((res_x, res_y, res_z), dtype=bool)
    
    # Texture Scale
    rib_count = 12
    rib_depth = 2.0
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        z_norm = z_mm / height # 0 to 1
        
        # Hyperboloid Profile interpolation
        # Let's place waist at z_norm = 0.4
        waist_z = 0.4
        
        # Curve function: quadratic bezier approximation or simple hyperbolic
        # r(z) = sqrt(waist^2 + c * (z-waist_z)^2)
        
        # Determine 'c' based on boundary conditions?
        # Let's just interpolate linearly between parabolas
        
        if z_norm < waist_z:
            # Bottom section
            t = (waist_z - z_norm) / waist_z # 1 at bottom, 0 at waist
            current_base_radius = waist_radius + (base_radius - waist_radius) * (t**1.5)
        else:
            # Top section
            t = (z_norm - waist_z) / (1.0 - waist_z) # 0 at waist, 1 at top
            current_base_radius = waist_radius + (top_radius - waist_radius) * (t**2.0) # Stretchy look
            
        for x_idx in range(res_x):
            x_mm = (x_idx * step) - max_radius
            
            for y_idx in range(res_y):
                y_mm = (y_idx * step) - max_radius
                
                dist = math.sqrt(x_mm**2 + y_mm**2)
                angle = math.atan2(y_mm, x_mm)
                
                # Texture: Ribs that twist slightly
                twist = z_norm * math.pi * 0.5
                rib_mod = math.cos(rib_count * angle + twist)
                effective_radius = current_base_radius + (rib_mod * rib_depth)
                
                is_solid = False
                
                # Outer Shell
                if dist <= effective_radius:
                    is_solid = True
                    
                # Inner Core (Cable Channel)
                if dist < core_radius:
                    is_solid = False
                    
                # Nipple Holes (Ends)
                if z_mm < nipple_depth or z_mm > (height - nipple_depth):
                    if dist < nipple_radius:
                        is_solid = False
                        
                grid[x_idx,y_idx,z_idx] = is_solid

    # Mesh Extraction
    def add_quad(v1, v2, v3, v4):
        idx = len(vertices)
        vertices.extend([v1, v2, v3, v4])
        faces.append((idx, idx+1, idx+2))
        faces.append((idx, idx+2, idx+3))

    for z in range(res_z):
        z_mm = z * step
        for x in range(res_x):
            x_mm = (x * step) - max_radius
            for y in range(res_y):
                y_mm = (y * step) - max_radius
                if not grid[x,y,z]: continue
                s2 = step/2
                if x==res_x-1 or not grid[x+1,y,z]: add_quad((x_mm+s2, y_mm-s2, z_mm-s2), (x_mm+s2, y_mm+s2, z_mm-s2), (x_mm+s2, y_mm+s2, z_mm+s2), (x_mm+s2, y_mm-s2, z_mm+s2))
                if x==0 or not grid[x-1,y,z]: add_quad((x_mm-s2, y_mm-s2, z_mm+s2), (x_mm-s2, y_mm+s2, z_mm+s2), (x_mm-s2, y_mm+s2, z_mm-s2), (x_mm-s2, y_mm-s2, z_mm-s2))
                if y==res_y-1 or not grid[x,y+1,z]: add_quad((x_mm+s2, y_mm+s2, z_mm-s2), (x_mm-s2, y_mm+s2, z_mm-s2), (x_mm-s2, y_mm+s2, z_mm+s2), (x_mm+s2, y_mm+s2, z_mm+s2))
                if y==0 or not grid[x,y-1,z]: add_quad((x_mm-s2, y_mm-s2, z_mm-s2), (x_mm+s2, y_mm-s2, z_mm-s2), (x_mm+s2, y_mm+s2, z_mm-s2), (x_mm-s2, y_mm-s2, z_mm-s2))
                if z==res_z-1 or not grid[x,y,z+1]: add_quad((x_mm+s2, y_mm-s2, z_mm+s2), (x_mm+s2, y_mm+s2, z_mm+s2), (x_mm-s2, y_mm+s2, z_mm+s2), (x_mm+s2, y_mm-s2, z_mm+s2))
                if z==0 or not grid[x,y,z-1]: add_quad((x_mm-s2, y_mm-s2, z_mm-s2), (x_mm+s2, y_mm-s2, z_mm-s2), (x_mm+s2, y_mm+s2, z_mm-s2), (x_mm-s2, y_mm-s2, z_mm-s2))

    write_binary_stl(output_path, vertices, faces)
    print(f"Saved: {output_path}")

if __name__ == "__main__":
    output_file = "fabrication/furniture/lamp_series_01/03_singularity/singularity_shaft.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_shaft(output_file)
