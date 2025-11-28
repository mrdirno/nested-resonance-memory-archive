"""
Cycle 2487: The Gardener (Gate 115)
Experiment: Introduce new environmental pressures.
Goal: Drive further adaptation and complexity.
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
from src.life.signal import Signal

def run_gardener_experiment():
    print("🌳 CYCLE 2487: THE GARDENER - INTRODUCING COMPLEXITY")
    
    # Setup Ecosystem
    capacity = 100
    duration = 2000
    env = Ecosystem(capacity=capacity)
    
    # Seed Population
    print("🌱 Seeding population...")
    for i in range(50):
        agent = DigitalLifeform(name=f"Plant-{i}")
        agent.energy = 500 # Increased for better survival
        agent.genome = [random.random(), random.random(), random.random(), 0.5] # New gene: Foraging (0.5 default)
        env.add_agent(agent)
    
    # Seed Predators (initially fewer)
    for i in range(2): # Reduced initial predators
        predator = DigitalLifeform(name=f"Predator-{i}")
        predator.genome = [0.2, 0.1, 0.0, 0.8] # Low efficiency, low fertility, selfish, high hunting trait
        predator.is_predator = True # Custom trait for now
        env.add_agent(predator)
        
    # Prepare Output
    results_dir = Path("experiments/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    csv_path = results_dir / "cycle2487_gardener.csv"
    
    print(f"📝 Logging to {csv_path}")
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["tick", "total_pop", "plant_pop", "predator_pop", "avg_plant_forage_trait", "avg_predator_hunt_trait"])
        
        env.running = True
        
        for tick in range(1, duration + 1):
            # Introduce variable food sources (randomly appear in environment)
            # For now, simulate by giving random energy bursts to random agents
            if env.agents:
                for _ in range(max(1, int(len(env.agents) * 0.3))): # 30% get food
                    lucky_agent = random.choice(env.agents)
                    lucky_agent.energy += 30
            
            # Predators hunt (handled in act)
            
            env.update()
            
            # Collect Stats
            plant_pop = len([a for a in env.agents if not hasattr(a, 'is_predator')])
            predator_pop = len([a for a in env.agents if hasattr(a, 'is_predator')])
            total_pop = len(env.agents)
            
            avg_plant_forage_trait = 0
            if plant_pop > 0:
                avg_plant_forage_trait = sum(a.genome[3] for a in env.agents if not hasattr(a, 'is_predator') and len(a.genome) > 3) / plant_pop

            avg_predator_hunt_trait = 0
            if predator_pop > 0:
                avg_predator_hunt_trait = sum(a.genome[3] for a in env.agents if hasattr(a, 'is_predator') and len(a.genome) > 3) / predator_pop
            
            writer.writerow([tick, total_pop, plant_pop, predator_pop, f"{avg_plant_forage_trait:.4f}", f"{avg_predator_hunt_trait:.4f}"])
            
            # Console Feedback (every 100 ticks)
            if tick % 100 == 0:
                print(f"   Tick {tick}: TotalPop={total_pop}, Plants={plant_pop}, Preds={predator_pop}, AvgPlantForage={avg_plant_forage_trait:.3f}, AvgPredHunt={avg_predator_hunt_trait:.3f}")
            
            if total_pop == 0:
                print("💀 EXTINCTION EVENT. Simulation ended early.")
                break
                
    print("✅ EXPERIMENT COMPLETE.")
    print(f"   Final Stats: TotalPop={total_pop}, Plants={plant_pop}, Preds={predator_pop}")

if __name__ == "__main__":
    run_gardener_experiment()
