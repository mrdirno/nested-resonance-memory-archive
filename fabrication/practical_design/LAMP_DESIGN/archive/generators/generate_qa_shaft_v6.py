import numpy as np
import math
import struct
import os
import sys

# No AGPH needed for pure CSG solid
# But we keep the library for consistency if we want texture later.

# ==========================================
# CONFIGURATION
# ==========================================
OUTPUT_FILE = "fabrication/practical_design/LAMP_DESIGN/shaft_qa_v6_solid.stl"
RESOLUTION = 120 
SIZE_Z = 180.0   
MAX_DIAMETER = 40.0 
CROWN_DIAMETER = 55.0 
HOLE_DIAMETER = 14.0 
PLUG_DIAMETER = 40.0
PLUG_HEIGHT = 3.0
TWIST_RATE = 0.05
RIBS = 6

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
        z_mm = (z * step) + s # Fix Z-Offset (0.0mm bed adhesion)
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
                    vertices.extend([(x_mm-s, y_mm-s, z_mm-s), (x_mm+s, y_mm-s, z_mm-s), (x_mm+s, y_mm-s, z_mm+s), (x_mm-s, y_mm-s, z_mm+s)])
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

def generate_shaft_v6_solid():
    print(f"Initializing QA Shaft V6 (Pure Solid Ribs)...")
    
    max_width = max(MAX_DIAMETER, CROWN_DIAMETER)
    step = max_width / RESOLUTION
    res_x = RESOLUTION
    res_y = RESOLUTION
    res_z = int(SIZE_Z / step)
    
    center_x = max_width / 2.0
    center_y = max_width / 2.0
    
    grid = np.zeros((res_x, res_y, res_z), dtype=bool)
    
    print(f"  -> Grid: {res_x}x{res_y}x{res_z}")
    
    for z in range(res_z):
        pz = z * step
        zn = pz / SIZE_Z
        
        # Profile
        base_profile_factor = 1.0 - 0.4 * math.sin(zn * math.pi)
        base_radius = (MAX_DIAMETER / 2.0) * base_profile_factor
        
        # Flare
        flare_start_z = SIZE_Z - 20.0
        if pz > flare_start_z:
            flare_norm = (pz - flare_start_z) / 20.0
            f = flare_norm * flare_norm * (3.0 - 2.0 * flare_norm)
            r_start = (MAX_DIAMETER / 2.0) * (1.0 - 0.4 * math.sin((flare_start_z/SIZE_Z) * math.pi))
            r_end = CROWN_DIAMETER / 2.0
            current_radius = r_start + (r_end - r_start) * f
        else:
            current_radius = base_radius
            
        is_plug = (pz < PLUG_HEIGHT)
        is_plug_transition = (pz >= PLUG_HEIGHT) and (pz < PLUG_HEIGHT + 5.0)
        is_top_cap = (pz > SIZE_Z - 2.0)
        
        angle_offset = pz * TWIST_RATE
        
        # Mouse Ears Logic moved inside X/Y loop below

        for x in range(res_x):
            px = (x * step) - center_x
            for y in range(res_y):
                py = (y * step) - center_y
                
                r = math.sqrt(px**2 + py**2)
                
                # 1. Hole
                if r < (HOLE_DIAMETER / 2.0): continue

                # 2. Interfaces
                if is_plug:
                    if r < (PLUG_DIAMETER / 2.0): grid[x,y,z] = True
                    continue 
                if is_plug_transition:
                    if r < (PLUG_DIAMETER / 2.0): grid[x,y,z] = True
                    continue
                if is_top_cap:
                    if r < current_radius: grid[x,y,z] = True
                    continue
                
                # Mouse Ear Logic (Correct Placement)
                if pz < 0.3:
                     ear_r = 8.0
                     ear_dist = (MAX_DIAMETER / 2.0) + 5.0
                     in_ear = False
                     for i in range(3):
                         angle = (i * 120.0) * (math.pi / 180.0)
                         ex = ear_dist * math.cos(angle)
                         ey = ear_dist * math.sin(angle)
                         if math.sqrt((px-ex)**2 + (py-ey)**2) < ear_r:
                             in_ear = True
                     if in_ear:
                         grid[x,y,z] = True
                         # Continue? No, we want it merged with the main body.
                         # Just set true and let the rest run (union) or continue if r > current_radius?
                         # If in ear, we are done for this voxel.
                         continue

                if r > current_radius: continue
                
                # 3. Rib Pattern (CSG SOLID)
                theta = math.atan2(py, px)
                val = math.cos((theta + angle_offset) * RIBS)
                
                rib_depth = current_radius * 0.3
                r_limit = current_radius - rib_depth * (1.0 - val)/2.0
                
                if r < r_limit:
                    grid[x,y,z] = True

    v, f = mesh_grid(grid, step, center_x, center_y)
    write_binary_stl(OUTPUT_FILE, v, f)

if __name__ == "__main__":
    generate_shaft_v6_solid()
