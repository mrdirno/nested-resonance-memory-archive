import struct
import os
import sys
import math

def validate_stl(file_path):
    print(f"Validating: {file_path}")
    
    if not os.path.exists(file_path):
        print("❌ ERROR: File not found.")
        return

    file_size = os.path.getsize(file_path)
    print(f"File Size: {file_size} bytes ({file_size / (1024*1024):.2f} MB)")

    with open(file_path, 'rb') as f:
        header = f.read(80)
        if b'solid' in header[:5].lower():
            print("⚠️ WARNING: Header starts with 'solid'. This might confuse some parsers into thinking it's ASCII.")
        
        count_bytes = f.read(4)
        if len(count_bytes) < 4:
            print("❌ ERROR: File too short to contain triangle count.")
            return
            
        num_triangles = struct.unpack('<I', count_bytes)[0]
        print(f"Declared Triangle Count: {num_triangles}")
        
        expected_size = 80 + 4 + (num_triangles * 50)
        print(f"Expected File Size:    {expected_size} bytes")
        
        if file_size != expected_size:
            diff = file_size - expected_size
            print(f"❌ ERROR: Size Mismatch! Diff: {diff} bytes.")
            if file_size < expected_size:
                print("   (File is TRUNCATED)")
            else:
                print("   (File has EXTRA data)")
        else:
            print("✅ File Size matches Triangle Count.")

        # Sample Check
        print("Checking first 1000 triangles for NaN/Inf...")
        try:
            for i in range(min(num_triangles, 1000)):
                tri_data = f.read(50)
                if len(tri_data) < 50:
                    print(f"❌ ERROR: Unexpected EOF at triangle {i}")
                    break
                
                # Unpack 12 floats
                floats = struct.unpack('<12f', tri_data[:48])
                if any(math.isnan(x) or math.isinf(x) for x in floats):
                    print(f"❌ ERROR: NaN or Inf detected in triangle {i}")
                    print(f"   Values: {floats}")
                    return
        except Exception as e:
            print(f"❌ ERROR reading triangles: {e}")
            return

    print("✅ structure Check Complete.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 validate_stl.py <file.stl>")
    else:
        validate_stl(sys.argv[1])
