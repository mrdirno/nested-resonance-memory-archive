import numpy as np
import math
import sys
import os
import random

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# CHILD V47 (Catalog #112): THE BARNSLEY FERN (Affine Transformations)
# -----------------------------------------------------------------------------
# Concept: A 3D extrusion of the famous Barnsley Fern fractal.
#          Uses an IFS (Iterated Function System) of affine transformations.
#          Projected onto a sphere to create a botanical, leaf-wrapped look.
# Parents: 17_lightning_bolt (L-System), 110_rauzy (IFS).
# Math: Probabilistic IFS (Chaos Game).
# -----------------------------------------------------------------------------

def generate_barnsley_fern(iterations=50000):
    # Standard Barnsley Fern IFS
    # Returns list of (x, y) points.
    # Domain roughly [-2.5, 2.7] x [0, 10] 
    
    points = []
    x, y = 0.0, 0.0
    
    # Transformations
    # 1. Stem (1% prob)
    # 2. Smaller leaflets (85% prob)
    # 3. Left leaflet (7% prob)
    # 4. Right leaflet (7% prob)
    
    for i in range(iterations):
        r = random.random()
        
        next_x, next_y = 0.0, 0.0
        
        if r < 0.01:
            next_x = 0.0
            next_y = 0.16 * y
        elif r < 0.86:
            next_x = 0.85 * x + 0.04 * y
            next_y = -0.04 * x + 0.85 * y + 1.6
        elif r < 0.93:
            next_x = 0.20 * x - 0.26 * y
            next_y = 0.23 * x + 0.22 * y + 1.6
        else:
            next_x = -0.15 * x + 0.28 * y
            next_y = 0.26 * x + 0.24 * y + 0.44
            
        x, y = next_x, next_y
        points.append(np.array([x, y]))
        
    return np.array(points)

def generate_child_v47(output_path, diameter=200.0, height=140.0, resolution=120, hole_diameter=14.0):
    print(f"Generating CHILD V47 (The Barnsley Fern): {output_path}")

    mount_hole_radius = hole_diameter / 2.0
    shell_thickness = 25.0
    
    max_dim = max(diameter, height)
    step = max_dim / resolution
    
    # Pad grid
    res_x = int(diameter / step) + 6
    res_y = int(diameter / step) + 6
    res_z = int(height / step) + 2
    
    grid = np.zeros((res_x, res_y, res_z), dtype=bool)
    
    radius = diameter / 2.0
    sphere_z_center = height - radius
    
    # ---------------------------------------------------------
    # FERN GENERATION
    # ---------------------------------------------------------
    
    points_2d = generate_barnsley_fern(150000) # High density points
    
    # Normalize
    # Map to spherical coords
    # Fern x is width, y is height (stem).
    # Map y -> theta (vertical arc)
    # Map x -> phi (width around)
    
    min_p = np.min(points_2d, axis=0)
    max_p = np.max(points_2d, axis=0)
    range_p = max_p - min_p
    
    norm_points = (points_2d - min_p) / range_p
    
    print("Mapping Fern to Sphere...")
    
    # We want multiple ferns wrapping the sphere?
    # Let's place 5 huge ferns.
    
    sphere_points = []
    
    num_ferns = 5
    
    for i in range(num_ferns):
        offset_phi = (i / num_ferns) * 2.0 * math.pi
        
        for p in norm_points:
            u, v = p
            
            # Fern grows UP
            # v=0 is bottom, v=1 is top.
            
            # Map v to theta (pole to pole)
            # 0 -> pi (bottom), 1 -> 0 (top)
            theta = (1.0 - v) * math.pi
            # Clamp slightly to avoid pole artifacts?
            theta = theta * 0.9 + 0.05
            
            # Map u to phi width
            # Fern is narrow.
            # Width approx pi/2?
            phi_width = math.pi / 1.5
            phi = (u - 0.5) * phi_width + offset_phi
            
            # Twist
            phi += theta * 0.3
            
            sx = radius * math.sin(theta) * math.cos(phi)
            sy = radius * math.sin(theta) * math.sin(phi)
            sz = radius * math.cos(theta) + sphere_z_center
            
            # Store
            sphere_points.append(np.array([sx, sy, sz]))
            
    print("Painting Fern Structure...")
    
    # Voxel Painting (Point Cloud)
    # Brush radius small to capture detail
    # Increased for connectivity
    brush_radius = 3.5 
    
    # Map points to unique voxel indices
    # To optimize, we iterate points and mark grid directly
    
    for p in sphere_points:
        gx = int((p[0] + radius) / step)
        gy = int((p[1] + radius) / step)
        gz = int(p[2] / step)
        
        # Brush
        brush = 1
        for bx in range(-brush, brush+1):
            ix = gx + bx
            if ix < 0 or ix >= res_x: continue
            for by in range(-brush, brush+1):
                iy = gy + by
                if iy < 0 or iy >= res_y: continue
                for bz in range(-brush, brush+1):
                    iz = gz + bz
                    if iz < 0 or iz >= res_z: continue
                    
                    # Physical check
                    vx = (ix * step) - radius
                    vy = (iy * step) - radius
                    vz = iz * step
                    
                    if math.sqrt((vx-p[0])**2 + (vy-p[1])**2 + (vz-p[2])**2) < brush_radius:
                        grid[ix, iy, iz] = True

    # 1. MOUNTING
    print("Applying Mounting...")
    for z_idx in range(res_z):
        z_mm = z_idx * step
        for x_idx in range(res_x):
            x_mm = (x_idx * step) - radius
            for y_idx in range(res_y):
                y_mm = (y_idx * step) - radius
                
                dist_xy = math.sqrt(x_mm**2 + y_mm**2)
                
                # Effective Z
                effective_z = z_mm
                if z_mm > (height - 10.0): effective_z = height - 10.0
                dz = effective_z - sphere_z_center
                term = radius**2 - dz**2
                curr_r = math.sqrt(term) if term > 0 else 0
                
                cap = lamp_lib.apply_solid_mounting_cap(
                    x_mm, y_mm, z_mm,
                    dist_xy,
                    mount_z_start=(height - 4.0),
                    mount_hole_radius=mount_hole_radius,
                    cap_radius=curr_r
                )
                if cap is not None:
                    grid[x_idx,y_idx,z_idx] = cap
                    continue
                    
                spider = lamp_lib.apply_spider_fitter(
                    x_mm, y_mm, z_mm,
                    dist_xy,
                    mount_z_start=(height - 40.0),
                    outer_radius=radius
                )
                if spider is not None:
                    grid[x_idx,y_idx,z_idx] = spider
                    
                dist_sq = x_mm**2 + y_mm**2 + (effective_z - sphere_z_center)**2
                dist_spherical = math.sqrt(dist_sq)
                
                in_outer = dist_spherical <= radius
                in_inner = dist_spherical < (radius - shell_thickness)
                in_hand_zone = (dist_xy < (radius - shell_thickness)) and (z_mm < (height - 40.0))
                
                if in_outer and not in_inner and not in_hand_zone:
                    if not grid[x_idx,y_idx,z_idx]: # If not fern
                        # Background lattice
                        base_scale = 2.0 * math.pi / 20.0
                        g_val = np.sin(x_mm*base_scale) * np.cos(y_mm*base_scale) + \
                                np.sin(y_mm*base_scale) * np.cos(z_mm*base_scale) + \
                                np.sin(z_mm*base_scale) * np.cos(x_mm*base_scale)
                        
                        # Thicker binder
                        if abs(g_val) < 0.45:
                            grid[x_idx,y_idx,z_idx] = True

    # Post-Processing
    grid = lamp_lib.clean_voxel_grid(grid)
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, diameter, diameter)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    output_dir = os.path.join(project_root, "fabrication/practical_design/FAVORITES/children")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "child_112_barnsley_fern.stl")
    
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_child_v47(output_file)