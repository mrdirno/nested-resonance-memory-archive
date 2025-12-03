import numpy as np
import math
import struct
import os

# ==========================================
# CONFIGURATION
# ==========================================
OUTPUT_FILE = "fabrication/practical_design/LAMP_DESIGN/shade_qa_v2.stl"
RESOLUTION = 150
SIZE_Z = 220.0
MAX_DIAMETER = 200.0
HOLE_DIAMETER = 42.0 # E26
HUB_DIAMETER = 60.0
SPOKE_WIDTH = 8.0
MOUNT_HEIGHT = 15.0
WALL_THICKNESS = 2.5 # Thin shell for the main body
RIB_DEPTH = 8.0
RIBS = 6
TWIST_RATE = 0.01 # Slower twist for the wider shade

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
def generate_shade_v2():
    print(f"Initializing QA Shade V2 (Blossom)...")
    
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
        
        # Profile: Bell Shape / Blossom
        # Top (z=220) is narrow (Hub)
        # Bottom (z=0) is wide
        
        # Reverse normalized Z (0 at top, 1 at bottom)
        z_inv = 1.0 - zn
        
        # Radius Profile
        # At top: HUB_DIAMETER/2 = 30mm
        # At bottom: MAX_DIAMETER/2 = 100mm
        # Curve: Exponential flare?
        # r = r_top + (r_bot - r_top) * z_inv^2
        r_top = HUB_DIAMETER / 2.0
        r_bot = MAX_DIAMETER / 2.0
        
        current_base_radius = r_top + (r_bot - r_top) * (z_inv**1.5)
        
        # Twist
        angle_offset = pz * TWIST_RATE
        
        dist_from_top = SIZE_Z - pz
        is_mount = (dist_from_top < MOUNT_HEIGHT)
        
        for x in range(res_x):
            px = (x * step) - center_x
            for y in range(res_y):
                py = (y * step) - center_y
                
                r = math.sqrt(px**2 + py**2)
                
                # 1. Global Bound
                # Max extent including ribs
                if r > (current_base_radius + RIB_DEPTH):
                    continue
                
                # 2. Mount Logic (Spider)
                if is_mount:
                    if r < (HOLE_DIAMETER / 2.0): continue
                    if r < (HUB_DIAMETER / 2.0):
                        grid[x,y,z] = True
                        continue
                    
                    # Spokes
                    # 3 Spokes
                    d_line1 = abs(py)
                    d_line2 = abs(math.sqrt(3)*px - py) / 2.0
                    d_line3 = abs(math.sqrt(3)*px + py) / 2.0
                    
                    if min(d_line1, d_line2, d_line3) < (SPOKE_WIDTH / 2.0):
                        if r < current_base_radius:
                            grid[x,y,z] = True
                        continue
                        
                    # Rim
                    if (current_base_radius - r) < WALL_THICKNESS:
                        grid[x,y,z] = True
                    
                    continue
                
                # 3. Main Body (Ribbed Shell)
                # We define a surface R(theta)
                theta = math.atan2(py, px)
                
                # Rib modulation
                # val = 1 at rib peak, -1 at valley
                val = math.cos((theta + angle_offset) * RIBS)
                
                # Effective Radius at this angle
                # r_surf = base + amp * val
                # But we want the ribs to protrude OUT from the base radius?
                # Or base radius is the average?
                # Let's say base radius is the inner shell surface.
                
                # Inner shell:
                # r_inner = current_base_radius
                
                # Outer shell (Ribbed):
                # r_outer = current_base_radius + WALL_THICKNESS + RIB_DEPTH * ((val + 1)/2)
                
                # Wait, that makes the wall thickness variable.
                # Better: Define a "Mid Surface" and thicken it?
                # Or simpler: Define Outer Radius function and Inner Radius function.
                
                # Outer:
                rib_factor = (val + 1.0) / 2.0 # 0 to 1
                r_outer = current_base_radius + (RIB_DEPTH * rib_factor)
                
                # Inner:
                # Constant wall thickness?
                r_inner = r_outer - WALL_THICKNESS
                
                # Hand access check
                if r < 45.0: # Keep out zone
                    continue
                
                if r < r_outer and r > r_inner:
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
    generate_shade_v2()
