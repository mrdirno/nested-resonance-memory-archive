import numpy as np
import sys
import os

def load_density_map(filename="rf_density_map.npy"):
    if not os.path.exists(filename):
        print(f"[ERROR] {filename} not found. Run Cycle 395 first.")
        sys.exit(1)
    return np.load(filename)

def export_voxel_mesh(density_grid, filename="rf_sculpture.obj", threshold=1):
    """
    Exports a voxel mesh (cubes) for all voxels > threshold.
    This avoids needing scikit-image for marching cubes.
    """
    print(f"[MESH] Generating Voxel Mesh (Threshold={threshold})...")
    
    # Find active voxels
    x_idxs, y_idxs, z_idxs = np.where(density_grid >= threshold)
    total_voxels = len(x_idxs)
    print(f"[MESH] Found {total_voxels} active voxels.")
    
    if total_voxels == 0:
        print("[WARN] No voxels found. Mesh will be empty.")
        return

    vertices = []
    faces = []
    
    # Cube offsets
    offsets = [
        (0,0,0), (1,0,0), (1,1,0), (0,1,0), # Bottom
        (0,0,1), (1,0,1), (1,1,1), (0,1,1)  # Top
    ]
    
    # Cube faces (vertex indices)
    cube_faces = [
        (0,1,2,3), (4,5,6,7), # Bottom, Top
        (0,1,5,4), (2,3,7,6), # Front, Back
        (0,3,7,4), (1,2,6,5)  # Left, Right
    ]
    
    v_count = 0
    
    with open(filename, 'w') as f:
        f.write(f"# RF Sculpture - Cycle 396\n")
        f.write(f"o RF_Cloud\n")
        
        for i in range(total_voxels):
            x, y, z = x_idxs[i], y_idxs[i], z_idxs[i]
            
            # Add vertices for this voxel
            for dx, dy, dz in offsets:
                # Scale to physical space (optional, here we keep grid coords)
                f.write(f"v {x+dx} {y+dy} {z+dz}\n")
            
            # Add faces
            for face in cube_faces:
                # OBJ is 1-indexed
                f_indices = [v_count + idx + 1 for idx in face]
                f.write(f"f {' '.join(map(str, f_indices))}\n")
            
            v_count += 8
            
            if i % 100 == 0:
                sys.stdout.write(f"\r[MESH] Processing voxel {i}/{total_voxels}")
                sys.stdout.flush()
                
    print(f"\n[SAVE] Saved mesh to {filename}")

def main():
    print("[INIT] Cycle 396: The Invisible Sculpture")
    
    # 1. Load Data
    grid = load_density_map()
    print(f"[DATA] Grid Shape: {grid.shape}, Max Density: {grid.max()}")
    
    # 2. Determine Threshold (e.g., ignore empty space)
    threshold = 1
    
    # 3. Export
    export_voxel_mesh(grid, "rf_sculpture.obj", threshold)
    
    print("[DONE] Cycle 396 Complete.")

if __name__ == "__main__":
    main()
