import struct
import sys
import os
import math

def calculate_bounds(file_path):
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return None

    min_x = float('inf')
    min_y = float('inf')
    min_z = float('inf')
    max_x = float('-inf')
    max_y = float('-inf')
    max_z = float('-inf')

    try:
        with open(file_path, 'rb') as f:
            f.read(80) # Skip header
            num_triangles = struct.unpack('<I', f.read(4))[0]
            
            for _ in range(num_triangles):
                # Read normal (12 bytes) + 3 vertices (36 bytes) + attribute (2 bytes)
                data = f.read(50)
                if len(data) < 50: break
                
                # Unpack vertices (floats at offsets 12, 16, 20, 24, 28, 32, 36, 40, 44)
                # We want x,y,z for v1, v2, v3
                # v1: 12, 16, 20
                # v2: 24, 28, 32
                # v3: 36, 40, 44
                
                floats = struct.unpack('<12f', data[:48])
                
                # v1
                min_x = min(min_x, floats[3])
                max_x = max(max_x, floats[3])
                min_y = min(min_y, floats[4])
                max_y = max(max_y, floats[4])
                min_z = min(min_z, floats[5])
                max_z = max(max_z, floats[5])
                
                # v2
                min_x = min(min_x, floats[6])
                max_x = max(max_x, floats[6])
                min_y = min(min_y, floats[7])
                max_y = max(max_y, floats[7])
                min_z = min(min_z, floats[8])
                max_z = max(max_z, floats[8])
                
                # v3
                min_x = min(min_x, floats[9])
                max_x = max(max_x, floats[9])
                min_y = min(min_y, floats[10])
                max_y = max(max_y, floats[10])
                min_z = min(min_z, floats[11])
                max_z = max(max_z, floats[11])

        width_x = max_x - min_x
        width_y = max_y - min_y
        height_z = max_z - min_z
        
        print(f"File: {os.path.basename(file_path)}")
        print(f"  Bounds X: {min_x:.2f} to {max_x:.2f} (Width: {width_x:.2f}mm)")
        print(f"  Bounds Y: {min_y:.2f} to {max_y:.2f} (Width: {width_y:.2f}mm)")
        print(f"  Bounds Z: {min_z:.2f} to {max_z:.2f} (Height: {height_z:.2f}mm)")
        
        # Ender 3 Check
        max_build_x = 220
        max_build_y = 220
        max_build_z = 250
        
        fits = True
        if width_x > max_build_x: fits = False
        if width_y > max_build_y: fits = False
        if height_z > max_build_z: fits = False
        
        if fits:
            print("  ✅ Fits in Ender 3 Volume")
        else:
            print("  ❌ EXCEEDS Ender 3 Volume!")
            
        return (width_x, width_y, height_z)

    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 validate_dimensions.py <file.stl> [file2.stl ...]")
    else:
        for f in sys.argv[1:]:
            calculate_bounds(f)
            print("-" * 30)
