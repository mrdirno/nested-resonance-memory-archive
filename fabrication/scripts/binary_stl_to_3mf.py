import struct
import sys
import os
import zipfile
import io

# 3MF Boilerplate
CONTENT_TYPES = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<Types xmlns=\"http://schemas.openxmlformats.org/package/2006/content-types\">\n <Default Extension=\"rels\" ContentType=\"application/vnd.openxmlformats-package.relationships+xml\"/>\n <Default Extension=\"model\" ContentType=\"application/vnd.ms-package.3dmanufacturing-3dmodel+xml\"/>\n</Types>\n"

RELS = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<Relationships xmlns=\"http://schemas.openxmlformats.org/package/2006/relationships\">\n <Relationship Target=\"/3D/3dmodel.model\" Id=\"rel0\" Type=\"http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel\"/>\n</Relationships>\n"

MODEL_HEADER = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<model unit=\"millimeter\" xml:lang=\"en-US\" xmlns=\"http://schemas.microsoft.com/3dmanufacturing/core/2015/02\">\n <resources>\n  <object id=\"1\" type=\"model\">\n   <mesh>\n    <vertices>\n"

def convert_binary_stl_to_3mf(stl_path, output_3mf_path):
    print(f"Converting {os.path.basename(stl_path)} to 3MF...")
    
    if not os.path.exists(stl_path):
        print("Error: Input file not found.")
        return

    # Data structures for mesh
    unique_vertices = {} # Map (x,y,z) -> index
    vertices_list = [] # Ordered list of (x,y,z) for XML writing
    triangles = [] # List of (v1,v2,v3) indices

    # Read STL
    try:
        with open(stl_path, 'rb') as f:
            header = f.read(80)
            count_bytes = f.read(4)
            num_triangles = struct.unpack('<I', count_bytes)[0]
            print(f"  Source Triangles: {num_triangles}")
            
            # Batch read for speed? 50 bytes per tri.
            # 2.6M tris = 130MB. We can read it all into RAM.
            
            chunk_size = 10000
            
            for _ in range(0, num_triangles, chunk_size):
                batch = f.read(50 * chunk_size)
                if not batch: break
                
                num_in_batch = len(batch) // 50
                
                for i in range(num_in_batch):
                    offset = i * 50
                    # Skip normal (12 bytes), read 3 vertices (36 bytes)
                    # Vertices start at offset 12
                    v_data = struct.unpack_from('<9f', batch, offset + 12)
                    
                    # v1
                    v1_key = (v_data[0], v_data[1], v_data[2])
                    if v1_key not in unique_vertices:
                        unique_vertices[v1_key] = len(vertices_list)
                        vertices_list.append(v1_key)
                    idx1 = unique_vertices[v1_key]
                    
                    # v2
                    v2_key = (v_data[3], v_data[4], v_data[5])
                    if v2_key not in unique_vertices:
                        unique_vertices[v2_key] = len(vertices_list)
                        vertices_list.append(v2_key)
                    idx2 = unique_vertices[v2_key]
                    
                    # v3
                    v3_key = (v_data[6], v_data[7], v_data[8])
                    if v3_key not in unique_vertices:
                        unique_vertices[v3_key] = len(vertices_list)
                        vertices_list.append(v3_key)
                    idx3 = unique_vertices[v3_key]
                    
                    triangles.append((idx1, idx2, idx3))
                    
    except Exception as e:
        print(f"  Error reading STL: {e}")
        return

    print(f"  Unique Vertices: {len(vertices_list)}")
    print("  Generating XML...")

    # Generate Model XML
    # Using StringIO for buffering might be heavy for 100MB string.
    # Better to write to a temp file, then zip that file.
    
    temp_xml_path = output_3mf_path + ".model.xml"
    
    with open(temp_xml_path, 'w') as f:
        f.write(MODEL_HEADER)
        
        # Write Vertices
        for v in vertices_list:
            f.write(f'<vertex x="{v[0]:.4f}" y="{v[1]:.4f}" z="{v[2]:.4f}" />\n')
            
        f.write('    </vertices>\n    <triangles>\n')
        
        # Write Triangles
        for t in triangles:
            f.write(f'<triangle v1="{t[0]}" v2="{t[1]}" v3="{t[2]}" />\n')
            
        f.write('    </triangles>\n   </mesh>\n  </object>\n </resources>\n <build>\n  <item objectid="1" />\n </build>\n</model>')

    print("  Zipping to 3MF...")
    
    with zipfile.ZipFile(output_3mf_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", CONTENT_TYPES)
        zf.writestr("_rels/.rels", RELS)
        zf.write(temp_xml_path, "3D/3dmodel.model")
        
    os.remove(temp_xml_path)
    
    # Stats
    stl_size = os.path.getsize(stl_path)
    mf_size = os.path.getsize(output_3mf_path)
    print(f"  Done. STL: {stl_size/1024/1024:.1f}MB -> 3MF: {mf_size/1024/1024:.1f}MB ({(1-mf_size/stl_size)*100:.1f}% reduction)")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 binary_stl_to_3mf.py <input.stl> <output.3mf>")
    else:
        convert_binary_stl_to_3mf(sys.argv[1], sys.argv[2])
