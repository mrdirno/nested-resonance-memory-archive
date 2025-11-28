
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
    cx = sum(n.x for n in neighbors) / len(neighbors)
    cy = sum(n.y for n in neighbors) / len(neighbors)
    return math.sqrt((agent.x - cx)**2 + (agent.y - cy)**2)

def dissonance_field(bx, by, truth_x, truth_y):
    return math.sqrt((bx - truth_x)**2 + (by - truth_y)**2)

def run_paradigm_experiment():
    print("🌌 CYCLE 2551: THE PARADIGM SHIFT - ADAPTATION TEST")
    print("   (Moving Truth vs. Static Beliefs)")
    
    TRUTH_X = 20.0
    TRUTH_Y = 20.0
    
    scientists = []
    for i in range(20):
        a = DigitalLifeform(name=f"Scientist-{i}")
        a.x, a.y = 20, 20 # Start near Old Truth
        a.energy = 100
        a.knowledge['w_truth'] = 1.0
        a.knowledge['w_social'] = 0.1
        scientists.append(a)
        
    cultists = []
    for i in range(20):
        a = DigitalLifeform(name=f"Cultist-{i}")
        a.x, a.y = 20, 20 # Start near Old Truth
        a.energy = 100
        a.knowledge['w_truth'] = 0.1
        a.knowledge['w_social'] = 5.0 # Extreme conformity
        cultists.append(a)
        
    all_agents = scientists + cultists
    
    duration = 100
    results_dir = Path("experiments/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    csv_path = results_dir / "cycle2551_paradigm_shift.csv"
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["tick", "truth_pos", "sci_error", "sci_pop", "cult_error", "cult_pop"])
        
        for tick in range(1, duration + 1):
            
            # GRADUAL SHIFT (The Drift)
            if tick > 20 and TRUTH_X < 80:
                TRUTH_X += 1.0
                TRUTH_Y += 1.0
                if tick % 10 == 0:
                    print(f"⚠️  TRUTH DRIFTING -> ({TRUTH_X}, {TRUTH_Y})")
                
            for agent in all_agents:
                if not agent.alive: continue
                
                peers = scientists if agent in scientists else cultists
                alive_peers = [p for p in peers if p.alive]
                
                current_diss = dissonance_field(agent.x, agent.y, TRUTH_X, TRUTH_Y)
                
                # Reality Check (Damage from Falsehood)
                # If far from Truth, lose energy
                damage = current_diss * 0.1
                agent.energy -= damage
                if agent.energy <= 0:
                    agent.alive = False
                    # print(f"💀 {agent.name} died of Delusion.")
                    continue
                    
                # Movement Logic
                d_truth = current_diss
                d_social = get_social_gravity(agent, alive_peers)
                
                w_t = agent.knowledge['w_truth']
                w_s = agent.knowledge['w_social']
                
                current_pot = (w_t * d_truth) + (w_s * d_social)
                
                # Try Move
                step_size = 5.0
                dx = random.uniform(-step_size, step_size)
                dy = random.uniform(-step_size, step_size)
                tx = max(0, min(100, agent.x + dx))
                ty = max(0, min(100, agent.y + dy))
                
                new_diss = dissonance_field(tx, ty, TRUTH_X, TRUTH_Y)
                
                cx = sum(p.x for p in alive_peers) / len(alive_peers) if alive_peers else tx
                cy = sum(p.y for p in alive_peers) / len(alive_peers) if alive_peers else ty
                new_social = math.sqrt((tx - cx)**2 + (ty - cy)**2)
                
                new_pot = (w_t * new_diss) + (w_s * new_social)
                
                if new_pot < current_pot:
                    agent.x = tx
                    agent.y = ty
                    agent.energy += 2.0 # Reward for updating? Or just less damage?
                    # Let's give a small regen to survivors
                    
            # Metrics
            alive_sci = [a for a in scientists if a.alive]
            alive_cult = [a for a in cultists if a.alive]
            
            s_err = math.sqrt((np.mean([a.x for a in alive_sci])-TRUTH_X)**2 + (np.mean([a.y for a in alive_sci])-TRUTH_Y)**2) if alive_sci else 0
            c_err = math.sqrt((np.mean([a.x for a in alive_cult])-TRUTH_X)**2 + (np.mean([a.y for a in alive_cult])-TRUTH_Y)**2) if alive_cult else 0
            
            writer.writerow([tick, f"{TRUTH_X}|{TRUTH_Y}", f"{s_err:.1f}", len(alive_sci), f"{c_err:.1f}", len(alive_cult)])
            
            if tick % 10 == 0:
                print(f"   Tick {tick}: Truth=({TRUTH_X},{TRUTH_Y}) SciPop={len(alive_sci)} (Err {s_err:.0f}) | CultPop={len(alive_cult)} (Err {c_err:.0f})")

    print("✅ EXPERIMENT COMPLETE.")

if __name__ == "__main__":
    run_paradigm_experiment()
