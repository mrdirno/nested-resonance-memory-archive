import trimesh
import sys
import os

def convert_stl_to_3mf(stl_path, output_path):
    print(f"Loading STL: {stl_path}")
    try:
        # Load the mesh
        mesh = trimesh.load(stl_path)
        
        if not isinstance(mesh, trimesh.Trimesh):
            # If it loaded a scene or something else, try to extract the geometry
            if hasattr(mesh, 'geometry') and len(mesh.geometry) > 0:
                # Grab the first geometry
                key = list(mesh.geometry.keys())[0]
                mesh = mesh.geometry[key]
            else:
                print("Error: Could not load valid geometry from STL.")
                sys.exit(1)

        print(f"Mesh loaded: {len(mesh.vertices)} vertices, {len(mesh.faces)} faces.")
        print(f"Exporting to 3MF: {output_path}")
        
        # Export using trimesh's built-in 3MF exporter
        mesh.export(output_path, file_type='3mf')
        print("Success.")
        
    except Exception as e:
        print(f"Error converting mesh: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 convert_to_3mf_trimesh.py <input_stl> <output_3mf>")
        sys.exit(1)
        
    convert_stl_to_3mf(sys.argv[1], sys.argv[2])
