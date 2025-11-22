"""
CYCLE 330: The Universal Physics Adapter
Objective: Validate the SubstrateInterface by running two different physics engines (NRM and Acoustic) through the same API.
Hypothesis: The adapter correctly encapsulates the physical differences (wave speed, damping, scale).
Author: Aldrin Payopay (aldrin.gdf@gmail.com)
Co-Authored-By: Gemini 2.5 Flash (MOG Pilot)
"""
import numpy as np
import json
import os
import sys

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from code.helios.substrate import NRMSubstrate, AcousticSubstrate
from experiments.cycle320_forward_cymatics_2d import Emitter
from experiments.cycle319_target_field import TargetField

def test_substrate(substrate, name):
    print(f"\n--- Testing {name} Substrate ---")
    props = substrate.get_properties()
    print(f"Properties: {props}")
    
    # Create standard emitters
    # Center, and Offset
    w, h = substrate.width, substrate.height
    emitters = [
        Emitter(w/2, h/2, frequency=0.5, phase=0.0, amplitude=1.0),
        Emitter(w/4, h/2, frequency=0.5, phase=np.pi, amplitude=1.0)
    ]
    
    print(f"Propagating 2 Emitters on {w}x{h} grid...")
    field = substrate.propagate(emitters)
    
    print(f"Field Stats: Min={np.min(field):.4f}, Max={np.max(field):.4f}, Mean={np.mean(field):.4f}")
    
    # Visualize (Center Slice)
    mid_y = h // 2
    slice_data = field[mid_y, :]
    
    # Simple ASCII plot of the slice
    # Normalize slice to 0-1 for plotting
    norm_slice = (slice_data - np.min(slice_data)) / (np.max(slice_data) - np.min(slice_data) + 1e-9)
    
    plot_width = 60
    # Downsample slice to plot width
    indices = np.linspace(0, len(norm_slice)-1, plot_width).astype(int)
    downsampled = norm_slice[indices]
    
    print(f"Center Slice ({name}):")
    chars = " .:-=+*#%@"
    line = ""
    for val in downsampled:
        char_idx = int(val * (len(chars)-1))
        line += chars[char_idx]
    print(f"[{line}]")
    
    return props, np.std(field)

def main():
    print("CYCLE 330: UNIVERSAL PHYSICS ADAPTER TEST")
    print("=========================================")
    
    # 1. Test NRM (Abstract/Slow)
    nrm = NRMSubstrate(width=64, height=64)
    nrm_props, nrm_std = test_substrate(nrm, "NRM")
    
    # 2. Test Acoustic (Real/Fast)
    # 100mm x 100mm grid, 1mm resolution -> 100x100 pixels
    acoustic = AcousticSubstrate(width_mm=100, height_mm=100, resolution_mm=1)
    ac_props, ac_std = test_substrate(acoustic, "Acoustic")
    
    # Validation Logic
    # Acoustic field should have much higher frequency components (more ripples) due to real-world scale vs speed
    # NRM is normalized 0-1, Acoustic is raw pressure. 
    
    success = True
    if nrm_props['v'] != 1.0: success = False
    if ac_props['v'] != 343.0: success = False
    
    print("\n--- Comparison ---")
    print(f"NRM Speed: {nrm_props['v']}, Damping: {nrm_props['gamma']}")
    print(f"Acoustic Speed: {ac_props['v']}, Damping: {ac_props['gamma']}")
    
    # Save Results
    results = {
        "cycle": 330,
        "nrm": nrm_props,
        "acoustic": ac_props,
        "success": success
    }
    
    os.makedirs("experiments/results", exist_ok=True)
    with open("experiments/results/c330_universal_adapter.json", "w") as f:
        json.dump(results, f, indent=2)
        
    if success:
        print("\n>> SUCCESS: Universal Adapter correctly instantiated distinct physical models.")
        print("   The Solver can now speak to Air as easily as it speaks to Simulation.")
    else:
        print("\n>> FAILURE: Adapter properties incorrect.")

if __name__ == "__main__":
    main()
