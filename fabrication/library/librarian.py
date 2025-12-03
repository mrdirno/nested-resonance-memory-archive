import os
import sys
import json
import re
import ast

def extract_metadata(file_path):
    with open(file_path, 'r') as f:
        content = f.read()
        
    metadata = {
        "logic": "Unknown",
        "method": "Unknown",
        "standard": "Unknown",
        "dims": {},
        "resolution": 0
    }
    
    # Extract Docstring info
    # Looking for lines like "# Logic: ..."
    logic_match = re.search(r'# Logic:\s*(.*)', content)
    if logic_match: metadata["logic"] = logic_match.group(1).strip()
    
    method_match = re.search(r'# Method:\s*(.*)', content)
    if method_match: metadata["method"] = method_match.group(1).strip()
    
    std_match = re.search(r'# Standard:\s*(.*)', content)
    if std_match: metadata["standard"] = std_match.group(1).strip()
    
    # Parse generate function args
    try:
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name.startswith("generate_"):
                # Get default args
                args = node.args.args
                defaults = node.args.defaults
                # defaults correspond to the last n args
                offset = len(args) - len(defaults)
                for i, default in enumerate(defaults):
                    arg_name = args[offset + i].arg
                    if isinstance(default, (ast.Constant, ast.Num, ast.Str)): # python 3.8+
                        val = default.value if isinstance(default, ast.Constant) else (default.n if isinstance(default, ast.Num) else default.s)
                        if arg_name in ["diameter", "height", "resolution", "hole_diameter"]:
                            metadata["dims"][arg_name] = val
                            if arg_name == "resolution": metadata["resolution"] = val
    except Exception as e:
        print(f"Error parsing AST for {file_path}: {e}")
        
    return metadata

def compile_library():
    base_path = "fabrication/furniture"
    library = {
        "meta": {
            "version": "2.0",
            "system": "HELIOS",
            "cycle": 2690
        },
        "series": {}
    }
    
    # Walk directory
    series_dirs = sorted([d for d in os.listdir(base_path) if d.startswith("lamp_series_")])
    
    for s_dir in series_dirs:
        s_path = os.path.join(base_path, s_dir)
        if not os.path.isdir(s_path): continue
        
        library["series"][s_dir] = {}
        
        designs = sorted([d for d in os.listdir(s_path) if not d.startswith('.')])
        
        for design in designs:
            d_path = os.path.join(s_path, design)
            if not os.path.isdir(d_path): continue
            
            # Extract Design ID and Name
            # e.g. 01_redshift
            parts = design.split('_')
            if len(parts) > 1 and parts[0].isdigit():
                design_id = parts[0]
                design_name = "_".join(parts[1:])
            else:
                design_id = "XX"
                design_name = design
            
            design_entry = {
                "id": design_id,
                "name": design_name,
                "path": d_path,
                "components": {}
            }
            
            # Find generators
            gen_files = [f for f in os.listdir(d_path) if f.endswith("_gen.py")]
            
            for gf in gen_files:
                comp_type = "unknown"
                if "shade" in gf: comp_type = "shade"
                elif "base" in gf: comp_type = "base"
                elif "shaft" in gf: comp_type = "shaft"
                
                meta = extract_metadata(os.path.join(d_path, gf))
                design_entry["components"][comp_type] = {
                    "file": gf,
                    "metadata": meta
                }
            
            library["series"][s_dir][design] = design_entry
            print(f"Indexed {design}")

    # Save JSON
    with open("fabrication/library/HELIOS_LIBRARY_V2.json", "w") as f:
        json.dump(library, f, indent=2)
    
    print("Library Compilation Complete.")

if __name__ == "__main__":
    compile_library()
