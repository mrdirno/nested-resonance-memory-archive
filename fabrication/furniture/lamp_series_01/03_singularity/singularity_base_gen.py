import numpy as np
import math
import sys
import struct
import os

# Add project root to path for library import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES 01: THE SINGULARITY (BASE) - V4 QA
# -----------------------------------------------------------------------------
# Logic:
# 1. Shape: Gravity Well (Concave Top).
# 2. Features: Wire Channel, Feet Recesses (V4 Std).
# 3. Mass: Solid/Dense look.
# -----------------------------------------------------------------------------

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

def generate_base(output_path, diameter=140.0, height=35.0, resolution=100):
    print(f"Generating SINGULARITY BASE (V4 QA): {output_path}")
    
    radius = diameter / 2.0
    
    # Wire Channel (V4 Std)
    channel_width = 8.0
    channel_height = 8.0
    
    # Feet (V4 Std)
    feet_inset = 15.0
    feet_radius = 10.0
    feet_depth = 3.0
    
    # Central Hole
    center_hole_radius = 7.0 # 14mm dia (V4 Std)
    recess_radius = 20.0
    recess_depth = 5.0
    
    step = diameter / resolution
    res_xy = int(diameter / step) + 2
    res_z = int(height / step) + 1
    
    print(f"Grid: {res_xy}x{res_xy}x{res_z}")
    
    vertices = []
    faces = []
    grid = np.zeros((res_xy, res_xy, res_z), dtype=bool)
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        
        for x_idx in range(res_xy):
            x_mm = (x_idx * step) - radius
            for y_idx in range(res_xy):
                y_mm = (y_idx * step) - radius
                
                dist = math.sqrt(x_mm**2 + y_mm**2)
                
                # V4 Features (Wire Channel, Feet, Hole)
                feature_check = lamp_lib.apply_base_v4_features(
                    x_mm, y_mm, z_mm, dist,
                    height=height,
                    hole_radius=center_hole_radius,
                    channel_height=channel_height,
                    channel_width=channel_width,
                    foot_depth=feet_depth,
                    foot_radius=feet_radius,
                    foot_offset=feet_inset,
                    radius=radius
                )
                
                if feature_check is not None:
                    grid[x_idx,y_idx,z_idx] = feature_check
                    continue
                
                # Calculate Surface Height at this radius
                dip = 10.0 * (1.0 - (dist/radius)) 
                if dip < 0: dip = 0
                surface_height = height - dip
                
                # Base Body
                if dist <= radius:
                    # AGPH SINGULARITY BASE: Accretion Disk
                    
                    # P: Taper a(z) - Flat disk rising to a peak
                    # No taper, but height function
                    
                    # H: Helix R(z) - Swirling into center
                    angle_twist = (1.0 - dist/radius) * 4.0 * math.pi # 720 deg twist at center
                    
                    # A: Anisotropy A(z) - Radial Stretching (Spaghettification)
                    # As we get closer to center, stretch radially
                    radial_stretch = 1.0 + 2.0 * (1.0 - dist/radius)
                    
                    # Coordinate Transform
                    ca = math.cos(angle_twist)
                    sa = math.sin(angle_twist)
                    tx = x_mm * ca - y_mm * sa
                    ty = x_mm * sa + y_mm * ca
                    
                    # Apply Anisotropy
                    lx = tx * (2.0 * math.pi / 30.0) * radial_stretch
                    ly = ty * (2.0 * math.pi / 30.0)
                    lz = z_mm * (2.0 * math.pi / 30.0)
                    
                    # G: Gyroid
                    val = math.sin(lx)*math.cos(ly) + math.sin(ly)*math.cos(lz) + math.sin(lz)*math.cos(lx)
                    
                    # Boundary Logic
                    if z_mm <= surface_height:
                        # Shell or Lattice?
                        if z_mm < 4.0: # Solid Bottom
                            grid[x_idx,y_idx,z_idx] = True
                        elif dist > (radius - 5.0): # Solid Rim
                            grid[x_idx,y_idx,z_idx] = True
                        elif dist < 12.0: # Solid Core around hole
                            grid[x_idx,y_idx,z_idx] = True
                        elif abs(val) < 0.55: # Thicker Lattice (was 0.45)
                            grid[x_idx,y_idx,z_idx] = True
                else:
                    grid[x_idx,y_idx,z_idx] = False

    # Clean Dust (Strict QA)
    grid = lamp_lib.clean_voxel_grid(grid)

    # Mesh Extraction
    def add_quad(v1, v2, v3, v4):
        idx = len(vertices)
        vertices.extend([v1, v2, v3, v4])
        faces.append((idx, idx+1, idx+2))
        faces.append((idx, idx+2, idx+3))

    # ... mesh extraction loop ...
    # Actually, use lamp_lib.extract_mesh_from_grid since we imported it? 
    # No, manual code exists. Let's just fix the write path.
    
    # RE-IMPLEMENTING MESH EXTRACTION WITH LAMP_LIB TO BE SAFE/CLEAN
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, diameter, diameter)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "singularity_base.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_base(output_file)
