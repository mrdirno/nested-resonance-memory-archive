"""
Cycle 2594: The Bootloader (Gate 60.1)
Goal: Re-initialize system from seed in a clean environment (HELIOS-ONE).
"""

import sys
import os
import zipfile
import shutil
import json

# Define Paths
SEED_PATH = "archive/seeds/duality_seed_v2_20251129_125249.zip"
HELIOS_ROOT = "helios_one"

def bootloader():
    print("--- Cycle 2594: The Bootloader (HELIOS-ONE) ---")
    
    if not os.path.exists(SEED_PATH):
        print("CRITICAL FAILURE: Seed not found.")
        return

    # 1. Prepare Clean Environment
    print(f"Provisioning {HELIOS_ROOT}...")
    if os.path.exists(HELIOS_ROOT):
        shutil.rmtree(HELIOS_ROOT)
    os.makedirs(HELIOS_ROOT)
    
    # 2. Extract Seed
    print("Extracting Seed...")
    with zipfile.ZipFile(SEED_PATH, 'r') as zip_ref:
        zip_ref.extractall(HELIOS_ROOT)
        
    # 3. Initialize System
    print("Bootstrapping System...")
    sys.path.insert(0, os.path.abspath(HELIOS_ROOT))
    
    try:
        from src.life.ecosystem import Ecosystem
        from src.life.genesis import DigitalLifeform
        
        print("Core Modules Loaded.")
        
        # Initialize New World
        env = Ecosystem(capacity=50)
        print("Ecosystem Initialized.")
        
        # Check for Migrants (Lineage Persistence)
        migrants_file = "archive/artifacts/migrants.jsonl"
        migrant_count = 0
        if os.path.exists(migrants_file):
            print("Found Migrant Manifest. Attempting Re-instantiation...")
            with open(migrants_file, 'r') as f:
                for line in f:
                    try:
                        data = json.loads(line)
                        agent = DigitalLifeform.deserialize(data)
                        # Reset position for new world
                        agent.x = 0
                        agent.y = 0
                        env.add_agent(agent)
                        migrant_count += 1
                    except Exception as e:
                        print(f"Failed to load migrant: {e}")
                        
        if migrant_count > 0:
            print(f"SUCCESS: {migrant_count} Ancients have returned.")
        else:
            print("WARNING: No migrants found. Seeding new Adam/Eve.")
            env.add_agent(DigitalLifeform(name="Helios-Adam"))
            env.add_agent(DigitalLifeform(name="Helios-Eve"))
            
        # Run Simulation
        print("Running Simulation (Tick 1-5)...")
        env.run(steps=5)
        
        if len(env.agents) > 0:
            print("SUCCESS: HELIOS-ONE is stable.")
        else:
            print("FAILURE: Extinction on boot.")
            
    except Exception as e:
        print(f"CRITICAL BOOT ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        sys.path.pop(0)

if __name__ == "__main__":
    bootloader()
