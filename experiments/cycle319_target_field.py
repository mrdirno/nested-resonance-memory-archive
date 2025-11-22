"""
CYCLE 319: Target Field Definition
Objective: Verify the functionality of the TargetField class.
"""
import sys
import os
import numpy as np

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from code.helios.target_field import TargetField

def run_test():
    print("CYCLE 319: TARGET FIELD DEFINITION")
    print("==================================")
    
    # 1. Instantiate TargetField
    resolution = (50, 50)
    tf = TargetField(resolution=resolution)
    print(f"Initialized TargetField with resolution {resolution}")
    
    # 2. Create Square Target
    center = (25, 25)
    size = 20
    tf.create_square(center, size)
    print(f"Created Square Target at {center} with size {size}")
    
    # 3. Visualize
    print("\n--- Target Visualization ---")
    print(tf.visualize())
    print("----------------------------")
    
    # 4. Verify Perfect Match
    perfect_density = tf.field.copy()
    error_perfect = tf.get_error(perfect_density)
    print(f"\nTest 1: Perfect Match Error = {error_perfect:.6f}")
    
    if error_perfect == 0.0:
        print(">> SUCCESS: Perfect match yields 0 error.")
    else:
        print(">> FAILURE: Perfect match error is not 0.")
        
    # 5. Verify Mismatch (Random Density)
    random_density = np.random.rand(*resolution)
    error_random = tf.get_error(random_density)
    print(f"Test 2: Random Density Error = {error_random:.6f}")
    
    if error_random > 0.0:
        print(">> SUCCESS: Random density yields positive error.")
    else:
        print(">> FAILURE: Random density error is 0.")
        
    # 6. Verify Mismatch (Empty Density)
    empty_density = np.zeros(resolution)
    error_empty = tf.get_error(empty_density)
    print(f"Test 3: Empty Density Error = {error_empty:.6f}")
    
    # Expected error calculation for empty density against the square
    # Square area = 20x20 = 400 pixels (approx, due to integer math)
    # Total pixels = 50x50 = 2500
    # Expected MSE = (Sum of (1-0)^2 for target pixels) / Total Pixels
    #              = 400 / 2500 = 0.16
    print(f"Expected Error ~ 0.16")
    
    if 0.1 < error_empty < 0.2:
        print(">> SUCCESS: Empty density error is within expected range.")
    else:
        print(">> FAILURE: Empty density error is unexpected.")

    # Final Conclusion
    if error_perfect == 0.0 and error_random > 0.0 and 0.1 < error_empty < 0.2:
        print("\n--- C319 Complete: TargetField Verified ---")
        return True
    else:
        print("\n--- C319 Failed ---")
        return False

if __name__ == "__main__":
    run_test()
