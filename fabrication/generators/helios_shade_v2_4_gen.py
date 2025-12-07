import numpy as np
import math
import sys
import struct
import os

# --- UTILS ---

def write_binary_stl(filename, vertices, faces):
    print(f"Writing Binary STL ({len(faces)} triangles)...")
    def normal(v1, v2, v3):
        u = v2 - v1
        w = v3 - v1
        nx = u[1]*w[2] - u[2]*w[1]
        ny = u[2]*w[0] - u[0]*w[2]
        nz = u[0]*w[1] - u[1]*w[0]
        n = np.array([nx, ny, nz])
        nm = np.linalg.norm(n)
        return n / nm if nm > 0 else np.array([0, 0, 1])

    with open(filename, 'wb') as f:
        f.write(b'\0' * 80)
        f.write(struct.pack('<I', len(faces)))
        for face in faces:
            v1 = np.array(vertices[face[0]])
            v2 = np.array(vertices[face[1]])
            v3 = np.array(vertices[face[2]])
            n = normal(v1, v2, v3)
            data = struct.pack('<3f3f3f3f', n[0], n[1], n[2], v1[0], v1[1], v1[2], v2[0], v2[1], v2[2], v3[0], v3[1], v3[2])
            f.write(data)
            f.write(struct.pack('<H', 0))

# --- GENERATOR ---

def generate_shade_v2_4(output_path, base_width=194.0, top_width=85.4, height=217.65, resolution=200):
    print(f"Generating SHADE v2.4 (Event Horizon - Revised): {output_path}")
    print(f"Dims: {base_width} -> {top_width} x {height}mm")
    
    # Wall Thickness (Variable)
    wall_bottom = 12.7 # 1/2 inch
    wall_top = 6.35    # 1/4 inch
    
    # Grid Setup
    max_dim = max(base_width, height)
    # Adjust resolution to keep reasonable voxel size
    # v02 used 150 res for 224mm height (~1.5mm voxel)
    # We want higher quality? User said "check math".
    # I'll use ~1mm voxel. 220 res.
    step = max_dim / resolution
    
    res_xy = int(base_width / step) + 5
    res_z = int(height / step) + 1
    
    print(f"Grid: {res_xy}x{res_xy}x{res_z} (Voxel size: {step:.2f}mm)")
    
    grid = np.zeros((res_xy, res_xy, res_z), dtype=bool)
    
    # Swirl Parameters (From v02)
    scale = 2.0 * math.pi / 40.0
    
    print("Calculating Field...")
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        z_norm = z_mm / height
        if z_norm > 1.0: z_norm = 1.0
        
        # Frustum Logic
        current_width = base_width * (1.0 - z_norm) + top_width * z_norm
        current_wall = wall_bottom * (1.0 - z_norm) + wall_top * z_norm
        
        current_outer_half_width = current_width / 2.0
        current_inner_half_width = current_outer_half_width - current_wall
        
        # Scale factor (for texture mapping)
        scale_factor = base_width / current_width if current_width > 0 else 1.0
        
        for x_idx in range(res_xy):
            x_mm = (x_idx * step) - (base_width / 2.0)
            
            for y_idx in range(res_xy):
                y_mm = (y_idx * step) - (base_width / 2.0)
                
                dist_from_center = math.sqrt(x_mm**2 + y_mm**2)
                
                # 1. Global Bound
                if abs(x_mm) > current_outer_half_width or abs(y_mm) > current_outer_half_width:
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                
                # --- PRIORITY 1: ROBUST SOLID CAP ---
                if z_mm > (height - 4.0):
                    if dist_from_center <= 7.0: # 14mm Hole
                        grid[x_idx,y_idx,z_idx] = False
                    elif abs(x_mm) < current_outer_half_width and abs(y_mm) < current_outer_half_width:
                        grid[x_idx,y_idx,z_idx] = True
                    continue

                # --- PRIORITY 2: BOTTOM RIM ---
                if z_mm < 4.0:
                    if abs(x_mm) > current_inner_half_width or abs(y_mm) > current_inner_half_width:
                        grid[x_idx,y_idx,z_idx] = True
                        continue
                
                # --- PRIORITY 3: BODY ---
                # Inner Void
                if abs(x_mm) < current_inner_half_width and abs(y_mm) < current_inner_half_width:
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                
                # Inner Skin (Connectivity Anchor)
                if abs(x_mm) < (current_inner_half_width + 3.0) and abs(y_mm) < (current_inner_half_width + 3.0):
                    # Ribs
                    if abs(x_mm) < 5.0 or abs(y_mm) < 5.0:
                        grid[x_idx,y_idx,z_idx] = True
                        continue
                    if abs(x_mm) > (current_inner_half_width - 8.0) and abs(y_mm) > (current_inner_half_width - 8.0):
                        grid[x_idx,y_idx,z_idx] = True
                        continue
                    # Louvers
                    if (z_mm % 6.0) > 2.0:
                        grid[x_idx,y_idx,z_idx] = True
                        continue
                
                # EVENT HORIZON LOGIC (The "Correct Pattern")
                angle = math.atan2(y_mm, x_mm)
                r = dist_from_center
                
                twist = (z_mm/height * 2.0 * math.pi) + (r/(base_width/2.0) * 2.0 * math.pi)
                angle_warped = angle + twist
                
                tx = x_mm * math.cos(twist) - y_mm * math.sin(twist)
                ty = x_mm * math.sin(twist) + y_mm * math.cos(twist)
                
                sx = tx * scale_factor * scale
                sy = ty * scale_factor * scale
                sz = z_mm * scale
                
                val = math.sin(sx)*math.cos(sy) + math.sin(sy)*math.cos(sz) + math.sin(sz)*math.cos(sx)
                
                is_lattice = abs(val) < 0.7
                
                rib_val = math.sin(4.0 * angle_warped)
                is_rib = rib_val > 0.5
                
                if is_lattice or is_rib:
                    grid[x_idx,y_idx,z_idx] = True
                else:
                    grid[x_idx,y_idx,z_idx] = False

    print("Extracting Isosurface (Voxel)...")
    vertices = []
    faces = []
    
    def add_quad(v1, v2, v3, v4):
        idx = len(vertices)
        vertices.extend([v1, v2, v3, v4])
        faces.append((idx, idx+1, idx+2))
        faces.append((idx, idx+2, idx+3))

    # Using the same mesher logic as helios_anisotropic_prism_gen
    for z_idx in range(res_z):
        pz = z_idx * step
        # Re-calc dimensions for this Z (approx) to scale vertices if we were doing smooth meshing
        # But we are doing voxel meshing here for robustness matching the grid
        # Wait, the previous generator used Voxel Quads but "Projected" vertices onto the boundary?
        # No, helios_anisotropic used `vx_raw` and `curr_w_x / base`.
        # Here we have a complex grid. Standard Voxel Meshing (Minecraft style) is safest to preserve the "Pattern".
        # shade_v02_gen used `lamp_lib.extract_mesh_from_grid`.
        # I'll use standard voxel meshing (faces between True/False blocks).
        
        for x_idx in range(res_x_loop := res_xy):
            for y_idx in range(res_y_loop := res_xy):
                if not grid[x_idx,y_idx,z_idx]: continue
                
                # Center of voxel
                vx = (x_idx * step) - (base_width / 2.0)
                vy = (y_idx * step) - (base_width / 2.0)
                vz = z_idx * step
                
                s = step / 2.0
                
                # Check 6 neighbors
                # X+
                if x_idx == res_xy-1 or not grid[x_idx+1,y_idx,z_idx]:
                    add_quad((vx+s, vy-s, vz-s), (vx+s, vy+s, vz-s), (vx+s, vy+s, vz+s), (vx+s, vy-s, vz+s))
                # X-
                if x_idx == 0 or not grid[x_idx-1,y_idx,z_idx]:
                    add_quad((vx-s, vy-s, vz+s), (vx-s, vy+s, vz+s), (vx-s, vy+s, vz-s), (vx-s, vy-s, vz-s))
                # Y+
                if y_idx == res_xy-1 or not grid[x_idx,y_idx+1,z_idx]:
                    add_quad((vx+s, vy+s, vz-s), (vx-s, vy+s, vz-s), (vx-s, vy+s, vz+s), (vx+s, vy+s, vz+s))
                # Y-
                if y_idx == 0 or not grid[x_idx,y_idx-1,z_idx]:
                    add_quad((vx-s, vy-s, vz-s), (vx+s, vy-s, vz-s), (vx+s, vy-s, vz+s), (vx-s, vy-s, vz+s))
                # Z+
                if z_idx == res_z-1 or not grid[x_idx,y_idx,z_idx+1]:
                    add_quad((vx+s, vy-s, vz+s), (vx+s, vy+s, vz+s), (vx-s, vy+s, vz+s), (vx-s, vy-s, vz+s))
                # Z-
                if z_idx == 0 or not grid[x_idx,y_idx,z_idx-1]:
                    add_quad((vx-s, vy-s, vz-s), (vx-s, vy+s, vz-s), (vx+s, vy+s, vz-s), (vx+s, vy-s, vz-s))

    write_binary_stl(output_path, vertices, faces)
    print(f"STL written to {output_path}")

if __name__ == "__main__":
    out_file = sys.argv[1] if len(sys.argv) > 1 else "lamp_shade_v2.4.stl"
    generate_shade_v2_4(out_file)
