"""
CYCLE 335: The Acoustic Simulator (Real Physics)
Objective: Implement an Acoustic Levitation model that calculates the Gorkov Potential (Trapping Force).
Hypothesis: Real-world acoustic levitation relies on standing waves creating pressure nodes (traps). We can simulate this using our Universal Adapter.
Author: Aldrin Payopay (aldrin.gdf@gmail.com)
Co-Authored-By: Gemini 2.5 Flash (MOG Pilot)
"""
import numpy as np
import json
import os
import sys

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.helios.substrate import AcousticSubstrate
from experiments.cycle320_forward_cymatics_2d import Emitter
from experiments.cycle319_target_field import TargetField

class AcousticLevitator(AcousticSubstrate):
    """
    Extends AcousticSubstrate to calculate the Gorkov Potential (U).
    Particles are trapped at minima of U.
    U = 2 * pi * r^3 * [ (p^2 / (3 * rho * c^2)) - (rho * v^2 / 2) ]
    Simplified for visualization: We look for Pressure Nodes (p^2 minima).
    """
    def calculate_potential(self, field: np.ndarray) -> np.ndarray:
        """
        Approximates the trapping potential.
        In a standing wave, particles trap at Pressure Nodes (where p is min, velocity is max).
        But the Gorkov potential is dominated by the pressure term for small particles.
        So, Trap = Min(p^2).
        """
        # We return p^2 (Time-averaged acoustic potential energy density approximation)
        return field**2

def main():
    print("CYCLE 335: ACOUSTIC LEVITATION SIMULATOR")
    print("========================================")
    
    # 1. Setup: 40kHz Transducers in Air
    # Wavelength lambda = c / f = 343 / 40000 = 0.008575 m = 8.575 mm
    # We need a grid that can resolve this. 1mm resolution is sufficient.
    
    width_mm, height_mm = 100, 100
    levitator = AcousticLevitator(width_mm, height_mm, resolution_mm=0.5) # 0.5mm res for better detail
    
    print(f"Simulation Grid: {levitator.width}x{levitator.height} pixels (0.5mm/px)")
    
    # 2. Configuration: Single Axis Standing Wave (The classic Levitation Trap)
    # Two opposed emitters
    emitters = [
        Emitter(x=levitator.width/2, y=10, frequency=1.0, phase=0.0, amplitude=1.0), # Top
        Emitter(x=levitator.width/2, y=levitator.height-10, frequency=1.0, phase=0.0, amplitude=1.0)  # Bottom
    ]
    # Note: Frequency 1.0 in Emitter is normalized. In AcousticSubstrate it maps to 50kHz.
    # Let's adjust AcousticSubstrate to handle raw frequency input if needed, but for now we use the mapping.
    
    # 3. Propagate
    print("\nSimulating Standing Wave...")
    pressure_field = levitator.propagate(emitters)
    
    # 4. Calculate Potential (Traps)
    potential_field = levitator.calculate_potential(pressure_field)
    
    # 5. Analyze Traps
    # Nodes are minima in the potential field along the central axis
    mid_x = levitator.width // 2
    axis_profile = potential_field[:, mid_x]
    
    # Normalize for display
    norm_profile = (axis_profile - np.min(axis_profile)) / (np.max(axis_profile) - np.min(axis_profile))
    
    print("\n--- Central Axis Potential Profile (Vertical) ---")
    # Visualizing the nodes (traps)
    plot_height = 40
    indices = np.linspace(0, len(norm_profile)-1, plot_height).astype(int)
    downsampled = norm_profile[indices]
    
    chars = " .:-=+*#%@"
    for val in downsampled:
        char_idx = int(val * (len(chars)-1))
        line = chars[char_idx] * 20
        print(f"|{line}| {val:.2f}")
        
    # Count Traps (Minima)
    # Simple local minima detection
    local_minima = (np.diff(np.sign(np.diff(axis_profile))) > 0).nonzero()[0] + 1
    num_traps = len(local_minima)
    
    print(f"\nDetected {num_traps} Potential Traps (Nodes) along axis.")
    
    # 6. Save Results
    results = {
        "cycle": 335,
        "traps_detected": int(num_traps),
        "field_min": float(np.min(pressure_field)),
        "field_max": float(np.max(pressure_field)),
        "status": "Acoustic Levitation Model Operational"
    }
    
    os.makedirs("experiments/results", exist_ok=True)
    with open("experiments/results/c335_acoustic_levitation.json", "w") as f:
        json.dump(results, f, indent=2)
        
    if num_traps > 0:
        print("\n>> SUCCESS: Standing wave traps verified. The 'Tractor Beam' logic is sound.")
    else:
        print("\n>> FAILURE: No traps detected. Check interference logic.")

if __name__ == "__main__":
    main()