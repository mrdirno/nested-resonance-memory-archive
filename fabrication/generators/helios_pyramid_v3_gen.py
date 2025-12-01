import numpy as np
import math
import sys
import struct

def write_binary_stl(filename, vertices, faces):
    """
    Writes a mesh to a Binary STL file. Faster and smaller than ASCII.
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

def generate_anisotropic_gyroid_prism(output_path, size_x=60.0, size_y=60.0, size_z=120.0, resolution=120, k_mod=0.01, robust_base_height=25.4, top_extend_height=25.4, k_expansion=0.00, expand_outward=True):
    """
    V3: Restored Legacy Logic with Binary STL.
    Generates a 3D mesh representing an Anisotropic Gyroid Prism with Z-axis frequency modulation
    and optional cross-sectional expansion/contraction.
    """
    print(f"Generating Anisotropic Gyroid Prism (V3): {output_path}")
    
    effective_size_z = size_z + robust_base_height + top_extend_height
    
    # Base scale for X/Y (initial frequency) 
    base_scale_xy_val_x = 2.0 * math.pi / (size_x / 3.0) 
    base_scale_xy_val_y = 2.0 * math.pi / (size_y / 3.0)
    
    # Determine resolution
    max_dim = max(size_x, size_y)
    # Adjust resolution to account for height
    eff_res = max(resolution, int(effective_size_z / max_dim * resolution))
    
    step_x = size_x / resolution # Logic from legacy script: uses base resolution for X/Y
    step_y = size_y / resolution
    step_z = effective_size_z / eff_res # Z step scales with height
    
    # Recalculate exact grid size
    res_x = resolution
    res_y = resolution
    res_z = eff_res
    
    print(f"Grid: {res_x}x{res_y}x{res_z}")
    
    vertices = []
    faces = []
    
    # 3D Array of field values
    grid = np.zeros((res_x, res_y, res_z), dtype=bool)
    
    print("Calculating Anisotropic Field...")
    for z_idx in range(res_z):
        pz_raw = (z_idx * step_z) - (effective_size_z/2)
        pz = pz_raw + (effective_size_z/2) 
        
        z_for_expansion_norm = max(0.0, min(1.0, (pz - robust_base_height) / size_z))
        
        expansion_factor = 1.0
        if k_expansion != 0.0:
            if expand_outward: 
                expansion_factor = 1.0 + k_expansion * z_for_expansion_norm
            else: 
                expansion_factor = 1.0 + k_expansion * (1.0 - z_for_expansion_norm)
        
        # Clamp expansion to avoid zero/negative
        if expansion_factor < 0.01: expansion_factor = 0.01

        # Spatial coords scaling
        # In this logic, px/py are scaled relative to the base size
        
        for x_idx in range(res_x):
            for y_idx in range(res_y):
                # Map grid to spatial coords (centered at 0,0,0)
                px_base = (x_idx * step_x) - (size_x/2)
                py_base = (y_idx * step_y) - (size_y/2)
                
                # Apply expansion to spatial coordinates for the equation
                # If expansion_factor < 1 (shrinking), px becomes LARGER relative to pattern, so pattern shrinks?
                # Wait. If object shrinks, pattern should shrink too (Redshift).
                # If object width is W_new = W_old * factor.
                # Coordinate X on object maps to X / factor on pattern space.
                # Yes.
                px = px_base / expansion_factor
                py = py_base / expansion_factor
                
                # --- Z-Axis Frequency Modulation Logic ---
                base_wavelength_z = size_z / 3.0 
                base_scale_z_val = 2.0 * math.pi / base_wavelength_z
                
                z_for_modulation = (pz - robust_base_height)
                z_for_modulation = max(0.0, min(size_z, z_for_modulation))
                z_norm = z_for_modulation / size_z
                
                modulated_scale_z = base_scale_z_val / (1 + k_mod * z_norm)
                
                current_scale_z = modulated_scale_z
                if pz < robust_base_height:
                    coarse_scale_factor = 0.5 
                    scale_z_at_transition = base_scale_z_val / (1 + k_mod * (robust_base_height / size_z))
                    t_interp = pz / robust_base_height
                    current_scale_z = (1 - t_interp) * (base_scale_z_val * coarse_scale_factor) + t_interp * scale_z_at_transition
                    
                val = math.sin(px * base_scale_xy_val_x) * math.cos(py * base_scale_xy_val_y) + \
                      math.sin(py * base_scale_xy_val_y) * math.cos(pz * current_scale_z) + \
                      math.sin(pz * current_scale_z) * math.cos(px * base_scale_xy_val_x)
                
                if abs(val) < 0.4: 
                    grid[x_idx,y_idx,z_idx] = True

    print("Extracting Isosurface...")
    
    def add_quad(v1, v2, v3, v4):
        idx = len(vertices)
        vertices.extend([v1, v2, v3, v4])
        faces.append((idx, idx+1, idx+2))
        faces.append((idx, idx+2, idx+3))

    for z_idx in range(res_z):
        pz_raw = (z_idx * step_z) - (effective_size_z/2)
        pz = pz_raw + (effective_size_z/2)
        
        z_for_expansion_norm = max(0.0, min(1.0, (pz - robust_base_height) / size_z))
        
        expansion_factor = 1.0
        if k_expansion != 0.0:
            if expand_outward:
                expansion_factor = 1.0 + k_expansion * z_for_expansion_norm
            else:
                expansion_factor = 1.0 + k_expansion * (1.0 - z_for_expansion_norm)
        
        if expansion_factor < 0.01: expansion_factor = 0.01

        for x_idx in range(res_x):
            for y_idx in range(res_y):
                if not grid[x_idx,y_idx,z_idx]:
                    continue
                
                # Vertex Calculation - Here we SCALE the vertex position by the expansion factor
                # to make the object physically grow/shrink
                px_base = (x_idx * step_x) - (size_x/2)
                py_base = (y_idx * step_y) - (size_y/2)
                
                vx = px_base * expansion_factor
                vy = py_base * expansion_factor
                vz = pz_raw 
                
                s2x = (step_x / 2) * expansion_factor
                s2y = (step_y / 2) * expansion_factor
                s2z = step_z / 2
                
                # Neighbors 
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
        print("Usage: python helios_pyramid_v3_gen.py <output.stl> ...")
    else:
        output_file = sys.argv[1]
        params = {
            "size_x": float(sys.argv[2]),
            "size_y": float(sys.argv[3]),
            "size_z": float(sys.argv[4]),
            "resolution": int(sys.argv[5]),
            "k_mod": float(sys.argv[6]),
            "robust_base_height": float(sys.argv[7]),
            "top_extend_height": float(sys.argv[8]),
            "k_expansion": float(sys.argv[9]),
            "expand_outward": sys.argv[10].lower() == 'true'
        }
        generate_anisotropic_gyroid_prism(output_file, **params)