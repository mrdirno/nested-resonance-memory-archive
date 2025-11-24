"""
Cycle 491: Vector Test
Role: The Math Teacher
Responsibility: Verify vector arithmetic.
"""
import sys
import os

sys.path.append(os.getcwd())
from nrm_core.vector import Vector

def run_experiment():
    print("Cycle 491: Vector Class Test")
    print("============================")
    
    v1 = Vector([1, 0, 0])
    v2 = Vector([0, 1, 0])
    v3 = Vector([1, 1, 0])
    
    print(f"v1: {v1}")
    print(f"v2: {v2}")
    print(f"v3: {v3}")
    
    # Dot Product
    dot = v1.dot(v2)
    print(f"v1 . v2 = {dot} (Expected 0.0)")
    
    # Magnitude
    mag = v3.magnitude
    print(f"|v3| = {mag:.4f} (Expected 1.4142)")
    
    # Cosine Similarity
    sim = v1.cosine_similarity(v3)
    print(f"Cos(v1, v3) = {sim:.4f} (Expected 0.7071)")
    
    # Addition
    v_sum = v1 + v2
    print(f"v1 + v2 = {v_sum} (Expected [1.0, 1.0, 0.0])")
    
    if abs(sim - 0.7071) < 0.001:
        print("SUCCESS: Vector math is correct.")
    else:
        print("FAIL: Math error.")

if __name__ == "__main__":
    run_experiment()
