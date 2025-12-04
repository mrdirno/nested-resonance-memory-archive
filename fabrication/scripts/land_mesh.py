import struct
import numpy as np
import os
import sys

def land_stl(filename):
    print(f"Landing: {filename}")
    try:
        with open(filename, "rb") as f:
            header = f.read(80)
            count_bytes = f.read(4)
            count = struct.unpack("<I", count_bytes)[0]
            
            dt = np.dtype([
                ('n', np.float32, (3,)),
                ('v1', np.float32, (3,)),
                ('v2', np.float32, (3,)),
                ('v3', np.float32, (3,)),
                ('attr', np.uint16)
            ])
            
            data = np.frombuffer(f.read(), dtype=dt)
            
        # Find min Z
        all_z = np.concatenate((data['v1'][:,2], data['v2'][:,2], data['v3'][:,2]))
        min_z = np.min(all_z)
        
        print(f"  Current Min Z: {min_z:.4f}")
        
        if abs(min_z) < 0.001:
            print("  Already landed.")
            return

        offset = -min_z
        print(f"  Applying offset: {offset:.4f}")
        
        # Apply offset
        # We need to be careful with numpy read-only arrays if frombuffer is read-only
        # But we can modify fields if we copy or if it's writable.
        # Let's make a copy to be safe and writable
        
        new_data = data.copy()
        new_data['v1'][:,2] += offset
        new_data['v2'][:,2] += offset
        new_data['v3'][:,2] += offset
        
        # Write back
        with open(filename, "wb") as f:
            f.write(header)
            f.write(count_bytes)
            f.write(new_data.tobytes())
            
        print("  Landed successfully.")

    except Exception as e:
        print(f"[ERROR] Failed to land {filename}: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        files = sys.argv[1:]
    else:
        files = [
            "lamp_base_v9_quantum.stl",
            "lamp_shade_v9_quantum.stl",
            "lamp_shaft_v9_quantum.stl"
        ]
    
    for f in files:
        if os.path.exists(f):
            land_stl(f)
        else:
            print(f"Missing: {f}")
