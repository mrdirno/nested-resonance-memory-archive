import sys
import os
import uuid
from zipfile import ZipFile

# XML Templates
HEADER = """<?xml version="1.0" encoding="UTF-8"?>
<model unit="millimeter" xml:lang="en-US" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" xmlns:BambuStudio="http://schemas.bambulab.com/package/2021" xmlns:p="http://schemas.microsoft.com/3dmanufacturing/production/2015/06" requiredextensions="p">
 <metadata name="Application">OrcaSlicer</metadata>
 <resources>
  <object id="1" type="model">
   <mesh>
    <vertices>
"""

MIDDLE = """    </vertices>
    <triangles>
"""

FOOTER = """    </triangles>
   </mesh>
  </object>
 </resources>
 <build>
  <item objectid="1" transform="1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"/>
 </build>
</model>
"""

def parse_stl_and_generate_xml(stl_path, output_xml_path):
    print(f"Processing {stl_path}...")
    
    vertices = [] # List of (x,y,z) tuples
    unique_verts = {} # Map "x,y,z" string to index
    triangles = [] # List of (v1, v2, v3) indices
    
    with open(stl_path, 'r') as f:
        current_face_verts = []
        for line in f:
            line = line.strip()
            if line.startswith("vertex"):
                parts = line.split()
                # vertex x y z
                x, y, z = parts[1], parts[2], parts[3]
                key = f"{x},{y},{z}"
                
                if key not in unique_verts:
                    unique_verts[key] = len(vertices)
                    vertices.append((x, y, z))
                
                current_face_verts.append(unique_verts[key])
                
            elif line.startswith("endloop"):
                if len(current_face_verts) == 3:
                    triangles.append(tuple(current_face_verts))
                current_face_verts = []

    print(f"Found {len(vertices)} vertices and {len(triangles)} triangles.")
    
    # Write XML
    with open(output_xml_path, 'w') as f:
        f.write(HEADER)
        
        # Write Vertices
        for v in vertices:
            f.write(f'     <vertex x="{v[0]}" y="{v[1]}" z="{v[2]}" />\n')
            
        f.write(MIDDLE)
        
        # Write Triangles
        for t in triangles:
            f.write(f'     <triangle v1="{t[0]}" v2="{t[1]}" v3="{t[2]}" />\n')
            
        f.write(FOOTER)
    
    print(f"XML generated at {output_xml_path}")

def update_3mf(template_dir, stl_path, output_3mf_path):
    # 1. Generate new 3dmodel.model
    model_path = os.path.join(template_dir, "3D/3dmodel.model")
    parse_stl_and_generate_xml(stl_path, model_path)
    
    # 2. Zip it up
    print(f"Creating 3MF archive at {output_3mf_path}...")
    with ZipFile(output_3mf_path, 'w') as zipf:
        for root, dirs, files in os.walk(template_dir):
            for file in files:
                file_path = os.path.join(root, file)
                # Arcname should be relative to template_dir
                arcname = os.path.relpath(file_path, template_dir)
                zipf.write(file_path, arcname)
                
    print("Done.")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python stl_to_3mf.py <template_dir> <input_stl> <output_3mf>")
        sys.exit(1)
        
    update_3mf(sys.argv[1], sys.argv[2], sys.argv[3])
