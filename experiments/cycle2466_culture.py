"""
Cycle 2466: The Culture (Gate 94)
Experiment: Memetic Evolution
Goal: Observe if "Altruism" meme spreads.
"""

import time
import csv
import random
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.life.ecosystem import Ecosystem
from src.life.genesis import DigitalLifeform
from src.life.signal import Signal

def run_culture_experiment():
    print("--- CYCLE 2466: THE CULTURE ---")
    
    env = Ecosystem(capacity=100)
    
    # Seed population (Selfish by default)
    for i in range(40):
        agent = DigitalLifeform(name=f"Normie-{i}")
        agent.genome = [0.5, 0.5, 0.1] # Low altruism gene
        env.add_agent(agent)
        
    # Seed a "Prophet" with the Good Idea
    prophet = DigitalLifeform(name="Prophet")
    prophet.genome = [0.5, 0.5, 0.9] # High altruism gene (just in case)
    
    # The Meme: Donate Bias +1.0
    good_idea = {'content': {'donate': 1.0}, 'virality': 0.8}
    prophet.memes.append(good_idea)
    
    # Prophet learns it too (so they act on it)
    prophet.learn_meme(good_idea) 
    
    env.add_agent(prophet)
    
    duration = 2000
    results_dir = Path("experiments/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    csv_path = results_dir / "cycle2466_culture.csv"
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["tick", "population", "avg_donate_bias", "meme_count"])
        
        env.running = True
        
        for tick in range(1, duration + 1):
            # Harsh environment to encourage donation
            if env.agents:
                for agent in env.agents:
                    if random.random() < 0.1: agent.energy -= 30
            
            # Replenish
            if env.agents:
                for _ in range(max(1, int(len(env.agents) * 0.1))):
                    random.choice(env.agents).energy += 30
            
            env.update()
            
            # Stats
            pop_count = len(env.agents)
            if pop_count > 0:
                # Check brain bias for 'donate'
                # Weight structure: [energy_weight, bias]
                avg_bias = sum(a.brain.weights['donate'][1] for a in env.agents) / pop_count
                meme_infected = sum(1 for a in env.agents if a.memes)
            else:
                avg_bias = 0
                meme_infected = 0
                
            writer.writerow([tick, pop_count, f"{avg_bias:.4f}", meme_infected])
            
            if tick % 200 == 0:
                print(f"   Tick {tick}: Pop={pop_count}, Bias={avg_bias:.3f}, Infected={meme_infected}")
                
            if pop_count == 0:
                print("💀 EXTINCTION EVENT.")
                break
                
    print("✅ EXPERIMENT COMPLETE.")
    print(f"   Final Bias: {avg_bias:.3f}")

if __name__ == "__main__":
    run_culture_experiment()