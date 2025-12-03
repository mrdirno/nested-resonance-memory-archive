import struct
import numpy as np
import os

# Specs from QA_PROTOCOL.md
SPECS = {
    "base_qa_v6.stl": {
        "target_dims": (150.0, 150.0, 45.0),
        "tolerance": 1.0, # mm
        "description": "Base V6 (Arch Tunnel)"
    },
    "shaft_qa_v5.stl": {
        "target_dims": (55.0, 55.0, 180.0), # Max width is crown (55mm)
        "tolerance": 1.0,
        "description": "Shaft V5 (Cable Safe)"
    },
    "shade_qa_v4.stl": {
        "target_dims": (200.0, 200.0, 220.0),
        "tolerance": 2.0, # slightly looser for organic shape
        "description": "Shade V4 (Blossom Grip)"
    }
}

def read_stl(filename):
    if not os.path.exists(filename):
        print(f"[ERROR] File not found: {filename}")
        return None

    with open(filename, "rb") as f:
        header = f.read(80)
        count_bytes = f.read(4)
        num_triangles = struct.unpack("<I", count_bytes)[0]
        
        print(f"[{filename}] Analyzing {num_triangles} triangles...")
        
        # Each triangle is 50 bytes: 12 (normal) + 36 (verts) + 2 (attr)
        # We can read it all into a numpy array for speed
        dtype = np.dtype([
            ('normal', np.float32, (3,)),
            ('v1', np.float32, (3,)),
            ('v2', np.float32, (3,)),
            ('v3', np.float32, (3,)),
            ('attr', np.uint16)
        ])
        
        data = np.fromfile(f, dtype=dtype, count=num_triangles)
        
        # Extract vertices
        v1 = data['v1']
        v2 = data['v2']
        v3 = data['v3']
        
        all_verts = np.concatenate((v1, v2, v3), axis=0)
        
        min_coords = np.min(all_verts, axis=0)
        max_coords = np.max(all_verts, axis=0)
        
        dims = max_coords - min_coords
        
        return {
            "min": min_coords,
            "max": max_coords,
            "dims": dims,
            "tri_count": num_triangles
        }

def check_artifact(filename, spec):
    data = read_stl(filename)
    if data is None: return False
    
    dims = data["dims"]
    target = spec["target_dims"]
    tol = spec["tolerance"]
    
    print(f"  Measured: {dims[0]:.2f} x {dims[1]:.2f} x {dims[2]:.2f} mm")
    print(f"  Target:   {target[0]:.2f} x {target[1]:.2f} x {target[2]:.2f} mm")
    
    valid = True
    # Check X
    if abs(dims[0] - target[0]) > tol:
        print(f"  [FAIL] X Dimension deviation > {tol}mm")
        valid = False
    # Check Y
    if abs(dims[1] - target[1]) > tol:
        print(f"  [FAIL] Y Dimension deviation > {tol}mm")
        valid = False
    # Check Z
    if abs(dims[2] - target[2]) > tol:
        print(f"  [FAIL] Z Dimension deviation > {tol}mm")
        valid = False
        
    if valid:
        print(f"  [PASS] Geometry verified.")
    else:
        print(f"  [FAIL] Geometry mismatch.")
        
    return valid

def main():
    base_dir = "fabrication/practical_design/LAMP_DESIGN"
    print("=== HELIOS QA VERIFICATION START ===\n")
    
    all_pass = True
    
    for f, s in SPECS.items():
        path = os.path.join(base_dir, f)
        print(f"Verifying: {s['description']}")
        if not check_artifact(path, s):
            all_pass = False
        print("-" * 40)
        
    if all_pass:
        print("\n=== [SUCCESS] ALL ARTIFACTS PASS GEOMETRIC QA ===")
    else:
        print("\n=== [FAILURE] SOME ARTIFACTS FAILED QA ===")
        exit(1)

if __name__ == "__main__":
    main()
