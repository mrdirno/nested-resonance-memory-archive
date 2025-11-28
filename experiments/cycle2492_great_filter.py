"""
Cycle 2492: The Great Filter (Gate 120)
Experiment: Drastically increase selection pressure (High Lethality).
Goal: Break stasis and force rapid adaptation or extinction.
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

def run_great_filter():
    print("🔥 CYCLE 2492: THE GREAT FILTER - HIGH LETHALITY")
    
    # Setup Ecosystem
    capacity = 200
    duration = 2000
    env = Ecosystem(capacity=capacity)
    
    # Seed Prey (High Efficiency baseline)
    print("🌱 Seeding Prey...")
    for i in range(150):
        agent = DigitalLifeform(name=f"Prey-{i}")
        agent.energy = 100
        # Genome: [Efficiency, Fertility, Mutation, Foraging, Hunting, Altruism...]
        # High Efficiency (0.8-0.9) to survive entropy
        agent.genome = [random.uniform(0.8, 0.95), random.uniform(0.3, 0.7), 0.1, 0.5, 0.1, 0.5]
        agent.genome.extend([0.5] * 4) 
        agent.is_prey = True
        agent.is_predator = False
        env.add_agent(agent)
        
    # Seed Predators
    print("🦈 Seeding Predators...")
    for i in range(20):
        agent = DigitalLifeform(name=f"Predator-{i}")
        agent.energy = 150
        # High Hunting (0.8-0.95) to survive low energy rewards
        agent.genome = [random.uniform(0.4, 0.6), random.uniform(0.3, 0.7), 0.1, 0.5, random.uniform(0.8, 0.95), 0.5]
        agent.genome.extend([0.5] * 4)
        agent.is_prey = False
        agent.is_predator = True
        env.add_agent(agent)
    
    # Prepare Output
    results_dir = Path("experiments/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    csv_path = results_dir / "cycle2492_great_filter.csv"
    
    print(f"📝 Logging to {csv_path}")
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["tick", "prey_pop", "pred_pop", "avg_prey_eff", "avg_prey_fert", "avg_pred_hunt", "avg_pred_eff"])
        
        env.running = True
        
        for tick in range(1, duration + 1):
            
            # Limited Food (Scarcity)
            if env.agents:
                prey_list = [a for a in env.agents if a.is_prey]
                if prey_list:
                    # Reduced feed rate: 20% instead of 40%
                    num_fed = max(1, int(len(prey_list) * 0.2)) 
                    for _ in range(num_fed):
                        # Forage reward is now 10 (hardcoded in genesis.py), so we just trigger forage logic or give energy
                        # genesis.py forage() gives 10 * efficiency.
                        # Here we simulate finding food source.
                        lucky_agent = random.choice(prey_list)
                        lucky_agent.forage() 
            
            # Predators Hunt
            predators = [a for a in env.agents if a.is_predator]
            prey_list = [a for a in env.agents if a.is_prey]
            
            for pred in predators:
                # Hunt if not full (threshold increased to 500 because costs are higher)
                if prey_list and pred.energy < 500: 
                    target = random.choice(prey_list)
                    pred.hunt(target)
                    if target.energy <= 0:
                        # Kill reward handled in hunt() method? 
                        # genesis.py hunt() adds 10 energy. 
                        # We can add a "meat" bonus here if the kill is successful to simulate consumption.
                        meat_energy = 50 
                        pred.energy += meat_energy
            
            env.update()
            
            # Collect Stats
            current_prey = [a for a in env.agents if a.is_prey]
            current_pred = [a for a in env.agents if a.is_predator]
            
            prey_pop = len(current_prey)
            pred_pop = len(current_pred)
            
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
                print(f"   Tick {tick}: Prey={prey_pop} (Eff={avg_prey_eff:.3f}), Preds={pred_pop} (Hunt={avg_pred_hunt:.3f})")
            
            if prey_pop == 0 and pred_pop == 0:
                print(f"💀 TOTAL EXTINCTION at Tick {tick}.")
                break
                
    print("✅ EXPERIMENT COMPLETE.")
    print(f"   Final Stats: Prey={prey_pop}, Preds={pred_pop}")

if __name__ == "__main__":
    run_great_filter()
