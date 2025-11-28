
import sys
import os
import csv
import time
import random
import math
import numpy as np
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class Resonator:
    def __init__(self, name, natural_freq, hopping=False):
        self.name = name
        self.natural_freq = natural_freq
        self.hopping = hopping
        self.energy = 0.0
        self.t = 0.0
        
    def update(self, input_signal, dt):
        self.t += dt
        
        # Frequency Hopping
        current_f = self.natural_freq
        if self.hopping:
            # Hop every 1.0s
            if int(self.t) % 2 == 0:
                current_f = self.natural_freq + 5.0
            else:
                current_f = self.natural_freq - 5.0
                
        # Resonance Physics (Simple Harmonic Oscillator)
        # Energy increases if Input matches Current Freq
        # E += |Input * sin(current_f * t)|
        # This is basically correlation
        
        # Attack Signal assumed to be sin(attack_f * t)
        # We check alignment
        
        # Let's simulate amplitude growth directly
        # driven harmonic oscillator: x'' + 2z w x' + w^2 x = F(t)
        # If F(t) resonates with w, x explodes.
        
        # Simplified: Energy += Coupling * InputAmplitude
        # Coupling = 1 / (1 + |f_sys - f_in|) (Lorentzian)
        
        # Input is a sum of frequencies? Assume input is a single frequency attack
        attack_f = 10.0 # Attacker targets the known base frequency
        coupling = 1.0 / (1.0 + 10.0 * abs(current_f - attack_f))
        
        input_amp = 1.0 # Attack strength
        
        # Energy Accumulation
        self.energy += coupling * input_amp * dt
        
        # Dissipation (Natural Damping)
        self.energy *= 0.99 

def run_shield_experiment():
    print("🛡️ CYCLE 2566: THE SHIELD - RESONANT DEFENSE")
    print("   (Frequency Hopping vs. Targeted Attack)")
    
    static_sys = Resonator("Static", 10.0, hopping=False)
    agile_sys = Resonator("Agile", 10.0, hopping=True)
    
    dt = 0.1
    duration = 1000 # steps
    
    results_dir = Path("experiments/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    csv_path = results_dir / "cycle2566_the_shield.csv"
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["tick", "static_energy", "agile_energy"])
        
        for i in range(duration):
            static_sys.update(1.0, dt)
            agile_sys.update(1.0, dt)
            
            writer.writerow([i, f"{static_sys.energy:.2f}", f"{agile_sys.energy:.2f}"])
            
            if i % 100 == 0:
                print(f"   Tick {i}: StaticE={static_sys.energy:.2f} AgileE={agile_sys.energy:.2f}")
                
            if static_sys.energy > 5.0:
                # print("⚠️ STATIC SYSTEM OVERLOAD.")
                pass

    print("✅ EXPERIMENT COMPLETE.")

if __name__ == "__main__":
    run_shield_experiment()
