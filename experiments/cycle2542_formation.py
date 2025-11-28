
import sys
import os
import csv
import time
import random
import math
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.life.genesis import DigitalLifeform
from src.life.ecosystem import Ecosystem

def run_formation_experiment():
    print("🛡️ CYCLE 2542: THE FORMATION - ACTIVE STABILIZATION TEST")
    print("   (Holding Shape Against Entropy)")
    
    # 1. Initialize Ecosystem
    env = Ecosystem(capacity=50, width=50, height=50)
    
    # 2. Spawn Agents (The Formation)
    print("🤖 Spawning 20 Drones...")
    drones = []
    for i in range(20):
        agent = DigitalLifeform(name=f"Drone-{i}")
        agent.energy = 1000 # High energy for maneuvering
        # Start on the Ring (Ideal State)
        angle = (2 * math.pi / 20) * i
        agent.x = int(25 + 10 * math.cos(angle))
        agent.y = int(25 + 10 * math.sin(angle))
        env.add_agent(agent)
        drones.append(agent)
        
    # Target Parameters
    target_x, target_y = 25, 25
    target_radius = 10
    
    duration = 50
    noise_level = 1.0 # Magnitude of Brownian Motion
    
    results_dir = Path("experiments/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    csv_path = results_dir / "cycle2542_formation.csv"
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["tick", "avg_deviation", "energy_cost", "correction_count"])
        
        env.running = True
        
        for tick in range(1, duration + 1):
            correction_count = 0
            total_deviation = 0
            tick_energy_cost = 0
            
            # 1. Apply Entropy (Noise)
            for agent in drones:
                # Random Drift
                drift_x = random.choice([-1, 0, 1])
                drift_y = random.choice([-1, 0, 1])
                agent.x += drift_x
                agent.y += drift_y
                
                # Keep in bounds
                agent.x = max(0, min(50, agent.x))
                agent.y = max(0, min(50, agent.y))
            
            # 2. Apply Active Control (Correction)
            for agent in drones:
                dx = agent.x - target_x
                dy = agent.y - target_y
                dist = math.sqrt(dx*dx + dy*dy)
                if dist == 0: dist = 0.001
                
                deviation = abs(dist - target_radius)
                total_deviation += deviation
                
                # Control Loop: Correct if deviation > threshold
                if deviation > 1.0:
                    correction_count += 1
                    
                    # Calculate Correction Vector
                    nx = dx / dist
                    ny = dy / dist
                    
                    move_dir = 1 if dist > target_radius else -1
                    
                    # Corrective Step
                    step_x = int(-nx * move_dir * 1) 
                    step_y = int(-ny * move_dir * 1)
                    
                    agent.move(step_x, step_y)
                    
                    # Track Cost
                    # move() consumes energy, let's track the delta
                    # Assuming move cost is ~0.2 per step
                    tick_energy_cost += 0.2

            avg_dev = total_deviation / len(drones)
            writer.writerow([tick, f"{avg_dev:.2f}", f"{tick_energy_cost:.1f}", correction_count])
            
            if tick % 10 == 0:
                print(f"   Tick {tick}: Dev={avg_dev:.2f}, Corrections={correction_count}, Cost={tick_energy_cost:.1f}")
                
    print("✅ EXPERIMENT COMPLETE.")

if __name__ == "__main__":
    run_formation_experiment()
