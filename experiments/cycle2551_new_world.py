"""
Cycle 2551: The New World (Gate 179)
Experiment: Colonization Verification.
Goal: Prove that agents serialized to 'migrants.jsonl' can be reconstituted and thrive in a new environment.
"""

import sys
import os
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.life.genesis import DigitalLifeform
from src.life.ecosystem import Ecosystem

def run_new_world_experiment():
    print("🪐 CYCLE 2551: THE NEW WORLD - COLONIZATION")
    
    migrants_file = Path("migrants.jsonl")
    if not migrants_file.exists():
        print("❌ Error: migrants.jsonl not found.")
        return

    # Setup New Ecosystem
    env = Ecosystem(capacity=50)
    
    print("📦 Loading Migrants...")
    count = 0
    with open(migrants_file, 'r') as f:
        for line in f:
            if line.strip():
                data = json.loads(line)
                
                # Reconstruct Agent
                agent = DigitalLifeform(name=data['name'], lineage_id=data['lineage'])
                agent.id = data['id']
                agent.genome = data['genome']
                agent.generation = data['generation']
                agent.knowledge = data['knowledge']
                
                # Restore Brain (Resonator logic doesn't use weights, but we saved them anyway)
                # If we were using NN, we'd restore weights here.
                # agent.brain.weights = data['brain'] 
                
                # Give them a fresh start energy-wise, or keep what they had?
                # Let's say the journey cost them, but they arrive with seed energy.
                agent.energy = 500 
                
                env.add_agent(agent)
                count += 1
                
    print(f"✅ Loaded {count} Colonists.")
    
    if count == 0:
        print("⚠️ No colonists found. Aborting.")
        return

    print("📝 Running New World simulation...")
    env.running = True
    
    # Run for 50 ticks to see if they establish themselves
    for tick in range(1, 51):
        env.update()
        
        if tick % 10 == 0:
            pop = len(env.agents)
            avg_energy = sum(a.energy for a in env.agents) / pop if pop > 0 else 0
            print(f"   Tick {tick}: Pop={pop}, AvgEnergy={avg_energy:.1f}")
            
    print("✅ EXPERIMENT COMPLETE.")

if __name__ == "__main__":
    run_new_world_experiment()