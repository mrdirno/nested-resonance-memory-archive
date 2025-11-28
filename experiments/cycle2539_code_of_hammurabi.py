
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

def run_hammurabi_experiment():
    print("⚖️ CYCLE 2539: THE CODE OF HAMMURABI - LAW & ORDER TEST")
    
    # 1. Initialize Ecosystem
    env = Ecosystem(capacity=100)
    
    # 2. Populate with Aggressive Agents (Potential Criminals)
    print("👺 Seeding Criminals (High Aggression)...")
    for i in range(20):
        agent = DigitalLifeform(name=f"Criminal-{i}", lineage_id="Bandits")
        agent.energy = 500 
        agent.is_predator = True # Predators hunt
        # Gene 4 = Aggression/Hunting
        agent.genome[4] = 0.9 
        # Gene 7 = Cannibalism (High)
        agent.genome[7] = 0.9 
        env.add_agent(agent)
        
    # 3. Populate with Victims
    print("🐑 Seeding Victims...")
    for i in range(80):
        agent = DigitalLifeform(name=f"Citizen-{i}", lineage_id="Citizens")
        agent.energy = 200
        agent.is_prey = True
        agent.genome[6] = 0.1 # Low Evasion
        env.add_agent(agent)
        
    # 4. Enable/Disable Law (Toggle for A/B Testing?)
    # We will assume Law is ON by default in this implementation.
    # Law: Murder = -1000 Energy.
    
    duration = 200
    results_dir = Path("experiments/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    csv_path = results_dir / "cycle2539_code_of_hammurabi.csv"
    
    print(f"📝 Logging to {csv_path}")
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["tick", "pop", "predator_count", "avg_predator_energy", "murders"])
        
        env.running = True
        total_murders = 0
        
        for tick in range(1, duration + 1):
            # Track pre-update deaths to count murders approximately
            # Actually, we can't easily count murders from outside without hooking the print/log.
            # Let's infer from predator energy drops or just watch population dynamics.
            # If Law works, Predators who kill should lose energy and die.
            
            start_preds = [a for a in env.agents if a.is_predator]
            
            env.update()
            
            end_preds = [a for a in env.agents if a.is_predator]
            
            # Calculate Avg Energy of Predators
            avg_pred_e = sum(a.energy for a in end_preds) / len(end_preds) if end_preds else 0
            
            writer.writerow([tick, len(env.agents), len(end_preds), f"{avg_pred_e:.1f}", "N/A"])
            
            if tick % 20 == 0:
                print(f"   Tick {tick}: Pop={len(env.agents)}, Predators={len(end_preds)}, Pred Energy={avg_pred_e:.1f}")
                
            if len(end_preds) == 0:
                print("⚖️ JUSTICE PREVAILS. All criminals executed/starved.")
                break
                
    print("✅ EXPERIMENT COMPLETE.")

if __name__ == "__main__":
    run_hammurabi_experiment()
