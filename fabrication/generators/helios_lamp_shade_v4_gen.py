import numpy as np
import math
import sys
import struct

def write_binary_stl(filename, vertices, faces):
    """
    Writes a mesh to a Binary STL file.
    """
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
    print(f"Writing Binary STL ({num_triangles} triangles)...")

    with open(filename, 'wb') as f:
        f.write(b'\0' * 80)
        f.write(struct.pack('<I', num_triangles))
        for face in faces:
            v1 = np.array(vertices[face[0]])
            v2 = np.array(vertices[face[1]])
            v3 = np.array(vertices[face[2]])
            n = normal(v1, v2, v3)
            data = struct.pack('<3f3f3f3f', n[0], n[1], n[2], v1[0], v1[1], v1[2], v2[0], v2[1], v2[2], v3[0], v3[1], v3[2])
            f.write(data)
            f.write(struct.pack('<H', 0))

def generate_lamp_shade_v4(output_path, 
                           size_x=60.0,      # Top Size X (Reference)
                           size_y=60.0,      # Top Size Y (Reference)
                           size_z=220.0,     # Height
                           resolution=100,   # Grid resolution
                           k_mod=0.01,       # Frequency modulation
                           k_expansion=2.5,  # Expansion factor (Base/Top ratio - 1.0)
                           wall_thickness=25.4, # 1 inch wall thickness
                           hole_diam=14.0):  # 14mm clearance hole
    
    print(f"Generating Helios Lamp Shade V4 (QA Compliant): {output_path}")
    
    # Parameters
    hub_diam = 40.0 # 40mm Hub
    spoke_width = 8.0 
    top_mount_height = 15.0 # Height of the solid spider fitter section
    
    # Grid setup
    # We assume size_x/size_y is the TOP dimension (smallest).
    # The base will be larger by k_expansion.
    
    # Effective Z includes the mount
    effective_size_z = size_z 
    
    # Base scale for Gyroid
    base_scale_xy = 2.0 * math.pi / (size_x / 3.0) 
    
    # Resolution
    # We need enough resolution to capture the 14mm hole and 25mm wall.
    # 60mm top / 100 res = 0.6mm/voxel. Good enough.
    
    res_x = resolution
    res_y = resolution
    # Scale Z resolution
    step_ref = size_x / resolution
    res_z = int(size_z / step_ref)
    
    step_x = size_x / res_x
    step_y = size_y / res_y
    step_z = size_z / res_z
    
    print(f"Grid: {res_x}x{res_y}x{res_z} (Voxel: ~{step_x:.2f}mm)")
    
    vertices = []
    faces = []
    
    # 3D Array
    grid = np.zeros((res_x, res_y, res_z), dtype=bool)
    
    print("Calculating Field & QA Logic...")
    
    # Precompute Z logic
    for z_idx in range(res_z):
        # Physical Z (0 at bottom, size_z at top)
        # Wait, legacy code centered Z. Let's stick to 0..size_z for clarity.
        pz = z_idx * step_z
        
        # Normalized Height (0.0 bottom -> 1.0 top)
        z_norm = pz / size_z
        
        # Expansion Factor (Pyramid Taper)
        # We want Wide Base -> Narrow Top.
        # If size_x is Top Size (Small).
        # factor = 1.0 + k_expansion * (1.0 - z_norm)
        # At z=1 (Top), factor=1.0. At z=0 (Bottom), factor=1+k.
        expansion_factor = 1.0 + k_expansion * (1.0 - z_norm)
        
        # Physical width at this height
        current_width_x = size_x * expansion_factor
        current_width_y = size_y * expansion_factor
        
        # Gyroid Z-Scale Modulation
        base_wavelength_z = size_z / 4.0 
        base_scale_z_val = 2.0 * math.pi / base_wavelength_z
        modulated_scale_z = base_scale_z_val / (1 + k_mod * z_norm)
        
        # Spider Fitter Zone (Top of the lamp)
        is_top_mount = (pz > (size_z - top_mount_height))
        
        for x_idx in range(res_x):
            for y_idx in range(res_y):
                # Reference coordinates (Top Scale)
                # Centered at 0,0
                px_ref = (x_idx * step_x) - (size_x/2)
                py_ref = (y_idx * step_y) - (size_y/2)
                
                # Physical coordinates at this layer (Expanded)
                px_phys = px_ref * expansion_factor
                py_phys = py_ref * expansion_factor
                
                r_phys = math.sqrt(px_phys**2 + py_phys**2)
                
                # --- LOGIC TREE ---
                
                # 1. GLOBAL BOUNDARY (The Outer Prism/Pyramid)
                # If outside the current width, it's void.
                if abs(px_phys) > (current_width_x/2) or abs(py_phys) > (current_width_y/2):
                    continue # Empty
                    
                # 2. SPIDER FITTER OVERRIDE (Top Section)
                if is_top_mount:
                    # A. HOLE CHECK (Global Override)
                    if r_phys < (hole_diam / 2):
                        grid[x_idx, y_idx, z_idx] = False # HOLE
                        continue
                        
                    # B. HUB CHECK
                    if r_phys < (hub_diam / 2):
                        grid[x_idx, y_idx, z_idx] = True # SOLID HUB
                        continue
                        
                    # C. SPOKE CHECK
                    # Cross spokes along X and Y axes
                    if (abs(px_phys) < (spoke_width/2)) or (abs(py_phys) < (spoke_width/2)):
                        grid[x_idx, y_idx, z_idx] = True # SOLID SPOKE
                        continue
                        
                    # D. SHELL MERGE (Rim)
                    # If we are at the outer rim, keep it solid to merge with spokes
                    dist_to_edge_x = (current_width_x/2) - abs(px_phys)
                    dist_to_edge_y = (current_width_y/2) - abs(py_phys)
                    if min(dist_to_edge_x, dist_to_edge_y) < wall_thickness:
                         grid[x_idx, y_idx, z_idx] = True
                         continue
                         
                    # Else empty space between spokes
                    grid[x_idx, y_idx, z_idx] = False
                    continue

                # 3. STANDARD BODY (Gyroid + Shell)
                
                # A. SHELL MASK (Wall Thickness)
                # We only generate Gyroid/Solid within the "Crust".
                # Inner void is empty.
                
                # Calculate distance to nearest outer edge
                dist_to_edge_x = (current_width_x/2) - abs(px_phys)
                dist_to_edge_y = (current_width_y/2) - abs(py_phys)
                dist_to_edge = min(dist_to_edge_x, dist_to_edge_y)
                
                if dist_to_edge > wall_thickness:
                    # INSIDE THE VOID -> EMPTY
                    grid[x_idx, y_idx, z_idx] = False
                    continue
                
                # B. GYROID GENERATION (Within the shell)
                # We use the REFERENCE coordinates for the pattern (uv mapping style)
                # or Physical? If Physical, the pattern stretches.
                # Legacy used px_ref (warped coordinates) effectively.
                # Using px_ref keeps the number of cells constant (cells get bigger at bottom).
                # Using px_phys keeps cell size constant (more cells at bottom).
                # "Anisotropic Gyroid" usually implies stretching. Let's use px_ref to match style.
                
                val = math.sin(px_ref * base_scale_xy) * math.cos(py_ref * base_scale_xy) + \
                      math.sin(py_ref * base_scale_xy) * math.cos(pz * modulated_scale_z) + \
                      math.sin(pz * modulated_scale_z) * math.cos(px_ref * base_scale_xy)
                
                # Threshold for solidity
                if abs(val) > 0.4: # Inverted logic? |val| < threshold is wall.
                    # Typically |val| < t is the wall.
                    pass 
                
                # Let's check legacy: `if abs(val) < 0.4: grid = True`
                if abs(val) < 0.4:
                    grid[x_idx, y_idx, z_idx] = True
                    
    print("Meshing...")
    
    def add_quad(v1, v2, v3, v4):
        idx = len(vertices)
        vertices.extend([v1, v2, v3, v4])
        faces.append((idx, idx+1, idx+2))
        faces.append((idx, idx+2, idx+3))

    # Meshing Loop (Greedy/Naive)
    for z_idx in range(res_z):
        pz = z_idx * step_z
        z_norm = pz / size_z
        expansion_factor = 1.0 + k_expansion * (1.0 - z_norm)
        
        for x_idx in range(res_x):
            for y_idx in range(res_y):
                if not grid[x_idx,y_idx,z_idx]:
                    continue
                
                # Vertex Generation (Apply Expansion Here)
                px_ref = (x_idx * step_x) - (size_x/2)
                py_ref = (y_idx * step_y) - (size_y/2)
                
                vx = px_ref * expansion_factor
                vy = py_ref * expansion_factor
                vz = pz
                
                # Approximate voxel size at this location
                s2x = (step_x * expansion_factor) / 2
                s2y = (step_y * expansion_factor) / 2
                s2z = step_z / 2
                
                # Neighbor Checks (Topology based)
                if x_idx == res_x-1 or not grid[x_idx+1,y_idx,z_idx]:
                    add_quad((vx+s2x, vy-s2y, vz-s2z), (vx+s2x, vy+s2y, vz-s2z), (vx+s2x, vy+s2y, vz+s2z), (vx+s2x, vy-s2y, vz+s2z))
                if x_idx == 0 or not grid[x_idx-1,y_idx,z_idx]:
                    add_quad((vx-s2x, vy-s2y, vz+s2z), (vx-s2x, vy+s2y, vz+s2z), (vx-s2x, vy+s2y, vz-s2z), (vx-s2x, vy-s2y, vz-s2z))
                if y_idx == res_y-1 or not grid[x_idx,y_idx+1,z_idx]:
                    add_quad((vx+s2x, vy+s2y, vz-s2z), (vx-s2x, vy+s2y, vz-s2z), (vx-s2x, vy+s2y, vz+s2z), (vx+s2x, vy+s2y, vz+s2z))
                if y_idx == 0 or not grid[x_idx,y_idx-1,z_idx]:
                    add_quad((vx-s2x, vy-s2y, vz-s2z), (vx+s2x, vy-s2y, vz-s2z), (vx+s2x, vy-s2y, vz+s2z), (vx-s2x, vy-s2y, vz+s2z))
                if z_idx == res_z-1 or not grid[x_idx,y_idx,z_idx+1]:
                    add_quad((vx+s2x, vy-s2y, vz+s2z), (vx+s2x, vy+s2y, vz+s2z), (vx-s2x, vy+s2y, vz+s2z), (vx-s2x, vy-s2y, vz+s2z))
                if z_idx == 0 or not grid[x_idx,y_idx,z_idx-1]:
                    add_quad((vx-s2x, vy-s2y, vz-s2z), (vx-s2x, vy+s2y, vz-s2z), (vx+s2x, vy+s2y, vz-s2z), (vx+s2x, vy-s2y, vz-s2z))

    write_binary_stl(output_path, vertices, faces)
    print(f"STL written to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python helios_lamp_shade_v4_gen.py <output.stl>")
        print("Defaults used if args missing.")
        # Default test run
        generate_lamp_shade_v4("test_shade_v4.stl")
    else:
        output_file = sys.argv[1]
        generate_lamp_shade_v4(output_file)
