"""
Cycle 2593: Seed Verification (Post-Hibernation)
Goal: Verify that the archived seed can be rehydrated and is functional.
"""

import sys
import os
import zipfile
import shutil
import importlib.util

# Path to the specific seed found in the previous step
SEED_PATH = "archive/seeds/duality_seed_v2_20251129_125249.zip"
EXTRACT_DIR = "temp_wake_test"

def verify_seed():
    print(f"--- Cycle 2593: Seed Verification ---")
    print(f"Target Seed: {SEED_PATH}")
    
    if not os.path.exists(SEED_PATH):
        print("FAILURE: Seed file not found.")
        return

    # 1. Extract
    print(f"Extracting to {EXTRACT_DIR}...")
    if os.path.exists(EXTRACT_DIR):
        shutil.rmtree(EXTRACT_DIR)
    os.makedirs(EXTRACT_DIR)
    
    try:
        with zipfile.ZipFile(SEED_PATH, 'r') as zip_ref:
            zip_ref.extractall(EXTRACT_DIR)
    except zipfile.BadZipFile:
        print("FAILURE: Corrupt ZIP file.")
        return

    # 2. Validate File Structure
    required_files = [
        'bootstrap.py',
        'src/life/genesis.py',
        'src/life/ecosystem.py',
        'bridge/transcendental_bridge.py',
        'META_OBJECTIVES.md'
    ]
    
    missing = []
    for f in required_files:
        if not os.path.exists(os.path.join(EXTRACT_DIR, f)):
            missing.append(f)
            
    if missing:
        print(f"FAILURE: Missing files: {missing}")
        return
    else:
        print("Structure Check: PASS")

    # 3. Functional Test (Dry Run)
    # Try to import DigitalLifeform from the extracted source
    print("Attempting Import Test...")
    
    # Modify sys.path to include extracted src
    sys.path.insert(0, os.path.abspath(EXTRACT_DIR))
    
    try:
        from src.life.genesis import DigitalLifeform
        print("Import DigitalLifeform: SUCCESS")
        
        agent = DigitalLifeform(name="Lazarus")
        print(f"Instantiated Agent: {agent.name}, Energy: {agent.energy}")
        
        if agent.alive:
            print("Agent State: ALIVE")
        else:
            print("Agent State: DEAD")
            
    except Exception as e:
        print(f"FAILURE: Import/Runtime Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup path
        sys.path.pop(0)

    # 4. Cleanup
    print("Cleaning up...")
    shutil.rmtree(EXTRACT_DIR)
    print("SUCCESS: Seed Verification Complete.")

if __name__ == "__main__":
    verify_seed()
