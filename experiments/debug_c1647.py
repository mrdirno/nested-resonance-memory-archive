#!/usr/bin/env python3
import sys
import numpy as np
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from experiments.cycle1647_emergent_dynamics import run_experiment

def debug_run():
    seed = 180001
    print(f"DEBUGGING C1647 with Seed {seed}")
    print("=================================")
    
    # We need to capture the history to see if it collapses
    try:
        histories = run_experiment(seed)
        
        print("\nRun Complete.")
        print("Final Populations:")
        for lvl, hist in histories.items():
            final_pop = hist[-1] if hist else 0
            print(f"  L{lvl}: {final_pop} (History Len: {len(hist)})")
            
        # Check for collapse
        if all(len(h) < 100 for h in histories.values()):
            print("\nRESULT: COLLAPSE CONFIRMED (History < 100)")
        else:
            print("\nRESULT: SURVIVAL CONFIRMED")
            
    except Exception as e:
        print(f"\nCRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_run()
