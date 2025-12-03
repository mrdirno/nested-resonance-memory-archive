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
OUTPUT_FILE = "fabrication/practical_design/LAMP_DESIGN/shade_qa_v6.stl"
RESOLUTION = 100
SIZE_Z = 220.0
MAX_DIAMETER = 200.0
HOLE_DIAMETER = 42.0
HUB_DIAMETER = 60.0
SPOKE_WIDTH = 10.0
MOUNT_HEIGHT = 15.0
WALL_THICKNESS = 4.0
TWIST_RATE = 0.01

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
                
                # Check neighbors
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
                    vertices.extend([(x_mm-s, y_mm-s, z_mm-s), (x_mm+s, y_mm-s, z_mm-s), (x_mm+s, y_mm-s, z_mm+s), (x_mm-s, y_mm+s, z_mm-s)])
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

def generate_shade_v6_unified():
    print(f"Initializing QA Shade V6 (Unified Logic)...")
    
    agph = AGPHCore(
        scale_x=0.3, scale_y=0.3, scale_z=0.3,
        twist_rate=TWIST_RATE,
        anisotropy=(1.0, 1.0, 2.0),
        gyroid_thickness=0.7
    )

    step = MAX_DIAMETER / RESOLUTION
    res_x = RESOLUTION
    res_y = RESOLUTION
    res_z = int(SIZE_Z / step)
    center_x = MAX_DIAMETER / 2.0
    center_y = MAX_DIAMETER / 2.0

    grid = np.zeros((res_x, res_y, res_z), dtype=bool)

    for z in range(res_z):
        pz = z * step
        zn = pz / SIZE_Z
        
        z_inv = 1.0 - zn
        r_top = HUB_DIAMETER / 2.0
        r_bot = MAX_DIAMETER / 2.0
        
        # Bell Curve Profile
        current_radius = r_top + (r_bot - r_top) * (z_inv**1.8)
        macro_scale = current_radius / r_top

        dist_from_top = SIZE_Z - pz
        
        # Zones
        is_mount = (dist_from_top < MOUNT_HEIGHT)
        # Overlapping grip zone
        is_grip_zone = (dist_from_top > (MOUNT_HEIGHT - 5.0)) and (dist_from_top < (MOUNT_HEIGHT + 20.0))

        for x in range(res_x):
            px = (x * step) - center_x
            for y in range(res_y):
                py = (y * step) - center_y
                r = math.sqrt(px**2 + py**2)
                
                # Global cutoff
                if r > current_radius: continue
                
                is_solid = False
                
                # 1. Mount Logic (Hub + Spokes)
                if is_mount:
                    if r > (HOLE_DIAMETER / 2.0):
                        if r < (HUB_DIAMETER / 2.0):
                            is_solid = True
                        else:
                            # Triskelion Spokes
                            d_line1 = abs(py)
                            d_line2 = abs(math.sqrt(3)*px - py) / 2.0
                            d_line3 = abs(math.sqrt(3)*px + py) / 2.0
                            if min(d_line1, d_line2, d_line3) < (SPOKE_WIDTH / 2.0):
                                is_solid = True
                
                # 2. Grip Logic (Solid Internal Ring with Chamfer)
                if is_grip_zone:
                    if r > 45.0: # Hand clearance
                         # Calculate chamfer profile to avoid overhangs
                         # Grip Zone is dist_from_top in (10, 35)
                         d_in_zone = dist_from_top - 10.0 # 0 to 25
                         
                         grip_thickness = 8.0
                         if d_in_zone < 5.0: # Top taper
                             grip_thickness = 8.0 * (d_in_zone / 5.0)
                         elif d_in_zone > 20.0: # Bottom taper
                             grip_thickness = 8.0 * ((25.0 - d_in_zone) / 5.0)
                             
                         if r > (current_radius - grip_thickness):
                             is_solid = True
                             
                # 3. Shell Logic (Runs Everywhere)
                # Only generates where r is within the wall thickness
                if r > (current_radius - WALL_THICKNESS):
                    # Skin (Inner/Outer)
                    if (current_radius - r) < 1.5: 
                        is_solid = True
                    elif (r - (current_radius - WALL_THICKNESS)) < 1.5: 
                        is_solid = True
                    else:
                        # Internal Lattice
                        val = agph.get_field_value(px, py, pz, macro_scale_factor=macro_scale)
                        if agph.is_solid(val): 
                            is_solid = True

                if is_solid:
                    grid[x,y,z] = True

    v, f = mesh_grid(grid, step, center_x, center_y)
    write_binary_stl(OUTPUT_FILE, v, f)

if __name__ == "__main__":
    generate_shade_v6_unified()