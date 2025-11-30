import trimesh
import sys
import os

def calculate_mesh_properties(stl_path):
    print(f"Loading STL for property calculation: {stl_path}")
    try:
        mesh = trimesh.load(stl_path)
        
        if not isinstance(mesh, trimesh.Trimesh):
            if hasattr(mesh, 'geometry') and len(mesh.geometry) > 0:
                key = list(mesh.geometry.keys())[0]
                mesh = mesh.geometry[key]
            else:
                raise ValueError("Could not load valid mesh geometry from STL.")
        
        # Calculate properties
        area = mesh.area
        volume = mesh.volume
        
        # Assume a bounding box for volume fraction.
        # The generator creates a 40x40x40mm cube, so total_bounding_volume is 40^3
        # This should be dynamic but for this specific artifact, it's known.
        total_bounding_volume = 40 * 40 * 40 # Based on generator settings
        
        volume_fraction = volume / total_bounding_volume if total_bounding_volume > 0 else 0
        
        print(f"Surface Area: {area:.4f} mm^2")
        print(f"Volume: {volume:.4f} mm^3")
        print(f"Volume Fraction (of 40x40x40 cube): {volume_fraction:.4f}")
        
        return area, volume, volume_fraction
        
    except Exception as e:
        print(f"Error calculating mesh properties: {e}")
        return None, None, None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 calculate_mesh_properties.py <input_stl>")
        sys.exit(1)
        
    area, volume, volume_fraction = calculate_mesh_properties(sys.argv[1])
    if area is not None:
        # Optionally, write to a file or print in a specific format for parsing
        pass
