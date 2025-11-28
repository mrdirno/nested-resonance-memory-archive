
import sys
import os
import csv
import time
import random
import math
import numpy as np
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.life.genesis import DigitalLifeform
from src.life.ecosystem import Ecosystem

class Substrate:
    def __init__(self):
        self.storage = {}
        
    def write(self, key, value):
        self.storage[key] = value
        
    def read(self, key):
        return self.storage.get(key, None)

def run_oracle_experiment():
    print("🔮 CYCLE 2556: THE ORACLE - KNOWLEDGE ACCESS")
    print("   (Replacing Trial-and-Error with Education)")
    
    substrate = Substrate()
    
    # 1. Write Knowledge (The Truth)
    # 0 = Safe, 1 = Poison
    TRUTH = {0: 'SAFE', 1: 'POISON'}
    substrate.write('BERRY_KNOWLEDGE', TRUTH)
    print("✍️  Oracle wrote Truth to Library.")
    
    # 2. Initialize Agents
    ignorant_agents = [DigitalLifeform(name=f"Ignorant-{i}") for i in range(20)]
    educated_agents = [DigitalLifeform(name=f"Educated-{i}") for i in range(20)]
    
    for a in educated_agents:
        # Access Library
        knowledge = substrate.read('BERRY_KNOWLEDGE')
        a.knowledge.update(knowledge)
        
    # 3. The Test (Foraging)
    print("🍎 Foraging Test Begins...")
    
    ignorant_survival = 0
    educated_survival = 0
    
    results_dir = Path("experiments/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    csv_path = results_dir / "cycle2556_the_oracle.csv"
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["tick", "ignorant_alive", "educated_alive"])
        
        for tick in range(1, 101):
            # Each tick, agents encounter a random berry (0 or 1)
            berry_type = random.choice([0, 1])
            
            # Ignorant: Randomly eat (50/50)
            for a in ignorant_agents:
                if not a.alive: continue
                if random.random() < 0.5: # Eat?
                    if TRUTH[berry_type] == 'POISON':
                        a.alive = False
                        
            # Educated: Check Knowledge
            for a in educated_agents:
                if not a.alive: continue
                # Check internal knowledge
                if a.knowledge.get(berry_type) == 'SAFE':
                    # Eat (Gain energy? Survival is metric here)
                    pass
                elif a.knowledge.get(berry_type) == 'POISON':
                    # Don't eat
                    pass
                else:
                    # Fallback (shouldn't happen if educated)
                    if random.random() < 0.5 and TRUTH[berry_type] == 'POISON':
                        a.alive = False
                        
            ig_count = len([a for a in ignorant_agents if a.alive])
            ed_count = len([a for a in educated_agents if a.alive])
            
            writer.writerow([tick, ig_count, ed_count])
            
            if tick % 20 == 0:
                print(f"   Tick {tick}: Ignorant={ig_count} Educated={ed_count}")
                
    print("✅ EXPERIMENT COMPLETE.")

if __name__ == "__main__":
    run_oracle_experiment()
