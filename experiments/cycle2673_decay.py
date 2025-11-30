#!/usr/bin/env python3
"""
Experiment: Cycle 2673 - The Decay
Goal: Degrade sensor accuracy over time.
"""

import sys
import random
from pathlib import Path

# Add current directory
sys.path.append(str(Path(__file__).parent))

try:
    from cycle2602_hive import Vector2, HiveAgent
except ImportError:
    sys.exit(1)

def run_decay_simulation():
    print("Cycle 2673: The Decay - Sensor Degradation")
    
    agent = HiveAgent("Old-Timer", Vector2(0,0))
    true_target = Vector2(50, 50)
    
    steps = 5
    noise_level = 0.0
    
    for i in range(steps):
        noise_level += 5.0 # Increase noise each step
        
        # Simulate noisy sensor reading
        noise = Vector2(random.uniform(-noise_level, noise_level), random.uniform(-noise_level, noise_level))
        perceived_target = true_target + noise
        
        error = ((perceived_target.x - true_target.x)**2 + (perceived_target.y - true_target.y)**2)**0.5
        
        print(f"Step {i}: Noise Level {noise_level:.1f} -> Error: {error:.2f}")
        
    if error > 20.0:
        print("SUCCESS: Sensors significantly degraded.")
    else:
        print("FAILURE: Sensors too robust.")
        sys.exit(1)

if __name__ == "__main__":
    run_decay_simulation()
