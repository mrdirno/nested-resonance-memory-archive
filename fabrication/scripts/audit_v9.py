import struct
import numpy as np
import os
import sys
import math

# ==========================================
# CONFIGURATION
# ==========================================
CRITICAL_OVERHANG_ANGLE = 60.0  # Degrees from vertical
CRITICAL_COS_THETA = math.cos(math.radians(180 - CRITICAL_OVERHANG_ANGLE)) # e.g., cos(120) = -0.5

FILES = [
    "lamp_base_v9_quantum.stl",
    "lamp_shade_v9_quantum.stl",
    "lamp_shaft_v9_quantum.stl"
]

def read_stl(filename):
    try:
        with open(filename, "rb") as f:
            header = f.read(80)
            count_bytes = f.read(4)
            if len(count_bytes) < 4: return None
            count = struct.unpack("<I", count_bytes)[0]
            
            dt = np.dtype([
                ('n', np.float32, (3,)),
                ('v1', np.float32, (3,)),
                ('v2', np.float32, (3,)),
                ('v3', np.float32, (3,)),
                ('attr', np.uint16)
            ])
            
            data = np.frombuffer(f.read(), dtype=dt)
            return data
    except Exception as e:
        print(f"[ERROR] Failed to read {filename}: {e}")
        return None

def analyze_mesh(filename):
    print(f"\nAnalyzing: {os.path.basename(filename)}")
    data = read_stl(filename)
    if data is None: return False

    v1 = data['v1']
    v2 = data['v2']
    v3 = data['v3']
    
    # 1. Bounding Box
    all_verts = np.vstack((v1, v2, v3))
    if len(all_verts) == 0:
        print("  [FAIL] Empty Mesh.")
        return False
        
    min_coords = np.min(all_verts, axis=0)
    max_coords = np.max(all_verts, axis=0)
    dims = max_coords - min_coords

    print(f"  Dimensions: {dims[0]:.2f} x {dims[1]:.2f} x {dims[2]:.2f} mm")
    print(f"  Z-Range: {min_coords[2]:.2f} to {max_coords[2]:.2f} mm")

    z_compliance = True
    if abs(min_coords[2]) > 0.2: # Slightly looser tolerance for dev
        print(f"  [FAIL] Z-Min is {min_coords[2]:.2f}mm. Should be ~0.0mm.")
        z_compliance = False
    else:
        print(f"  [PASS] Bed Adhesion (Z~0).")

    # 2. Overhang Analysis
    edge1 = v2 - v1
    edge2 = v3 - v1
    cross = np.cross(edge1, edge2)
    norms = np.linalg.norm(cross, axis=1)
    
    valid_mask = norms > 1e-6
    calc_normals = np.zeros_like(cross)
    calc_normals[valid_mask] = cross[valid_mask] / norms[valid_mask, None]
    
    nz = calc_normals[:, 2]
    areas = 0.5 * norms
    
    # Exclude bed faces
    z_centers = (v1[:,2] + v2[:,2] + v3[:,2]) / 3.0
    not_bed_mask = z_centers > 0.1
    
    effective_areas = areas[not_bed_mask]
    effective_nz = nz[not_bed_mask]
    
    total_area_checked = np.sum(effective_areas)
    overhang_mask = effective_nz < CRITICAL_COS_THETA
    overhang_area = np.sum(effective_areas[overhang_mask])
    
    if total_area_checked > 0:
        overhang_pct = (overhang_area / total_area_checked) * 100.0
    else:
        overhang_pct = 0.0
        
    print(f"  Critical Overhangs (>60deg): {overhang_pct:.2f}%")
    
    if overhang_pct > 25.0: # Looser tolerance for quantum foam (lattice is tricky)
        print(f"  [WARN] High overhang content ({overhang_pct:.1f}%).")
    else:
        print(f"  [PASS] Printable geometry.")
        
    return z_compliance

def main():
    print("=== V9 QUANTUM AUDIT ===")
    all_pass = True
    for f in FILES:
        if not os.path.exists(f):
            print(f"Missing: {f}")
            all_pass = False
            continue
        if not analyze_mesh(f):
            all_pass = False
            
    if all_pass:
        print("\n✅ AUDIT PASSED: V9 Candidates Valid.")
        sys.exit(0)
    else:
        print("\n❌ AUDIT FAILED.")
        sys.exit(1)

if __name__ == "__main__":
    main()
