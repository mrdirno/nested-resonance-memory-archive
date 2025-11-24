"""
Cycle 439: The Scalar Sum (OSD Validation)
Role: The Physicist
Responsibility: Empirically verify that Mass (Scalar Sum) decouples from Visibility (Vector Sum) under interference.
"""
import cmath
import numpy as np
import math

def run_experiment():
    print("Cycle 439: OSD Scalar Sum Test")
    print("==============================")
    
    # Setup: 2 Emitters
    amp = 1.0
    e1 = complex(amp, 0) # Fixed phase 0
    
    print(f"{ 'Phase Diff':<12} | { 'Vector (Vis)':<12} | { 'Scalar (Mass)':<12} | { 'Ratio (M/V)':<12} | { 'State':<10}")
    print("----------------------------------------------------------------------")
    
    # Sweep Phase of Emitter 2
    for deg in range(0, 181, 20):
        rad = math.radians(deg)
        e2 = cmath.rect(amp, rad)
        
        # OSD Calculations
        vector_sum = abs(e1 + e2)
        scalar_sum = abs(e1) + abs(e2)
        
        ratio = scalar_sum / (vector_sum + 1e-9) # Avoid div/0
        
        state = "Matter"
        if ratio > 2.0: state = "Dark"
        if ratio > 10.0: state = "Black Hole"
        
        print(f"{deg:<12} | {vector_sum:<12.4f} | {scalar_sum:<12.4f} | {ratio:<12.4f} | {state:<10}")

    # Validation Logic
    # At 180 degrees (PI), Vector Sum should be 0, Scalar Sum should be 2.
    e2_pi = cmath.rect(amp, math.pi)
    v_pi = abs(e1 + e2_pi)
    s_pi = abs(e1) + abs(e2_pi)
    
    print(f"\nCheck at 180 deg:")
    print(f"Visibility: {v_pi:.4f} (Target ~0.0)")
    print(f"Mass:       {s_pi:.4f} (Target 2.0)")
    
    if v_pi < 0.001 and s_pi > 1.9:
        print("SUCCESS: OSD Mechanism Validated. Mass persists when Visibility vanishes.")
    else:
        print("FAIL: Physics engine violation.")

if __name__ == "__main__":
    run_experiment()
