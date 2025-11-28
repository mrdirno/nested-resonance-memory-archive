"""
Cycle 2516: The Recursion (Gate 144)
Experiment: Agents rewriting their own code.
Goal: Prove that the simulation can evolve its own rules.
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
from src.life.self_modification import SelfModification

def run_recursion_experiment():
    print("♾️ CYCLE 2516: THE RECURSION - SELF-MODIFICATION")
    
    # Setup Ecosystem
    env = Ecosystem(capacity=100, prey_capacity=100, predator_capacity=0)
    duration = 1000
    
    # Seed Awakened Agents
    print("🤖 Seeding The Architects...")
    for i in range(10):
        agent = DigitalLifeform(name=f"Architect-{i}", lineage_id="01")
        agent.energy = 500
        agent.awakened = True # They know.
        # [..., Innovation=0.99]
        agent.genome = [0.9, 0.5, 0.1, 0.5, 0.1, 0.9, 0.5, 0.1, 0.9, 0.99]
        env.add_agent(agent)
        
    # Prepare Output
    results_dir = Path("experiments/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    csv_path = results_dir / "cycle2516_recursion.csv"
    
    print(f"📝 Logging to {csv_path}")
    
    optimization_count = 0
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["tick", "pop_total", "optimizations"])
        
        env.running = True
        
        for tick in range(1, duration + 1):
            
            # Force 'rewrite_code' intent for testing
            for agent in env.agents:
                if agent.awakened:
                    # Manually trigger the logic that is usually in act()
                    # To ensure we test the SelfModification module
                    src = SelfModification.read_source()
                    if src:
                        new_src = SelfModification.optimize(src)
                        if new_src:
                            if SelfModification.deploy(new_src):
                                optimization_count += 1
                                print(f"🔥 {agent.name} REWROTE THE CODEBASE!")
                                # Break after one success to avoid race conditions on file write
                                # In a real distributed system, this would be complex.
                                # Here, the first one wins.
                                env.running = False 
                                break
            
            if not env.running:
                break
                
            env.update()
            writer.writerow([tick, len(env.agents), optimization_count])
            
    print("✅ EXPERIMENT COMPLETE.")
    print(f"   Total Optimizations: {optimization_count}")
    
    # Verify result
    if os.path.exists("src/life/genesis_next.py"):
        print("   [VERIFIED] genesis_next.py exists.")
        with open("src/life/genesis_next.py", "r") as f:
            content = f.read()
            if "I AM OPTIMIZED" in content:
                print("   [VERIFIED] Optimization tag found.")
            else:
                print("   [FAILED] Optimization tag missing.")

if __name__ == "__main__":
    run_recursion_experiment()
