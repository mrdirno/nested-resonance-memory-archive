import trimesh
import numpy as np
import sys

def calculate_shadow_density(stl_path, resolution=100):
    print(f"Analyzing Optical Porosity for: {stl_path}")
    
    mesh = trimesh.load(stl_path)
    
    # Get bounds
    bounds = mesh.bounds
    min_b = bounds[0]
    max_b = bounds[1]
    
    print(f"Bounds: {min_b} to {max_b}")
    
    # Ray Casting Setup
    # We will cast rays from TOP to BOTTOM (Z-axis) to test "Vertical Transparency"
    # And from SIDE to SIDE (X-axis) to test "Horizontal Transparency"
    
    # 1. Vertical Scan (Z-Axis Transparency)
    # Create a grid of rays looking down
    x = np.linspace(min_b[0], max_b[0], resolution)
    y = np.linspace(min_b[1], max_b[1], resolution)
    xv, yv = np.meshgrid(x, y)
    
    origins = np.column_stack((xv.flatten(), yv.flatten(), np.full_like(xv.flatten(), max_b[2] + 1.0)))
    direction = np.array([0, 0, -1]) # Down
    
    # Ray intersects location
    # We count how many rays hit the mesh
    
    # Using trimesh ray Intersector (Triangle - Slower but robust)
    intersector = trimesh.ray.ray_triangle.RayMeshIntersector(mesh)
    
    print("Casting Vertical Rays (Top-Down)...")
    index_tri, index_ray, locations = intersector.intersects_id(
        origins,
        np.tile(direction, (len(origins), 1)),
        return_locations=True, 
        multiple_hits=False # We just want to know if it's blocked
    )
    
    blocked_rays = len(index_ray)
    total_rays = len(origins)
    vertical_opacity = blocked_rays / total_rays
    
    print(f"Vertical Opacity (Top-Down Shadow): {vertical_opacity:.2%}")
    print(f"Vertical Transparency: {(1.0 - vertical_opacity):.2%}")
    
    # 2. Horizontal Gradient Scan (X-Axis)
    # We want to see opacity change vs Height (Z)
    # We slice the object into 10 vertical sections and cast rays through each
    
    print("\nCalculating Horizontal Gradient Opacity (Side-On)...")
    z_slices = np.linspace(min_b[2], max_b[2], 11)
    
    print(f"{'Height (Z)':<15} | {'Opacity'}")
    print("-" * 30)
    
    for i in range(len(z_slices) - 1):
        z_start = z_slices[i]
        z_end = z_slices[i+1]
        mid_z = (z_start + z_end) / 2
        
        # Rays from X- to X+
        y_scan = np.linspace(min_b[1], max_b[1], resolution)
        z_scan = np.linspace(z_start, z_end, int(resolution/10)) # Fewer rays for slice
        yv_s, zv_s = np.meshgrid(y_scan, z_scan)
        
        origins_side = np.column_stack((np.full_like(yv_s.flatten(), min_b[0] - 1.0), yv_s.flatten(), zv_s.flatten()))
        direction_side = np.array([1, 0, 0]) # Right
        
        index_tri_s, index_ray_s = intersector.intersects_id(
            origins_side,
            np.tile(direction_side, (len(origins_side), 1)),
            multiple_hits=False
        )
        
        opacity = len(index_ray_s) / len(origins_side)
        print(f"{mid_z:<15.2f} | {opacity:.2%}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python calculate_shadow.py <input.stl>")
    else:
        calculate_shadow_density(sys.argv[1])
