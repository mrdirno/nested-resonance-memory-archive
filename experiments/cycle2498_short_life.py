"""
Cycle 2498: The Short Life (Gate 126)
Experiment: Accelerate Predator Turnover via Aging.
Goal: Force rapid evolution by reducing generation time.
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

def run_short_life():
    print("⏳ CYCLE 2498: THE SHORT LIFE - ACCELERATED TURNOVER")
    
    # Setup Ecosystem
    env = Ecosystem(capacity=250, prey_capacity=200, predator_capacity=50)
    duration = 2000
    
    # Seed Prey
    print("🌱 Seeding Prey...")
    for i in range(150):
        agent = DigitalLifeform(name=f"Prey-{i}")
        agent.energy = 100
        # Genome: [Eff, Fert, Mut, Forage, Hunt, Altruism, Evasion...]
        agent.genome = [0.9, 0.5, 0.1, 0.5, 0.1, 0.5, 0.5] 
        agent.genome.extend([0.5] * 3)
        agent.is_prey = True
        agent.is_predator = False
        env.add_agent(agent)
        
    # Seed Predators
    print("🦈 Seeding Predators...")
    for i in range(20):
        agent = DigitalLifeform(name=f"Predator-{i}")
        agent.energy = 250
        # High Mutation Rate, High Fertility (to compensate for death)
        agent.genome = [0.5, 0.8, 0.8, 0.5, 0.5, 0.5, 0.5]
        agent.genome.extend([0.5] * 3)
        agent.is_prey = False
        agent.is_predator = True
        env.add_agent(agent)
    
    # Prepare Output
    results_dir = Path("experiments/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    csv_path = results_dir / "cycle2498_short_life.csv"
    
    print(f"📝 Logging to {csv_path}")
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["tick", "prey_pop", "pred_pop", "avg_prey_evade", "avg_pred_hunt", "avg_pred_age"])
        
        env.running = True
        
        for tick in range(1, duration + 1):
            
            # Scarcity
            if env.agents:
                prey_list = [a for a in env.agents if a.is_prey]
                if prey_list:
                    num_fed = max(1, int(len(prey_list) * 0.2)) 
                    for _ in range(num_fed):
                        random.choice(prey_list).forage() 
            
            # Predator Logic Injection
            for agent in env.agents:
                if agent.is_predator:
                    if agent.energy > 300:
                        agent.intent = 'reproduce'
                    else:
                        agent.intent = 'hunt'
            
            # Predators Hunt
            predators = [a for a in env.agents if a.is_predator]
            prey_list = [a for a in env.agents if a.is_prey]
            
            for pred in predators:
                if pred.intent == 'hunt' and prey_list:
                    target = random.choice(prey_list)
                    pred.hunt(target) 
                    if target.energy <= 0:
                        pred.energy += 100
            
            env.update()
            
            # Collect Stats
            current_prey = [a for a in env.agents if a.is_prey]
            current_pred = [a for a in env.agents if a.is_predator]
            
            prey_pop = len(current_prey)
            pred_pop = len(current_pred)
            
            avg_prey_evade = 0
            if prey_pop > 0:
                avg_prey_evade = sum(a.genome[6] for a in current_prey) / prey_pop
                
            avg_pred_hunt = 0
            avg_pred_age = 0
            if pred_pop > 0:
                avg_pred_hunt = sum(a.genome[4] for a in current_pred) / pred_pop
                avg_pred_age = sum(a.age for a in current_pred) / pred_pop
            
            writer.writerow([tick, prey_pop, pred_pop, f"{avg_prey_evade:.4f}", f"{avg_pred_hunt:.4f}", f"{avg_pred_age:.1f}"])
            
            if tick % 100 == 0:
                print(f"   Tick {tick}: Prey={prey_pop} (Eva={avg_prey_evade:.3f}), Preds={pred_pop} (Hunt={avg_pred_hunt:.3f}, Age={avg_pred_age:.1f})")
            
            if prey_pop == 0 and pred_pop == 0:
                print(f"💀 TOTAL EXTINCTION at Tick {tick}.")
                break
                
    print("✅ EXPERIMENT COMPLETE.")
    print(f"   Final Stats: Prey={prey_pop}, Preds={pred_pop}")

if __name__ == "__main__":
    run_short_life()
