"""
Cycle 2493: The Trophic Ladder (Gate 121)
Experiment: Implement Trophic Levels to allow Predator evolution.
Goal: Observe Predator adaptation when ecological niches are reserved.
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

def run_trophic_levels():
    print("🪜 CYCLE 2493: THE TROPHIC LADDER - NICHE PARTITIONING")
    
    # Setup Ecosystem with Trophic Levels
    # Total 250: 200 Prey, 50 Predators
    env = Ecosystem(capacity=250, prey_capacity=200, predator_capacity=50)
    duration = 2000
    
    # Seed Prey (High Efficiency baseline from C2492)
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
        agent.energy = 150
        # High Hunting (0.8-0.95)
        agent.genome = [random.uniform(0.4, 0.6), random.uniform(0.3, 0.7), 0.1, 0.5, random.uniform(0.8, 0.95), 0.5]
        agent.genome.extend([0.5] * 4)
        agent.is_prey = False
        agent.is_predator = True
        env.add_agent(agent)
    
    # Prepare Output
    results_dir = Path("experiments/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    csv_path = results_dir / "cycle2493_trophic_levels.csv"
    
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
            
            # Predators Hunt
            # Note: In C2492 we injected logic here.
            # We need to do the same because genesis.py's hunt() is passive (just method definition).
            # Wait, ecosystem.py update() now calls agent.act().
            # But agent.act() in genesis.py doesn't set 'hunt' intent autonomously yet (it says "Ecosystem handles...").
            # And ecosystem.py update() ONLY calls hunt() if agent.intent == 'hunt'.
            # So we MUST force intent or inject hunting here.
            
            # Let's force intent for predators if hungry
            for agent in env.agents:
                if agent.is_predator and agent.energy < 500:
                    agent.intent = 'hunt'
            
            # Actually, ecosystem.py update() logic for predators is:
            # if agent.intent == 'hunt': find target, agent.hunt(target)
            # So setting intent is enough!
            # BUT, genesis.py act() overwrites intent based on brain.decide().
            # We haven't trained the brain.
            # So let's stick to the manual injection loop from C2492 to be safe and consistent.
            
            # Update: ecosystem.py update() calls act(), THEN checks intent.
            # So if we set intent here, it might be overwritten by act() if act() is called inside update().
            # Yes, update() calls act().
            # So we should inject hunting explicitly in this loop AFTER update() or BEFORE?
            # In C2492 we did it *before* update().
            # But ecosystem.py *also* has a predator phase.
            # Let's rely on C2492's explicit loop for consistency.
            
            predators = [a for a in env.agents if a.is_predator]
            prey_list = [a for a in env.agents if a.is_prey]
            
            for pred in predators:
                if prey_list and pred.energy < 500: 
                    target = random.choice(prey_list)
                    pred.hunt(target)
                    if target.energy <= 0:
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
    run_trophic_levels()
