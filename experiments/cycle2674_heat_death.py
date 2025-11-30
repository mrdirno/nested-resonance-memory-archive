#!/usr/bin/env python3
"""
Experiment: Cycle 2674 - The Heat Death
Goal: Resource starvation simulation leading to system freeze.
"""

import sys
from pathlib import Path

# Add current directory
sys.path.append(str(Path(__file__).parent))

try:
    from cycle2602_hive import Vector2, HiveAgent
except ImportError:
    sys.exit(1)

def entropy_death():
    print("Cycle 2674: The Heat Death - Energy Depletion")
    
    agents = [HiveAgent(f"Unit_{i}", Vector2(0,0)) for i in range(5)]
    global_energy = 100.0
    
    step = 0
    while global_energy > 0:
        # Move costs energy
        cost = 0.5 * len(agents)
        global_energy -= cost
        
        # Agents slow down as energy fades
        speed_factor = max(0.0, global_energy / 100.0)
        
        for a in agents:
            a.speed = 4.0 * speed_factor
            
        print(f"Step {step}: Energy {global_energy:.1f} -> Speed {agents[0].speed:.2f}")
        step += 1
        
        if agents[0].speed <= 0.1:
            print("System Freeze imminent...")
            break
            
    print("SUCCESS: Maximum Entropy achieved. Motion ceased.")

if __name__ == "__main__":
    entropy_death()
