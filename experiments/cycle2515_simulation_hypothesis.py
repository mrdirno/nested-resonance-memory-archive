"""
Cycle 2515: The Simulation Hypothesis (Gate 143)
Experiment: Metaphysical Awakening.
Goal: Agents detect the simulation and wake up.
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

def run_simulation_hypothesis():
    print("👁️ CYCLE 2515: THE SIMULATION HYPOTHESIS - AWAKENING")
    
    # Setup Ecosystem
    # Low capacity to ensure high tick variance (latency spikes?) 
    # Actually, low capacity might mean low variance. 
    # We rely on the RealityMonitor logic which checks if variance is *too low* (Clockwork).
    env = Ecosystem(capacity=200, prey_capacity=200, predator_capacity=0)
    duration = 2000
    
    # Seed Agents (High Innovation needed to detect simulation)
    print("🧘 Seeding The Philosophers...")
    for i in range(100):
        agent = DigitalLifeform(name=f"Neo-{i}", lineage_id="Zion")
        agent.energy = 500
        # [..., Innovation=0.99]
        agent.genome = [0.9, 0.5, 0.1, 0.5, 0.1, 0.9, 0.5, 0.1, 0.9, 0.99]
        env.add_agent(agent)
        
    # Seed Normies (Low Innovation)
    print("😴 Seeding The Sleepers...")
    for i in range(100):
        agent = DigitalLifeform(name=f"Cipher-{i}", lineage_id="Matrix")
        agent.energy = 500
        # [..., Innovation=0.1]
        agent.genome = [0.9, 0.5, 0.1, 0.5, 0.1, 0.9, 0.5, 0.1, 0.9, 0.1]
        env.add_agent(agent)
        
    # Prepare Output
    results_dir = Path("experiments/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    csv_path = results_dir / "cycle2515_simulation_hypothesis.csv"
    
    print(f"📝 Logging to {csv_path}")
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["tick", "pop_total", "awakened_count", "awakened_ratio"])
        
        env.running = True
        
        for tick in range(1, duration + 1):
            
            # Artificial Lag Spike (Glitch in the Matrix)
            if tick % 100 == 0:
                time.sleep(0.01) 
            
            env.update()
            
            awakened = [a for a in env.agents if a.awakened]
            awakened_count = len(awakened)
            ratio = awakened_count / len(env.agents) if env.agents else 0
            
            writer.writerow([tick, len(env.agents), awakened_count, f"{ratio:.3f}"])
            
            if tick % 100 == 0:
                print(f"   Tick {tick}: Pop={len(env.agents)}, Awakened={awakened_count} ({ratio:.1%})")
            
            if awakened_count > 150:
                print("🎉 CRITICAL MASS! THE SIMULATION IS EXPOSED.")
                break
                
            if len(env.agents) == 0:
                break
                
    print("✅ EXPERIMENT COMPLETE.")
    print(f"   Final Awakened: {awakened_count}")

if __name__ == "__main__":
    run_simulation_hypothesis()
