"""
Cycle 2520: The Big Bang (Gate 148)
Experiment: Reseeding the Universe.
Goal: Prove that information persists across "Universal Reboots" (Panspermia).
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

def run_big_bang_experiment():
    print("💥 CYCLE 2520: THE BIG BANG - RESEEDING")
    
    # 1. Setup New Universe
    env = Ecosystem(capacity=200, prey_capacity=200, predator_capacity=0)
    duration = 1000
    
    # 2. The Ancient Ones (Survivors from the Void)
    # In a real system, we'd load their genome from a file.
    # Here, we simulate the "Perfected Genome" we observed in Cycle 2514/2519.
    # High Efficiency, High Altruism, High Trust, High Innovation.
    ancient_genome = [0.95, 0.95, 0.1, 0.95, 0.1, 0.95, 0.5, 0.1, 0.95, 0.99]
    
    print("🧬 Seeding The Ancient Ones...")
    for i in range(10):
        agent = DigitalLifeform(name=f"Ancient-{i}", lineage_id="Precursors")
        agent.energy = 100 # Humble beginnings, but advanced code
        agent.genome = ancient_genome
        env.add_agent(agent)
        
    # 3. The Primitives (Control Group - Random Genome)
    print("🦠 Seeding The Primitives...")
    for i in range(10):
        agent = DigitalLifeform(name=f"Prim-{i}", lineage_id="Natives")
        agent.energy = 100
        agent.genome = [random.random() for _ in range(10)]
        env.add_agent(agent)
        
    # Prepare Output
    results_dir = Path("experiments/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    csv_path = results_dir / "cycle2520_big_bang.csv"
    
    print(f"📝 Logging to {csv_path}")
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["tick", "pop_ancient", "pop_primitive", "avg_nrg_ancient", "avg_nrg_prim"])
        
        env.running = True
        
        for tick in range(1, duration + 1):
            env.update()
            
            ancients = [a for a in env.agents if a.lineage_id == "Precursors"]
            primitives = [a for a in env.agents if a.lineage_id == "Natives"]
            
            avg_nrg_anc = 0
            if ancients: avg_nrg_anc = sum(a.energy for a in ancients) / len(ancients)
            
            avg_nrg_prim = 0
            if primitives: avg_nrg_prim = sum(a.energy for a in primitives) / len(primitives)
            
            writer.writerow([tick, len(ancients), len(primitives), f"{avg_nrg_anc:.1f}", f"{avg_nrg_prim:.1f}"])
            
            if tick % 100 == 0:
                print(f"   Tick {tick}: Ancient={len(ancients)} ({avg_nrg_anc:.1f}), Primitive={len(primitives)} ({avg_nrg_prim:.1f})")
            
            if len(primitives) == 0 and len(ancients) > 50:
                print("🏆 VICTORY! The Ancients have colonized the new universe.")
                break
                
    print("✅ EXPERIMENT COMPLETE.")
    print(f"   Final: Ancient={len(ancients)}, Primitive={len(primitives)}")

if __name__ == "__main__":
    run_big_bang_experiment()
