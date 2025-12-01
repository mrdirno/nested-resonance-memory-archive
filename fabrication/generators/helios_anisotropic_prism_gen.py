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

def generate_anisotropic_gyroid_prism(output_path, size_x=60.0, size_y=60.0, size_z=120.0, resolution=120, k_mod=0.01, robust_base_height=25.4, top_extend_height=25.4):
    """
    Generates a 3D mesh representing an Anisotropic Gyroid Prism with Z-axis frequency modulation.
    The wavelength of the Gyroid pattern stretches vertically with height (z).
    Includes a robust base region and top extension for printability.

    Equation: sin(x*scale_x)cos(y*scale_y) + sin(y*scale_y)cos(z*scale_z(z)) + sin(z*scale_z(z))cos(x*scale_x) > threshold
    """
    print(f"Generating Anisotropic Gyroid Prism: {output_path}")
    
    # Calculate effective Z-range after applying offsets
    effective_size_z = size_z + robust_base_height + top_extend_height
    
    # Grid Parameters - Using original size_x, size_y, and the new effective_size_z
    scale_xy = 2.0 * math.pi / (size_x / 3.0) # 3 periods across X/Y for initial base scale
    
    # Marching Cubes (Simplified: Voxel Surface Extraction)
    step_x = size_x / resolution
    step_y = size_y / resolution
    step_z = effective_size_z / resolution # Adjust step_z for the new effective height
    
    vertices = []
    faces = []
    
    # 3D Array of field values
    grid = np.zeros((resolution, resolution, resolution), dtype=bool)
    
    print("Calculating Anisotropic Field...")
    for x_idx in range(resolution):
        for y_idx in range(resolution):
            for z_idx in range(resolution):
                # Map grid to spatial coords (centered at 0,0,0)
                px = (x_idx * step_x) - (size_x/2)
                py = (y_idx * step_y) - (size_y/2)
                pz_raw = (z_idx * step_z) - (effective_size_z/2) # Raw Z, from -eff_size_z/2 to eff_size_z/2
                
                # Adjust pz_raw to be 0 at the effective start of the base
                pz = pz_raw + (effective_size_z/2) # pz now from 0 to effective_size_z
                
                # --- Z-Axis Frequency Modulation Logic ---
                # Based on: lambda(z) = lambda_base * (1 + k * z_norm)
                # So, scale_z(z) = scale_base / (1 + k * z_norm)
                
                # Original period for Z-axis in an isotropic Gyroid (e.g., 3 periods over size_z)
                # This needs to be the 'base_wavelength' from the README concept
                base_wavelength_z = size_z / 3.0 
                base_scale_z_val = 2.0 * math.pi / base_wavelength_z
                
                # Determine the 'z' value that influences the modulation.
                # It should represent the original logical Z-position within the pattern.
                
                # Map pz (0 to effective_size_z) to a z-range that starts at 0 for modulation
                # The modulation applies to the 'size_z' part of the overall effective_size_z.
                z_for_modulation = (pz - robust_base_height) # Start modulation above robust base
                
                # Ensure z_for_modulation is within bounds for the actual patterned section
                z_for_modulation = max(0.0, min(size_z, z_for_modulation))
                
                # Normalized z for modulation (0 to 1 over size_z)
                z_norm = z_for_modulation / size_z
                
                # Modulated scale_z
                # Wavelength increases with z, so frequency (scale) decreases.
                modulated_scale_z = base_scale_z_val / (1 + k_mod * z_norm)
                
                # --- Robust Base Logic ---
                # In the robust base region, we want coarser features (lower frequency, larger wavelength).
                current_scale_z = modulated_scale_z
                if pz < robust_base_height:
                    # Smoothly transition from a coarser scale at pz=0 to the modulated scale at robust_base_height
                    coarse_scale_factor = 0.5 # Example: At pz=0, scale is 0.5x of normal
                    
                    # Scale for the base: lower value = coarser pattern = more printable
                    # Linearly interpolate current_scale_z from a very low frequency to the modulated_scale_z
                    
                    # Calculate the desired scale_z at the top of the robust base
                    scale_z_at_transition = base_scale_z_val / (1 + k_mod * (robust_base_height / size_z))
                    
                    # Linearly interpolate between a very coarse scale at pz=0 and scale_z_at_transition
                    t_interp = pz / robust_base_height
                    current_scale_z = (1 - t_interp) * (base_scale_z_val * coarse_scale_factor) + t_interp * scale_z_at_transition
                    
                # OSD Gyroid Equation - use current_scale_z for z component
                val = math.sin(px * scale_xy) * math.cos(py * scale_xy) + \
                      math.sin(py * scale_xy) * math.cos(pz * current_scale_z) + \
                      math.sin(pz * current_scale_z) * math.cos(px * scale_xy)
                
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
                
                # Voxel center coords
                vx = (x_idx * step_x) - (size_x/2)
                vy = (y_idx * step_y) - (size_y/2)
                vz = (z_idx * step_z) - (effective_size_z/2)
                s2x = step_x / 2
                s2y = step_y / 2
                s2z = step_z / 2
                
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
        print("Usage: python helios_anisotropic_prism_gen.py <output.stl> [size_x] [size_y] [size_z] [resolution] [k_mod] [robust_base_height] [top_extend_height]")
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
            "top_extend_height": 25.4 # 1 inch in mm
        }
        
        # Parse optional arguments
        if len(sys.argv) > 2: params["size_x"] = float(sys.argv[2])
        if len(sys.argv) > 3: params["size_y"] = float(sys.argv[3])
        if len(sys.argv) > 4: params["size_z"] = float(sys.argv[4])
        if len(sys.argv) > 5: params["resolution"] = int(sys.argv[5])
        if len(sys.argv) > 6: params["k_mod"] = float(sys.argv[6])
        if len(sys.argv) > 7: params["robust_base_height"] = float(sys.argv[7])
        if len(sys.argv) > 8: params["top_extend_height"] = float(sys.argv[8])

        generate_anisotropic_gyroid_prism(output_file, **params)
