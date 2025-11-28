
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

from src.life.genesis import DigitalLifeform

class Citizen(DigitalLifeform):
    def __init__(self, name, intent_freq):
        super().__init__(name=name)
        self.intent_freq = intent_freq
        
    def act_legal(self):
        # Action intensity ~ Frequency
        return self.intent_freq

def run_law_experiment():
    print("⚖️ CYCLE 2562: JURISPRUDENCE - THE LOW PASS FILTER")
    print("   (Law as Noise Reduction)")
    
    citizens = []
    # Law Abiding (Low Freq)
    for i in range(15):
        citizens.append(Citizen(f"Good-{i}", random.uniform(1, 10)))
        
    # Criminals (High Freq)
    for i in range(5):
        citizens.append(Citizen(f"Bad-{i}", random.uniform(50, 100)))
        
    police_capacity = 200.0 # Total Damping Power
    
    duration = 50
    results_dir = Path("experiments/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    csv_path = results_dir / "cycle2562_jurisprudence.csv"
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["tick", "total_noise", "crimes_committed", "police_load"])
        
        for tick in range(1, duration + 1):
            total_noise = 0
            crimes = 0
            damping_used = 0
            
            for c in citizens:
                action = c.act_legal()
                
                # Law: Limit actions > 20 Hz
                if action > 20.0:
                    # Crime Detected!
                    # Police attempt to damp
                    cost = action * 0.5 # Energy to stop crime
                    if police_capacity >= cost:
                        police_capacity -= cost
                        damping_used += cost
                        # Crime prevented? Or just punished?
                        # Let's say Damped = Mitigated.
                        total_noise += 20.0 # Reduced to limit
                    else:
                        # Police overwhelmed
                        crimes += 1
                        total_noise += action
                else:
                    total_noise += action
                    
            # Police Recharge
            police_capacity += 50.0
            police_capacity = min(police_capacity, 500.0)
            
            writer.writerow([tick, f"{total_noise:.1f}", crimes, f"{police_capacity:.1f}"])
            
            if tick % 10 == 0:
                print(f"   Tick {tick}: Noise={total_noise:.0f} Crimes={crimes} PoliceCap={police_capacity:.0f}")

    print("✅ EXPERIMENT COMPLETE.")

if __name__ == "__main__":
    run_law_experiment()
