import numpy as np
import math
import struct
import os
import sys

# Import AGPH Library
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from agph_lib import AGPHCore

# ==========================================
# CONFIGURATION: V4 Shaft Retrofit (AGPH Deep)
# ==========================================
OUTPUT_FILE = "fabrication/practical_design/LAMP_DESIGN/shaft_v4_agph_retrofit.stl"
RESOLUTION = 120 
SIZE_Z = 180.0   
MAX_DIAMETER = 40.0 # Main body
CROWN_DIAMETER = 55.0 # Flared top
HOLE_DIAMETER = 14.0 # Core rod
CABLE_CLEARANCE = 15.0 
PLUG_DIAMETER = 40.0
PLUG_HEIGHT = 3.0
TWIST_RATE = 0.05 # Fast twist

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

def mesh_grid(grid, step, center_x, center_y):
    print("  -> Meshing...")
    vertices = []
    faces = []
    s = step / 2.0
    res_x, res_y, res_z = grid.shape
    
    for z in range(res_z):
        z_mm = z * step
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

# ==========================================
# GENERATOR
# ==========================================
def generate_shaft_v4_retro():
    print(f"Initializing V4 Shaft Retrofit (Volumetric AGPH)...")
    
    # AGPH Core: High Anisotropy
    # Scale X/Y: 0.5 (Medium freq)
    # Scale Z: 0.1 (Very Low freq -> Stretched vertically = Strands)
    # Twist: High
    agph = AGPHCore(
        scale_x=0.5, scale_y=0.5, scale_z=0.1, 
        twist_rate=TWIST_RATE,
        anisotropy=(1.0, 1.0, 1.0),
        gyroid_thickness=0.5 # Thick strands
    )
    
    max_width = max(MAX_DIAMETER, CROWN_DIAMETER)
    step = max_width / RESOLUTION
    res_x = RESOLUTION
    res_y = RESOLUTION
    res_z = int(SIZE_Z / step)
    
    center = max_width / 2.0
    
    grid = np.zeros((res_x, res_y, res_z), dtype=bool)
    
    for z in range(res_z):
        pz = z * step
        zn = pz / SIZE_Z
        
        # Profile: Hourglass + Crown Flare (V5 Standard)
        base_profile_factor = 1.0 - 0.4 * math.sin(zn * math.pi)
        base_radius = (MAX_DIAMETER / 2.0) * base_profile_factor
        
        flare_start_z = SIZE_Z - 20.0
        if pz > flare_start_z:
            flare_norm = (pz - flare_start_z) / 20.0
            f = flare_norm * flare_norm * (3.0 - 2.0 * flare_norm)
            r_start = (MAX_DIAMETER / 2.0) * (1.0 - 0.4 * math.sin((flare_start_z/SIZE_Z) * math.pi))
            r_end = CROWN_DIAMETER / 2.0
            current_radius = r_start + (r_end - r_start) * f
        else:
            current_radius = base_radius
            
        macro_scale = current_radius / (MAX_DIAMETER/2.0)
        
        is_plug = (pz < PLUG_HEIGHT)
        is_top_cap = (pz > SIZE_Z - 2.0)
        
        for x in range(res_x):
            px = (x * step) - center
            for y in range(res_y):
                py = (y * step) - center
                r = math.sqrt(px**2 + py**2)
                
                # 1. Hole (Cable Safe)
                if r < (CABLE_CLEARANCE / 2.0):
                    continue
                
                # 2. Solid Interfaces
                if is_plug:
                    if r < (PLUG_DIAMETER / 2.0):
                        grid[x,y,z] = True
                    continue 
                
                if is_top_cap:
                    if r < current_radius:
                        grid[x,y,z] = True
                    continue
                
                # 3. Body
                if r > current_radius:
                    continue
                
                # 4. AGPH Volumetric Field
                # This is the key fix. Instead of surface ribs, we sample the field volume.
                val = agph.get_field_value(px, py, pz, macro_scale_factor=macro_scale)
                
                # Solidify if field > threshold
                if agph.is_solid(val):
                    grid[x,y,z] = True
                
                # Skin (Thin outer shell to define boundary if lattice is porous)
                # Maybe 0.5mm skin?
                if r > (current_radius - 0.8):
                    grid[x,y,z] = True
                    
                # Inner wall skin
                if r < ((CABLE_CLEARANCE/2.0) + 1.0):
                    grid[x,y,z] = True

    v, f = mesh_grid(grid, step, center, center)
    write_binary_stl(OUTPUT_FILE, v, f)

if __name__ == "__main__":
    generate_shaft_v4_retro()
