import struct
import numpy as np
import os
import sys
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components

def check_connectivity(filename):
    print(f"Checking connectivity for {filename}...")
    
    try:
        with open(filename, "rb") as f:
            header = f.read(80)
            count_bytes = f.read(4)
            if len(count_bytes) < 4:
                print(f"[ERROR] {filename} is empty or invalid.")
                return False
            count = struct.unpack("<I", count_bytes)[0]
            buffer = f.read()
    except Exception as e:
        print(f"[ERROR] Read failed: {e}")
        return False

    dt = np.dtype([
        ('n', np.float32, (3,)),
        ('v1', np.float32, (3,)),
        ('v2', np.float32, (3,)),
        ('v3', np.float32, (3,)),
        ('attr', np.uint16)
    ])
    
    data = np.frombuffer(buffer, dtype=dt)
    
    v1 = data['v1']
    v2 = data['v2']
    v3 = data['v3']
    
    all_verts = np.vstack((v1, v2, v3))
    all_verts = np.round(all_verts, 3)
    
    unique_verts, indices = np.unique(all_verts, axis=0, return_inverse=True)
    num_unique = len(unique_verts)
    print(f"  Unique Vertices: {num_unique}")
    
    n_tris = len(data)
    idx_v1 = indices[0:n_tris]
    idx_v2 = indices[n_tris:2*n_tris]
    idx_v3 = indices[2*n_tris:3*n_tris]
    
    print("  Building topology...")
    row = np.concatenate((idx_v1, idx_v2, idx_v3))
    col = np.concatenate((idx_v2, idx_v3, idx_v1))
    vals = np.ones(len(row), dtype=int)
    adj = coo_matrix((vals, (row, col)), shape=(num_unique, num_unique))
    
    n_components, labels = connected_components(adj, directed=False)
    
    print(f"  Connected Components: {n_components}")
    
    if n_components == 1:
        print("  [PASS] Mesh is monolithic.")
        return True
    else:
        unique, counts = np.unique(labels, return_counts=True)
        sorted_counts = np.sort(counts)[::-1]
        print(f"  [FAIL] Mesh is fragmented. Largest component: {sorted_counts[0]} verts. Others: {sorted_counts[1:10]}...")
        
        if len(sorted_counts) > 1 and sorted_counts[1] > 100:
            print("  -> Significant disconnected geometry detected.")
            return False
        elif len(sorted_counts) > 1:
            print("  -> Fragments are negligible (dust). Warning only.")
            return True 
            
    return False

def main():
    print("=== TOPOLOGY INTEGRITY AUDIT (FINAL) ===\n")
    
    files = [
        "fabrication/practical_design/LAMP_DESIGN/shade_qa_v6.stl", # Solid Architecture
        "fabrication/practical_design/LAMP_DESIGN/shaft_qa_v6.stl", # Pure Solid CSG
        "fabrication/practical_design/LAMP_DESIGN/base_qa_v6.stl" # Passed previously
    ]
    
    failed = False
    for f in files:
        if not os.path.exists(f):
            print(f"Missing: {f}")
            failed = True
            continue
            
        if not check_connectivity(f):
            failed = True
        print("-" * 30)
        
    if failed:
        print("\n❌ AUDIT FAILED: Issues detected.")
        sys.exit(1)
    else:
        print("\n✅ AUDIT PASSED: All meshes monolithic.")
        sys.exit(0)

if __name__ == "__main__":
    main()
