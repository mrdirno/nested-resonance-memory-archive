import numpy as np
import math
import struct
import os

# ==========================================
# CONFIGURATION
# ==========================================
OUTPUT_FILE = "fabrication/practical_design/LAMP_DESIGN/shaft_qa_v3.stl"
RESOLUTION = 120 
SIZE_Z = 180.0   
MAX_DIAMETER = 40.0 # Main body
CROWN_DIAMETER = 55.0 # Flared top
MIN_DIAMETER = 20.0 
HOLE_DIAMETER = 14.0 
RIBS = 6
TWIST_RATE = 0.05 
PLUG_DIAMETER = 40.0
PLUG_HEIGHT = 3.0

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
def generate_shaft_v3():
    print(f"Initializing QA Shaft V3 (Crown Flare)...")
    
    # Ensure grid covers the wider crown
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
        
        # Profile with Crown Flare
        # Base body: Hourglass
        # Flare: Top 20mm (z > 160)
        
        zn = pz / SIZE_Z
        
        # Standard Profile
        base_profile_factor = 1.0 - 0.4 * math.sin(zn * math.pi)
        base_radius = (MAX_DIAMETER / 2.0) * base_profile_factor
        
        # Flare Logic
        # If z > 160, linearly interpolate from base_radius to CROWN_RADIUS
        flare_start_z = SIZE_Z - 20.0
        if pz > flare_start_z:
            flare_norm = (pz - flare_start_z) / 20.0 # 0 to 1
            # Smoothstep? smoothstep(t) = t*t*(3-2t)
            f = flare_norm * flare_norm * (3.0 - 2.0 * flare_norm)
            
            # Interpolate
            # Start radius at flare_start
            r_start = (MAX_DIAMETER / 2.0) * (1.0 - 0.4 * math.sin((flare_start_z/SIZE_Z) * math.pi))
            r_end = CROWN_DIAMETER / 2.0
            
            current_radius = r_start + (r_end - r_start) * f
        else:
            current_radius = base_radius
        
        # Twist
        angle_offset = pz * TWIST_RATE
        
        is_plug = (pz < PLUG_HEIGHT)
        is_top_cap = (pz > SIZE_Z - 2.0)
        
        for x in range(res_x):
            px = (x * step) - center_x
            for y in range(res_y):
                py = (y * step) - center_y
                
                r = math.sqrt(px**2 + py**2)
                
                # 1. Hole
                if r < (HOLE_DIAMETER / 2.0):
                    continue
                
                # 2. Plug
                if is_plug:
                    if r < (PLUG_DIAMETER / 2.0):
                        grid[x,y,z] = True
                    continue 
                
                # 3. Top Cap (Flat)
                if is_top_cap:
                    if r < current_radius:
                        grid[x,y,z] = True
                    continue
                
                # 4. Body Boundary
                if r > current_radius:
                    continue
                
                # 5. Rib Pattern
                theta = math.atan2(py, px)
                val = math.cos((theta + angle_offset) * RIBS)
                
                # Constant rib depth relative to current radius?
                # Yes, keep the aesthetic consistent
                rib_depth = current_radius * 0.3
                r_limit = current_radius - rib_depth * (1.0 - val)/2.0 
                
                if r < r_limit:
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
    generate_shaft_v3()
