import numpy as np
import math
import sys

def write_stl(filename, vertices, faces):
    """
    Writes a mesh to an ASCII STL file.
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

    with open(filename, 'w') as f:
        f.write(f"solid {filename}\n")
        for face in faces:
            v1 = np.array(vertices[face[0]])
            v2 = np.array(vertices[face[1]])
            v3 = np.array(vertices[face[2]])
            n = normal(v1, v2, v3)
            
            f.write(f"facet normal {n[0]:.4f} {n[1]:.4f} {n[2]:.4f}\n")
            f.write("  outer loop\n")
            f.write(f"    vertex {v1[0]:.4f} {v1[1]:.4f} {v1[2]:.4f}\n")
            f.write(f"    vertex {v2[0]:.4f} {v2[1]:.4f} {v2[2]:.4f}\n")
            f.write(f"    vertex {v3[0]:.4f} {v3[1]:.4f} {v3[2]:.4f}\n")
            f.write("  endloop\n")
            f.write("endfacet\n")
        f.write(f"endsolid {filename}\n")

def generate_anisotropic_gyroid_prism(output_path, size_x=60.0, size_y=60.0, size_z=120.0, resolution=120, k_mod=0.01, robust_base_height=25.4, top_extend_height=25.4, k_expansion=0.00, expand_outward=True):
    """
    Generates a 3D mesh representing an Anisotropic Gyroid Prism with Z-axis frequency modulation
    and optional cross-sectional expansion/contraction.
    The wavelength of the Gyroid pattern stretches vertically with height (z).
    Includes a robust base region and top extension for printability.

    Equation: sin(x*scale_x(z))cos(y*scale_y(z)) + sin(y*scale_y(z))cos(z*scale_z(z)) + sin(z*scale_z(z))cos(x*scale_x(z)) > threshold
    """
    print(f"Generating Anisotropic Gyroid Prism: {output_path}")
    
    # Calculate effective Z-range after applying offsets
    effective_size_z = size_z + robust_base_height + top_extend_height
    
    # Base scale for X/Y (initial frequency)
    base_scale_xy_val_x = 2.0 * math.pi / (size_x / 3.0) 
    base_scale_xy_val_y = 2.0 * math.pi / (size_y / 3.0)
    
    # Marching Cubes (Simplified: Voxel Surface Extraction)
    step_x = size_x / resolution
    step_y = size_y / resolution
    step_z = effective_size_z / resolution
    
    vertices = []
    faces = []
    
    # 3D Array of field values
    grid = np.zeros((resolution, resolution, resolution), dtype=bool)
    
    print("Calculating Anisotropic Field...")
    for x_idx in range(resolution):
        for y_idx in range(resolution):
            for z_idx in range(resolution):
                # Map grid to spatial coords (centered at 0,0,0)
                px_base = (x_idx * step_x) - (size_x/2)
                py_base = (y_idx * step_y) - (size_y/2)
                pz_raw = (z_idx * step_z) - (effective_size_z/2)
                
                # Adjust pz_raw to be 0 at the effective start of the base
                pz = pz_raw + (effective_size_z/2) # pz now from 0 to effective_size_z
                
                # --- Cross-sectional Expansion/Contraction Logic ---
                # Normalized z for expansion (0 at bottom, 1 at top of the patterned section)
                z_for_expansion_norm = max(0.0, min(1.0, (pz - robust_base_height) / size_z))
                
                expansion_factor = 1.0
                if k_expansion != 0.0:
                    if expand_outward: # Pyramid growing upwards
                        expansion_factor = 1.0 + k_expansion * z_for_expansion_norm
                    else: # Inverted pyramid (shrinking upwards)
                        expansion_factor = 1.0 + k_expansion * (1.0 - z_for_expansion_norm)
                
                # Apply expansion to spatial coordinates
                px = px_base / expansion_factor
                py = py_base / expansion_factor
                
                # --- Z-Axis Frequency Modulation Logic ---
                base_wavelength_z = size_z / 3.0 
                base_scale_z_val = 2.0 * math.pi / base_wavelength_z
                
                z_for_modulation = (pz - robust_base_height)
                z_for_modulation = max(0.0, min(size_z, z_for_modulation))
                z_norm = z_for_modulation / size_z
                
                modulated_scale_z = base_scale_z_val / (1 + k_mod * z_norm)
                
                # --- Robust Base Logic ---
                current_scale_z = modulated_scale_z
                if pz < robust_base_height:
                    coarse_scale_factor = 0.5 
                    scale_z_at_transition = base_scale_z_val / (1 + k_mod * (robust_base_height / size_z))
                    t_interp = pz / robust_base_height
                    current_scale_z = (1 - t_interp) * (base_scale_z_val * coarse_scale_factor) + t_interp * scale_z_at_transition
                    
                # OSD Gyroid Equation
                val = math.sin(px * base_scale_xy_val_x) * math.cos(py * base_scale_xy_val_y) + \
                      math.sin(py * base_scale_xy_val_y) * math.cos(pz * current_scale_z) + \
                      math.sin(pz * current_scale_z) * math.cos(px * base_scale_xy_val_x)
                
                # Threshold determines wall thickness
                if abs(val) < 0.4: 
                    grid[x_idx,y_idx,z_idx] = True

    # Extract Surface Mesh (Standard voxel face extraction)
    print("Extracting Isosurface...")
    
    def add_quad(v1, v2, v3, v4):
        idx = len(vertices)
        vertices.extend([v1, v2, v3, v4])
        faces.append((idx, idx+1, idx+2)) # Tri 1
        faces.append((idx, idx+2, idx+3)) # Tri 2

    for x_idx in range(resolution):
        for y_idx in range(resolution):
            for z_idx in range(resolution):
                if not grid[x_idx,y_idx,z_idx]:
                    continue
                
                # Voxel center coords - these need to be scaled by expansion_factor for the surface
                px_base = (x_idx * step_x) - (size_x/2)
                py_base = (y_idx * step_y) - (size_y/2)
                pz_raw = (z_idx * step_z) - (effective_size_z/2)
                pz_actual = pz_raw + (effective_size_z/2)
                
                z_for_expansion_norm = max(0.0, min(1.0, (pz_actual - robust_base_height) / size_z))
                expansion_factor = 1.0
                if k_expansion != 0.0:
                    if expand_outward:
                        expansion_factor = 1.0 + k_expansion * z_for_expansion_norm
                    else:
                        expansion_factor = 1.0 + k_expansion * (1.0 - z_for_expansion_norm)
                
                vx = px_base * expansion_factor
                vy = py_base * expansion_factor
                vz = pz_raw # Z-coordinate remains unscaled in terms of physical dimension
                
                # Scaled step sizes for drawing faces (approximated for now)
                s2x = (step_x / 2) * expansion_factor
                s2y = (step_y / 2) * expansion_factor
                s2z = step_z / 2 # Z step is constant
                
                # Neighbors (Up, Down, Left, Right, Front, Back)
                # If neighbor is out of bounds or False, draw face
                
                # X+ Face
                if x_idx == resolution-1 or not grid[x_idx+1,y_idx,z_idx]:
                    add_quad((vx+s2x, vy-s2y, vz-s2z), (vx+s2x, vy+s2y, vz-s2z), (vx+s2x, vy+s2y, vz+s2z), (vx+s2x, vy-s2y, vz+s2z))
                # X- Face
                if x_idx == 0 or not grid[x_idx-1,y_idx,z_idx]:
                    add_quad((vx-s2x, vy-s2y, vz+s2z), (vx-s2x, vy+s2y, vz+s2z), (vx-s2x, vy+s2y, vz-s2z), (vx-s2x, vy-s2y, vz-s2z))
                    
                # Y+ Face
                if y_idx == resolution-1 or not grid[x_idx,y_idx+1,z_idx]:
                    add_quad((vx+s2x, vy+s2y, vz-s2z), (vx-s2x, vy+s2y, vz-s2z), (vx-s2x, vy+s2y, vz+s2z), (vx+s2x, vy+s2y, vz+s2z))
                # Y- Face
                if y_idx == 0 or not grid[x_idx,y_idx-1,z_idx]:
                    add_quad((vx-s2x, vy-s2y, vz-s2z), (vx+s2x, vy-s2y, vz-s2z), (vx+s2x, vy-s2y, vz+s2z), (vx-s2x, vy-s2y, vz+s2z))

                # Z+ Face
                if z_idx == resolution-1 or not grid[x_idx,y_idx,z_idx+1]:
                    add_quad((vx+s2x, vy-s2y, vz+s2z), (vx+s2x, vy+s2y, vz+s2z), (vx-s2x, vy+s2y, vz+s2z), (vx-s2x, vy-s2y, vz+s2z))
                # Z- Face
                if z_idx == 0 or not grid[x_idx,y_idx,z_idx-1]:
                    add_quad((vx-s2x, vy-s2y, vz-s2z), (vx-s2x, vy+s2y, vz-s2z), (vx+s2x, vy+s2y, vz-s2z), (vx+s2x, vy-s2y, vz-s2z))

    write_stl(output_path, vertices, faces)
    print(f"STL written to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python helios_anisotropic_prism_gen.py <output.stl> [size_x] [size_y] [size_z] [resolution] [k_mod] [robust_base_height] [top_extend_height] [k_expansion] [expand_outward (bool)]")
    else:
        output_file = sys.argv[1]
        
        # Default values
        params = {
            "size_x": 60.0,
            "size_y": 60.0,
            "size_z": 120.0,
            "resolution": 120,
            "k_mod": 0.01,
            "robust_base_height": 25.4, # 1 inch in mm
            "top_extend_height": 25.4,  # 1 inch in mm
            "k_expansion": 0.00,        # No expansion by default
            "expand_outward": True      # Expand outward by default
        }
        
        # Parse optional arguments
        if len(sys.argv) > 2: params["size_x"] = float(sys.argv[2])
        if len(sys.argv) > 3: params["size_y"] = float(sys.argv[3])
        if len(sys.argv) > 4: params["size_z"] = float(sys.argv[3]) # Typo fixed from original: size_y -> size_z
        if len(sys.argv) > 5: params["resolution"] = int(sys.argv[5])
        if len(sys.argv) > 6: params["k_mod"] = float(sys.argv[6])
        if len(sys.argv) > 7: params["robust_base_height"] = float(sys.argv[7])
        if len(sys.argv) > 8: params["top_extend_height"] = float(sys.argv[8])
        if len(sys.argv) > 9: params["k_expansion"] = float(sys.argv[9])
        if len(sys.argv) > 10: params["expand_outward"] = sys.argv[10].lower() == 'true'

        generate_anisotropic_gyroid_prism(output_file, **params)
