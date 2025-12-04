import os
import sys
import glob
import subprocess

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

def convert_stl_to_3mf(stl_path):
    if not stl_path.endswith(".stl"):
        return
    
    base_name = os.path.splitext(stl_path)[0]
    output_path = base_name + ".3mf"
    
    if os.path.exists(output_path):
        print(f"Skipping existing: {output_path}")
        return

    print(f"Converting: {stl_path} -> {output_path}")
    
    # Use the existing conversion script
    # Path: fabrication/scripts/convert_to_3mf_trimesh.py
    # Current: fabrication/practical_design/FAVORITES/children/generators/
    converter_script = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../scripts/convert_to_3mf_trimesh.py"))
    
    # FORCE USE OF VENV PYTHON
    # The project has a venv at .venv (seen in initial ls)
    # We must use THAT python executable to have access to libraries
    venv_python = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../../.venv/bin/python3"))
    
    if not os.path.exists(venv_python):
         print(f"ERROR: Virtual environment python not found at {venv_python}")
         return

    cmd = [venv_python, converter_script, stl_path, output_path]
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error converting {stl_path}: {e}")

def batch_convert_children():
    children_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
    stl_files = sorted(glob.glob(os.path.join(children_dir, "child_*.stl")))
    
    print(f"Found {len(stl_files)} STL files in {children_dir}")
    
    for stl_file in stl_files:
        convert_stl_to_3mf(stl_file)

if __name__ == "__main__":
    batch_convert_children()