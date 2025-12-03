import numpy as np
import math
import struct
import os

# ==========================================
# CONFIGURATION
# ==========================================
OUTPUT_FILE = "fabrication/practical_design/LAMP_DESIGN/shade_qa_v1.stl"
RESOLUTION = 150  # Voxel resolution (higher = smoother but slower)
SIZE_Z = 220.0
TOP_DIAMETER = 70.0
EXPANSION_FACTOR = 2.8  # How much wider the bottom is
WALL_THICKNESS = 25.0   # Thickness of the sponge shell
HOLE_DIAMETER = 42.0    # Standard E26 Socket Ring clearance
HUB_DIAMETER = 60.0     # Solid hub around hole
SPOKE_WIDTH = 8.0       # Width of spider spokes
MOUNT_HEIGHT = 15.0     # Height of the solid top section

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
    
    # Ensure dir exists
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    with open(filename, 'wb') as f:
        f.write(b'\0' * 80)
        f.write(struct.pack('<I', num_triangles))
        for face in faces:
            v1 = np.array(vertices[face[0]])
            v2 = np.array(vertices[face[1]])
            v3 = np.array(vertices[face[2]])
            n = normal(v1, v2, v3)
            # Little-endian float32
            f.write(struct.pack('<3f3f3f3f', n[0], n[1], n[2], v1[0], v1[1], v1[2], v2[0], v2[1], v2[2], v3[0], v3[1], v3[2]))
            f.write(struct.pack('<H', 0))
    print("  -> Done.")

# ==========================================
# GENERATOR
# ==========================================
def generate_shade():
    print(f"Initializing QA Shade Generation...")
    print(f"  - Resolution: {RESOLUTION}")
    print(f"  - Height: {SIZE_Z}mm")
    print(f"  - Mount Hole: {HOLE_DIAMETER}mm")

    # Calculate bounds
    max_width = TOP_DIAMETER * EXPANSION_FACTOR
    step = max_width / RESOLUTION
    res_x = RESOLUTION
    res_y = RESOLUTION
    res_z = int(SIZE_Z / step)
    
    print(f"  - Grid: {res_x}x{res_y}x{res_z}")
    print(f"  - Voxel Size: {step:.3f}mm")

    # Initialize Boolean Grid
    grid = np.zeros((res_x, res_y, res_z), dtype=bool)
    
    # Pre-calculate constants
    center_x = max_width / 2.0
    center_y = max_width / 2.0
    
    # Pattern Constants (Domain Warped Gyroid)
    # Warping frequency
    warp_freq = 0.05
    warp_amp = 10.0
    # Gyroid frequency
    base_freq = 0.15
    
    print("  -> Computing Voxel Grid...")
    
    for z in range(res_z):
        pz = z * step
        # Normalized Z (0.0 bottom to 1.0 top)
        zn = pz / SIZE_Z
        
        # Width Profile: Linear expansion from top to bottom
        # Top (zn=1) width = TOP_DIAMETER
        # Bottom (zn=0) width = TOP_DIAMETER * EXPANSION_FACTOR
        # factor = 1.0 + (EXPANSION_FACTOR - 1.0) * (1.0 - zn)
        # Wait, we want shape to be defined. Let's stick to simple conical bounds.
        current_diameter = TOP_DIAMETER + (max_width - TOP_DIAMETER) * (1.0 - zn)
        current_radius = current_diameter / 2.0
        
        # Top Mount Logic
        dist_from_top = SIZE_Z - pz
        is_mount_zone = (dist_from_top < MOUNT_HEIGHT)
        is_transition_zone = (dist_from_top < (MOUNT_HEIGHT + 10.0))
        
        for x in range(res_x):
            px = (x * step) - center_x
            
            for y in range(res_y):
                py = (y * step) - center_y
                
                r_sq = px*px + py*py
                r = math.sqrt(r_sq)
                
                # 1. Global Bound Check
                if r > current_radius:
                    continue
                
                # 2. Top Mount / Spider Fitter (Hard Logic)
                if is_mount_zone:
                    # Hole Clearance
                    if r < (HOLE_DIAMETER / 2.0):
                        continue
                    
                    # Solid Hub
                    if r < (HUB_DIAMETER / 2.0):
                        grid[x,y,z] = True
                        continue
                    
                    # Spokes (Triskelion - 3 way symmetry)
                    # Angle calculation
                    # We define 3 lines at 0, 120, 240 deg
                    # Distance from point to line: |Ax + By + C| / sqrt(A^2+B^2)
                    # Line 1: y = 0 (Horizontal) -> dist = |y|
                    # Line 2: y = sqrt(3)x (60 deg slope? No 30? 120 deg is 2pi/3)
                    # Vector 1: (1, 0) -> Line eq: y = 0
                    # Vector 2: (-0.5, sqrt(3)/2) -> Normal is (sqrt(3)/2, 0.5). Point dot Normal = 0
                    # Let's use simple rotation check.
                    
                    # Just check distance to 3 rays
                    # Ray 1: (1, 0)
                    d1 = abs(py) if px > 0 else 9999 # Only +X ray? No, spokes are full lines or rays? usually rays from hub
                    # Let's do lines for robustness.
                    # Line 1: y=0
                    d_line1 = abs(py)
                    # Line 2: y = sqrt(3)x -> sqrt(3)x - y = 0. Dist = |sqrt(3)x - y|/2
                    d_line2 = abs(math.sqrt(3)*px - py) / 2.0
                    # Line 3: y = -sqrt(3)x -> sqrt(3)x + y = 0. Dist = |sqrt(3)x + y|/2
                    d_line3 = abs(math.sqrt(3)*px + py) / 2.0
                    
                    if min(d_line1, d_line2, d_line3) < (SPOKE_WIDTH / 2.0):
                        # Ensure we are within the outer shell
                        dist_to_shell = current_radius - r
                        if dist_to_shell < WALL_THICKNESS:
                             grid[x,y,z] = True # Merge with shell
                        elif r < (current_radius - 5.0): # Inside, be a spoke
                             grid[x,y,z] = True
                        continue
                    
                    # Rim (Top Ring)
                    if (current_radius - r) < WALL_THICKNESS:
                        grid[x,y,z] = True
                        continue
                        
                    # Otherwise Void (Air gaps between spokes)
                    continue

                # 3. Shell Mask (Hollow center)
                # We want a shell of WALL_THICKNESS at the perimeter
                dist_to_edge = current_radius - r
                
                # 4. Keep-Out Zone (Hand access)
                # Max internal radius = 90mm / 2 = 45mm
                if r < 45.0:
                    continue 
                
                # 5. Pattern Generation (The "Meat")
                if dist_to_edge < WALL_THICKNESS:
                    # Apply Domain Warp
                    # q = (x,y,z) + warp_amp * noise(p)
                    # Simple warp:
                    wx = px + warp_amp * math.sin(py * warp_freq)
                    wy = py + warp_amp * math.sin(pz * warp_freq)
                    wz = pz + warp_amp * math.sin(px * warp_freq)
                    
                    # Gyroid approximation
                    val = math.sin(wx * base_freq) * math.cos(wy * base_freq) + \
                          math.sin(wy * base_freq) * math.cos(wz * base_freq) + \
                          math.sin(wz * base_freq) * math.cos(wx * base_freq)
                          
                    # Solid threshold
                    if abs(val) < 0.3: # Thickness of gyroid wall
                        grid[x,y,z] = True
                    
                    # Force Solid Transition near top
                    if is_transition_zone:
                        # Blend factor 0 (bottom) to 1 (top of transition)
                        t_blend = 1.0 - ((dist_from_top - MOUNT_HEIGHT) / 10.0)
                        if t_blend > 0.5: # Make it solid
                             grid[x,y,z] = True

    # Meshing
    print("  -> Meshing...")
    vertices = []
    faces = []
    s = step / 2.0
    
    # Vectorized neighbors? No, stick to robust loop for now to avoid memory explosion on large grids
    # Just iterating is fine for 150^3 ~ 3M voxels.
    
    for z in range(res_z):
        z_mm = z * step
        for x in range(res_x):
            x_mm = (x * step) - center_x
            for y in range(res_y):
                if not grid[x,y,z]: continue
                
                y_mm = (y * step) - center_y
                
                # Add quads for exposed faces
                # +X
                if x==res_x-1 or not grid[x+1,y,z]:
                    idx = len(vertices)
                    vertices.extend([(x_mm+s, y_mm-s, z_mm-s), (x_mm+s, y_mm+s, z_mm-s), (x_mm+s, y_mm+s, z_mm+s), (x_mm+s, y_mm-s, z_mm+s)])
                    faces.extend([(idx, idx+1, idx+2), (idx, idx+2, idx+3)])
                # -X
                if x==0 or not grid[x-1,y,z]:
                    idx = len(vertices)
                    vertices.extend([(x_mm-s, y_mm-s, z_mm+s), (x_mm-s, y_mm+s, z_mm+s), (x_mm-s, y_mm+s, z_mm-s), (x_mm-s, y_mm-s, z_mm-s)])
                    faces.extend([(idx, idx+1, idx+2), (idx, idx+2, idx+3)])
                # +Y
                if y==res_y-1 or not grid[x,y+1,z]:
                    idx = len(vertices)
                    vertices.extend([(x_mm+s, y_mm+s, z_mm-s), (x_mm-s, y_mm+s, z_mm-s), (x_mm-s, y_mm+s, z_mm+s), (x_mm+s, y_mm+s, z_mm+s)])
                    faces.extend([(idx, idx+1, idx+2), (idx, idx+2, idx+3)])
                # -Y
                if y==0 or not grid[x,y-1,z]:
                    idx = len(vertices)
                    vertices.extend([(x_mm-s, y_mm-s, z_mm-s), (x_mm+s, y_mm-s, z_mm-s), (x_mm+s, y_mm-s, z_mm+s), (x_mm-s, y_mm-s, z_mm+s)])
                    faces.extend([(idx, idx+1, idx+2), (idx, idx+2, idx+3)])
                # +Z
                if z==res_z-1 or not grid[x,y,z+1]:
                    idx = len(vertices)
                    vertices.extend([(x_mm+s, y_mm-s, z_mm+s), (x_mm+s, y_mm+s, z_mm+s), (x_mm-s, y_mm+s, z_mm+s), (x_mm-s, y_mm-s, z_mm+s)])
                    faces.extend([(idx, idx+1, idx+2), (idx, idx+2, idx+3)])
                # -Z
                if z==0 or not grid[x,y,z-1]:
                    idx = len(vertices)
                    vertices.extend([(x_mm-s, y_mm-s, z_mm-s), (x_mm-s, y_mm+s, z_mm-s), (x_mm+s, y_mm+s, z_mm-s), (x_mm+s, y_mm-s, z_mm-s)])
                    faces.extend([(idx, idx+1, idx+2), (idx, idx+2, idx+3)])

    write_binary_stl(OUTPUT_FILE, vertices, faces)

if __name__ == "__main__":
    generate_shade()
