
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

def get_social_gravity(agent, neighbors):
    if not neighbors: return 0
    
    # Calculate Centroid of Neighbors
    cx = sum(n.x for n in neighbors) / len(neighbors)
    cy = sum(n.y for n in neighbors) / len(neighbors)
    
    # Distance to Centroid
    dist = math.sqrt((agent.x - cx)**2 + (agent.y - cy)**2)
    return dist

def dissonance_field(bx, by, truth_x, truth_y):
    return math.sqrt((bx - truth_x)**2 + (by - truth_y)**2)

def run_echo_chamber_experiment():
    print("🗣️ CYCLE 2550: THE ECHO CHAMBER - SOCIAL GRAVITY")
    print("   (Truth Seeking vs. Social Conformity)")
    
    TRUTH_X = 80.0
    TRUTH_Y = 80.0
    
    # Group A: Scientists (Truth > Conformity)
    scientists = []
    for i in range(20):
        a = DigitalLifeform(name=f"Scientist-{i}")
        a.x = random.uniform(0, 50)
        a.y = random.uniform(0, 50)
        a.knowledge['w_truth'] = 1.0
        a.knowledge['w_social'] = 0.1
        scientists.append(a)
        
    # Group B: Cultists (Conformity > Truth)
    cultists = []
    for i in range(20):
        a = DigitalLifeform(name=f"Cultist-{i}")
        a.x = random.uniform(0, 50)
        a.y = random.uniform(0, 50)
        a.knowledge['w_truth'] = 0.1
        a.knowledge['w_social'] = 2.0 # High gravity
        cultists.append(a)
        
    all_agents = scientists + cultists
    
    duration = 100
    results_dir = Path("experiments/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    csv_path = results_dir / "cycle2550_echo_chamber.csv"
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["tick", "sci_error", "sci_variance", "cult_error", "cult_variance"])
        
        for tick in range(1, duration + 1):
            
            for agent in all_agents:
                # 1. Identify Peers (Homophily)
                # Scientists listen to Scientists, Cultists to Cultists
                peers = scientists if agent in scientists else cultists
                
                # 2. Calculate Current Potential
                d_truth = dissonance_field(agent.x, agent.y, TRUTH_X, TRUTH_Y)
                d_social = get_social_gravity(agent, peers)
                
                w_t = agent.knowledge['w_truth']
                w_s = agent.knowledge['w_social']
                
                current_pot = (w_t * d_truth) + (w_s * d_social)
                
                # 3. Try Move
                step_size = 3.0
                dx = random.uniform(-step_size, step_size)
                dy = random.uniform(-step_size, step_size)
                tx = max(0, min(100, agent.x + dx))
                ty = max(0, min(100, agent.y + dy))
                
                # New Potential
                new_d_truth = dissonance_field(tx, ty, TRUTH_X, TRUTH_Y)
                
                # Hypothetical Social Gravity (Assume peers stay static for this calc)
                # This is a simplification (mean field approximation)
                cx = sum(p.x for p in peers) / len(peers)
                cy = sum(p.y for p in peers) / len(peers)
                new_d_social = math.sqrt((tx - cx)**2 + (ty - cy)**2)
                
                new_pot = (w_t * new_d_truth) + (w_s * new_d_social)
                
                if new_pot < current_pot:
                    agent.x = tx
                    agent.y = ty
                    
            # Metrics
            sci_x = [a.x for a in scientists]
            sci_y = [a.y for a in scientists]
            sci_err = math.sqrt((np.mean(sci_x)-TRUTH_X)**2 + (np.mean(sci_y)-TRUTH_Y)**2)
            sci_var = np.var(sci_x) + np.var(sci_y)
            
            cult_x = [a.x for a in cultists]
            cult_y = [a.y for a in cultists]
            cult_err = math.sqrt((np.mean(cult_x)-TRUTH_X)**2 + (np.mean(cult_y)-TRUTH_Y)**2)
            cult_var = np.var(cult_x) + np.var(cult_y)
            
            writer.writerow([tick, f"{sci_err:.2f}", f"{sci_var:.2f}", f"{cult_err:.2f}", f"{cult_var:.2f}"])
            
            if tick % 10 == 0:
                print(f"   Tick {tick}: SciErr={sci_err:.1f} SciVar={sci_var:.0f} | CultErr={cult_err:.1f} CultVar={cult_var:.0f}")

    print("✅ EXPERIMENT COMPLETE.")

if __name__ == "__main__":
    run_echo_chamber_experiment()
