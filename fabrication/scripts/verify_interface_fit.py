import numpy as np
import struct
import sys
import os
import math

def read_stl_triangles(filename):
    try:
        with open(filename, "rb") as f:
            header = f.read(80)
            count_bytes = f.read(4)
            if len(count_bytes) < 4: return None
            
            dt = np.dtype([
                ('n', np.float32, (3,)),
                ('v1', np.float32, (3,)),
                ('v2', np.float32, (3,)),
                ('v3', np.float32, (3,)),
                ('attr', np.uint16)
            ])
            data = np.frombuffer(f.read(), dtype=dt)
            return data['v1'], data['v2'], data['v3']
    except Exception as e:
        print(f"Error: {e}")
        return None, None, None

def get_cross_section_segments(v1, v2, v3, z_height):
    # Identify triangles that cross z_height
    min_z = np.minimum(np.minimum(v1[:,2], v2[:,2]), v3[:,2])
    max_z = np.maximum(np.maximum(v1[:,2], v2[:,2]), v3[:,2])
    
    mask = (min_z <= z_height) & (max_z >= z_height)
    
    fv1 = v1[mask]
    fv2 = v2[mask]
    fv3 = v3[mask]
    
    segments = []
    
    for i in range(len(fv1)):
        # Find edges crossing Z plane
        pts = [fv1[i], fv2[i], fv3[i]]
        intersections = []
        
        # Check edges (0-1, 1-2, 2-0)
        for j in range(3):
            p_a = pts[j]
            p_b = pts[(j+1)%3]
            
            dz_a = p_a[2] - z_height
            dz_b = p_b[2] - z_height
            
            # Check sign change
            if (dz_a > 0 and dz_b <= 0) or (dz_a <= 0 and dz_b > 0):
                t = dz_a / (dz_a - dz_b)
                p_x = p_a[0] + t * (p_b[0] - p_a[0])
                p_y = p_a[1] + t * (p_b[1] - p_a[1])
                intersections.append((p_x, p_y))
        
        if len(intersections) == 2:
            segments.append(intersections)
            
    return segments

def analyze_circular_feature(segments):
    # Collect all points
    points = []
    for s in segments:
        points.append(s[0])
        points.append(s[1])
    
    if not points: return 0.0, 0.0
    
    pts = np.array(points)
    
    # Calculate bounding box center
    min_x, min_y = np.min(pts, axis=0)
    max_x, max_y = np.max(pts, axis=0)
    center = ((min_x + max_x)/2, (min_y + max_y)/2)
    
    # Calculate radii from center (assuming roughly circular)
    dists = np.sqrt((pts[:,0] - center[0])**2 + (pts[:,1] - center[1])**2)
    
    avg_radius = np.mean(dists)
    diameter = avg_radius * 2.0
    
    return diameter, len(segments)

def verify_fit(file_path, type_check):
    print(f"Verifying: {os.path.basename(file_path)} as {type_check}")
    v1, v2, v3 = read_stl_triangles(file_path)
    if v1 is None: return False

    if type_check == "BASE":
        # Check Socket at Z=2.0mm (Should be void)
        # This is tricky because the mesh is a lattice.
        # We need to find the INNERMOST hull near the center (radius ~20mm).
        # Or better: check if area at r < 20 is empty?
        # Simplified: Measure the bounding box of the central void.
        
        # Let's slice at Z=2.0
        segs = get_cross_section_segments(v1, v2, v3, 2.0)
        # Filter segments near the socket wall (radius ~20mm)
        socket_segs = []
        for s in segs:
            r1 = math.sqrt(s[0][0]**2 + s[0][1]**2)
            if r1 < 30.0 and r1 > 10.0: # Look for the 40.5mm hole
                socket_segs.append(s)
        
        diam, count = analyze_circular_feature(socket_segs)
        print(f"  Measured Socket ID: {diam:.2f}mm")
        
        if diam >= 40.4:
            print("  [PASS] Socket fits Shaft (>= 40.5mm).")
            return True
        else:
            print(f"  [FAIL] Socket too tight ({diam:.2f}mm < 40.5mm).")
            return False

    elif type_check == "SHAFT":
        # Check Plug at Z=1.0mm (Should be solid ring)
        segs = get_cross_section_segments(v1, v2, v3, 1.0)
        # Look for outer wall near r=20
        plug_segs = []
        for s in segs:
            r1 = math.sqrt(s[0][0]**2 + s[0][1]**2)
            if r1 < 22.0 and r1 > 18.0:
                plug_segs.append(s)
                
        diam, count = analyze_circular_feature(plug_segs)
        print(f"  Measured Plug OD: {diam:.2f}mm")
        
        if diam <= 40.1: # Tolerance
            print("  [PASS] Plug fits Base (<= 40.0mm).")
            return True
        else:
            print(f"  [FAIL] Plug too loose/tight logic mismatch. Measured {diam:.2f}.")
            return False

    elif type_check == "SHADE":
        # Check Mount Hole at Top
        # First find top Z
        all_z = np.concatenate((v1[:,2], v2[:,2], v3[:,2]))
        max_z = np.max(all_z)
        target_z = max_z - 2.0
        
        segs = get_cross_section_segments(v1, v2, v3, target_z)
        # Look for hole near r=21
        hole_segs = []
        for s in segs:
            r1 = math.sqrt(s[0][0]**2 + s[0][1]**2)
            if r1 < 25.0 and r1 > 15.0:
                hole_segs.append(s)
                
        diam, count = analyze_circular_feature(hole_segs)
        print(f"  Measured Mount Hole: {diam:.2f}mm")
        
        if diam >= 41.8:
            print("  [PASS] Mount fits Ring (>= 42.0mm).")
            return True
        else:
            print(f"  [FAIL] Mount Hole too small ({diam:.2f}mm).")
            return False

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: verify_interface_fit.py <file.stl> <BASE|SHAFT|SHADE>")
    else:
        verify_fit(sys.argv[1], sys.argv[2])
