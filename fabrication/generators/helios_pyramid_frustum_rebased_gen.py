import numpy as np
import math
import sys
import struct
import os

def compute_normal(v1, v2, v3):
    """Compute face normal from three vertices."""
    u = np.array(v2) - np.array(v1)
    w = np.array(v3) - np.array(v1)
    nx = u[1]*w[2] - u[2]*w[1]
    ny = u[2]*w[0] - u[0]*w[2]
    nz = u[0]*w[1] - u[1]*w[0]
    n = np.array([nx, ny, nz])
    norm = np.linalg.norm(n)
    return n / norm if norm > 0 else np.array([0, 0, 1])

def write_ascii_stl(filename, vertices, faces):
    """
    Writes a mesh to an ASCII STL file. Compatible with all slicers.
    """
    num_triangles = len(faces)
    print(f"Writing ASCII STL ({num_triangles:,} triangles)...")

    solid_name = os.path.splitext(os.path.basename(filename))[0]

    with open(filename, 'w') as f:
        f.write(f'solid {solid_name}\n')

        for i, face in enumerate(faces):
            if i % 500000 == 0 and i > 0:
                print(f"  {i:,} / {num_triangles:,} ({100*i//num_triangles}%)")

            v1 = vertices[face[0]]
            v2 = vertices[face[1]]
            v3 = vertices[face[2]]
            n = compute_normal(v1, v2, v3)

            f.write(f'facet normal {n[0]:.6e} {n[1]:.6e} {n[2]:.6e}\n')
            f.write('  outer loop\n')
            f.write(f'    vertex {v1[0]:.6f} {v1[1]:.6f} {v1[2]:.6f}\n')
            f.write(f'    vertex {v2[0]:.6f} {v2[1]:.6f} {v2[2]:.6f}\n')
            f.write(f'    vertex {v3[0]:.6f} {v3[1]:.6f} {v3[2]:.6f}\n')
            f.write('  endloop\n')
            f.write('endfacet\n')

        f.write(f'endsolid {solid_name}\n')

def write_binary_stl(filename, vertices, faces):
    """
    Writes a mesh to a Binary STL file. Faster and smaller than ASCII.
    Note: Some slicers (e.g., OrcaSlicer) may have issues with binary STL.
    """
    num_triangles = len(faces)
    print(f"Writing Binary STL ({num_triangles:,} triangles)...")

    with open(filename, 'wb') as f:
        # 80-byte header
        header = f"Binary STL - {num_triangles} triangles".encode('ascii')
        f.write(header.ljust(80, b'\0'))
        f.write(struct.pack('<I', num_triangles))

        for i, face in enumerate(faces):
            if i % 500000 == 0 and i > 0:
                print(f"  {i:,} / {num_triangles:,} ({100*i//num_triangles}%)")

            v1 = np.array(vertices[face[0]])
            v2 = np.array(vertices[face[1]])
            v3 = np.array(vertices[face[2]])
            n = compute_normal(v1, v2, v3)

            f.write(struct.pack('<12f', n[0], n[1], n[2],
                                v1[0], v1[1], v1[2],
                                v2[0], v2[1], v2[2],
                                v3[0], v3[1], v3[2]))
            f.write(struct.pack('<H', 0))  # attribute byte count

def generate_anisotropic_gyroid_prism(output_path, size_x=60.0, size_y=60.0, size_z=120.0, resolution=120, k_mod=0.01, robust_base_height=25.4, top_extend_height=25.4, k_expansion=0.00, expand_outward=True, stl_format='ascii'):
    """
    V3 Rebased: Restored Legacy Logic with STL output & Frustum support via k_expansion.
    Generates a 3D mesh representing an Anisotropic Gyroid Prism with Z-axis frequency modulation
    and optional cross-sectional expansion/contraction.

    Args:
        stl_format: 'ascii' (default, compatible with all slicers) or 'binary' (smaller files)
    """
    print(f"Generating Anisotropic Gyroid Prism (V3 Rebased): {output_path}")
    print(f"STL Format: {stl_format.upper()}")
    
    # Calculate effective Z-range after applying offsets
    effective_size_z = size_z + robust_base_height + top_extend_height
    
    # Base scale for X/Y (initial frequency)
    base_scale_xy_val_x = 2.0 * math.pi / (size_x / 3.0) 
    base_scale_xy_val_y = 2.0 * math.pi / (size_y / 3.0)
    
    # Determine resolution
    max_dim = max(size_x, size_y)
    # Adjust resolution to account for height
    eff_res = max(resolution, int(effective_size_z / max_dim * resolution))
    
    step_x = size_x / resolution 
    step_y = size_y / resolution
    step_z = effective_size_z / eff_res
    
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
        
        if expansion_factor < 0.01: expansion_factor = 0.01

        px_base_pattern_scale_x = base_scale_xy_val_x
        py_base_pattern_scale_y = base_scale_xy_val_y
        
        for x_idx in range(res_x):
            for y_idx in range(res_y):
                px_base = (x_idx * step_x) - (size_x/2)
                py_base = (y_idx * step_y) - (size_y/2)
                
                # Apply expansion to spatial coordinates for the equation
                px = px_base / expansion_factor
                py = py_base / expansion_factor
                
                # Z Modulation
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
                    
                val = math.sin(px * px_base_pattern_scale_x) * math.cos(py * py_base_pattern_scale_y) + \
                      math.sin(py * py_base_pattern_scale_y) * math.cos(pz * current_scale_z) + \
                      math.sin(pz * current_scale_z) * math.cos(px * px_base_pattern_scale_x)
                
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
                
                px_base = (x_idx * step_x) - (size_x/2)
                py_base = (y_idx * step_y) - (size_y/2)
                
                vx = px_base * expansion_factor
                vy = py_base * expansion_factor
                vz = pz_raw 
                
                s2x = (step_x / 2) * expansion_factor
                s2y = (step_y / 2) * expansion_factor
                s2z = step_z / 2
                
                # Check neighbors and draw faces
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

    # Write STL in selected format
    if stl_format.lower() == 'binary':
        write_binary_stl(output_path, vertices, faces)
    else:
        write_ascii_stl(output_path, vertices, faces)

    file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"STL written to {output_path} ({file_size_mb:.1f} MB)")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python helios_pyramid_frustum_rebased_gen.py <output.stl> [options...]")
        print("")
        print("Positional args (in order):")
        print("  size_x, size_y, size_z, resolution, k_mod,")
        print("  robust_base_height, top_extend_height, k_expansion,")
        print("  expand_outward (true/false), stl_format (ascii/binary)")
        print("")
        print("Defaults: 60x60x120mm, res=120, k_mod=0.01, base=25.4mm, top=25.4mm")
        print("          k_expansion=0.0, expand_outward=true, stl_format=ascii")
    else:
        output_file = sys.argv[1]

        # Default values
        params = {
            "size_x": 60.0,
            "size_y": 60.0,
            "size_z": 120.0,
            "resolution": 120,
            "k_mod": 0.01,
            "robust_base_height": 25.4,  # 1 inch in mm
            "top_extend_height": 25.4,   # 1 inch in mm
            "k_expansion": 0.00,         # No expansion by default
            "expand_outward": True,      # Expand outward by default
            "stl_format": "ascii"        # ASCII format for slicer compatibility
        }

        # Parse optional arguments
        arg_idx = 2
        if len(sys.argv) > arg_idx: params["size_x"] = float(sys.argv[arg_idx]); arg_idx += 1
        if len(sys.argv) > arg_idx: params["size_y"] = float(sys.argv[arg_idx]); arg_idx += 1
        if len(sys.argv) > arg_idx: params["size_z"] = float(sys.argv[arg_idx]); arg_idx += 1
        if len(sys.argv) > arg_idx: params["resolution"] = int(sys.argv[arg_idx]); arg_idx += 1
        if len(sys.argv) > arg_idx: params["k_mod"] = float(sys.argv[arg_idx]); arg_idx += 1
        if len(sys.argv) > arg_idx: params["robust_base_height"] = float(sys.argv[arg_idx]); arg_idx += 1
        if len(sys.argv) > arg_idx: params["top_extend_height"] = float(sys.argv[arg_idx]); arg_idx += 1
        if len(sys.argv) > arg_idx: params["k_expansion"] = float(sys.argv[arg_idx]); arg_idx += 1
        if len(sys.argv) > arg_idx: params["expand_outward"] = sys.argv[arg_idx].lower() == 'true'; arg_idx += 1
        if len(sys.argv) > arg_idx: params["stl_format"] = sys.argv[arg_idx].lower(); arg_idx += 1

        generate_anisotropic_gyroid_prism(output_file, **params)