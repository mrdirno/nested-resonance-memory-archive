"""
Headless Verification Script (Gate 6)
Validates the Fabricator pipeline without a web server.
Direct Python API execution.
"""

import os
import sys
import time

# Ensure src is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.helios.fabricator import Fabricator

def run_headless_test():
    print("="*60)
    print("HEADLESS FABRICATION TEST (GATE 6)")
    print("="*60)
    
    # 1. Create Test Asset
    mesh_path = "data/headless_test.obj"
    print(f"Creating test asset: {mesh_path}")
    with open(mesh_path, "w") as f:
        f.write("v 0 0 0\nv 0.01 0 0\nv 0 0.01 0\nf 1 2 3\n")
        
    # 2. Initialize Fabricator (Virtual Mode)
    print("Initializing Fabricator (Virtual Mode)...")
    fab = Fabricator(virtual=True)
    
    # 3. Connect
    if not fab.connect():
        print("❌ Connection Failed")
        return False
    print("✅ Connected to Virtual Array")
        
    # 4. Materialize (The "Create Cube" equivalent)
    print("Executing Materialize Command...")
    start = time.time()
    fab.materialize(mesh_path, duration=2)
    elapsed = time.time() - start
    
    # 5. Cleanup
    fab.disconnect()
    if os.path.exists(mesh_path):
        os.remove(mesh_path)
        
    print(f"✅ Cycle Complete in {elapsed:.2f}s")
    return True

if __name__ == "__main__":
    success = run_headless_test()
    sys.exit(0 if success else 1)
