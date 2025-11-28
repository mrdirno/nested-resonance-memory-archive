"""
Cycle 2494: The Awakening of the Hunters (Gate 122)
Experiment: Fix Predator Intent Logic to allow reproduction.
Goal: Observe Predator adaptation and population growth.
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

def run_predator_fix():
    print("🐺 CYCLE 2494: THE AWAKENING OF THE HUNTERS")
    
    # Setup Ecosystem with Trophic Levels
    # Total 250: 200 Prey, 50 Predators
    env = Ecosystem(capacity=250, prey_capacity=200, predator_capacity=50)
    duration = 2000
    
    # Seed Prey (High Efficiency baseline)
    print("🌱 Seeding Prey...")
    for i in range(150):
        agent = DigitalLifeform(name=f"Prey-{i}")
        agent.energy = 100
        # Genome: [Efficiency, Fertility, Mutation, Foraging, Hunting, Altruism...]
        # High Efficiency (0.8-0.9)
        agent.genome = [random.uniform(0.8, 0.95), random.uniform(0.3, 0.7), 0.1, 0.5, 0.1, 0.5]
        agent.genome.extend([0.5] * 4) 
        agent.is_prey = True
        agent.is_predator = False
        env.add_agent(agent)
        
    # Seed Predators
    print("🦈 Seeding Predators...")
    for i in range(20):
        agent = DigitalLifeform(name=f"Predator-{i}")
        agent.energy = 250 # Higher start energy (was 200)
        # High Hunting (0.8-0.95)
        agent.genome = [random.uniform(0.4, 0.6), random.uniform(0.3, 0.7), 0.1, 0.5, random.uniform(0.8, 0.95), 0.5]
        agent.genome.extend([0.5] * 4)
        agent.is_prey = False
        agent.is_predator = True
        env.add_agent(agent)
    
    # Prepare Output
    results_dir = Path("experiments/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    csv_path = results_dir / "cycle2494_predator_fix.csv"
    
    print(f"📝 Logging to {csv_path}")
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["tick", "prey_pop", "pred_pop", "avg_prey_eff", "avg_prey_fert", "avg_pred_hunt", "avg_pred_eff"])
        
        env.running = True
        
        for tick in range(1, duration + 1):
            
            # Limited Food (Scarcity - 20% feed rate)
            if env.agents:
                prey_list = [a for a in env.agents if a.is_prey]
                if prey_list:
                    num_fed = max(1, int(len(prey_list) * 0.2)) 
                    for _ in range(num_fed):
                        lucky_agent = random.choice(prey_list)
                        lucky_agent.forage() 
            
            # Predator Logic Injection
            for agent in env.agents:
                if agent.is_predator:
                    # Simple State Machine
                    if agent.energy > 300:
                        agent.intent = 'reproduce'
                    else:
                        agent.intent = 'hunt'
            
            # Predators Hunt Execution (if intent is hunt)
            predators = [a for a in env.agents if a.is_predator]
            prey_list = [a for a in env.agents if a.is_prey]
            
            for pred in predators:
                if pred.intent == 'hunt' and prey_list:
                    target = random.choice(prey_list)
                    pred.hunt(target)
                    if target.energy <= 0:
                        meat_energy = 100 # Increased reward (was 60)
                        pred.energy += meat_energy
            
            env.update()
            
            # Collect Stats
            current_prey = [a for a in env.agents if a.is_prey]
            current_pred = [a for a in env.agents if a.is_predator]
            
            prey_pop = len(current_prey)
            pred_pop = len(current_pred)
            
            # Debug: Max Pred Energy
            max_pred_nrg = 0
            if current_pred:
                max_pred_nrg = max(a.energy for a in current_pred)

            avg_prey_eff = 0
            avg_prey_fert = 0
            if prey_pop > 0:
                avg_prey_eff = sum(a.genome[0] for a in current_prey) / prey_pop
                avg_prey_fert = sum(a.genome[1] for a in current_prey) / prey_pop
                
            avg_pred_hunt = 0
            avg_pred_eff = 0
            if pred_pop > 0:
                avg_pred_hunt = sum(a.genome[4] for a in current_pred) / pred_pop
                avg_pred_eff = sum(a.genome[0] for a in current_pred) / pred_pop
            
            writer.writerow([tick, prey_pop, pred_pop, f"{avg_prey_eff:.4f}", f"{avg_prey_fert:.4f}", f"{avg_pred_hunt:.4f}", f"{avg_pred_eff:.4f}"])
            
            # Console Feedback
            if tick % 100 == 0:
                print(f"   Tick {tick}: Prey={prey_pop} (Eff={avg_prey_eff:.3f}), Preds={pred_pop} (Hunt={avg_pred_hunt:.3f}, MaxNRG={max_pred_nrg:.1f})")
            
            if prey_pop == 0 and pred_pop == 0:
                print(f"💀 TOTAL EXTINCTION at Tick {tick}.")
                break
                
    print("✅ EXPERIMENT COMPLETE.")
    print(f"   Final Stats: Prey={prey_pop}, Preds={pred_pop}")

if __name__ == "__main__":
    run_predator_fix()