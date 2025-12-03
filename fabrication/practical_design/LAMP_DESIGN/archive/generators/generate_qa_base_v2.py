import numpy as np
import math
import struct
import os

# ==========================================
# CONFIGURATION
# ==========================================
OUTPUT_FILE = "fabrication/practical_design/LAMP_DESIGN/base_qa_v2.stl"
RESOLUTION = 150  # Higher resolution for texture
SIZE_Z = 45.0     # Slightly taller
MAX_DIAMETER = 150.0
HOLE_DIAMETER = 14.0
WIRE_CHANNEL_W = 10.0 # Slightly wider for ease
WIRE_CHANNEL_H = 10.0
FOOT_DEPTH = 2.5
FOOT_RADIUS = 12.0
FOOT_OFFSET_R = 55.0

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
def generate_base_v2():
    print(f"Initializing QA Base V2 (Radial Roots)...")
    
    step = MAX_DIAMETER / RESOLUTION
    res_x = RESOLUTION
    res_y = RESOLUTION
    res_z = int(SIZE_Z / step)
    
    center_x = MAX_DIAMETER / 2.0
    center_y = MAX_DIAMETER / 2.0
    
    grid = np.zeros((res_x, res_y, res_z), dtype=bool)
    
    print(f"  -> Grid: {res_x}x{res_y}x{res_z}")
    
    # Pattern Parameters
    # Interference of radial waves
    num_roots = 12
    twist_strength = 0.02
    
    for z in range(res_z):
        pz = z * step
        
        # Global Profile: Organic Mound
        # Uses a power curve for a "weighted" feel
        # r = R_max * (1 - (z/H)^2) ??
        zn = pz / SIZE_Z
        # Shape: Wide bottom, tapering to flat top (40mm diam for hub mating)
        # Top diam needs to match shaft base approx? Shaft base is ~40mm.
        # Let's taper to 45mm at top.
        
        taper_factor = 1.0 - (zn * 0.7) # 1.0 -> 0.3 (150 -> 45)
        current_radius_limit = (MAX_DIAMETER / 2.0) * taper_factor
        
        for x in range(res_x):
            px = (x * step) - center_x
            for y in range(res_y):
                py = (y * step) - center_y
                
                r = math.sqrt(px**2 + py**2)
                
                # 1. Hole
                if r < (HOLE_DIAMETER / 2.0):
                    continue
                
                # 2. Global Limit
                if r > current_radius_limit:
                    continue
                
                # 3. Wire Channel (+X)
                if pz < WIRE_CHANNEL_H:
                    if px > 0 and abs(py) < (WIRE_CHANNEL_W / 2.0):
                        continue
                        
                # 4. Feet Recesses (4 corners, aligned to axes)
                if pz < FOOT_DEPTH:
                    # +X, -X, +Y, -Y feet at FOOT_OFFSET_R
                    in_foot = False
                    if math.sqrt((px-FOOT_OFFSET_R)**2 + py**2) < FOOT_RADIUS: in_foot = True
                    if math.sqrt((px+FOOT_OFFSET_R)**2 + py**2) < FOOT_RADIUS: in_foot = True
                    if math.sqrt(px**2 + (py-FOOT_OFFSET_R)**2) < FOOT_RADIUS: in_foot = True
                    if math.sqrt(px**2 + (py+FOOT_OFFSET_R)**2) < FOOT_RADIUS: in_foot = True
                    if in_foot: continue

                # 5. "Radial Roots" Pattern
                # Create ridges that flow out from center
                theta = math.atan2(py, px)
                
                # Perturb theta with Z (twist)
                theta_twisted = theta + (pz * twist_strength)
                
                # Modulation function
                # cos(N*theta) creates ridges
                # We want "veins" standing out
                
                # Ridge height modulation
                # Near center (r small), smooth. Near edge (r large), ridged.
                
                # Radial distance factor
                r_norm = r / (MAX_DIAMETER / 2.0)
                
                # Height of the ridge at this point
                # val = 1 at ridge peak, -1 at valley
                val = math.cos(theta_twisted * num_roots)
                
                # We define the surface radius `r_surf` as:
                # r_surf = current_radius_limit * (1 - amp * (1-val))
                # basically carving IN from the max radius
                
                amplitude = 0.15 * r_norm # Deeper ridges at outside
                
                # Map val (-1..1) to (0..1) depth
                depth_norm = (val + 1.0) / 2.0 # 0..1 (1 is peak)
                
                # Invert: we want valleys carved out
                # If we want ridges to be the max radius:
                # effective_radius = current_radius_limit * (1.0 - amplitude * (1.0 - depth_norm))
                
                # Let's make it "Roots" -> Ridges protrude? 
                # Since we iterate over (x,y) inside Global Limit, we essentially check if r < r_surf
                
                effective_limit = current_radius_limit * (1.0 - amplitude * (1.0 - depth_norm))
                
                # Solid Core check (ensure minimum thickness around hole)
                # Maintain at least 5mm solid wall around hole
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
    generate_base_v2()
