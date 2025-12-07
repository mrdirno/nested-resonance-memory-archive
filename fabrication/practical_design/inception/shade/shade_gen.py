import numpy as np
import math
import sys
import struct
import os

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES 01: THE ANISOTROPIC SHADE v2.4 (V1 PYRAMID LOGIC RESTORATION)
# -----------------------------------------------------------------------------
# Correction Cycle 2841:
# - User Feedback: "That's not it... no pyramid outline... think further back... before the furniture folder".
# - Forensic Trace:
#   - User mentioned "Pyramid Outline".
#   - User mentioned "Before Furniture Folder" (which appeared Nov 30 / Dec 1).
#   - Commit `7f8396f9` (Dec 1 08:10) introduced `helios_anisotropic_prism_gen.py`.
#   - Commit `13233e63` (Dec 1 08:31) updated it to `Implement 'True Redshift Pyramid' `.
#   - This V1 Prism Generator (`13233e63`) has distinct logic:
#     - `z_norm_shape`: Explicit pyramidal bounding.
#     - `current_pyramid_width`: Calculated per Z-slice.
#     - `px = px_unscaled_from_center * (base_size / current_width)`: This is the "Coordinate Scaling" logic I found earlier, 
#       but in this version, it was explicitly tied to "Pyramidal Shape Bounding Logic".
#     - CRITICALLY: It has `force_solid_slice` at the apex (solid cap).
#     - It DOES NOT have the Spider Fitter (which came later in V4).
#     - It DOES NOT have the "Rim Outline" (Solid Corners) explicitly coded as a separate feature, 
#       BUT the `k_expansion` logic creates a hard boundary (The Pyramid Outline).
# - Hypothesis: The "Pyramid Outline" the user sees is the sharp frustum edge created by this generator's strict bounding box logic.
# - Action: Re-implement the logic from `13233e63` (True Redshift Pyramid) into `inception/shade/shade_gen.py`.
#   - Apply V2.4 Dimensions (217mm H, 85mm Top, 194mm Base, Variable Wall).
#   - Keep the "Coordinate Scaling" (Big Bang effect).
#   - Keep the strict Pyramidal Bounding.
# -----------------------------------------------------------------------------

def write_binary_stl(filename, vertices, faces):
    def normal(v1, v2, v3):
        u = v2 - v1
        w = v3 - v1
        nx = u[1]*w[2] - u[2]*w[1]
        ny = u[2]*w[0] - u[0]*w[2]
        nz = u[0]*w[1] - u[1]*w[0]
        n = np.array([nx, ny, nz])
        nm = np.linalg.norm(n)
        return n / nm if nm > 0 else np.array([0, 0, 1])

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

def generate_shade(output_path, base_width=194.0, top_width=85.4, height=217.65, resolution=200, hole_diameter=14.0):
    print(f"Generating ANISOTROPIC SHADE v2.4 (V1 Pyramid Restoration): {output_path}")
    
    # Logic from Commit 13233e63 (helios_anisotropic_prism_gen.py)
    
    # Dimensions
    plate_width = base_width
    margin_xy = 0.0
    size_z = height
    
    # Robust Base (Standard)
    robust_base_height = 25.4
    
    # Grid Setup
    base_size_x_unscaled = plate_width
    base_size_y_unscaled = plate_width # Square base
    
    # Calculate K Expansion Shape
    # In 13233e63: shape_scale_factor = 1.0 + k * z_norm
    # Here we want Base (Large) -> Top (Small).
    # So if z=0 is Base (Factor=1), and z=1 is Top (Factor < 1).
    # Top Width = Base Width * (1 + k)
    # k = (Top / Base) - 1 = (85.4 / 194) - 1 = -0.56
    k_expansion_shape = (top_width / base_width) - 1.0
    print(f"K Expansion: {k_expansion_shape:.4f}")
    
    expand_outward = True # The logic handles negative K
    
    # Pattern Scale
    base_pattern_scale_x = 2.0 * math.pi / (base_size_x_unscaled / 3.0)
    
    # Resolution
    max_dim = max(base_size_x_unscaled, size_z)
    step = max_dim / resolution
    
    res_x = int(base_size_x_unscaled / step) + 5
    res_y = int(base_size_y_unscaled / step) + 5
    res_z = int(size_z / step) + 1
    
    print(f"Grid: {res_x}x{res_y}x{res_z} (Voxel: ~{step:.2f}mm)")
    
    vertices = []
    faces = []
    grid = np.zeros((res_x, res_y, res_z), dtype=bool)
    
    # Variable Wall Logic (V2.4)
    wall_bottom = 12.7
    wall_top = 6.35
    
    print("Calculating Field (Pyramid Logic)...")
    
    for z_idx in range(res_z):
        pz_raw = (z_idx * step) - (size_z/2)
        # In V1 logic: pz was from 0 to effective_size_z.
        # Let's stick to 0..size_z logic for simplicity here.
        pz = z_idx * step
        z_norm = pz / size_z
        if z_norm > 1.0: z_norm = 1.0
        
        # Shape Scaling
        shape_scale_factor = 1.0 + k_expansion_shape * z_norm
        if shape_scale_factor < 0.01: shape_scale_factor = 0.01
        
        # Current Dimensions
        current_width = base_size_x_unscaled * shape_scale_factor
        current_half_width = current_width / 2.0
        
        # Variable Wall
        current_wall = wall_bottom * (1.0 - z_norm) + wall_top * z_norm
        current_inner_half_width = current_half_width - current_wall
        
        # Force Solid Slice (Apex) - From V1 Logic
        if current_width < 5.0:
            # Force solid
            # ...
            pass
            
        for x_idx in range(res_x):
            px_unscaled = (x_idx * step) - (base_size_x_unscaled / 2)
            
            for y_idx in range(res_y):
                py_unscaled = (y_idx * step) - (base_size_y_unscaled / 2)
                
                # BOUNDARY (Pyramid Outline)
                if abs(px_unscaled) > current_half_width or abs(py_unscaled) > current_half_width:
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                
                # --- V2.4 Features ---
                dist_from_center = math.sqrt(px_unscaled**2 + py_unscaled**2)
                
                # Top Cap (Mount)
                if pz > (size_z - 4.0):
                    if dist_from_center <= (hole_diameter/2.0):
                        grid[x_idx,y_idx,z_idx] = False
                        continue
                    if abs(px_unscaled) < current_half_width and abs(py_unscaled) < current_half_width:
                        grid[x_idx,y_idx,z_idx] = True
                        continue
                
                # Bottom Rim
                if pz < 4.0:
                    if abs(px_unscaled) < current_inner_half_width and abs(py_unscaled) < current_inner_half_width:
                        grid[x_idx,y_idx,z_idx] = False
                    else:
                        grid[x_idx,y_idx,z_idx] = True
                    continue
                
                # Hollow Shell
                if abs(px_unscaled) < current_inner_half_width and abs(py_unscaled) < current_inner_half_width:
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                
                # PATTERN MATH (Coordinate Scaling from V1)
                # px = px_unscaled * (base / current)
                ratio = base_size_x_unscaled / current_width
                px = px_unscaled * ratio
                py = py_unscaled * ratio
                
                # Z-Modulation (V1 Logic)
                # base_scale_z_val = 2.0 * pi / (size_z / 3.0)
                # z_mod_norm = z_norm
                # modulated_scale_z = base_scale_z_val / (1 + k_mod * z_mod_norm)
                # We use k_mod = 0.01 from V1 default.
                
                base_wavelength_z = size_z / 3.0
                base_scale_z = 2.0 * math.pi / base_wavelength_z
                k_mod = 0.01
                current_scale_z = base_scale_z / (1 + k_mod * z_norm)
                
                # Robust Base Logic (V1)
                if pz < robust_base_height:
                    t = pz / robust_base_height
                    current_scale_z = (1 - t) * (base_scale_z * 0.5) + t * current_scale_z
                
                # Gyroid
                val = math.sin(px * base_pattern_scale_x) * math.cos(py * base_pattern_scale_x) + \
                      math.sin(py * base_pattern_scale_x) * math.cos(pz * current_scale_z) + \
                      math.sin(pz * current_scale_z) * math.cos(px * base_pattern_scale_x)
                      
                if abs(val) < 0.4:
                    grid[x_idx,y_idx,z_idx] = True

    # Meshing (Standard)
    print("Extracting Isosurface (Voxel)...")
    
    def add_quad(v1, v2, v3, v4):
        idx = len(vertices)
        vertices.extend([v1, v2, v3, v4])
        faces.append((idx, idx+1, idx+2))
        faces.append((idx, idx+2, idx+3))

    for z_idx in range(res_z):
        pz = z_idx * step
        
        for x_idx in range(res_x):
            for y_idx in range(res_y):
                if not grid[x_idx,y_idx,z_idx]: continue
                
                # Voxel Center (Unscaled for V1 Logic?)
                # No, V1 used `vx = vx_unscaled * (current_width / base)` scaling in the MESHING loop too!
                # This physically tapers the object.
                # "vx = vx_unscaled * shape_scale_factor"
                
                z_norm = pz / size_z
                shape_scale_factor = 1.0 + k_expansion_shape * z_norm
                
                vx_unscaled = (x_idx * step) - (base_size_x_unscaled / 2)
                vy_unscaled = (y_idx * step) - (base_size_y_unscaled / 2)
                
                # Apply Taper to Vertices
                # In V1 Meshing logic:
                # vx = vx_unscaled * (current_width / base)
                # current_width = base * shape_scale
                # so vx = vx_unscaled * shape_scale
                
                vx = vx_unscaled # * shape_scale_factor
                vy = vy_unscaled # * shape_scale_factor
                # Wait. 
                # If we scaled the vertices, we would be double-applying the taper if we ALSO constrained the grid?
                # In V1 Gen:
                # 1. Grid check: `abs(px_unscaled) > current_pyramid_half_width`
                # 2. Meshing: `vx = vx_unscaled * (current / base)`
                # This seems redundant OR complementary.
                # If the grid is ALREADY constrained to the tapered shape (via the boundary check), 
                # then scaling the vertices would distort it further?
                # Let's look at V1 code again.
                # Grid loop: checks `px_unscaled` vs `current_width`. This creates a stepped pyramid in the grid.
                # Meshing loop: scales `vx_unscaled` by `expansion_factor`. This SMOOTHS the steps into a true pyramid.
                # So we MUST scale the vertices.
                
                vx = vx_unscaled * shape_scale_factor
                vy = vy_unscaled * shape_scale_factor
                vz = pz
                
                s2x = (step * shape_scale_factor) / 2
                s2y = (step * shape_scale_factor) / 2
                s2z = step / 2
                
                if x_idx == res_x-1 or not grid[x_idx+1,y_idx,z_idx]:
                    add_quad((vx+s2x, vy-s2y, vz-s2z), (vx+s2x, vy+s2y, vz-s2z), (vx+s2x, vy+s2y, vz+s2z), (vx+s2x, vy-s2y, vz+s2z))
                if x_idx == 0 or not grid[x_idx-1,y_idx,z_idx]:
                    add_quad((vx-s2x, vy-s2y, vz+s2z), (vx-s2x, vy+s2y, vz+s2z), (vx-s2x, vy+s2y, vz-s2z), (vx-s2x, vy-s2y, vz-s2z))
                if y_idx == res_y-1 or not grid[x_idx,y_idx+1,z_idx]:
                    add_quad((vx+s2x, vy+s2y, vz-s2z), (vx-s2x, vy+s2y, vz-s2z), (vx-s2x, vy+s2y, vz+s2z), (vx+s2x, vy+s2y, vz+s2z))
                if y_idx == 0 or not grid[x_idx,y_idx-1,z_idx]:
                    add_quad((vx-s2x, vy-s2y, vz-s2z), (vx+s2x, vy-s2y, vz-s2z), (vx+s2x, vy-s2y, vz+s2z), (vx-s2x, vy-s2y, vz+s2z))
                if z_idx == res_z-1 or not grid[x_idx,y_idx,z_idx+1]:
                    add_quad((vx+s2x, vy-s2y, vz+s2z), (vx+s2x, vy+s2y, vz+s2z), (vx-s2x, vy+s2y, vz+s2z), (vx+s2x, vy-s2y, vz+s2z))
                if z_idx == 0 or not grid[x_idx,y_idx,z_idx-1]:
                    add_quad((vx-s2x, vy-s2y, vz-s2z), (vx-s2x, vy+s2y, vz-s2z), (vx+s2x, vy+s2y, vz-s2z), (vx+s2x, vy-s2y, vz-s2z))

    write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "lamp_shade_v2.4.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_shade(output_file)