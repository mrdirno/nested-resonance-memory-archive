import numpy as np
import struct
import sys
import os
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection

def read_stl_triangles(filename):
    triangles = []
    try:
        with open(filename, "rb") as f:
            header = f.read(80)
            count_bytes = f.read(4)
            count = struct.unpack("<I", count_bytes)[0]
            
            # Read all data at once
            data = f.read()
            
            # 50 bytes per triangle
            # Normal (12), v1 (12), v2 (12), v3 (12), attr (2)
            # We only need vertices
            
            num_tris = len(data) // 50
            
            # Use numpy for speed
            dt = np.dtype([
                ('n', np.float32, (3,)),
                ('v1', np.float32, (3,)),
                ('v2', np.float32, (3,)),
                ('v3', np.float32, (3,)),
                ('attr', np.uint16)
            ])
            
            arr = np.frombuffer(data, dtype=dt)
            
            v1 = arr['v1']
            v2 = arr['v2']
            v3 = arr['v3']
            
            return v1, v2, v3
            
    except Exception as e:
        print(f"Error reading STL: {e}")
        return None, None, None

def intersect_triangle_plane(v1, v2, v3, plane_axis=1, plane_val=0.0):
    """
    Finds intersection of triangle (v1,v2,v3) with plane (axis=val).
    Returns a line segment ((x1,z1), (x2,z2)) projected onto the other two axes.
    Assume plane_axis=1 (Y), returns (X,Z).
    """
    
    # Check if vertices are on different sides of the plane
    d1 = v1[plane_axis] - plane_val
    d2 = v2[plane_axis] - plane_val
    d3 = v3[plane_axis] - plane_val
    
    # If all same sign, no intersection
    if (d1 > 0 and d2 > 0 and d3 > 0) or (d1 < 0 and d2 < 0 and d3 < 0):
        return None
        
    # Edges
    edges = [(v1, v2, d1, d2), (v2, v3, d2, d3), (v3, v1, d3, d1)]
    points = []
    
    for va, vb, da, db in edges:
        # If edge crosses plane
        if (da > 0 and db <= 0) or (da <= 0 and db > 0):
            # Lerp
            t = da / (da - db)
            p = va + t * (vb - va)
            
            # Project to X, Z (indices 0, 2)
            points.append((p[0], p[2]))
            
    if len(points) == 2:
        return points
    return None

def generate_slice(filename, output_png):
    print(f"Slicing {os.path.basename(filename)}...")
    
    v1, v2, v3 = read_stl_triangles(filename)
    if v1 is None: return
    
    segments = []
    
    # Iterate (Vectorized would be better but complex for intersection logic)
    # We'll loop for simplicity/robustness first. 
    # Optimization: Filter triangles bounding box vs plane first.
    
    # Min/Max Y check
    min_y = np.minimum(np.minimum(v1[:,1], v2[:,1]), v3[:,1])
    max_y = np.maximum(np.maximum(v1[:,1], v2[:,1]), v3[:,1])
    
    # Only process triangles crossing Y=0
    mask = (min_y <= 0) & (max_y >= 0)
    
    fv1 = v1[mask]
    fv2 = v2[mask]
    fv3 = v3[mask]
    
    print(f"  Processing {len(fv1)} candidate triangles...")
    
    for i in range(len(fv1)):
        seg = intersect_triangle_plane(fv1[i], fv2[i], fv3[i])
        if seg:
            segments.append(seg)
            
    print(f"  Found {len(segments)} intersection segments.")
    
    if not segments:
        print("  No intersection with Y=0 plane.")
        return

    # Plot
    fig, ax = plt.subplots(figsize=(10, 10))
    
    lc = LineCollection(segments, colors='black', linewidths=0.5)
    ax.add_collection(lc)
    
    # Auto scale
    all_pts = np.array([p for s in segments for p in s])
    ax.set_xlim(all_pts[:,0].min() - 5, all_pts[:,0].max() + 5)
    ax.set_ylim(all_pts[:,1].min() - 5, all_pts[:,1].max() + 5)
    ax.set_aspect('equal')
    
    plt.title(f"Cross Section (Y=0): {os.path.basename(filename)}")
    plt.grid(True, which='both', alpha=0.3)
    
    plt.savefig(output_png, dpi=150)
    plt.close()
    print(f"  Saved preview to {output_png}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 generate_slice_preview.py <input.stl> [output.png]")
    else:
        infile = sys.argv[1]
        outfile = sys.argv[2] if len(sys.argv) > 2 else infile + ".png"
        generate_slice(infile, outfile)
