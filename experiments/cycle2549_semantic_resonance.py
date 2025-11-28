
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
from src.life.ecosystem import Ecosystem

def dissonance_field(bx, by, truth_x, truth_y):
    """
    Calculates Cognitive Dissonance (Potential).
    Lower is better.
    """
    # Euclidean distance to Truth
    return math.sqrt((bx - truth_x)**2 + (by - truth_y)**2)

def run_semantic_experiment():
    print("🧠 CYCLE 2549: THE THOUGHT FORM - SEMANTIC RESONANCE")
    print("   (Self-Correction of Beliefs towards Truth)")
    
    # 1. Setup Truth (The Target Concept)
    TRUTH_X = 75.0 # e.g., High Liberty
    TRUTH_Y = 25.0 # e.g., Moderate Tradition
    print(f"🌟 Absolute Truth located at ({TRUTH_X}, {TRUTH_Y})")
    
    # 2. Spawn Thinkers (Random Beliefs)
    thinkers = []
    for i in range(50):
        agent = DigitalLifeform(name=f"Thinker-{i}")
        # Beliefs mapped to Spatial Coordinates 0-100
        agent.x = random.uniform(0, 100) 
        agent.y = random.uniform(0, 100)
        agent.energy = 100
        thinkers.append(agent)
        
    duration = 100
    results_dir = Path("experiments/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    csv_path = results_dir / "cycle2549_semantic_resonance.csv"
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["tick", "avg_dissonance", "converged_count", "consensus_variance"])
        
        for tick in range(1, duration + 1):
            total_dissonance = 0
            converged_count = 0
            
            bx_list = []
            by_list = []
            
            for agent in thinkers:
                # 1. Sense Dissonance (Current)
                current_diss = dissonance_field(agent.x, agent.y, TRUTH_X, TRUTH_Y)
                
                # 2. Consider "Changing Mind" (Random Perturbation)
                # Exploration step
                step_size = 2.0
                test_dx = random.uniform(-step_size, step_size)
                test_dy = random.uniform(-step_size, step_size)
                
                test_x = max(0, min(100, agent.x + test_dx))
                test_y = max(0, min(100, agent.y + test_dy))
                
                new_diss = dissonance_field(test_x, test_y, TRUTH_X, TRUTH_Y)
                
                # 3. Update Belief if Dissonance is Reduced (Gradient Descent)
                if new_diss < current_diss:
                    agent.x = test_x
                    agent.y = test_y
                    current_diss = new_diss
                    
                total_dissonance += current_diss
                if current_diss < 5.0: converged_count += 1
                
                bx_list.append(agent.x)
                by_list.append(agent.y)
                
            avg_diss = total_dissonance / len(thinkers)
            variance = np.var(bx_list) + np.var(by_list)
            
            writer.writerow([tick, f"{avg_diss:.2f}", converged_count, f"{variance:.2f}"])
            
            if tick % 10 == 0:
                print(f"   Tick {tick}: AvgDissonance={avg_diss:.2f} Enlightened={converged_count}/50 Var={variance:.0f}")
                
            if converged_count == len(thinkers):
                print("✨ ENLIGHTENMENT ACHIEVED.")
                break

    print("✅ EXPERIMENT COMPLETE.")

if __name__ == "__main__":
    run_semantic_experiment()
