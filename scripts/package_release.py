"""
Cycle 2433: Deployment Packaging (Gate 61)
Role: The Release Engineer
Responsibility: Bundle the system for distribution.
Logic:
1. Create a `release/` directory.
2. Copy `nrm_core/` (The Physics Engine).
3. Copy `src/helios/` (The UI/Control).
4. Copy `FPGA/bitstreams/` (The Hardware Logic).
5. Copy `README.md` and `FINAL_REPORT.md`.
6. Create a zip archive `DUALITY_ZERO_V2_RELEASE.zip`.
"""

import os
import shutil
import datetime

def package_release():
    print("Cycle 2433: Deployment Packaging")
    print("================================")
    
    release_dir = "release_build"
    if os.path.exists(release_dir):
        shutil.rmtree(release_dir)
    os.makedirs(release_dir)
    
    print(f"Created build directory: {release_dir}")
    
    # Define artifacts to copy
    artifacts = [
        ("nrm_core", "nrm_core"),
        ("src/helios", "helios"),
        ("FPGA/bitstreams", "fpga_bitstreams"),
        ("README.md", "README.md"),
        ("FINAL_REPORT.md", "FINAL_REPORT.md"),
        ("LICENSE", "LICENSE") # Assuming LICENSE exists, if not we skip
    ]
    
    for src, dst in artifacts:
        src_path = os.path.abspath(src)
        dst_path = os.path.join(release_dir, dst)
        
        if os.path.exists(src_path):
            if os.path.isdir(src_path):
                shutil.copytree(src_path, dst_path)
                print(f"Copied directory: {src} -> {dst}")
            else:
                shutil.copy2(src_path, dst_path)
                print(f"Copied file: {src} -> {dst}")
        else:
            print(f"WARNING: Artifact not found: {src}")
            
    # Create Release Notes
    with open(os.path.join(release_dir, "RELEASE_NOTES.txt"), "w") as f:
        f.write(f"DUALITY-ZERO V2 RELEASE\n")
        f.write(f"Date: {datetime.datetime.now()}\n")
        f.write(f"Status: SYSTEM COMPLETE\n")
        f.write(f"Includes: Physics Core, Helios UI, FPGA Bitstreams.\n")
        
    print("Created RELEASE_NOTES.txt")
    
    # Zip it
    shutil.make_archive("DUALITY_ZERO_V2_RELEASE", 'zip', release_dir)
    print(f"SUCCESS: Created DUALITY_ZERO_V2_RELEASE.zip")
    
    # Cleanup
    shutil.rmtree(release_dir)
    print("Cleaned up build directory.")
    
    return True

if __name__ == "__main__":
    package_release()
