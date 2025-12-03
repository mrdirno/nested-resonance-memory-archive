import numpy as np
import math
import struct
import os
import sys

# Import AGPH Library
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from agph_lib import AGPHCore

# ==========================================
# CONFIGURATION
# ==========================================
OUTPUT_FILE = "fabrication/practical_design/LAMP_DESIGN/base_qa_v6.stl"
RESOLUTION = 150 
SIZE_Z = 45.0     
MAX_DIAMETER = 150.0
HOLE_DIAMETER = 14.0
WIRE_CHANNEL_W = 12.0 # Widened
WIRE_CHANNEL_H = 12.0 # Widened
FOOT_DEPTH = 2.5
FOOT_RADIUS = 12.0
FOOT_OFFSET_R = 55.0
RECESS_DIAMETER = 40.5
RECESS_DEPTH = 3.0
TWIST_RATE = 0.02

# Hardware Interface
NUT_RECESS_DIAMETER = 25.0 # Clearance for socket wrench
NUT_RECESS_DEPTH = 6.0     # Deep enough for nut + washer

# ==========================================
# UTILITIES
# ==========================================
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

# ==========================================
# GENERATOR
# ==========================================
def generate_base_v6():
    print(f"Initializing QA Base V6 (UX Optimized)...")
    
    agph = AGPHCore(
        scale_x=0.2, scale_y=0.2, scale_z=0.2,
        twist_rate=TWIST_RATE,
        anisotropy=(1.0, 1.0, 1.0), # Vertical stretch to reduce overhangs
        gyroid_thickness=0.8 
    )
    
    step = MAX_DIAMETER / RESOLUTION
    res_x = RESOLUTION
    res_y = RESOLUTION
    res_z = int(SIZE_Z / step)
    
    center_x = MAX_DIAMETER / 2.0
    center_y = MAX_DIAMETER / 2.0
    
    grid = np.zeros((res_x, res_y, res_z), dtype=bool)
    
    print(f"  -> Grid: {res_x}x{res_y}x{res_z}")
    
    for z in range(res_z):
        pz = z * step
        zn = pz / SIZE_Z
        
        taper_factor = 1.0 - (zn * 0.7)
        current_radius_limit = (MAX_DIAMETER / 2.0) * taper_factor
        macro_scale = current_radius_limit / (MAX_DIAMETER/2.0)
        
        dist_from_top = SIZE_Z - pz
        is_recess = (dist_from_top < RECESS_DEPTH)
        
        for x in range(res_x):
            px = (x * step) - center_x
            for y in range(res_y):
                py = (y * step) - center_y
                
                r = math.sqrt(px**2 + py**2)
                
                # 1. Recess
                if is_recess:
                    if r < (RECESS_DIAMETER / 2.0): continue
                    if r < current_radius_limit:
                        grid[x,y,z] = True
                        continue
                    else: continue
                
                # 2. Hole
                if r < (HOLE_DIAMETER / 2.0):
                    continue
                
                # 2b. Nut Recess (Bottom Counterbore)
                if pz < NUT_RECESS_DEPTH:
                    if r < (NUT_RECESS_DIAMETER / 2.0):
                        continue
                
                # 3. Global Limit
                if r > current_radius_limit:
                    continue
                
                # 4. Wire Channel (Widened Arch + Chamfer Logic)
                if px > 0:
                    y_norm = py / (WIRE_CHANNEL_W / 2.0)
                    if abs(y_norm) < 1.0:
                        arch_h = WIRE_CHANNEL_H * (1.0 - y_norm**2)
                        
                        # Exit Flare: Increase height/width near the edge
                        dist_to_edge = current_radius_limit - r
                        if dist_to_edge < 5.0: # Last 5mm
                             flare_factor = 1.0 + (1.0 - dist_to_edge/5.0) # 1.0 to 2.0
                             arch_h *= flare_factor
                        
                        if pz < arch_h:
                            continue
                        
                # 5. Feet
                if pz < FOOT_DEPTH:
                    in_foot = False
                    if math.sqrt((px-FOOT_OFFSET_R)**2 + py**2) < FOOT_RADIUS: in_foot = True
                    if math.sqrt((px+FOOT_OFFSET_R)**2 + py**2) < FOOT_RADIUS: in_foot = True
                    if math.sqrt(px**2 + (py-FOOT_OFFSET_R)**2) < FOOT_RADIUS: in_foot = True
                    if math.sqrt(px**2 + (py+FOOT_OFFSET_R)**2) < FOOT_RADIUS: in_foot = True
                    if in_foot: continue

                # 6. AGPH Solid Field
                val = agph.get_field_value(px, py, pz, macro_scale_factor=macro_scale)
                
                # Chamfer Bias (Bottom 5mm) to prevent overhangs
                if pz < 5.0:
                    bias = 0.8 * (1.0 - (pz / 5.0))
                    val += bias
                
                if val > -0.8:
                    grid[x,y,z] = True
                
                # Core solidity
                if r < ((HOLE_DIAMETER/2.0) + 8.0):
                    grid[x,y,z] = True

    # Meshing
    print("  -> Meshing...")
    vertices = []
    faces = []
    s = step / 2.0
    
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

    write_binary_stl(OUTPUT_FILE, vertices, faces)

if __name__ == "__main__":
    generate_base_v6()
