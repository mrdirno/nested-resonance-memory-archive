"""
Cycle 2514: The Dyson Sphere (Gate 142)
Experiment: Mega-Scale Engineering.
Goal: Coordinate the entire civilization to build a structure larger than any individual.
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

def run_dyson_experiment():
    print("☀️ CYCLE 2514: THE DYSON SPHERE - TYPE I CIVILIZATION")
    
    # Setup Ecosystem
    env = Ecosystem(capacity=500, prey_capacity=500, predator_capacity=0)
    duration = 2000
    
    # Seed Civilization (High Trust, High Altruism, High Innovation)
    print("🌍 Seeding The Builders...")
    for i in range(200):
        agent = DigitalLifeform(name=f"Builder-{i}", lineage_id="Builders")
        agent.energy = 500
        # [..., Altruism=0.9, ..., Trust=0.9, Innovation=0.9]
        agent.genome = [0.9, 0.5, 0.1, 0.5, 0.1, 0.9, 0.5, 0.1, 0.9, 0.9]
        env.add_agent(agent)
        
    # The Mega-Project
    project_progress = 0
    project_target = 1000000 # 1 Million Energy
    
    # Prepare Output
    results_dir = Path("experiments/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    csv_path = results_dir / "cycle2514_dyson.csv"
    
    print(f"📝 Logging to {csv_path}")
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["tick", "population", "avg_energy", "project_progress"])
        
        env.running = True
        
        for tick in range(1, duration + 1):
            
            # Work Phase
            # Agents with surplus energy contribute to the project
            # This simulates "Taxes" or "Philanthropy" directed at a specific goal
            
            daily_contribution = 0
            
            for agent in env.agents:
                if agent.energy > 200:
                    # Contribute 10% of surplus
                    surplus = agent.energy - 200
                    contribution = surplus * 0.1
                    agent.energy -= contribution
                    daily_contribution += contribution
            
            project_progress += daily_contribution
            
            env.update()
            
            avg_nrg = 0
            if env.agents: avg_nrg = sum(a.energy for a in env.agents) / len(env.agents)
            
            writer.writerow([tick, len(env.agents), f"{avg_nrg:.1f}", f"{project_progress:.1f}"])
            
            if tick % 100 == 0:
                print(f"   Tick {tick}: Pop={len(env.agents)}, AvgNrg={avg_nrg:.1f}, Progress={project_progress:.0f}/{project_target} ({project_progress/project_target:.1%})")
            
            if project_progress >= project_target:
                print("🎉 SUCCESS! THE DYSON SPHERE IS COMPLETE.")
                print(f"   Time: {tick} ticks. Civilization Level: Type I.")
                break
                
            if len(env.agents) == 0:
                print("💀 EXTINCTION. Project Abandoned.")
                break
                
    print("✅ EXPERIMENT COMPLETE.")
    print(f"   Final Progress: {project_progress:.0f}")

if __name__ == "__main__":
    run_dyson_experiment()
