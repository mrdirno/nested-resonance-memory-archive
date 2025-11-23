import sys
import os
import numpy as np
import json

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.helios.operator import UniversalOperator

def run_cycle398():
    print("Cycle 398: RF-to-Acoustic Bridge")
    print("--------------------------------")
    
    obj_path = os.path.abspath("rf_sculpture.obj")
    if not os.path.exists(obj_path):
        print(f"Error: {obj_path} not found.")
        return

    print(f"Loading RF Sculpture from: {obj_path}")
    
    # Initialize Operator
    # Disable GPU for reliability in this test, or enable if confident.
    # The system seems to support CPU fallback.
    operator = UniversalOperator(resolution_mm=6.0, use_gpu=False) 
    # Increased resolution_mm to 6.0 to reduce voxel count
    
    try:
        # Create Object
        # Scale to 40mm to fit nicely and reduce points
        print("Compiling Matter Configuration...")
        obj_id, num_voxels = operator.create_from_file(obj_path, scale_mm=40.0)
        
        print(f"Compilation Complete.")
        print(f"Object ID: {obj_id}")
        print(f"Voxels/Traps: {num_voxels}")
        
        # Analyze Stability
        print("Analyzing Trap Stability...")
        
        # DEBUG: Inspect targets
        targets = operator.active_objects[obj_id]['targets']
        print(f"First 3 targets: {targets[:3]}")
        
        stability = operator.get_stability(obj_id)
        print(f"Stability Index (Gorkov Potential): {stability:.6e}")
        
        # DEBUG: Check if stability is exactly zero
        if stability == 0.0:
            print("WARNING: Stability is exactly 0.0. Checking potential field...")
            # Manually access box to check potential
            operator.box.update_emitters(operator.emitters) # Ensure emitters are updated
            field = operator.box.propagate(operator.emitters)
            potential = operator.box.calculate_gorkov_potential(field)
            print(f"Potential Field Max: {np.max(potential)}")
            print(f"Potential Field Min: {np.min(potential)}")
            print(f"Potential Field Shape: {potential.shape}")
        
        # Verification
        if stability < 0:
            print("RESULT: STABLE TRAP CONFIRMED.")
            print("The Radio Field has been physically instantiated.")
        else:
            print("RESULT: UNSTABLE.")
            print("Refinement required.")
            
        # Save Results
        results = {
            "cycle": 398,
            "object_id": obj_id,
            "voxels": num_voxels,
            "stability": stability,
            "status": "SUCCESS" if stability < 0 else "FAILURE"
        }
        
        with open("experiments/cycle398_results.json", "w") as f:
            json.dump(results, f, indent=2)
            
    except Exception as e:
        print(f"Error during compilation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_cycle398()
