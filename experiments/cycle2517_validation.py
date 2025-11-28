"""
Cycle 2517: The Hot Swap (Gate 145)
Experiment: Validation of Self-Modified Code.
Goal: Ensure the new kernel is functional and contains the optimization tag.
"""

import sys
import os
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.life.genesis import DigitalLifeform
from src.life.ecosystem import Ecosystem

def run_validation_experiment():
    print("🔄 CYCLE 2517: THE HOT SWAP - VALIDATION")
    
    # Setup Ecosystem
    env = Ecosystem(capacity=10, prey_capacity=10, predator_capacity=0)
    
    # Seed 1 Agent
    agent = DigitalLifeform(name="Eve-Optimized")
    env.add_agent(agent)
    
    # Check for optimization tag in runtime
    # We need to inspect the source code of the running object method?
    # Or just trust the file read.
    
    # Let's read the file again to be sure
    with open('src/life/genesis.py', 'r') as f:
        source = f.read()
        if "I AM OPTIMIZED" in source:
            print("   [VERIFIED] Optimization tag found in genesis.py.")
        else:
            print("   [FAILED] Optimization tag missing.")
            
    # Run a few ticks to ensure stability
    print("   Running stability check...")
    try:
        env.run(steps=10)
        print("   [VERIFIED] Ecosystem stable.")
    except Exception as e:
        print(f"   [FAILED] Ecosystem crashed: {e}")
        
    print("✅ EXPERIMENT COMPLETE.")

if __name__ == "__main__":
    run_validation_experiment()
