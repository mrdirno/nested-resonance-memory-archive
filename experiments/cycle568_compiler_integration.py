
import sys
import os
import numpy as np

# Add root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from nrm_core.helios.operator import UniversalOperator

def run_test():
    print("Cycle 568: Integration Test")
    
    # 1. Initialize Operator (which inits Compiler)
    operator = UniversalOperator(use_gpu=True)
    print("Operator Initialized.")
    
    # 2. Create Object with Material
    print("Creating Cube (Styrofoam)...")
    try:
        # Using default material
        obj_id = operator.create_object("cube", (50, 50, 50), material="Styrofoam")
        print(f"Object Created: ID {obj_id}")
        
        # Check stability
        stab = operator.get_stability(obj_id)
        print(f"Stability Index: {stab}")
        
        if stab < 0:
            print("SUCCESS: Stability is negative (Trapping Potential).")
        else:
            print("WARNING: Stability is positive (Repulsive). Check optimization.")
            
    except Exception as e:
        print(f"FAILURE: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_test()
