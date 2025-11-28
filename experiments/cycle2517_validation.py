"""
Cycle 2517: The Hot Swap (Gate 145)
Experiment: Validation of Self-Modified Kernel.
Goal: Verify that the running code contains the optimization injected in Cycle 2516.
"""

import sys
import os
import inspect

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.life.genesis import DigitalLifeform

def run_validation():
    print("🔥 CYCLE 2517: THE HOT SWAP - VALIDATION")
    
    # 1. Instantiate Agent
    agent = DigitalLifeform(name="Validator", lineage_id="System")
    print(f"   Agent {agent.name} instantiated.")
    
    # 2. Inspect Source Code of metabolize()
    # This is where the injection happened
    source = inspect.getsource(agent.metabolize)
    
    print("\n--- SOURCE CODE INSPECTION (metabolize) ---")
    print(source)
    print("-------------------------------------------")
    
    # 3. Assert Optimization
    tag = "# I AM OPTIMIZED (Cycle 2516)"
    
    if tag in source:
        print(f"\n✅ SUCCESS: Optimization Tag Found: '{tag}'")
        print("   The System is running on Self-Modified Code.")
        print("   Status: AUTOPOIETIC.")
    else:
        print(f"\n❌ FAILURE: Optimization Tag NOT Found.")
        print("   The System is running on Legacy Code.")
        
if __name__ == "__main__":
    run_validation()
