import struct
import sys
import os
from collections import defaultdict

def check_topology(file_path):
    print(f"Checking Topology: {os.path.basename(file_path)}")
    
    if not os.path.exists(file_path):
        print("❌ File not found.")
        return

    edge_counts = defaultdict(int)
    
    try:
        with open(file_path, 'rb') as f:
            f.read(80) # Header
            num_triangles = struct.unpack('<I', f.read(4))[0]
            print(f"  Triangles: {num_triangles}")
            
            for _ in range(num_triangles):
                data = f.read(50)
                # Unpack vertices
                floats = struct.unpack('<12f', data[:48])
                # v1: 3,4,5
                # v2: 6,7,8
                # v3: 9,10,11
                v1 = (floats[3], floats[4], floats[5])
                v2 = (floats[6], floats[7], floats[8])
                v3 = (floats[9], floats[10], floats[11])
                
                # Define edges (sorted tuples of vertices)
                edges = [
                    tuple(sorted((v1, v2))),
                    tuple(sorted((v2, v3))),
                    tuple(sorted((v3, v1)))
                ]
                
                for e in edges:
                    edge_counts[e] += 1
                    
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return

    # Analyze
    open_edges = 0
    non_manifold_edges = 0
    
    for count in edge_counts.values():
        if count == 1:
            open_edges += 1
        elif count > 2:
            non_manifold_edges += 1
            
    if open_edges == 0 and non_manifold_edges == 0:
        print("  ✅ MANIFOLD (Watertight).")
    else:
        print(f"  ⚠️ ISSUES FOUND:")
        print(f"     Open Edges (Holes): {open_edges}")
        print(f"     Non-Manifold Edges: {non_manifold_edges}")
        print("     (Note: Single-wall meshes like Lamp Shades often have open edges at the rim if not capped.)")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 validate_topology.py <file.stl>")
    else:
        check_topology(sys.argv[1])
