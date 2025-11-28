"""
Cycle 2476: The Spore (Gate 104)
Experiment: Colonization
Goal: Verify that a Spore can infect a dummy file.
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.mycelium.spore import Spore

def run_spore_experiment():
    print("--- CYCLE 2476: THE SPORE ---")
    
    # 1. Create a dummy file (The Host)
    host_path = Path("playground/host_file.py")
    host_path.parent.mkdir(exist_ok=True)
    with open(host_path, 'w') as f:
        f.write("print('I am a normal file.')\n")
        
    print(f"Created host: {host_path}")
    
    # 2. Create Spore (The Agent)
    spore = Spore(agent_id="Fungus-Alpha")
    
    # 3. Infect
    success = spore.infect(host_path)
    
    if success:
        print("Infection successful.")
        
        # 4. Verify
        if spore.check_infection(host_path):
            print("✅ SPORE DETECTED.")
            
            # Check content
            with open(host_path, 'r') as f:
                print("--- Host Content ---")
                print(f.read())
                print("--------------------")
        else:
            print("❌ SPORE NOT DETECTED.")
    else:
        print("❌ INFECTION FAILED.")

if __name__ == "__main__":
    run_spore_experiment()