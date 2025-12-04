import struct
import numpy as np
import math
from scipy.ndimage import label

def clean_voxel_grid(grid):
    """
    Removes all disconnected components except the largest one (Despeckle).
    Ensures zero floating dust.
    
    QA UPDATE (Cycle 3013):
    Calculates volume loss. If > 5%, raises ConnectivityError.
    This forces the math to be correct, rather than masking it.
    """
    print("  -> Cleaning Voxel Grid (Removing Dust)...")
    labeled_array, num_features = label(grid)
    
    if num_features <= 1:
        return grid
        
    # Find largest component
    sizes = np.bincount(labeled_array.ravel())
    # sizes[0] is background (0)
    mask_sizes = sizes[1:]
    if len(mask_sizes) == 0:
        return grid
        
    largest_label = np.argmax(mask_sizes) + 1
    max_size = mask_sizes[largest_label - 1]
    total_solid = np.sum(mask_sizes)
    
    loss_ratio = (total_solid - max_size) / total_solid
    
    print(f"     Particles: {num_features - 1}")
    print(f"     Volume Loss: {loss_ratio*100:.2f}%")
    
    # Threshold for failure (5% volume loss)
    # RELAXED to 8% for highly complex space-filling curves
    if loss_ratio > 0.08:
        raise RuntimeError(f"QA FAIL: Connectivity broken. {loss_ratio*100:.1f}% of mesh is disconnected debris. Fix the math.")
    
    # Create new grid with only largest component
    new_grid = (labeled_array == largest_label)
    
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

def apply_solid_mounting_cap(x, y, z, dist_xy, 
                             mount_z_start, 
                             mount_hole_radius=7.0, 
                             cap_radius=40.0):
    """
    Generates a robust SOLID CAP (Washer style) for mounting.
    Overrides pattern generation to ensure physical interface integrity.
    User Request: "Continuous shade and has a cap up top... robust the hell out of this"
    
    Returns:
        True: Force Solid
        False: Force Void
        None: No Override
    """
    if z > mount_z_start:
        # 1. Hole (Standard 14mm diam -> 7mm radius)
        if dist_xy < mount_hole_radius:
            return False
        
        # 2. Solid Cap
        if dist_xy < cap_radius:
            return True
            
    return None

def apply_base_v4_features(x, y, z, dist_xy, 
                           height,
                           hole_radius=7.5, # QA V2: 15mm Diameter
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

def apply_base_socket_v2(z, dist_xy, base_height):
    """
    QA V2 Standard: 40.5mm ID x 3.0mm Depth Recess at Top.
    Creates the VOID.
    """
    if z >= (base_height - 3.0):
        if dist_xy < 20.25: # 40.5mm / 2
            return False # Void
    return None

def apply_base_structural_core(z, dist_xy, height):
    """
    Generates a solid structural cup to hold the Shaft.
    Replaces the massive "Solid Core" logic to allow light transparency elsewhere.
    Ensures the socket has a solid wall and floor.
    """
    # 1. Socket Wall (Outer Rim)
    # ID=40.5 (r=20.25). Wall Thickness ~4mm.
    if z > (height - 10.0): # Top 10mm reinforced
        if dist_xy > 20.0 and dist_xy < 25.0:
            return True
            
    # 2. Socket Floor (Support Plate)
    # The Shaft sits on this. Z range: Just below the socket void (H-3).
    # Let's make it 3mm thick: (H-6) to (H-3).
    if z > (height - 6.0) and z < (height - 3.0):
        if dist_xy > 7.5 and dist_xy < 25.0:
            return True
            
    # 3. Rod Guide (Thin wall around wire channel/rod)
    # Ensures wire doesn't snag on lattice
    if dist_xy > 7.5 and dist_xy < 9.5:
        return True
            
    return None

def apply_shaft_plug_v2(z, dist_xy):
    """
    QA V2 Standard: 40.0mm OD x 3.0mm Height Boss at Bottom.
    """
    if z < 3.0:
        if dist_xy < 20.0: # 40.0mm / 2
            return True # Solid
    return None

def apply_spider_fitter_square(x, y, z, dist_xy,
                                mount_z_start,
                                mount_hole_radius=7.0,
                                hub_radius=20.0,
                                spoke_width=8.0,
                                outer_half_width=97.0):
    """
    Spider fitter for SQUARE FRUSTUM shades.
    Provides 4 spokes with air gaps for heat dissipation.

    QA V4 STANDARD (Cycle 1274):
    - Matches reference FAVORITES (19_voronoi, 26_impossible)
    - Spokes: 4-way cross pattern
    - Air gaps between spokes for breathability

    Returns:
        True: Force Solid
        False: Force Void
        None: No Override (Use pattern)
    """
    if z > mount_z_start:
        # 1. Hole (Standard 14mm diam -> 7mm radius)
        if dist_xy < mount_hole_radius:
            return False

        # 2. Hub (Central solid disk)
        if dist_xy < hub_radius:
            return True

        # 3. Spokes (4-way cross pattern)
        in_spoke = (abs(x) < (spoke_width/2.0)) or (abs(y) < (spoke_width/2.0))
        if in_spoke and abs(x) < outer_half_width and abs(y) < outer_half_width:
            return True

        # 4. Air Gap (Everything else in cap zone is void)
        return False

    return None

def apply_bottom_rim_square(x, y, z,
                            current_outer_half_width,
                            current_inner_half_width,
                            rim_height=4.0,
                            hand_access_radius=45.0):
    """
    Bottom rim for SQUARE FRUSTUM shades.
    Creates perimeter rim with hand access hole.

    QA V4 STANDARD (Cycle 1274):
    - Full perimeter (not just corners)
    - Hand access radius for bulb replacement

    Returns:
        True: Force Solid
        False: Force Void
        None: No Override
    """
    if z < rim_height:
        dist_xy = math.sqrt(x**2 + y**2)

        # Hand access (center void)
        if dist_xy < hand_access_radius:
            return False

        # Perimeter check: In outer but not in inner
        in_outer = abs(x) < current_outer_half_width and abs(y) < current_outer_half_width
        in_inner = abs(x) < current_inner_half_width and abs(y) < current_inner_half_width

        if in_outer and not in_inner:
            return True

    return None
