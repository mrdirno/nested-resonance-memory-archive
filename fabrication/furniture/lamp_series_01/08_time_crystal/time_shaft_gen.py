import numpy as np
import math
import sys
import struct

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES 01: THE TIME CRYSTAL (SHAFT)
# -----------------------------------------------------------------------------
# Logic:
# 1. Shape: Twisted Hexagonal Prism.
# 2. Core: 14mm Central Channel.
# 3. Ends: 10mm Holes.
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
    print(f"Generating TIME SHAFT: {output_path}")
    
    # Dimensions
    radius = 20.0
    
    # Core
    core_radius = 7.0 
    nipple_radius = 5.0 
    nipple_depth = 15.0 
    
    step = height / resolution
    
    res_x = int(2 * radius / step) + 2
    res_y = int(2 * radius / step) + 2
    res_z = int(height / step) + 1
    
    print(f"Grid: {res_x}x{res_y}x{res_z}")
    
    vertices = []
    faces = []
    grid = np.zeros((res_x, res_y, res_z), dtype=bool)
    
    # Twist Params
    sides = 6
    total_twist = math.pi # 180 deg
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        z_norm = z_mm / height
        
        current_twist = z_norm * total_twist
        
        for x_idx in range(res_x):
            x_mm = (x_idx * step) - radius
            
            for y_idx in range(res_y):
                y_mm = (y_idx * step) - radius
                
                dist = math.sqrt(x_mm**2 + y_mm**2)
                
                # Rotate point to base frame
                rx = x_mm * math.cos(-current_twist) - y_mm * math.sin(-current_twist)
                ry = x_mm * math.sin(-current_twist) + y_mm * math.cos(-current_twist)
                
                angle = math.atan2(ry, rx)
                
                # Hexagon Logic
                # Dist to edge: r * cos(a - center)
                sector = 2*math.pi / sides
                a_quant = math.floor(angle / sector) * sector + (sector/2)
                
                # Distance to flat face
                d_poly = dist * math.cos(angle - a_quant)
                
                # Radius of inscribed circle = 15mm?
                r_in = 15.0
                
                is_solid = False
                
                # Polygon Shell
                if d_poly < r_in:
                    is_solid = True
                    
                # Inner Core
                if dist < core_radius:
                    is_solid = False
                    
                # Nipple Holes
                if z_mm < nipple_depth or z_mm > (height - nipple_depth):
                    if dist < nipple_radius:
                        is_solid = False
                        
                grid[x_idx,y_idx,z_idx] = is_solid

    # Mesh
    def add_quad(v1, v2, v3, v4):
        idx = len(vertices)
        vertices.extend([v1, v2, v3, v4])
        faces.append((idx, idx+1, idx+2))
        faces.append((idx, idx+2, idx+3))

    for z in range(res_z):
        z_mm = z * step
        for x in range(res_x):
            x_mm = (x * step) - radius
            for y in range(res_y):
                y_mm = (y * step) - radius
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
    output_file = "fabrication/furniture/lamp_series_01/08_time_crystal/time_shaft.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_shaft(output_file)
