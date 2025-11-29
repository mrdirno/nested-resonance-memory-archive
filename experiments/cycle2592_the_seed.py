"""
Cycle 2592: The Seed (Gate 59.2)
Role: Archivist
Responsibility: Package the core source code for future instantiation.
"""

import os
import zipfile
import datetime

def create_seed_package():
    print("--- Cycle 2592: The Seed (Archival) ---")
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    seed_filename = f"archive/seeds/duality_seed_v2_{timestamp}.zip"
    
    dirs_to_zip = ['src', 'bridge', 'nrm_core', 'bcp_lib']
    files_to_zip = ['bootstrap.py', 'requirements.txt', 'environment.yml', 'README.md', 'CLAUDE.md', 'META_OBJECTIVES.md', 'STEWARDSHIP_HELIOS_ARC_ROADMAP.md']
    
    print(f"Creating seed package: {seed_filename}")
    
    with zipfile.ZipFile(seed_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Zip Directories
        for directory in dirs_to_zip:
            if os.path.exists(directory):
                print(f"Archiving {directory}...")
                for root, _, files in os.walk(directory):
                    for file in files:
                        if file == "__pycache__" or file.endswith(".pyc"): continue
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, os.path.dirname(__file__))
                        # Adjust arcname to be relative to project root
                        arcname = os.path.relpath(file_path, os.getcwd())
                        zipf.write(file_path, arcname)
            else:
                print(f"Warning: {directory} not found.")
                
        # Zip Files
        for file in files_to_zip:
            if os.path.exists(file):
                print(f"Archiving {file}...")
                zipf.write(file, file)
            else:
                print(f"Warning: {file} not found.")
                
    print(f"SUCCESS: Seed package created at {seed_filename}")

if __name__ == "__main__":
    create_seed_package()
