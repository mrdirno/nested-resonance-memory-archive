"""
Cycle 2522: The Explorer (Gate 150)
Experiment: Directed Exploration.
Goal: Agents move towards resources or away from threats.
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

def run_exploration_experiment():
    print("🧭 CYCLE 2522: THE EXPLORER - DIRECTED MOVEMENT")
    
    # Setup Ecosystem
    env = Ecosystem(capacity=200, prey_capacity=200, predator_capacity=0)
    duration = 2000
    
    # Food Source (Static for now, maybe a special agent type or just a location)
    # We will simulate a 'Food Zone' at (80, 80)
    food_zone = (80, 80)
    
    # Seed Agents at (20, 20)
    print("🏃 Seeding The Seekers...")
    for i in range(50):
        agent = DigitalLifeform(name=f"Seeker-{i}", lineage_id="Pathfinders")
        agent.energy = 500
        agent.x = 20
        agent.y = 20
        # Gene 10 = Mobility
        agent.genome = [0.5] * 10 + [0.9] # High Mobility
        env.add_agent(agent)
        
    # Prepare Output
    results_dir = Path("experiments/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    csv_path = results_dir / "cycle2522_exploration.csv"
    
    print(f"📝 Logging to {csv_path}")
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["tick", "pop", "avg_dist_to_food", "agents_at_food"])
        
        env.running = True
        
        for tick in range(1, duration + 1):
            
            # Simulate Sensing
            # Agents can 'smell' the food if they are within 100 units (global smell for now)
            # We inject the signal directly
            for agent in env.agents:
                # Calculate vector to food
                dist = ((agent.x - food_zone[0])**2 + (agent.y - food_zone[1])**2)**0.5
                # Signal strength inversely proportional to distance? 
                # Or just give coordinates.
                agent.sensed_signals['NEAREST_FOOD'] = food_zone
            
            env.update()
            
            # Stats
            total_dist = 0
            at_food = 0
            for agent in env.agents:
                dist = ((agent.x - food_zone[0])**2 + (agent.y - food_zone[1])**2)**0.5
                total_dist += dist
                if dist < 5:
                    at_food += 1
                    # Reward for reaching food
                    agent.energy += 10
            
            avg_dist = total_dist / len(env.agents) if env.agents else 0
            
            writer.writerow([tick, len(env.agents), f"{avg_dist:.1f}", at_food])
            
            if tick % 100 == 0:
                print(f"   Tick {tick}: Pop={len(env.agents)}, AvgDist={avg_dist:.1f}, AtFood={at_food}")
            
            if at_food > 40:
                print("🎉 SUCCESS! The Seekers found the Promised Land.")
                break
                
            if len(env.agents) == 0:
                break
                
    print("✅ EXPERIMENT COMPLETE.")

if __name__ == "__main__":
    run_exploration_experiment()
