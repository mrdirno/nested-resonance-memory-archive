import struct
import numpy as np
import math
from scipy.ndimage import label

def clean_voxel_grid(grid):
    """
    Removes all disconnected components except the largest one (Despeckle).
    Ensures zero floating dust.
    """
    print("  -> Cleaning Voxel Grid (Removing Dust)...")
    labeled_array, num_features = label(grid)
    
    if num_features <= 1:
        return grid
        
    # Find largest component
    sizes = np.bincount(labeled_array.ravel())
    # sizes[0] is background (0), so ignore it
    mask_sizes = sizes[1:]
    if len(mask_sizes) == 0:
        return grid
        
    largest_label = np.argmax(mask_sizes) + 1
    
    # Create new grid with only largest component
    new_grid = (labeled_array == largest_label)
    
    print(f"     Removed {num_features - 1} floating particles.")
    return new_grid

def write_binary_stl(filename, vertices, faces):
    """
    Writes a mesh (vertices/faces) to a Binary STL file.
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
    print(f"  -> Writing Binary STL to {filename} ({num_triangles} triangles)...")

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
    print("  -> Done.")

def extract_mesh_from_grid(grid, step, base_width, base_depth, base_height_offset=0.0):
    """
    Simple voxel-based mesh extraction (Quads).
    """
    print("  -> Extracting Mesh from Voxel Grid...")
    vertices = []
    faces = []
    
    res_x, res_y, res_z = grid.shape
    
    def add_quad(v1, v2, v3, v4):
        idx = len(vertices)
        vertices.extend([v1, v2, v3, v4])
        faces.append((idx, idx+1, idx+2))
        faces.append((idx, idx+2, idx+3))

    for z in range(res_z):
        z_mm = (z * step) + base_height_offset # Z might have different step? Assuming uniform for now or handled outside
        # Actually, usually passed step is uniform.
        
        for x in range(res_x):
            x_mm = (x * step) - (base_width/2)
            for y in range(res_y):
                y_mm = (y * step) - (base_depth/2)
                
                if not grid[x,y,z]: continue
                
                s2 = step/2
                
                # Neighbors
                if x==res_x-1 or not grid[x+1,y,z]: add_quad((x_mm+s2, y_mm-s2, z_mm-s2), (x_mm+s2, y_mm+s2, z_mm-s2), (x_mm+s2, y_mm+s2, z_mm+s2), (x_mm+s2, y_mm-s2, z_mm+s2))
                if x==0 or not grid[x-1,y,z]: add_quad((x_mm-s2, y_mm-s2, z_mm+s2), (x_mm-s2, y_mm+s2, z_mm+s2), (x_mm-s2, y_mm+s2, z_mm-s2), (x_mm-s2, y_mm-s2, z_mm-s2))
                if y==res_y-1 or not grid[x,y+1,z]: add_quad((x_mm+s2, y_mm+s2, z_mm-s2), (x_mm-s2, y_mm+s2, z_mm-s2), (x_mm-s2, y_mm+s2, z_mm+s2), (x_mm+s2, y_mm+s2, z_mm+s2))
                if y==0 or not grid[x,y-1,z]: add_quad((x_mm-s2, y_mm-s2, z_mm-s2), (x_mm+s2, y_mm-s2, z_mm-s2), (x_mm+s2, y_mm+s2, z_mm+s2), (x_mm-s2, y_mm-s2, z_mm+s2))
                if z==res_z-1 or not grid[x,y,z+1]: add_quad((x_mm+s2, y_mm-s2, z_mm+s2), (x_mm+s2, y_mm+s2, z_mm+s2), (x_mm-s2, y_mm+s2, z_mm+s2), (x_mm-s2, y_mm-s2, z_mm+s2))
                if z==0 or not grid[x,y,z-1]: add_quad((x_mm-s2, y_mm-s2, z_mm-s2), (x_mm+s2, y_mm-s2, z_mm-s2), (x_mm+s2, y_mm+s2, z_mm-s2), (x_mm-s2, y_mm-s2, z_mm-s2))

    return vertices, faces

def apply_spider_fitter(x, y, z, dist_xy, 
                        mount_z_start, 
                        mount_hole_radius=7.0, 
                        hub_radius=20.0, 
                        spoke_width=8.0,
                        outer_radius=100.0):
    """
    Returns:
        True: Force Solid
        False: Force Void
        None: No Override (Use pattern)
    """
    if z > mount_z_start:
        # 1. Hole
        if dist_xy < mount_hole_radius:
            return False
        
        # 2. Hub
        if dist_xy < hub_radius:
            return True
            
        # 3. Spokes
        in_spoke = (abs(x) < (spoke_width/2.0)) or (abs(y) < (spoke_width/2.0))
        if in_spoke and dist_xy < outer_radius:
            return True
            
        # 4. Air Gap
        return False
    
    return None

def apply_base_v4_features(x, y, z, dist_xy, 
                           height,
                           hole_radius=7.0,
                           channel_height=8.0,
                           channel_width=8.0,
                           foot_depth=3.0,
                           foot_radius=10.0,
                           foot_offset=15.0,
                           radius=90.0):
    """
    Standard Base features: Wire Channel, Feet, Central Hole.
    Returns: False (Force Void) or None.
    """
    # 1. Central Hole
    if dist_xy < hole_radius:
        return False
        
    # 2. Wire Channel (Assuming +X exit)
    if z < channel_height:
        if x > 0 and abs(y) < (channel_width/2.0):
            return False
            
    # 3. Feet Recesses
    if z < foot_depth:
        r_center = radius - foot_offset
        # Check 4 corners
        if math.sqrt((x-r_center)**2 + y**2) < foot_radius: return False
        if math.sqrt((x+r_center)**2 + y**2) < foot_radius: return False
        if math.sqrt(x**2 + (y-r_center)**2) < foot_radius: return False
        if math.sqrt(x**2 + (y+r_center)**2) < foot_radius: return False
        
    return None
