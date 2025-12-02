import numpy as np
import math
import sys
import struct

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES 01: THE LATTICE (SHAFT)
# -----------------------------------------------------------------------------
# Logic: Cubic Lattice Column
# Dims: 50mm Square Column -> Height 200mm
# Core: Hollow Tube for Wire
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

def generate_shaft(output_path, width=50.0, height=200.0, resolution=100):
    print(f"Generating LATTICE SHAFT: {output_path}")
    
    # Core Parameters
    core_hole_radius = 5.0 # 10mm hole for M10 rod/wire
    core_wall_radius = 8.0 # 16mm solid core tube
    
    # Grid Setup
    step = width / resolution
    
    res_xy = int(width / step) + 5
    res_z = int(height / step) + 1
    
    print(f"Grid: {res_xy}x{res_xy}x{res_z} (Voxel size: {step:.2f}mm)")
    
    vertices = []
    faces = []
    grid = np.zeros((res_xy, res_xy, res_z), dtype=bool)
    
    # Lattice Parameters
    freq = 2.0 * math.pi / 25.0 # 25mm cells
    
    print("Calculating Field...")
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        
        for x_idx in range(res_xy):
            x_mm = (x_idx * step) - (width / 2.0)
            
            for y_idx in range(res_xy):
                y_mm = (y_idx * step) - (width / 2.0)
                
                # 1. Boundary (Square Column)
                if abs(x_mm) > (width/2.0) or abs(y_mm) > (width/2.0):
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                
                dist_xy = math.sqrt(x_mm**2 + y_mm**2)
                
                # 2. Inner Hole
                if dist_xy < core_hole_radius:
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                
                # 3. Solid Core Tube (Artery)
                if dist_xy < core_wall_radius:
                    grid[x_idx,y_idx,z_idx] = True
                    continue
                
                # 3a. PERFECTION LOOP: Solid Caps for Adhesion/Mating
                if z_mm < 3.0 or z_mm > (height - 3.0):
                    grid[x_idx,y_idx,z_idx] = True
                    continue

                # 4. Lattice Structure
                # Schwarz P
                val = math.cos(x_mm * freq) + math.cos(y_mm * freq) + math.cos(z_mm * freq)
                
                if abs(val) < 0.6:
                    grid[x_idx,y_idx,z_idx] = True
                else:
                    grid[x_idx,y_idx,z_idx] = False

    print("Extracting Mesh...")
    def add_quad(v1, v2, v3, v4):
        idx = len(vertices)
        vertices.extend([v1, v2, v3, v4])
        faces.append((idx, idx+1, idx+2))
        faces.append((idx, idx+2, idx+3))

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
                if y==0 or not grid[x,y-1,z]: add_quad((x_mm-s2, y_mm-s2, z_mm-s2), (x_mm+s2, y_mm-s2, z_mm-s2), (x_mm+s2, y_mm-s2, z_mm+s2), (x_mm-s2, y_mm-s2, z_mm-s2))
                if z==res_z-1 or not grid[x,y,z+1]: add_quad((x_mm+s2, y_mm-s2, z_mm+s2), (x_mm+s2, y_mm+s2, z_mm+s2), (x_mm-s2, y_mm+s2, z_mm+s2), (x_mm+s2, y_mm-s2, z_mm+s2))
                if z==0 or not grid[x,y,z-1]: add_quad((x_mm-s2, y_mm-s2, z_mm-s2), (x_mm-s2, y_mm+s2, z_mm-s2), (x_mm+s2, y_mm+s2, z_mm-s2), (x_mm-s2, y_mm+s2, z_mm-s2))

    write_binary_stl(output_path, vertices, faces)
    print(f"Saved: {output_path}")

if __name__ == "__main__":
    output_file = "fabrication/furniture/lamp_series_01/06_lattice/lattice_shaft.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_shaft(output_file)
