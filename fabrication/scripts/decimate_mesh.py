import trimesh
import sys
import os
import time
import numpy as np

def main():
    if len(sys.argv) < 2:
        print("Usage: python decimate_mesh.py <input_stl_path> [target_faces]")
        sys.exit(1)

    input_path = sys.argv[1]
    target_faces = int(sys.argv[2]) if len(sys.argv) > 2 else 850000

    print(f"Loading {input_path}...")
    start_time = time.time()
    try:
        mesh = trimesh.load(input_path)
    except Exception as e:
        print(f"Error loading mesh: {e}")
        sys.exit(1)
    
    print(f"Loaded in {time.time() - start_time:.2f}s")
    original_faces = len(mesh.faces)
    print(f"Original: {original_faces} faces, {len(mesh.vertices)} vertices")
    print(f"Is watertight: {mesh.is_watertight}")
    
    if original_faces <= target_faces:
        print(f"Mesh already has fewer faces ({original_faces}) than target ({target_faces}). Just converting to binary if needed.")
        simplified = mesh
    else:
        print(f"Targeting {target_faces} faces (Reduction: {100 - (target_faces/original_faces)*100:.1f}%)")

        try:
            print("Attempting decimation using pyfqmr...")
            import pyfqmr
            mesh_simplifier = pyfqmr.Simplify()
            
            verts = mesh.vertices
            faces = mesh.faces
            
            mesh_simplifier.setMesh(verts, faces)
            # preserve_border=False allows reducing open edges, which might be necessary if the mesh has many tiny holes
            mesh_simplifier.simplify_mesh(target_count=target_faces, preserve_border=False, verbose=10)
            
            new_verts, new_faces, new_normals = mesh_simplifier.getMesh()
            
            simplified = trimesh.Trimesh(vertices=new_verts, faces=new_faces, vertex_normals=new_normals)
            print("pyfqmr decimation successful.")
            
        except Exception as e:
            print(f"pyfqmr failed: {e}")
            simplified = mesh

    if simplified is not None:
        print("Performing final cleanup...")
        # simplified.fix_normals() # lightweight
        
        print(f"Result: {len(simplified.faces)} faces, {len(simplified.vertices)} vertices")
        print(f"Result watertight: {simplified.is_watertight}")
        
        dir_name, file_name = os.path.split(input_path)
        name_root, ext = os.path.splitext(file_name)
        name_root = name_root.replace("_ascii_medium", "").replace("_ascii", "")
        
        output_name = f"{name_root}_optimized.stl" 
        output_path = os.path.join(dir_name, output_name)
        
        print(f"Saving to {output_path} (Binary STL)...")
        simplified.export(output_path)
        print("Done.")
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()