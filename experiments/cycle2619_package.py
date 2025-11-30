#!/usr/bin/env python3
"""
Experiment: Cycle 2619 - The Package
Goal: Create a distributable archive of the system.
"""

import shutil
import tarfile
from pathlib import Path
import time

def create_package():
    print("Cycle 2619: The Package - Archiving Artifacts")
    
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    archive_name = f"HELIOS_ONE_RELEASE_{timestamp}"
    build_dir = Path("build_artifact")
    
    # Cleanup
    if build_dir.exists():
        shutil.rmtree(build_dir)
    build_dir.mkdir()
    
    # Copy Artifacts
    targets = [
        "experiments",
        "helios_one",
        "src"
    ]
    
    for t in targets:
        if Path(t).exists():
            print(f"  Copying {t}...")
            shutil.copytree(t, build_dir / t)
            
    # Create Tarball
    output_filename = f"{archive_name}.tar.gz"
    print(f"  Compressing to {output_filename}...")
    
    with tarfile.open(output_filename, "w:gz") as tar:
        tar.add(build_dir, arcname=archive_name)
        
    # Cleanup
    shutil.rmtree(build_dir)
    
    print(f"SUCCESS: Package created: {output_filename}")

if __name__ == "__main__":
    create_package()
