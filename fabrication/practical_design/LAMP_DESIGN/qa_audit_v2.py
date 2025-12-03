import struct
import numpy as np
import os
import sys

# Define the EXPECTED final configuration
TARGETS = {
    "base_qa_v6.stl": {
        "desc": "Base (Root / AGPH Dome)",
        "min_size_mb": 5.0,
        "dims": (150.0, 150.0, 45.0),
        "tolerance": 1.0
    },
    "shaft_qa_v5.stl": {
        "desc": "Shaft (Pillar / AGPH Hourglass)",
        "min_size_mb": 20.0, # Shaft is heavy gyroid
        "dims": (55.0, 55.0, 180.0), # 55mm Crown width
        "tolerance": 1.0
    },
    "shade_qa_v4.stl": {
        "desc": "Shade (Bell / AGPH Blossom)",
        "min_size_mb": 2.0, # Thin shell
        "dims": (200.0, 200.0, 220.0),
        "tolerance": 2.0
    }
}

BASE_DIR = "fabrication/practical_design/LAMP_DESIGN"

def check_file(filename, spec):
    path = os.path.join(BASE_DIR, filename)
    
    # 1. Existence
    if not os.path.exists(path):
        print(f"[FAIL] {filename} missing.")
        return False
        
    # 2. Size
    size_mb = os.path.getsize(path) / (1024*1024)
    if size_mb < spec["min_size_mb"]:
        print(f"[WARN] {filename} size ({size_mb:.2f}MB) below threshold ({spec['min_size_mb']}MB). Potential low-res or corruption.")
        # Not a hard fail, but suspicious
    else:
        print(f"[OK] {filename} size: {size_mb:.2f}MB")

    # 3. Geometry (Binary STL parse)
    try:
        with open(path, "rb") as f:
            header = f.read(80)
            count = struct.unpack("<I", f.read(4))[0]
            
            # Read vert data
            # numpy fromfile is fast
            # 50 bytes per triangle
            dtype = np.dtype([
                ('normal', np.float32, (3,)),
                ('v1', np.float32, (3,)),
                ('v2', np.float32, (3,)),
                ('v3', np.float32, (3,)),
                ('attr', np.uint16)
            ])
            data = np.fromfile(f, dtype=dtype, count=count)
            
            v1 = data['v1']
            v2 = data['v2']
            v3 = data['v3']
            
            all_verts = np.concatenate((v1, v2, v3), axis=0)
            if len(all_verts) == 0:
                print(f"[FAIL] {filename} has no geometry.")
                return False
                
            min_c = np.min(all_verts, axis=0)
            max_c = np.max(all_verts, axis=0)
            dims = max_c - min_c
            
            target_dims = spec["dims"]
            tol = spec["tolerance"]
            
            # Check dimensions
            diff = np.abs(dims - target_dims)
            if np.any(diff > tol):
                print(f"[FAIL] {filename} dimensions out of spec.")
                print(f"       Measured: {dims}")
                print(f"       Target:   {target_dims}")
                return False
            else:
                print(f"[PASS] {filename} geometry verified.")
                
    except Exception as e:
        print(f"[FAIL] {filename} verification error: {e}")
        return False
        
    return True

def main():
    print("=== HELIOS PRODUCTION AUDIT (Cycle 2992) ===\n")
    all_good = True
    for filename, spec in TARGETS.items():
        print(f"Auditing {spec['desc']}...")
        if not check_file(filename, spec):
            all_good = False
        print("-" * 40)
    
    if all_good:
        print("\n✅ SYSTEM GREEN: All artifacts ready for fabrication.")
        sys.exit(0)
    else:
        print("\n❌ SYSTEM RED: Audit failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()
