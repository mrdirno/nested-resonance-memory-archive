"""
Cycle 2521: The Grid (Gate 149)
Experiment: Spatial Dimension.
Goal: Introduce position, movement, and proximity-based interactions.
"""

import sys
import os
import csv
import time
import random
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.life.genesis import DigitalLifeform
from src.life.ecosystem import Ecosystem

def run_spatial_grid_experiment():
    print("🗺️ CYCLE 2521: THE GRID - SPATIAL DIMENSION")
    
    # Setup Ecosystem
    env = Ecosystem(capacity=200, prey_capacity=200, predator_capacity=0)
    duration = 2000
    
    # Seed Agents with Mobility Gene
    print("🚶 Seeding The Nomads...")
    for i in range(100):
        agent = DigitalLifeform(name=f"Nomad-{i}", lineage_id="Wanderers")
        agent.energy = 500
        # Gene 10 = Mobility
        agent.genome = [0.5] * 10 + [0.9] # High Mobility
        # Random start position
        agent.x = random.uniform(0, 100)
        agent.y = random.uniform(0, 100)
        env.add_agent(agent)
        
    # Seed Sedentary Agents
    print("🌲 Seeding The Settlers...")
    for i in range(100):
        agent = DigitalLifeform(name=f"Settler-{i}", lineage_id="Locals")
        agent.energy = 500
        agent.genome = [0.5] * 10 + [0.1] # Low Mobility
        agent.x = random.uniform(0, 100)
        agent.y = random.uniform(0, 100)
        env.add_agent(agent)
        
    # Prepare Output
    results_dir = Path("experiments/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    csv_path = results_dir / "cycle2521_spatial_grid.csv"
    
    print(f"📝 Logging to {csv_path}")
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["tick", "pop_nomad", "pop_settler", "avg_dist_moved_nomad", "avg_dist_moved_settler"])
        
        env.running = True
        
        # Track movement
        initial_pos = {}
        for a in env.agents:
            initial_pos[a.id] = (a.x, a.y)
            
        for tick in range(1, duration + 1):
            env.update()
            
            nomads = [a for a in env.agents if a.lineage_id == "Wanderers"]
            settlers = [a for a in env.agents if a.lineage_id == "Locals"]
            
            # Calculate avg distance from start (displacement)
            def get_dist(agents):
                total_dist = 0
                count = 0
                for a in agents:
                    if a.id in initial_pos:
                        ix, iy = initial_pos[a.id]
                        dist = ((a.x - ix)**2 + (a.y - iy)**2)**0.5
                        total_dist += dist
                        count += 1
                return total_dist / count if count else 0
                
            avg_dist_nomad = get_dist(nomads)
            avg_dist_settler = get_dist(settlers)
            
            writer.writerow([tick, len(nomads), len(settlers), f"{avg_dist_nomad:.1f}", f"{avg_dist_settler:.1f}"])
            
            if tick % 100 == 0:
                print(f"   Tick {tick}: Nomad={len(nomads)} (Dist={avg_dist_nomad:.1f}), Settler={len(settlers)} (Dist={avg_dist_settler:.1f})")
            
            if len(env.agents) == 0:
                break
                
    print("✅ EXPERIMENT COMPLETE.")

if __name__ == "__main__":
    run_spatial_grid_experiment()
