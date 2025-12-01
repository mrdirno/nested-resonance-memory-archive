import numpy as np
import math
import sys
import struct

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

def generate_shaft(output_path, height=200.0, resolution=150):
    print(f"Generating HELICAL SHAFT: {output_path}")
    
    # Dimensions
    core_radius = 7.5 # 15mm Diameter
    inner_radius = 5.0 # 10mm Diameter (Hole)
    
    # Helix Params
    helix_thickness = 5.0 
    # Helix Center Radius must be such that (Radius - Thickness/2) < Core_Radius
    # Target overlap = 1.0mm
    # Helix_Inner_Edge = 7.5 - 1.0 = 6.5mm
    # Helix_Radius - 2.5 = 6.5 => Helix_Radius = 9.0mm
    helix_radius = 9.0 
    
    pitch = 100.0 # mm per turn
    num_strands = 3
    
    # Grid
    width = (helix_radius + helix_thickness) * 2.5
    step = height / resolution
    
    res_xy = int(width / step) + 5
    res_z = int(height / step) + 1
    
    print(f"Grid: {res_xy}x{res_xy}x{res_z} (Voxel: {step:.2f}mm)")
    
    vertices = []
    faces = []
    grid = np.zeros((res_xy, res_xy, res_z), dtype=bool)
    
    print("Calculating Field...")
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        angle = (z_mm / pitch) * 2.0 * math.pi
        
        for x_idx in range(res_xy):
            x_mm = (x_idx * step) - (width/2)
            
            for y_idx in range(res_xy):
                y_mm = (y_idx * step) - (width/2)
                
                dist_sq = x_mm**2 + y_mm**2
                dist = math.sqrt(dist_sq)
                
                # 1. Inner Hole (Subtraction)
                if dist < inner_radius:
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                
                # 2. Central Core (Union)
                if dist < core_radius:
                    grid[x_idx,y_idx,z_idx] = True
                    continue
                
                # 3. Helical Strands (Union)
                # Check distance to helical path
                # Helix Center at Z: (R*cos(a + offset), R*sin(a + offset))
                is_helix = False
                for i in range(num_strands):
                    offset = (2.0 * math.pi / num_strands) * i
                    helix_x = helix_radius * math.cos(angle + offset)
                    helix_y = helix_radius * math.sin(angle + offset)
                    
                    # Distance from point (x,y) to helix center (hx, hy)
                    d_helix = math.sqrt((x_mm - helix_x)**2 + (y_mm - helix_y)**2)
                    
                    if d_helix < helix_thickness:
                        is_helix = True
                        break
                
                if is_helix:
                    grid[x_idx,y_idx,z_idx] = True

    print("Extracting Mesh...")
    def add_quad(v1, v2, v3, v4):
        idx = len(vertices)
        vertices.extend([v1, v2, v3, v4])
        faces.append((idx, idx+1, idx+2))
        faces.append((idx, idx+2, idx+3))

    # Extraction loop (Standard)
    for z in range(res_z):
        z_mm = z * step
        for x in range(res_xy):
            x_mm = (x * step) - (width/2)
            for y in range(res_xy):
                y_mm = (y * step) - (width/2)
                if not grid[x,y,z]: continue
                
                s2 = step/2
                if x==res_xy-1 or not grid[x+1,y,z]: add_quad((x_mm+s2, y_mm-s2, z_mm-s2), (x_mm+s2, y_mm+s2, z_mm-s2), (x_mm+s2, y_mm+s2, z_mm+s2), (x_mm+s2, y_mm-s2, z_mm+s2))
                if x==0 or not grid[x-1,y,z]: add_quad((x_mm-s2, y_mm-s2, z_mm+s2), (x_mm-s2, y_mm+s2, z_mm+s2), (x_mm-s2, y_mm+s2, z_mm-s2), (x_mm-s2, y_mm-s2, z_mm-s2))
                if y==res_xy-1 or not grid[x,y+1,z]: add_quad((x_mm+s2, y_mm+s2, z_mm-s2), (x_mm-s2, y_mm+s2, z_mm-s2), (x_mm-s2, y_mm+s2, z_mm+s2), (x_mm+s2, y_mm+s2, z_mm+s2))
                if y==0 or not grid[x,y-1,z]: add_quad((x_mm-s2, y_mm-s2, z_mm-s2), (x_mm+s2, y_mm-s2, z_mm-s2), (x_mm+s2, y_mm-s2, z_mm+s2), (x_mm-s2, y_mm-s2, z_mm+s2))
                if z==res_z-1 or not grid[x,y,z+1]: add_quad((x_mm+s2, y_mm-s2, z_mm+s2), (x_mm+s2, y_mm+s2, z_mm+s2), (x_mm-s2, y_mm+s2, z_mm+s2), (x_mm-s2, y_mm-s2, z_mm+s2))
                if z==0 or not grid[x,y,z-1]: add_quad((x_mm-s2, y_mm-s2, z_mm-s2), (x_mm+s2, y_mm-s2, z_mm-s2), (x_mm+s2, y_mm+s2, z_mm-s2), (x_mm-s2, y_mm+s2, z_mm-s2))

    write_binary_stl(output_path, vertices, faces)
    print(f"Saved: {output_path}")

if __name__ == "__main__":
    output_file = "fabrication/furniture/lamp_series_01/redshift_shaft.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_shaft(output_file)
