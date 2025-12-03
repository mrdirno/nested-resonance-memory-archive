import numpy as np
import math
import struct
import os
import sys

# ==========================================
# CONFIGURATION
# ==========================================
OUTPUT_FILE = "fabrication/practical_design/LAMP_DESIGN/qa_tolerance_test.stl"
RESOLUTION = 60 
SIZE_Z = 15.0
SIZE_XY = 50.0

# Socket Interface Specs (From Base V6)
RECESS_DIAMETER = 40.5
RECESS_DEPTH = 3.0

# Plug Interface Specs (From Shaft V6)
PLUG_DIAMETER = 40.0
PLUG_HEIGHT = 3.0

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
    print(f"  -> Writing Binary STL to {filename} ({num_triangles} triangles)...")
    
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    with open(filename, 'wb') as f:
        f.write(b'\0' * 80)
        f.write(struct.pack('<I', num_triangles))
        for face in faces:
            v1 = np.array(vertices[face[0]])
            v2 = np.array(vertices[face[1]])
            v3 = np.array(vertices[face[2]])
            n = normal(v1, v2, v3)
            f.write(struct.pack('<3f3f3f3f', n[0], n[1], n[2], v1[0], v1[1], v1[2], v2[0], v2[1], v2[2], v3[0], v3[1], v3[2]))
            f.write(struct.pack('<H', 0))
    print("  -> Done.")

def mesh_grid(grid, step, center_x, center_y):
    print("  -> Meshing...")
    vertices = []
    faces = []
    s = step / 2.0
    res_x, res_y, res_z = grid.shape

    for z in range(res_z):
        z_mm = (z * step) + s # Fix Z-Offset
        for x in range(res_x):
            x_mm = (x * step) - center_x
            for y in range(res_y):
                if not grid[x,y,z]: continue
                y_mm = (y * step) - center_y
                
                if x==res_x-1 or not grid[x+1,y,z]:
                    idx = len(vertices)
                    vertices.extend([(x_mm+s, y_mm-s, z_mm-s), (x_mm+s, y_mm+s, z_mm-s), (x_mm+s, y_mm+s, z_mm+s), (x_mm+s, y_mm-s, z_mm+s)])
                    faces.extend([(idx, idx+1, idx+2), (idx, idx+2, idx+3)])
                if x==0 or not grid[x-1,y,z]:
                    idx = len(vertices)
                    vertices.extend([(x_mm-s, y_mm-s, z_mm+s), (x_mm-s, y_mm+s, z_mm+s), (x_mm-s, y_mm+s, z_mm-s), (x_mm-s, y_mm-s, z_mm-s)])
                    faces.extend([(idx, idx+1, idx+2), (idx, idx+2, idx+3)])
                if y==res_y-1 or not grid[x,y+1,z]:
                    idx = len(vertices)
                    vertices.extend([(x_mm+s, y_mm+s, z_mm-s), (x_mm-s, y_mm+s, z_mm-s), (x_mm-s, y_mm+s, z_mm+s), (x_mm+s, y_mm+s, z_mm+s)])
                    faces.extend([(idx, idx+1, idx+2), (idx, idx+2, idx+3)])
                if y==0 or not grid[x,y-1,z]:
                    idx = len(vertices)
                    vertices.extend([(x_mm-s, y_mm-s, z_mm-s), (x_mm+s, y_mm-s, z_mm-s), (x_mm+s, y_mm-s, z_mm+s), (x_mm-s, y_mm+s, z_mm+s)])
                    faces.extend([(idx, idx+1, idx+2), (idx, idx+2, idx+3)])
                if z==res_z-1 or not grid[x,y,z+1]:
                    idx = len(vertices)
                    vertices.extend([(x_mm+s, y_mm-s, z_mm+s), (x_mm+s, y_mm+s, z_mm+s), (x_mm-s, y_mm+s, z_mm+s), (x_mm-s, y_mm-s, z_mm+s)])
                    faces.extend([(idx, idx+1, idx+2), (idx, idx+2, idx+3)])
                if z==0 or not grid[x,y,z-1]:
                    idx = len(vertices)
                    vertices.extend([(x_mm-s, y_mm-s, z_mm-s), (x_mm-s, y_mm+s, z_mm-s), (x_mm+s, y_mm+s, z_mm-s), (x_mm+s, y_mm-s, z_mm-s)])
                    faces.extend([(idx, idx+1, idx+2), (idx, idx+2, idx+3)])
    return vertices, faces

def generate_tolerance_test():
    print(f"Initializing QA Tolerance Test...")
    
    # We generate TWO objects side-by-side
    # 1. Base Recess Cutout (Negative)
    # 2. Shaft Plug (Positive)
    
    step = SIZE_XY / RESOLUTION
    res_x = int(SIZE_XY * 2.0 / step) # Double width
    res_y = int(SIZE_XY / step)
    res_z = int(SIZE_Z / step)
    
    center_x = SIZE_XY # Shifted center
    center_y = SIZE_XY / 2.0
    
    grid = np.zeros((res_x, res_y, res_z), dtype=bool)
    
    # Object 1 Center (Base Test)
    c1_x = SIZE_XY * 0.5
    c1_y = SIZE_XY * 0.5
    
    # Object 2 Center (Shaft Test)
    c2_x = SIZE_XY * 1.5
    c2_y = SIZE_XY * 0.5
    
    for z in range(res_z):
        pz = z * step
        dist_from_top = SIZE_Z - pz
        
        is_recess_depth = (dist_from_top < RECESS_DEPTH)
        
        for x in range(res_x):
            px_global = x * step
            
            for y in range(res_y):
                py_global = y * step
                
                # Object 1: Base Fragment
                dx1 = px_global - c1_x
                dy1 = py_global - c1_y
                r1 = math.sqrt(dx1**2 + dy1**2)
                
                if r1 < (SIZE_XY / 2.0 - 2.0): # Bounding box
                    if is_recess_depth:
                        if r1 > (RECESS_DIAMETER / 2.0):
                            grid[x,y,z] = True
                    else:
                        grid[x,y,z] = True
                        
                # Object 2: Shaft Fragment
                dx2 = px_global - c2_x
                dy2 = py_global - c2_y
                r2 = math.sqrt(dx2**2 + dy2**2)
                
                if r2 < (SIZE_XY / 2.0 - 2.0):
                    # Base plate
                    if pz < 5.0:
                        grid[x,y,z] = True
                    # Plug
                    elif pz < (5.0 + PLUG_HEIGHT):
                        if r2 < (PLUG_DIAMETER / 2.0):
                            grid[x,y,z] = True
                            
    v, f = mesh_grid(grid, step, center_x, center_y)
    write_binary_stl(OUTPUT_FILE, v, f)

if __name__ == "__main__":
    generate_tolerance_test()
