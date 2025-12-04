import numpy as np
import math
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# CHILD V24 (Catalog #89): THE LISSAJOUS KNOT 2 (Harmonic Tangle)
# -----------------------------------------------------------------------------
# Concept: A continuous, non-intersecting tube that weaves through space 
#          based on harmonic frequencies (Lissajous curve).
#          The tube itself is a porous lattice (Wireframe/Mesh).
# Parents: 34_lissajous_knot (Base), 50_torus_knot (Topology).
# Math: x=sin(5t), y=sin(7t), z=sin(9t).
# -----------------------------------------------------------------------------

def generate_child_v24(output_path, diameter=200.0, height=140.0, resolution=120, hole_diameter=14.0):
    print(f"Generating CHILD V24 (The Lissajous Knot 2): {output_path}")

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
    
    # Lissajous Parameters (Harmonic Ratios)
    # 3:4:5 is classic. 
    # 5:7:9 is denser.
    freq_x = 5.0
    freq_y = 7.0
    freq_z = 9.0
    
    # Pre-compute the curve points for distance field
    # We need enough points to approximate the curve smoothly
    num_points = 2000
    curve_points = []
    
    for i in range(num_points):
        t = (i / num_points) * 2.0 * math.pi
        
        # Parametric equations
        # Scaled to fit volume
        cx = (radius * 0.9) * math.sin(freq_x * t)
        cy = (radius * 0.9) * math.sin(freq_y * t)
        cz = (height * 0.9) * math.sin(freq_z * t)
        
        # Shift Z to be 0 to height (sine is -1 to 1)
        # Center is height/2
        cz = (height / 2.0) + (height * 0.45) * math.sin(freq_z * t)
        
        curve_points.append(np.array([cx, cy, cz]))
        
    curve_points = np.array(curve_points)
    
    # Optimization:
    # Calculating dist to 2000 points for 1M voxels is 2B operations. Slow.
    # We need a spatial index or a simpler field.
    
    # Alternative: Implicit Cylinder approximation?
    # Hard for general Lissajous.
    
    # Fast Distance Field:
    # Draw the curve into the grid?
    # 1. Iterate points, mark nearest voxels.
    # 2. Dilate?
    
    # Let's try the "Iterate Grid" approach but filter by bounding box? 
    # No, curve fills space.
    
    # Let's use a "Lattice Tube".
    # We only check voxels that are "close" to the curve.
    # We can iterate the curve points and "paint" the grid.
    
    # Tube Radius
    tube_radius = 14.0 
    
    # Paint Logic:
    # ...
    
    # Gyroid Lattice for the tube skin
    base_scale = 2.0 * math.pi / 10.0 # Fine mesh
    
    print("Painting trajectory...")
    
    # ...
    
    num_points_dense = 15000
    
    for i in range(num_points_dense):
        t = (i / num_points_dense) * 2.0 * math.pi
        
        # Grid indices
        # Convert mm to index
        g_x = int((cx + radius) / step)
        g_y = int((cy + radius) / step)
        g_z = int(cz / step)
        
        # Brush size in indices
        brush_rad = int(tube_radius / step) + 1
        
        # Iterate local box
        for bx in range(-brush_rad, brush_rad+1):
            ix = g_x + bx
            if ix < 0 or ix >= res_x: continue
            
            for by in range(-brush_rad, brush_rad+1):
                iy = g_y + by
                if iy < 0 or iy >= res_y: continue
                
                for bz in range(-brush_rad, brush_rad+1):
                    iz = g_z + bz
                    if iz < 0 or iz >= res_z: continue
                    
                    # Check if already set
                    if grid[ix, iy, iz]: continue
                    
                    # Physical coords of voxel
                    vx = (ix * step) - radius
                    vy = (iy * step) - radius
                    vz = iz * step
                    
                    # Distance to curve point
                    d = math.sqrt((vx-cx)**2 + (vy-cy)**2 + (vz-cz)**2)
                    
                    if d < tube_radius:
                        # We are inside the tube.
                        # Apply Lattice Mask (Wireframe)
                        # Gyroid
                        g = np.sin(vx*base_scale) * np.cos(vy*base_scale) + \
                            np.sin(vy*base_scale) * np.cos(vz*base_scale) + \
                            np.sin(vz*base_scale) * np.cos(vx*base_scale)
                        
                        # Wall thickness
                        if abs(g) < 0.45:
                            grid[ix, iy, iz] = True
                            
    # 1. MOUNTING (Post-Process to ensure it exists)
    # Iterate again? Or just overwrite?
    # Overwrite is safer.
    
    print("Applying Mounting...")
    for z_idx in range(res_z):
        z_mm = z_idx * step
        for x_idx in range(res_x):
            x_mm = (x_idx * step) - radius
            for y_idx in range(res_y):
                y_mm = (y_idx * step) - radius
                
                dist_xy = math.sqrt(x_mm**2 + y_mm**2)
                
                # Cap and Spider
                effective_z = z_mm
                if z_mm > (height - 10.0): effective_z = height - 10.0
                dz = effective_z - sphere_z_center
                term = radius**2 - dz**2
                curr_r = math.sqrt(term) if term > 0 else 0
                
                cap = lamp_lib.apply_solid_mounting_cap(
                    x_mm, y_mm, z_mm, dist_xy,
                    mount_z_start=(height - 4.0),
                    mount_hole_radius=mount_hole_radius,
                    cap_radius=curr_r
                )
                if cap is not None:
                    grid[x_idx,y_idx,z_idx] = cap
                    continue
                    
                spider = lamp_lib.apply_spider_fitter(
                    x_mm, y_mm, z_mm, dist_xy,
                    mount_z_start=(height - 40.0),
                    outer_radius=radius
                )
                if spider is not None:
                    grid[x_idx,y_idx,z_idx] = spider

    # Post-Processing
    grid = lamp_lib.clean_voxel_grid(grid)
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, diameter, diameter)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    output_dir = os.path.join(project_root, "fabrication/practical_design/FAVORITES/children")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "child_89_lissajous_knot_2.stl")
    
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_child_v24(output_file)
