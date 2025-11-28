"""
Cycle 2491: The Arms Race (Gate 119)
Experiment: Re-introduce Predators to efficient Prey.
Goal: Observe co-evolutionary dynamics (Red Queen Hypothesis).
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

def run_arms_race_experiment():
    print("⚔️ CYCLE 2491: THE ARMS RACE - CO-EVOLUTION")
    
    # Setup Ecosystem
    capacity = 200
    duration = 2000
    env = Ecosystem(capacity=capacity)
    
    # Seed Prey (Survivors of The Great Depression)
    print("🌱 Seeding Efficient Prey...")
    for i in range(100):
        agent = DigitalLifeform(name=f"Prey-{i}")
        agent.energy = 100
        # Genome: [Efficiency, Fertility, Mutation, Foraging, Hunting, Altruism, ...]
        # High Efficiency (0.8-0.9), Medium others
        agent.genome = [random.uniform(0.8, 0.95), random.uniform(0.3, 0.7), 0.1, 0.5, 0.1, 0.5]
        agent.genome.extend([0.5] * 4) # Fill to 10
        agent.is_prey = True
        agent.is_predator = False
        env.add_agent(agent)
        
    # Seed Predators
    print("🦈 Seeding Hunters...")
    for i in range(10):
        agent = DigitalLifeform(name=f"Predator-{i}")
        agent.energy = 150 # Higher start energy
        # High Hunting (0.8-0.95), Lower Efficiency (0.4-0.6)
        agent.genome = [random.uniform(0.4, 0.6), random.uniform(0.3, 0.7), 0.1, 0.5, random.uniform(0.8, 0.95), 0.5]
        agent.genome.extend([0.5] * 4)
        agent.is_prey = False # Predators don't eat each other (yet)
        agent.is_predator = True
        env.add_agent(agent)
    
    # Prepare Output
    results_dir = Path("experiments/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    csv_path = results_dir / "cycle2491_arms_race.csv"
    
    print(f"📝 Logging to {csv_path}")
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["tick", "prey_pop", "pred_pop", "avg_prey_eff", "avg_prey_fert", "avg_pred_hunt", "avg_pred_eff"])
        
        env.running = True
        
        for tick in range(1, duration + 1):
            
            # Environmental Conditions (Standard Abundance with Entropy)
            # Food for Prey
            if env.agents:
                prey_list = [a for a in env.agents if a.is_prey]
                if prey_list:
                    num_fed = max(1, int(len(prey_list) * 0.4)) # 40% feed rate
                    for _ in range(num_fed):
                        random.choice(prey_list).energy += 20
            
            # Predators Hunt (Logic is in agent.act(), but we need to ensure they have targets)
            # Ecosystem.update() calls agent.act()
            
            # Manual Hunting Logic Injection (if not in act)
            # genesis.py act() has: elif self.intent == 'hunt': pass
            # So we need to inject the hunt intent or logic here if genesis.py doesn't handle it fully.
            # genesis.py says: "Ecosystem handles the actual hunting logic for now."
            # But ecosystem.py update() just calls agent.act().
            # Let's force predators to hunt if they are hungry.
            
            predators = [a for a in env.agents if a.is_predator]
            prey_list = [a for a in env.agents if a.is_prey]
            
            for pred in predators:
                # Metabolic cost applies to everyone
                # Hunting logic:
                if prey_list and pred.energy < 400: # Hunt if not full
                    target = random.choice(prey_list)
                    pred.hunt(target)
                    if target.energy <= 0:
                        # Kill confirmed
                        pred.energy += 40 # Bonus for kill
                        # print(f"☠️ {pred.name} killed {target.name}")
            
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
            
            if prey_pop == 0:
                print(f"💀 PREY EXTINCTION at Tick {tick}.")
                break
            if pred_pop == 0:
                print(f"🕊️ PREDATOR EXTINCTION at Tick {tick}.")
                # Continue to see if prey drift back? No, usually end.
                # But maybe prey evolve? Let's keep running if only predators die.
                
    print("✅ EXPERIMENT COMPLETE.")
    print(f"   Final Stats: Prey={prey_pop}, Preds={pred_pop}")

if __name__ == "__main__":
    run_arms_race_experiment()
