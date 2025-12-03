import numpy as np
import math
import struct
import os
import sys

# Import AGPH Library
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from agph_lib import AGPHCore

# ==========================================
# CONFIGURATION: V5 "Void Ascendant"
# ==========================================
# SHARED SPECS
HOLE_DIAMETER = 14.0
WIRE_CHANNEL_W = 12.0
WIRE_CHANNEL_H = 12.0
RECESS_DIAMETER = 40.5
RECESS_DEPTH = 3.0
PLUG_DIAMETER = 40.0
PLUG_HEIGHT = 3.0
CABLE_CLEARANCE = 15.0
HUB_DIAMETER = 60.0
SPOKE_WIDTH = 8.0
MOUNT_HEIGHT = 15.0
WALL_THICKNESS = 2.5

# RESOLUTION
RESOLUTION = 100 # Medium-High for speed/quality balance in batch

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
    print(f"  -> Writing {filename} ({num_triangles} triangles)...")
    
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
                
                # 6 Neighbors check
                if x==res_x-1 or not grid[x+1,y,z]: # +X
                    idx = len(vertices)
                    vertices.extend([(x_mm+s, y_mm-s, z_mm-s), (x_mm+s, y_mm+s, z_mm-s), (x_mm+s, y_mm+s, z_mm+s), (x_mm+s, y_mm-s, z_mm+s)])
                    faces.extend([(idx, idx+1, idx+2), (idx, idx+2, idx+3)])
                if x==0 or not grid[x-1,y,z]: # -X
                    idx = len(vertices)
                    vertices.extend([(x_mm-s, y_mm-s, z_mm+s), (x_mm-s, y_mm+s, z_mm+s), (x_mm-s, y_mm+s, z_mm-s), (x_mm-s, y_mm-s, z_mm-s)])
                    faces.extend([(idx, idx+1, idx+2), (idx, idx+2, idx+3)])
                if y==res_y-1 or not grid[x,y+1,z]: # +Y
                    idx = len(vertices)
                    vertices.extend([(x_mm+s, y_mm+s, z_mm-s), (x_mm-s, y_mm+s, z_mm-s), (x_mm-s, y_mm+s, z_mm+s), (x_mm+s, y_mm+s, z_mm+s)])
                    faces.extend([(idx, idx+1, idx+2), (idx, idx+2, idx+3)])
                if y==0 or not grid[x,y-1,z]: # -Y
                    idx = len(vertices)
                    vertices.extend([(x_mm-s, y_mm-s, z_mm-s), (x_mm+s, y_mm-s, z_mm-s), (x_mm+s, y_mm-s, z_mm+s), (x_mm-s, y_mm-s, z_mm+s)])
                    faces.extend([(idx, idx+1, idx+2), (idx, idx+2, idx+3)])
                if z==res_z-1 or not grid[x,y,z+1]: # +Z
                    idx = len(vertices)
                    vertices.extend([(x_mm+s, y_mm-s, z_mm+s), (x_mm+s, y_mm+s, z_mm+s), (x_mm-s, y_mm+s, z_mm+s), (x_mm-s, y_mm-s, z_mm+s)])
                    faces.extend([(idx, idx+1, idx+2), (idx, idx+2, idx+3)])
                if z==0 or not grid[x,y,z-1]: # -Z
                    idx = len(vertices)
                    vertices.extend([(x_mm-s, y_mm-s, z_mm-s), (x_mm-s, y_mm+s, z_mm-s), (x_mm+s, y_mm+s, z_mm-s), (x_mm+s, y_mm-s, z_mm-s)])
                    faces.extend([(idx, idx+1, idx+2), (idx, idx+2, idx+3)])
    
    return vertices, faces

# ==========================================
# GENERATORS
# ==========================================

def generate_v5_base():
    print("Generating V5 Base: Gravity Well (Updated)...")
    SIZE_Z = 45.0
    MAX_DIAMETER = 150.0
    
    # Gravity Well: Radial gradient density. Dense center, sparse edge.
    # Updated: Use AGPH with radial scaling of frequency?
    
    step = MAX_DIAMETER / RESOLUTION
    res_x = RESOLUTION
    res_y = RESOLUTION
    res_z = int(SIZE_Z / step)
    center = MAX_DIAMETER / 2.0
    
    grid = np.zeros((res_x, res_y, res_z), dtype=bool)
    
    agph = AGPHCore(scale_x=0.2, scale_y=0.2, scale_z=0.2, gyroid_thickness=0.6)
    
    for z in range(res_z):
        pz = z * step
        zn = pz / SIZE_Z
        
        # Dome profile
        r_limit = (MAX_DIAMETER/2.0) * (1.0 - 0.6*zn)
        
        # Engineering Features
        is_recess = (pz > SIZE_Z - RECESS_DEPTH)
        is_feet = (pz < 2.5)
        
        for x in range(res_x):
            px = (x * step) - center
            for y in range(res_y):
                py = (y * step) - center
                r = math.sqrt(px**2 + py**2)
                
                # 1. Recess
                if is_recess:
                    if r < (RECESS_DIAMETER/2.0): continue
                    if r < r_limit: 
                        grid[x,y,z] = True
                        continue
                    else: continue
                
                # 2. Hole
                if r < (HOLE_DIAMETER/2.0): continue
                
                # 3. Limit
                if r > r_limit: continue
                
                # 4. Wire Channel (Arch)
                if px > 0:
                    y_norm = py / (WIRE_CHANNEL_W/2.0)
                    if abs(y_norm) < 1.0:
                        if pz < (WIRE_CHANNEL_H * (1.0 - y_norm**2)): continue
                
                # 5. Feet
                if is_feet:
                    # V5 Feet: Maybe radial slots? No, stick to QA Standard.
                    foot_offset = 55.0
                    in_foot = False
                    if math.sqrt((px-foot_offset)**2 + py**2) < 12.0: in_foot = True
                    if math.sqrt((px+foot_offset)**2 + py**2) < 12.0: in_foot = True
                    if math.sqrt(px**2 + (py-foot_offset)**2) < 12.0: in_foot = True
                    if math.sqrt(px**2 + (py+foot_offset)**2) < 12.0: in_foot = True
                    if in_foot: continue
                
                # 6. Gravity Well Pattern
                # Density decreases with R
                # We modulate gyroid threshold or frequency
                # Let's modulate threshold: solid near center, sparse near edge
                
                dist_factor = r / (MAX_DIAMETER/2.0)
                # Center (0) -> Thick (0.9)
                # Edge (1) -> Thin (0.2)
                local_thresh = 0.9 - (0.7 * dist_factor)
                
                # Also warp space towards center (Gravity)
                # p' = p * (1 - 0.5*exp(-r)) ?
                
                val = agph.get_field_value(px, py, pz)
                if val > -local_thresh:
                    grid[x,y,z] = True
                
                # Solid Core
                if r < (HOLE_DIAMETER/2.0 + 8.0):
                    grid[x,y,z] = True

    v, f = mesh_grid(grid, step, center, center)
    write_binary_stl("fabrication/practical_design/LAMP_DESIGN/base_v5_gravity_well.stl", v, f)


def generate_v5_shaft():
    print("Generating V5 Shaft: Flow Lensing (Updated)...")
    SIZE_Z = 180.0
    MAX_W = 55.0 # Crown width
    
    step = MAX_W / RESOLUTION
    res_x = RESOLUTION
    res_y = RESOLUTION
    res_z = int(SIZE_Z / step)
    center = MAX_W / 2.0
    
    grid = np.zeros((res_x, res_y, res_z), dtype=bool)
    
    # Flow Lensing: Quadratic Twist acceleration
    # twist(z) = k * z^2
    
    for z in range(res_z):
        pz = z * step
        zn = pz / SIZE_Z
        
        # Profile: Hourglass + Crown Flare
        base_r = 20.0 * (1.0 - 0.3 * math.sin(zn * math.pi))
        
        # Flare
        if pz > (SIZE_Z - 20.0):
            f_norm = (pz - (SIZE_Z - 20.0)) / 20.0
            f = f_norm * f_norm * (3 - 2*f_norm)
            r_limit = base_r + (27.5 - base_r) * f # 27.5 = 55/2
        else:
            r_limit = base_r
            
        # Twist Acceleration
        twist_angle = 0.0001 * (pz**2) # Quadratic
        
        is_plug = (pz < PLUG_HEIGHT)
        is_top = (pz > SIZE_Z - 2.0)
        
        for x in range(res_x):
            px = (x * step) - center
            for y in range(res_y):
                py = (y * step) - center
                r = math.sqrt(px**2 + py**2)
                
                # 1. Hole
                if r < (CABLE_CLEARANCE/2.0): continue
                
                # 2. Plug
                if is_plug:
                    if r < (PLUG_DIAMETER/2.0): grid[x,y,z] = True
                    continue
                
                # 3. Top Cap
                if is_top:
                    if r < r_limit: grid[x,y,z] = True
                    continue
                
                # 4. Body
                if r > r_limit: continue
                
                # 5. Pattern: Flow Lensing
                # Distort coordinates based on angle
                theta = math.atan2(py, px)
                theta_new = theta + twist_angle
                
                # Gyroid in cylindrical coords?
                # Standard gyroid on rotated coords
                rx = r * math.cos(theta_new)
                ry = r * math.sin(theta_new)
                
                val = math.sin(rx*0.3) * math.cos(ry*0.3) + math.sin(ry*0.3) * math.cos(pz*0.3) + math.sin(pz*0.3) * math.cos(rx*0.3)
                
                if abs(val) < 0.5: # Thick lattice
                    grid[x,y,z] = True
                
                # Skin
                if r > (r_limit - 1.0): grid[x,y,z] = True
                if r < (CABLE_CLEARANCE/2.0 + 1.5): grid[x,y,z] = True

    v, f = mesh_grid(grid, step, center, center)
    write_binary_stl("fabrication/practical_design/LAMP_DESIGN/shaft_v5_flow_lensing.stl", v, f)


def generate_v5_shade():
    print("Generating V5 Shade: Interference (Updated)...")
    SIZE_Z = 220.0
    MAX_D = 200.0
    
    step = MAX_D / RESOLUTION
    res_x = RESOLUTION
    res_y = RESOLUTION
    res_z = int(SIZE_Z / step)
    center = MAX_D / 2.0
    
    grid = np.zeros((res_x, res_y, res_z), dtype=bool)
    
    for z in range(res_z):
        pz = z * step
        zn = pz / SIZE_Z
        
        # Profile: Bell
        z_inv = 1.0 - zn
        r_top = HUB_DIAMETER / 2.0
        r_bot = MAX_D / 2.0
        r_limit = r_top + (r_bot - r_top) * (z_inv**1.5)
        
        dist_top = SIZE_Z - pz
        is_mount = (dist_top < MOUNT_HEIGHT)
        # Grip Zone
        is_grip = (dist_top > MOUNT_HEIGHT) and (dist_top < MOUNT_HEIGHT + 20.0)
        
        for x in range(res_x):
            px = (x * step) - center
            for y in range(res_y):
                py = (y * step) - center
                r = math.sqrt(px**2 + py**2)
                
                # 1. Limit
                if r > r_limit: continue
                if r < (r_limit - WALL_THICKNESS) and not is_mount: continue
                
                # 2. Mount
                if is_mount:
                    if r < (HOLE_DIAMETER/2.0): continue
                    if r < (HUB_DIAMETER/2.0):
                        grid[x,y,z] = True
                        continue
                    # Spokes
                    d1 = abs(py)
                    d2 = abs(math.sqrt(3)*px - py)/2
                    d3 = abs(math.sqrt(3)*px + py)/2
                    if min(d1,d2,d3) < (SPOKE_WIDTH/2.0):
                        if r < r_limit: grid[x,y,z] = True
                        continue
                    if (r_limit - r) < WALL_THICKNESS:
                        grid[x,y,z] = True
                    continue
                
                # 3. Keepout
                if r < 45.0: continue
                
                # 4. Pattern: Interference
                # Dual frequency gyroid
                # G1 + G2 > t
                
                if is_grip:
                    # Knurled Grip (High Freq)
                    val = math.sin(px*0.8)*math.cos(py*0.8) + math.sin(py*0.8)*math.cos(pz*0.8) + math.sin(pz*0.8)*math.cos(px*0.8)
                    if abs(val) < 0.6: grid[x,y,z] = True
                else:
                    # Interference Pattern
                    f1 = 0.15
                    f2 = 0.25
                    
                    g1 = math.sin(px*f1)*math.cos(py*f1) + math.sin(py*f1)*math.cos(pz*f1) + math.sin(pz*f1)*math.cos(px*f1)
                    g2 = math.sin(px*f2)*math.cos(py*f2) + math.sin(py*f2)*math.cos(pz*f2) + math.sin(pz*f2)*math.cos(px*f2)
                    
                    # Moiré-like interference
                    if abs(g1 + g2) < 0.5:
                        grid[x,y,z] = True

    v, f = mesh_grid(grid, step, center, center)
    write_binary_stl("fabrication/practical_design/LAMP_DESIGN/shade_v5_interference.stl", v, f)

if __name__ == "__main__":
    generate_v5_base()
    generate_v5_shaft()
    generate_v5_shade()
