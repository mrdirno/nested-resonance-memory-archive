import numpy as np
import math
import struct
import os

# ==========================================
# CONFIGURATION
# ==========================================
OUTPUT_FILE = "fabrication/practical_design/LAMP_DESIGN/shaft_qa_v1.stl"
RESOLUTION = 120 # Voxel resolution 
SIZE_Z = 180.0   # Shaft height
MAX_DIAMETER = 40.0
MIN_DIAMETER = 20.0 # Waist
HOLE_DIAMETER = 14.0 # 1/8 IP clearance
RIBS = 6
TWIST_RATE = 0.05 # Radians per mm

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
def generate_shaft():
    print(f"Initializing QA Shaft Generation...")
    
    step = MAX_DIAMETER / RESOLUTION
    res_x = RESOLUTION
    res_y = RESOLUTION
    res_z = int(SIZE_Z / step)
    
    center_x = MAX_DIAMETER / 2.0
    center_y = MAX_DIAMETER / 2.0
    
    grid = np.zeros((res_x, res_y, res_z), dtype=bool)
    
    print("  -> Computing Voxel Grid...")
    
    for z in range(res_z):
        pz = z * step
        
        # Profile: Hourglass (Thick bottom, thin middle, thick top)
        zn = pz / SIZE_Z
        profile_factor = 1.0 - 0.4 * math.sin(zn * math.pi) # 1.0 -> 0.6 -> 1.0
        current_radius = (MAX_DIAMETER / 2.0) * profile_factor
        
        # Twist angle
        angle_offset = pz * TWIST_RATE
        
        for x in range(res_x):
            px = (x * step) - center_x
            for y in range(res_y):
                py = (y * step) - center_y
                
                r = math.sqrt(px**2 + py**2)
                
                # 1. Hole
                if r < (HOLE_DIAMETER / 2.0):
                    continue
                
                # 2. Outer Boundary (Profile)
                if r > current_radius:
                    continue
                
                # 3. Rib Pattern
                # Angle
                theta = math.atan2(py, px)
                # Spiral: theta + angle_offset
                val = math.cos((theta + angle_offset) * RIBS)
                
                # Modulate radius based on ribs
                # r_surf = r_base + amp * cos(...)
                # Here we check if current r is inside the modulated boundary
                
                # We want deep ribs.
                # Max R at this height is current_radius.
                # Min R is current_radius * 0.6
                
                rib_depth = current_radius * 0.3
                r_limit = current_radius - rib_depth * (1.0 - val)/2.0 # Normalize cos to 0..1? No cos is -1..1
                # val is -1 to 1. (1-val)/2 is 1 to 0.
                # So at peak (val=1), r_limit = current_radius.
                # At trough (val=-1), r_limit = current_radius - rib_depth.
                
                if r < r_limit:
                    grid[x,y,z] = True
                    
                # 4. Solid End Caps (Top/Bottom 2mm)
                if pz < 2.0 or pz > (SIZE_Z - 2.0):
                    # Just a cylinder (respecting hole)
                    if r < current_radius:
                        grid[x,y,z] = True

    # Meshing
    print("  -> Meshing...")
    vertices = []
    faces = []
    s = step / 2.0
    
    for z in range(res_z):
        z_mm = z * step
        for x in range(res_x):
            x_mm = (x * step) - center_x
            for y in range(res_y):
                if not grid[x,y,z]: continue
                y_mm = (y * step) - center_y
                
                # Neighbors
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
    generate_shaft()
