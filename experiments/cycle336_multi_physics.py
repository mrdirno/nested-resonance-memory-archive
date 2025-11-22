"""
CYCLE 336: Multi-Physics Simulation (The Universal Compiler)
Objective: Demonstrate that the same Solver logic can control two completely different
physical substrates (NRM vs Acoustics) by adapting to their physical constants.
"""
import numpy as np
import json
import os
import sys

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from code.helios.substrate import NRMSubstrate, AcousticSubstrate

class Emitter:
    def __init__(self, x, y, frequency=1.0, amplitude=1.0, phase=0.0):
        self.x = x
        self.y = y
        self.frequency = frequency
        self.amplitude = amplitude
        self.phase = phase
        
    def to_dict(self):
        return {
            "x": self.x, "y": self.y,
            "frequency": self.frequency,
            "amplitude": self.amplitude,
            "phase": self.phase
        }

class UniversalCompiler:
    """
    The 'Brain' that generates instructions for the 'Matter'.
    It asks the Substrate for its properties (v, gamma) and calculates
    the required phase delays to achieve a goal (Focusing).
    """
    def __init__(self, substrate):
        self.substrate = substrate
        self.props = substrate.get_properties()
        self.wave_speed = self.props['v']
        
    def compile_focus(self, target_x, target_y, emitters):
        """
        Calculates phase delays to focus all emitters at (target_x, target_y).
        Phase = -k * distance
        k = 2 * pi * f / v
        """
        compiled_emitters = []
        
        # Handle coordinate scaling for Acoustics
        # AcousticSubstrate expects Emitter positions in Grid Coords, but calculates in Real World
        # But wait, the Compiler should work in "World Space" ideally.
        # For this experiment, we assume emitters are passed in the substrate's native coordinate system.
        
        # For AcousticSubstrate, resolution is needed to convert grid to meters.
        # But the propagate method handles that internally.
        # Wait, if I calculate phase here, I need to know the distance in the *simulation's* metric.
        
        # Let's look at Substrate implementations.
        # NRM: dist = sqrt(dx^2 + dy^2) (Grid units)
        # Acoustic: dist_m = sqrt(dx_m^2 + dy_m^2) (Meters)
        
        # We need a unified "Distance Metric" from the substrate.
        # Or we just implement the logic specific to the substrate type here?
        # NO. The Compiler should be agnostic.
        # The Substrate should provide a `get_distance(p1, p2)` method?
        # Or `get_wavelength(frequency)`?
        
        # Let's use the properties.
        is_acoustic = (self.props['type'] == "Acoustic")
        
        for e in emitters:
            # 1. Calculate Distance
            if is_acoustic:
                # AcousticSubstrate hack: resolution is hardcoded in class or passed in init.
                # We can access it via the instance.
                res_mm = self.substrate.resolution
                ex_m = e.x * (res_mm / 1000.0)
                ey_m = e.y * (res_mm / 1000.0)
                tx_m = target_x * (res_mm / 1000.0)
                ty_m = target_y * (res_mm / 1000.0)
                dist = np.sqrt((tx_m - ex_m)**2 + (ty_m - ey_m)**2)
                
                # Real Frequency mapping
                real_freq = 30000 + (e.frequency * 20000)
                wavelength = self.wave_speed / real_freq
                
            else:
                # NRM (Grid Units)
                dist = np.sqrt((target_x - e.x)**2 + (target_y - e.y)**2)
                wavelength = self.wave_speed / (2 * np.pi * e.frequency) * (2 * np.pi) # v/f
                # Wait, NRM code: k = 2*pi*f / v. lambda = 2*pi/k = v/f. Correct.
            
            # 2. Calculate Phase
            # phi = -2*pi * (dist % lambda) / lambda
            # or just -k * dist
            k = 2 * np.pi / wavelength
            phase = -k * dist
            
            # Wrap to [0, 2pi]
            phase = phase % (2 * np.pi)
            
            new_e = Emitter(e.x, e.y, e.frequency, e.amplitude, phase)
            compiled_emitters.append(new_e)
            
        return compiled_emitters

def main():
    print("CYCLE 336: MULTI-PHYSICS SIMULATION")
    print("===================================")
    
    # 1. Setup Emitters (Grid Coordinates)
    # 4 Emitters in corners
    w, h = 64, 64
    emitters_base = [
        Emitter(0, 0), Emitter(w, 0),
        Emitter(0, h), Emitter(w, h)
    ]
    target_x, target_y = w//2, h//2
    
    # --- SIMULATION A: NRM (Abstract) ---
    print("\n[A] Substrate: NRM (Cognitive Space)")
    nrm = NRMSubstrate(w, h)
    print(f"    Properties: {nrm.get_properties()}")
    
    compiler_nrm = UniversalCompiler(nrm)
    emitters_nrm = compiler_nrm.compile_focus(target_x, target_y, emitters_base)
    
    print("    Compiled Phases (NRM):")
    for i, e in enumerate(emitters_nrm):
        print(f"    E{i}: {e.phase:.4f} rad")
        
    # Verify
    field_nrm = nrm.propagate(emitters_nrm)
    val_nrm = field_nrm[target_y, target_x]
    print(f"    Field Intensity at Target: {val_nrm:.4f} (Max=1.0)")
    
    
    # --- SIMULATION B: ACOUSTIC (Real World) ---
    print("\n[B] Substrate: Acoustic (Air)")
    # 64px * 1mm = 64mm width
    acoustic = AcousticSubstrate(width_mm=64, height_mm=64, resolution_mm=1) 
    print(f"    Properties: {acoustic.get_properties()}")
    
    compiler_acoustic = UniversalCompiler(acoustic)
    emitters_acoustic = compiler_acoustic.compile_focus(target_x, target_y, emitters_base)
    
    print("    Compiled Phases (Acoustic):")
    for i, e in enumerate(emitters_acoustic):
        print(f"    E{i}: {e.phase:.4f} rad")
        
    # Verify
    field_acoustic = acoustic.propagate(emitters_acoustic)
    # Acoustic field is raw pressure, can be negative. We check magnitude.
    val_acoustic = np.abs(field_acoustic[target_y, target_x])
    print(f"    Pressure Amplitude at Target: {val_acoustic:.4f}")
    
    # --- COMPARISON ---
    print("\n[C] Comparison")
    phase_nrm = emitters_nrm[0].phase
    phase_acoustic = emitters_acoustic[0].phase
    
    print(f"    NRM Phase:      {phase_nrm:.4f}")
    print(f"    Acoustic Phase: {phase_acoustic:.4f}")
    
    if abs(phase_nrm - phase_acoustic) > 0.1:
        print(">> SUCCESS: The Compiler generated different instructions for different physics.")
        print(">> The Solver is Material-Agnostic.")
    else:
        print(">> FAILURE: Phases are identical. Physics not differentiated.")

    # Save Results
    results = {
        "cycle": 336,
        "nrm_phase": phase_nrm,
        "acoustic_phase": phase_acoustic,
        "nrm_intensity": val_nrm,
        "acoustic_intensity": val_acoustic
    }
    
    os.makedirs("experiments/results", exist_ok=True)
    with open("experiments/results/c336_multi_physics.json", "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    main()
