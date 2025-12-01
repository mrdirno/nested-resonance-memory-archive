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

def generate_anisotropic_gyroid_prism(output_path, plate_width=200.0, plate_depth=200.0, margin_xy=25.4, size_z=120.0, resolution=120, k_mod=0.01, robust_base_height=25.4, top_extend_height=0.0, top_dim_x=50.8, top_dim_y=50.8, k_expansion_shape=0.0, expand_outward=False, mimic_giza_pyramid=False):
    """
    Generates a 3D mesh representing an Anisotropic Gyroid Prism (Pyramid/Frustum)
    with Z-axis frequency modulation and cross-sectional expansion/contraction,
    capturing the "true redshift" effect. Can mimic the Great Pyramid of Giza's aspect ratio.

    The structure is bounded by a pyramid/frustum shape, with the Gyroid pattern
    infilling this volume. The internal Gyroid pattern also scales with the outer shape.
    Includes a robust base region and top extension for printability.
    A solid apex is generated when the pyramid dimensions become too small.

    Equation: sin(x*scale_x(z))cos(y*scale_y(z)) + sin(y*scale_y(z))cos(z*scale_z(z)) + sin(z*scale_z(z))cos(x*scale_x(z)) > threshold
    """
    print(f"Generating Anisotropic Gyroid Pyramid: {output_path}")

    GIZA_ASPECT_RATIO = 146.6 / 230.3 # Height / Base_Side (approx 0.6365)
    
    # Calculate initial base dimensions of the patterned section
    if mimic_giza_pyramid:
        # Given size_z (height of the patterned section), calculate base_size for Giza aspect ratio
        base_size_x_pattern = size_z / GIZA_ASPECT_RATIO
        base_size_y_pattern = size_z / GIZA_ASPECT_RATIO
        # For Giza, top dimensions are 0, and expand_outward is False
        top_dim_x = 0.0
        top_dim_y = 0.0
        expand_outward = False # Giza always shrinks
        
        # Adjust resolution to potentially be higher for Giza (larger base)
        resolution = max(resolution, 150) # Increase resolution for potentially larger base
    else:
        base_size_x_pattern = plate_width - 2 * margin_xy
        base_size_y_pattern = plate_depth - 2 * margin_xy

    # Ensure top dimensions are not larger than base dimensions when shrinking
    # This ensures consistency for frustum logic
    if top_dim_x > base_size_x_pattern and not expand_outward: top_dim_x = base_size_x_pattern
    if top_dim_y > base_size_y_pattern and not expand_outward: top_dim_y = base_size_y_pattern

    # Effective base dimensions for the grid and initial scale calculations
    effective_base_size_x = base_size_x_pattern
    effective_base_size_y = base_size_y_pattern
    
    # Calculate effective Z-range after applying offsets
    effective_size_z = size_z + robust_base_height + top_extend_height
    
    # Base scales for X/Y (initial frequency of the internal gyroid pattern)
    # These scales will be adjusted by the current_x_scale_factor and current_y_scale_factor
    base_pattern_scale_x = 2.0 * math.pi / (effective_base_size_x / 3.0) 
    base_pattern_scale_y = 2.0 * math.pi / (effective_base_size_y / 3.0)
    
    # Determine overall resolution based on largest dimension to maintain aspect ratio
    max_base_dim = max(effective_base_size_x, effective_base_size_y)
    # Ensure resolution respects height too.
    effective_resolution = max(resolution, int(effective_size_z / max_base_dim * resolution)) 

    step = max(effective_base_size_x, effective_base_size_y, effective_size_z) / effective_resolution
    
    # Calculate actual resolution counts for each dimension
    res_x = int(effective_base_size_x / step) +1
    res_y = int(effective_base_size_y / step) +1
    res_z = int(effective_size_z / step) +1

    # Ensure min resolution of 1
    if res_x < 1: res_x = 1
    if res_y < 1: res_y = 1
    if res_z < 1: res_z = 1

    vertices = []
    faces = []
    
    # 3D Array of field values
    grid = np.zeros((res_x, res_y, res_z), dtype=bool)
    

    
    print("Calculating Anisotropic Pyramid Field...")
    for z_idx in range(res_z): # Iterate Z first to calculate pyramid slice dimensions
        # Map grid index to spatial coords (centered at 0,0,0, relative to current pyramid slice)
        pz_raw = (z_idx * step) - (effective_size_z/2)
        pz = pz_raw + (effective_size_z/2) # pz now from 0 to effective_size_z
        
        # --- Pyramidal Shape Bounding Logic ---
        # Normalized z for shape expansion (0 at bottom, 1 at top of the patterned section)
        # This norm is for the pyramid's outer shape
        z_norm_shape = max(0.0, min(1.0, (pz - robust_base_height) / size_z))
        
        shape_scale_factor_x = 1.0 # Initialize
        shape_scale_factor_y = 1.0 # Initialize
        
        if mimic_giza_pyramid:
            # For a true pyramid, scale factor goes from 1 at base (z_norm_shape=0) to 0 at top (z_norm_shape=1)
            shape_scale_factor_x = (1.0 - z_norm_shape) 
            if shape_scale_factor_x < 0: shape_scale_factor_x = 0
            shape_scale_factor_y = shape_scale_factor_x # Symmetric for Giza
        elif k_expansion_shape != 0.0:
            if expand_outward: # Frustum expanding upwards
                # Linear interpolation from effective_base_size to top_dim, relative to effective_base_size
                shape_scale_factor_x = (effective_base_size_x * (1.0 - z_norm_shape) + top_dim_x * z_norm_shape) / effective_base_size_x
                shape_scale_factor_y = (effective_base_size_y * (1.0 - z_norm_shape) + top_dim_y * z_norm_shape) / effective_base_size_y
            else: # Frustum shrinking upwards (or constant if top_dim == base_size)
                # Linear interpolation from effective_base_size to top_dim, relative to effective_base_size
                shape_scale_factor_x = (effective_base_size_x * (1.0 - z_norm_shape) + top_dim_x * z_norm_shape) / effective_base_size_x
                shape_scale_factor_y = (effective_base_size_y * (1.0 - z_norm_shape) + top_dim_y * z_norm_shape) / effective_base_size_y
        else: # No expansion shape applied, default to constant size
            shape_scale_factor_x = 1.0
            shape_scale_factor_y = 1.0


        # Current X and Y dimensions of the pyramid slice at this Z level
        current_pyramid_width_x = effective_base_size_x * shape_scale_factor_x
        current_pyramid_width_y = effective_base_size_y * shape_scale_factor_y
        
        current_pyramid_half_width_x = current_pyramid_width_x / 2
        current_pyramid_half_width_y = current_pyramid_width_y / 2
        for x_idx in range(res_x):
            for y_idx in range(res_y):

                px_unscaled_from_center = (x_idx * step) - (effective_base_size_x / 2)
                py_unscaled_from_center = (y_idx * step) - (effective_base_size_y / 2)
                
                # Check if current unscaled voxel position is within the pyramid's X-Y bounds at this Z
                if abs(px_unscaled_from_center) > current_pyramid_half_width_x or \
                   abs(py_unscaled_from_center) > current_pyramid_half_width_y:
                    grid[x_idx,y_idx,z_idx] = False # Outside pyramid bounds
                    continue
                
                
                # --- Internal Gyroid Pattern Scaling ---
                # The internal gyroid pattern should also scale with the outer shape.
                # So the effective px, py used for the Gyroid equation need to be relative to the *current* pyramid slice size.
                # We normalize px_unscaled_from_center to a -1 to 1 range (relative to current pyramid half width),
                # then scale it back to a base_size_x_unscaled/2 range for the Gyroid equation
                
                # Rescale px, py relative to the effective base_size for the Gyroid equation
                # This makes the pattern appear to scale with the outer pyramid.
                px = px_unscaled_from_center * (effective_base_size_x / current_pyramid_width_x) if current_pyramid_width_x > 0 else 0 
                py = py_unscaled_from_center * (effective_base_size_y / current_pyramid_width_y)
                
                # --- Z-Axis Frequency Modulation Logic ---
                base_wavelength_z = size_z / 3.0 
                base_scale_z_val = 2.0 * math.pi / base_wavelength_z
                
                z_for_modulation = (pz - robust_base_height)
                z_for_modulation = max(0.0, min(size_z, z_for_modulation))
                z_norm_mod = z_for_modulation / size_z # Renamed to avoid confusion with z_norm_shape
                
                modulated_scale_z = base_scale_z_val / (1 + k_mod * z_norm_mod)
                
                # --- Robust Base Logic ---
                current_scale_z = modulated_scale_z
                if pz < robust_base_height:
                    coarse_scale_factor = 0.5 
                    scale_z_at_transition = base_scale_z_val / (1 + k_mod * (robust_base_height / size_z))
                    t_interp = pz / robust_base_height
                    current_scale_z = (1 - t_interp) * (base_scale_z_val * coarse_scale_factor) + t_interp * scale_z_at_transition
                    
                # OSD Gyroid Equation - use rescaled px, py and current_scale_z for z component
                val = math.sin(px * base_pattern_scale_x) * math.cos(py * base_pattern_scale_y) + \
                      math.sin(py * base_pattern_scale_y) * math.cos(pz * current_scale_z) + \
                      math.sin(pz * current_scale_z) * math.cos(px * base_pattern_scale_x)
                
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

    # Global mapping for vertices
    # The grid indices need to map to the final pyramidal shape's coordinates
    # For extraction, iterate through the high-resolution grid
    
    for z_idx in range(res_z):
        pz_raw_current = (z_idx * step) - (effective_size_z/2)
        pz_actual_current = pz_raw_current + (effective_size_z/2)

        z_norm_shape_current = max(0.0, min(1.0, (pz_actual_current - robust_base_height) / size_z))
        shape_scale_factor_current = 1.0
        if k_expansion_shape != 0.0:
            if expand_outward:
                shape_scale_factor_current = 1.0 + k_expansion_shape * z_norm_shape_current
            else:
                shape_scale_factor_current = 1.0 + k_expansion_shape * (1.0 - z_norm_shape_current)
        
        current_total_width_x = effective_base_size_x * shape_scale_factor_current
        current_total_width_y = effective_base_size_y * shape_scale_factor_current

        for x_idx in range(res_x):
            for y_idx in range(res_y):
                if not grid[x_idx,y_idx,z_idx]:
                    continue
                
                # Calculate voxel center coordinates for this particular grid cell.
                # These are now relative to the current slice's scaled dimensions.
                
                # Original unscaled position
                vx_unscaled = (x_idx * step) - (effective_base_size_x / 2)
                vy_unscaled = (y_idx * step) - (effective_base_size_y / 2)
                
                # Scale to fit current pyramid slice
                vx = vx_unscaled * (current_total_width_x / effective_base_size_x) if effective_base_size_x > 0 else 0
                vy = vy_unscaled * (current_total_width_y / effective_base_size_y) if effective_base_size_y > 0 else 0
                vz = pz_raw_current # Z-coordinate remains unscaled in terms of physical dimension
                
                # Scaled half-step sizes for drawing faces, adjusted for the current slice's scale
                s2x = (step / 2) * (current_total_width_x / effective_base_size_x) if effective_base_size_x > 0 else 0
                s2y = (step / 2) * (current_total_width_y / effective_base_size_y) if effective_base_size_y > 0 else 0
                s2z = step / 2 
                
                # Neighbors (Up, Down, Left, Right, Front, Back)
                # If neighbor is out of bounds or False, draw face
                
                # X+ Face
                if x_idx == res_x-1 or not grid[x_idx+1,y_idx,z_idx]:
                    add_quad((vx+s2x, vy-s2y, vz-s2z), (vx+s2x, vy+s2y, vz-s2z), (vx+s2x, vy+s2y, vz+s2z), (vx+s2x, vy-s2y, vz+s2z))
                # X- Face
                if x_idx == 0 or not grid[x_idx-1,y_idx,z_idx]:
                    add_quad((vx-s2x, vy-s2y, vz+s2z), (vx-s2x, vy+s2y, vz+s2z), (vx-s2x, vy+s2y, vz-s2z), (vx-s2x, vy-s2y, vz-s2z))
                    
                # Y+ Face
                if y_idx == res_y-1 or not grid[x_idx,y_idx+1,z_idx]:
                    add_quad((vx+s2x, vy+s2y, vz-s2z), (vx-s2x, vy+s2y, vz-s2z), (vx-s2x, vy+s2y, vz+s2z), (vx+s2x, vy+s2y, vz+s2z))
                # Y- Face
                if y_idx == 0 or not grid[x_idx,y_idx-1,z_idx]:
                    add_quad((vx-s2x, vy-s2y, vz-s2z), (vx+s2x, vy-s2y, vz-s2z), (vx+s2x, vy-s2y, vz+s2z), (vx-s2x, vy-s2y, vz+s2z))

                # Z+ Face
                if z_idx == res_z-1 or not grid[x_idx,y_idx,z_idx+1]:
                    add_quad((vx+s2x, vy-s2y, vz+s2z), (vx+s2x, vy+s2y, vz+s2z), (vx-s2x, vy+s2y, vz+s2z), (vx-s2x, vy-s2y, vz+s2z))
                # Z- Face
                if z_idx == 0 or not grid[x_idx,y_idx,z_idx-1]:
                    add_quad((vx-s2x, vy-s2y, vz-s2z), (vx-s2x, vy+s2y, vz-s2z), (vx+s2x, vy+s2y, vz-s2z), (vx+s2x, vy-s2y, vz-s2z))

    write_stl(output_path, vertices, faces)
    print(f"STL written to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python helios_anisotropic_prism_gen.py <output.stl> [plate_width] [plate_depth] [margin_xy] [size_z] [resolution] [k_mod] [robust_base_height] [top_extend_height] [top_dim_x] [top_dim_y] [k_expansion_shape] [expand_outward (bool)] [mimic_giza_pyramid (bool)]")
    else:
        output_file = sys.argv[1]
        
        # Default values
        params = {
            "plate_width": 200.0,
            "plate_depth": 200.0,
            "margin_xy": 25.4, # 1 inch in mm
            "size_z": 120.0,
            "resolution": 120,
            "k_mod": 0.01,
            "robust_base_height": 25.4, # 1 inch in mm
            "top_extend_height": 0.0,   # Set to 0.0 for pyramid tapering
            "top_dim_x": 50.8,          # 2 inches in mm
            "top_dim_y": 50.8,          # 2 inches in mm
            "k_expansion_shape": 0.0,   # Default to 0.0, will be overridden by Giza or set explicitly
            "expand_outward": False,    # Default to False for pyramid tapering
            "mimic_giza_pyramid": False # Do not mimic Giza pyramid by default
        }
        
        # Parse optional arguments
        arg_idx = 2
        if len(sys.argv) > arg_idx: params["plate_width"] = float(sys.argv[arg_idx]); arg_idx += 1
        if len(sys.argv) > arg_idx: params["plate_depth"] = float(sys.argv[arg_idx]); arg_idx += 1
        if len(sys.argv) > arg_idx: params["margin_xy"] = float(sys.argv[arg_idx]); arg_idx += 1
        if len(sys.argv) > arg_idx: params["size_z"] = float(sys.argv[arg_idx]); arg_idx += 1
        if len(sys.argv) > arg_idx: params["resolution"] = int(sys.argv[arg_idx]); arg_idx += 1
        if len(sys.argv) > arg_idx: params["k_mod"] = float(sys.argv[arg_idx]); arg_idx += 1
        if len(sys.argv) > arg_idx: params["robust_base_height"] = float(sys.argv[arg_idx]); arg_idx += 1
        if len(sys.argv) > arg_idx: params["top_extend_height"] = float(sys.argv[arg_idx]); arg_idx += 1
        if len(sys.argv) > arg_idx: params["top_dim_x"] = float(sys.argv[arg_idx]); arg_idx += 1
        if len(sys.argv) > arg_idx: params["top_dim_y"] = float(sys.argv[arg_idx]); arg_idx += 1
        if len(sys.argv) > arg_idx: params["k_expansion_shape"] = float(sys.argv[arg_idx]); arg_idx += 1
        if len(sys.argv) > arg_idx: params["expand_outward"] = sys.argv[arg_idx].lower() == 'true'; arg_idx += 1
        if len(sys.argv) > arg_idx: params["mimic_giza_pyramid"] = sys.argv[arg_idx].lower() == 'true'; arg_idx += 1

        generate_anisotropic_gyroid_prism(output_file, **params)
