import numpy as np
import math
import struct
import os

# ==========================================
# CONFIGURATION
# ==========================================
OUTPUT_FILE = "fabrication/practical_design/LAMP_DESIGN/base_qa_v4.stl"
RESOLUTION = 150 
SIZE_Z = 45.0     
MAX_DIAMETER = 150.0
HOLE_DIAMETER = 14.0
WIRE_CHANNEL_W = 10.0
WIRE_CHANNEL_H = 10.0 # Peak height of tunnel
FOOT_DEPTH = 2.5
FOOT_RADIUS = 12.0
FOOT_OFFSET_R = 55.0
RECESS_DIAMETER = 40.5
RECESS_DEPTH = 3.0

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
def generate_base_v4():
    print(f"Initializing QA Base V4 (Arch Tunnel)...")
    
    step = MAX_DIAMETER / RESOLUTION
    res_x = RESOLUTION
    res_y = RESOLUTION
    res_z = int(SIZE_Z / step)
    
    center_x = MAX_DIAMETER / 2.0
    center_y = MAX_DIAMETER / 2.0
    
    grid = np.zeros((res_x, res_y, res_z), dtype=bool)
    
    print(f"  -> Grid: {res_x}x{res_y}x{res_z}")
    
    num_roots = 12
    twist_strength = 0.02
    
    for z in range(res_z):
        pz = z * step
        zn = pz / SIZE_Z
        
        taper_factor = 1.0 - (zn * 0.7)
        current_radius_limit = (MAX_DIAMETER / 2.0) * taper_factor
        
        dist_from_top = SIZE_Z - pz
        is_recess = (dist_from_top < RECESS_DEPTH)
        
        for x in range(res_x):
            px = (x * step) - center_x
            for y in range(res_y):
                py = (y * step) - center_y
                
                r = math.sqrt(px**2 + py**2)
                
                # 1. Recess Logic
                if is_recess:
                    if r < (RECESS_DIAMETER / 2.0):
                        continue 
                    if r < current_radius_limit:
                        grid[x,y,z] = True
                        continue
                    else:
                        continue
                
                # 2. Hole
                if r < (HOLE_DIAMETER / 2.0):
                    continue
                
                # 3. Global Limit
                if r > current_radius_limit:
                    continue
                
                # 4. Wire Channel (ARCH TUNNEL)
                # Exit: +X direction
                # Condition: px > 0
                # Arch profile: Semi-circle or parabola?
                # Width = WIRE_CHANNEL_W (10mm)
                # Height = WIRE_CHANNEL_H (10mm)
                # Equation: (y / (W/2))^2 + (z / H)^2 < 1 ?? No that's ellipse.
                # Let's use a simple circular arch if H = W/2, but here H=W.
                # Profile in YZ plane:
                # z < H * (1 - (y / (W/2))^2) ?? Parabola
                # At y=0, z < H. At y=W/2, z < 0.
                
                if px > 0:
                    # Check if inside tunnel profile
                    # Normalized Y from -1 to 1 relative to half-width
                    y_norm = py / (WIRE_CHANNEL_W / 2.0)
                    if abs(y_norm) < 1.0:
                        # Parabolic arch height at this y
                        arch_h = WIRE_CHANNEL_H * (1.0 - y_norm**2)
                        if pz < arch_h:
                            continue # Void
                        
                # 5. Feet Recesses
                if pz < FOOT_DEPTH:
                    in_foot = False
                    if math.sqrt((px-FOOT_OFFSET_R)**2 + py**2) < FOOT_RADIUS: in_foot = True
                    if math.sqrt((px+FOOT_OFFSET_R)**2 + py**2) < FOOT_RADIUS: in_foot = True
                    if math.sqrt(px**2 + (py-FOOT_OFFSET_R)**2) < FOOT_RADIUS: in_foot = True
                    if math.sqrt(px**2 + (py+FOOT_OFFSET_R)**2) < FOOT_RADIUS: in_foot = True
                    if in_foot: continue

                # 6. Pattern
                theta = math.atan2(py, px)
                theta_twisted = theta + (pz * twist_strength)
                r_norm = r / (MAX_DIAMETER / 2.0)
                val = math.cos(theta_twisted * num_roots)
                amplitude = 0.15 * r_norm
                depth_norm = (val + 1.0) / 2.0
                effective_limit = current_radius_limit * (1.0 - amplitude * (1.0 - depth_norm))
                
                core_limit = (HOLE_DIAMETER/2.0) + 10.0
                
                if r < core_limit:
                    grid[x,y,z] = True
                elif r < effective_limit:
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
    generate_base_v4()
