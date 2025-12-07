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

def generate_variable_wall_prism(output_path, plate_width=200.0, plate_depth=200.0, margin_xy=25.4, size_z=120.0, resolution=120, k_mod=0.01, robust_base_height=25.4, top_extend_height=0.0, k_expansion_shape=0.0, threshold_bottom=0.4, threshold_top=0.4):
    """
    Generates a 3D mesh representing an Anisotropic Gyroid Prism with VARIABLE WALL THICKNESS.
    Interpolates isosurface threshold from bottom to top.
    """
    print(f"Generating Variable Wall Gyroid: {output_path}")
    print(f"Threshold Gradient: {threshold_bottom} -> {threshold_top}")

    base_size_x_unscaled = plate_width - 2 * margin_xy
    base_size_y_unscaled = plate_depth - 2 * margin_xy

    effective_size_z = size_z + robust_base_height + top_extend_height

    base_pattern_scale_x = 2.0 * math.pi / (base_size_x_unscaled / 3.0)
    base_pattern_scale_y = 2.0 * math.pi / (base_size_y_unscaled / 3.0)

    max_base_dim = max(base_size_x_unscaled, base_size_y_unscaled)
    effective_resolution = max(resolution, int(effective_size_z / max_base_dim * resolution))
    step = max(base_size_x_unscaled, base_size_y_unscaled, effective_size_z) / effective_resolution

    res_x = int(base_size_x_unscaled / step) + 1
    res_y = int(base_size_y_unscaled / step) + 1
    res_z = int(effective_size_z / step) + 1

    res_x, res_y, res_z = max(1, res_x), max(1, res_y), max(1, res_z)

    vertices = []
    faces = []

    grid = np.zeros((res_x, res_y, res_z), dtype=bool)

    print(f"Grid Dimensions: {res_x}x{res_y}x{res_z}")
    print("Calculating Field with Variable Threshold...")

    for z_idx in range(res_z):
        pz_raw = (z_idx * step) - (effective_size_z/2)
        pz = pz_raw + (effective_size_z/2)

        # Normalize Z for shape expansion (0 to 1 over size_z)
        z_norm_shape = max(0.0, min(1.0, (pz - robust_base_height) / size_z))
        
        # Calculate Threshold for this layer (Interpolate)
        # We want threshold to be based on physical Z height relative to the main body
        # Robust base is included in the "bottom" thickness usually
        # We interpolate from 0 (bottom of main body) to 1 (top of main body)
        
        # Determine interpolation factor t_thick
        # If pz < robust_base_height: use threshold_bottom
        # Else: interpolate
        
        if pz < robust_base_height:
             current_threshold = threshold_bottom
        elif pz > (robust_base_height + size_z):
             current_threshold = threshold_top
        else:
             t_thick = (pz - robust_base_height) / size_z
             current_threshold = (1 - t_thick) * threshold_bottom + t_thick * threshold_top

        shape_scale_factor = 1.0 + k_expansion_shape * z_norm_shape

        if shape_scale_factor < 0.01: shape_scale_factor = 0.01

        current_width_x = base_size_x_unscaled * shape_scale_factor
        current_width_y = base_size_y_unscaled * shape_scale_factor

        half_x = current_width_x / 2
        half_y = current_width_y / 2

        for x_idx in range(res_x):
            for y_idx in range(res_y):
                px_unscaled = (x_idx * step) - (base_size_x_unscaled / 2)
                py_unscaled = (y_idx * step) - (base_size_y_unscaled / 2)

                if abs(px_unscaled) > half_x or abs(py_unscaled) > half_y:
                    grid[x_idx,y_idx,z_idx] = False
                    continue

                px = px_unscaled * (base_size_x_unscaled / current_width_x)
                py = py_unscaled * (base_size_y_unscaled / current_width_y)

                base_scale_z = 2.0 * math.pi / (size_z / 3.0)
                z_mod_norm = max(0.0, min(1.0, (pz - robust_base_height) / size_z))
                modulated_scale_z = base_scale_z / (1 + k_mod * z_mod_norm)

                if pz < robust_base_height:
                    t = pz / robust_base_height
                    current_scale_z = (1 - t) * (base_scale_z * 0.5) + t * modulated_scale_z
                else:
                    current_scale_z = modulated_scale_z

                val = math.sin(px * base_pattern_scale_x) * math.cos(py * base_pattern_scale_y) + \
                      math.sin(py * base_pattern_scale_y) * math.cos(pz * current_scale_z) + \
                      math.sin(pz * current_scale_z) * math.cos(px * base_pattern_scale_x)

                if abs(val) < current_threshold:
                    grid[x_idx,y_idx,z_idx] = True

    print("Extracting Isosurface (Voxel approach)...")
    def add_quad(v1, v2, v3, v4):
        idx = len(vertices)
        vertices.extend([v1, v2, v3, v4])
        faces.append((idx, idx+1, idx+2))
        faces.append((idx, idx+2, idx+3))

    for z_idx in range(res_z):
        pz_raw = (z_idx * step) - (effective_size_z/2)
        pz = pz_raw + (effective_size_z/2)
        z_norm = max(0.0, min(1.0, (pz - robust_base_height) / size_z))
        scale = 1.0 + k_expansion_shape * z_norm
        if scale < 0.01: scale = 0.01

        curr_w_x = base_size_x_unscaled * scale
        curr_w_y = base_size_y_unscaled * scale

        for x_idx in range(res_x):
            for y_idx in range(res_y):
                if not grid[x_idx,y_idx,z_idx]: continue

                vx_raw = (x_idx * step) - (base_size_x_unscaled / 2)
                vy_raw = (y_idx * step) - (base_size_y_unscaled / 2)

                vx = vx_raw * (curr_w_x / base_size_x_unscaled)
                vy = vy_raw * (curr_w_y / base_size_y_unscaled)
                vz = pz_raw

                s2x = (step/2) * (curr_w_x / base_size_x_unscaled)
                s2y = (step/2) * (curr_w_y / base_size_y_unscaled)
                s2z = step/2

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
    print(f"Binary STL written to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python helios_variable_wall_gen.py <output.stl> [params...]")
    else:
        output_file = sys.argv[1]
        # Default fallback
        plate_width = 200.0
        plate_depth = 200.0
        margin_xy = 25.4
        size_z = 120.0
        resolution = 120
        k_mod = 0.01
        robust_base_height = 25.4
        top_extend_height = 0.0
        k_expansion_shape = 0.0
        threshold_bottom = 0.4
        threshold_top = 0.4

        if len(sys.argv) > 2: plate_width = float(sys.argv[2])
        if len(sys.argv) > 3: plate_depth = float(sys.argv[3])
        if len(sys.argv) > 4: margin_xy = float(sys.argv[4])
        if len(sys.argv) > 5: size_z = float(sys.argv[5])
        if len(sys.argv) > 6: resolution = int(sys.argv[6])
        if len(sys.argv) > 7: k_mod = float(sys.argv[7])
        if len(sys.argv) > 8: robust_base_height = float(sys.argv[8])
        if len(sys.argv) > 9: top_extend_height = float(sys.argv[9])
        if len(sys.argv) > 10: k_expansion_shape = float(sys.argv[10])
        if len(sys.argv) > 11: threshold_bottom = float(sys.argv[11])
        if len(sys.argv) > 12: threshold_top = float(sys.argv[12])

        generate_variable_wall_prism(
            output_file,
            plate_width, plate_depth, margin_xy, size_z,
            resolution, k_mod, robust_base_height, top_extend_height, k_expansion_shape,
            threshold_bottom, threshold_top
        )
