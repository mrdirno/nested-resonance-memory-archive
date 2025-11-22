"""
CYCLE 326: Material Physics (Viscosity & Thresholds)
Objective: Demonstrate that non-linear material properties (Viscosity, Thresholding) 
can recover sharp geometric shapes from soft interference patterns.
"""
import numpy as np
import json
import os
import sys
import scipy.ndimage

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from code.helios.target_field import TargetField

class ViscousField:
    """
    Simulates a field with viscosity (diffusion).
    Equation: dU/dt = nu * Laplacian(U)
    """
    def __init__(self, width, height, viscosity=0.1):
        self.width = width
        self.height = height
        self.viscosity = viscosity
        
    def apply(self, field, iterations=10):
        """Apply diffusion smoothing."""
        result = field.copy()
        for _ in range(iterations):
            # Simple Gaussian blur approximates diffusion over time
            # Sigma relates to sqrt(2 * viscosity * time)
            # We'll use a small sigma per step or just one big blur
            # Let's use explicit gaussian filter for stability
            result = scipy.ndimage.gaussian_filter(result, sigma=self.viscosity)
        return result

class ThresholdMatter:
    """
    Simulates a material that changes state based on a threshold.
    """
    def __init__(self, threshold=0.5, sharpness=10.0):
        self.threshold = threshold
        self.sharpness = sharpness # For sigmoid
        
    def apply_hard(self, field):
        """Binary Step Function (0 or 1)."""
        return (field > self.threshold).astype(float)
        
    def apply_sigmoid(self, field):
        """Continuous Sigmoid Transition."""
        # 1 / (1 + exp(-k * (x - x0)))
        return 1.0 / (1.0 + np.exp(-self.sharpness * (field - self.threshold)))

def generate_soft_square(width, height):
    """
    Generates a 'soft' square (like a blurry interference pattern).
    """
    y, x = np.mgrid[0:height, 0:width]
    
    # Center
    cx, cy = width // 2, height // 2
    size = width // 4
    
    # Create a perfect square
    perfect_square = np.zeros((height, width))
    perfect_square[cy-size:cy+size, cx-size:cx+size] = 1.0
    
    # Blur it heavily to simulate wave interference / diffraction limits
    soft_square = scipy.ndimage.gaussian_filter(perfect_square, sigma=5.0)
    
    # Add some wave-like noise (ringing)
    noise = 0.1 * np.sin(x * 0.5) * np.sin(y * 0.5)
    soft_square += noise
    
    # Normalize
    soft_square = np.clip(soft_square, 0.0, 1.0)
    
    return perfect_square, soft_square

def main():
    print("CYCLE 326: MATERIAL PHYSICS (VISCOSITY & THRESHOLDS)")
    print("====================================================")
    
    width, height = 128, 128
    
    # 1. Generate Data
    print("Generating 'Soft' Interference Pattern...")
    target_data, soft_input = generate_soft_square(width, height)
    
    target = TargetField(width, height)
    target.field = target_data
    
    # Calculate Initial Error
    initial_error = target.calculate_error(soft_input)
    print(f"Initial 'Soft' Error: {initial_error:.6f}")
    
    # 2. Apply Viscosity (Smoothing)
    print("\nApplying Viscosity (Diffusion)...")
    viscous_physics = ViscousField(width, height, viscosity=1.0)
    smoothed_field = viscous_physics.apply(soft_input, iterations=1)
    
    smooth_error = target.calculate_error(smoothed_field)
    print(f"Smoothed Error: {smooth_error:.6f} (May increase MSE due to blurring, but reduces noise)")
    
    # 3. Apply Thresholding (Sharpening)
    print("\nApplying Thresholding (Phase Transition)...")
    matter_physics = ThresholdMatter(threshold=0.5)
    
    # Hard Threshold
    hard_field = matter_physics.apply_hard(smoothed_field)
    hard_error = target.calculate_error(hard_field)
    print(f"Hard Threshold Error: {hard_error:.6f}")
    
    # 4. Results Analysis
    print("\n--- Results ---")
    print(f"Soft Input Error:   {initial_error:.6f}")
    print(f"Hard Output Error:  {hard_error:.6f}")
    improvement = (initial_error - hard_error) / initial_error * 100
    print(f"Improvement:        {improvement:.2f}%")
    
    # 5. Visualization (ASCII)
    print("\nVisualizing Center Slice (Row 64):")
    row = 64
    print("Target: ", "".join(["#" if x > 0.5 else "." for x in target.field[row, 32:96:2]]))
    print("Soft:   ", "".join(["#" if x > 0.5 else "." for x in soft_input[row, 32:96:2]]))
    print("Hard:   ", "".join(["#" if x > 0.5 else "." for x in hard_field[row, 32:96:2]]))
    
    # 6. Save Results
    results = {
        "cycle": 326,
        "initial_error": initial_error,
        "hard_error": hard_error,
        "improvement_percent": improvement,
        "physics": "Viscosity + Thresholding"
    }
    
    os.makedirs("experiments/results", exist_ok=True)
    with open("experiments/results/c326_material_physics.json", "w") as f:
        json.dump(results, f, indent=2)
        
    if hard_error < 0.05:
        print("\n>> SUCCESS: Material Physics successfully recovered the sharp geometry.")
    else:
        print("\n>> RESULT: Improvement observed, but error remains high.")

if __name__ == "__main__":
    main()
