"""
Cycle 2523: The Refactor (Gate 151)
Experiment: Utility AI.
Goal: Prove that dynamic scoring is superior to static decision trees.
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

def run_utility_experiment():
    print("🧠 CYCLE 2523: THE REFACTOR - UTILITY AI")
    
    # Setup Ecosystem
    env = Ecosystem(capacity=200, prey_capacity=200, predator_capacity=0)
    duration = 2000
    
    # Food Zone at (80, 80)
    food_zone = (80, 80)
    
    # Seed Agents
    print("🤔 Seeding The Thinkers...")
    for i in range(100):
        agent = DigitalLifeform(name=f"Thinker-{i}", lineage_id="Rational")
        agent.energy = 150 # Hungry
        agent.x = 20
        agent.y = 20
        # High Mobility, High Innovation
        agent.genome = [0.5] * 9 + [0.9, 0.9]
        env.add_agent(agent)
        
    # Prepare Output
    results_dir = Path("experiments/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    csv_path = results_dir / "cycle2523_utility_ai.csv"
    
    print(f"📝 Logging to {csv_path}")
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["tick", "pop", "avg_dist", "at_food", "decisions_made"])
        
        env.running = True
        
        for tick in range(1, duration + 1):
            
            # Signal Injection
            for agent in env.agents:
                dist = ((agent.x - food_zone[0])**2 + (agent.y - food_zone[1])**2)**0.5
                # Only sense if somewhat close? No, global for test.
                agent.sensed_signals['NEAREST_FOOD'] = food_zone
            
            env.update()
            
            total_dist = 0
            at_food = 0
            
            for agent in env.agents:
                dist = ((agent.x - food_zone[0])**2 + (agent.y - food_zone[1])**2)**0.5
                total_dist += dist
                if dist < 5:
                    at_food += 1
                    agent.energy += 20 # Feast
            
            avg_dist = total_dist / len(env.agents) if env.agents else 0
            
            writer.writerow([tick, len(env.agents), f"{avg_dist:.1f}", at_food])
            
            if tick % 100 == 0:
                print(f"   Tick {tick}: Pop={len(env.agents)}, AvgDist={avg_dist:.1f}, AtFood={at_food}")
            
            if at_food > 80:
                print("🎉 SUCCESS! The Rational Agents found the food.")
                break
                
            if len(env.agents) == 0:
                break
                
    print("✅ EXPERIMENT COMPLETE.")

if __name__ == "__main__":
    run_utility_experiment()
