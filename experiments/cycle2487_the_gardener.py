"""
Cycle 2487: The Gardener (Gate 115)
Role: The Ecologist
Responsibility: Introduce Predation and Seasonality.

Objective:
- Run for 500 ticks.
- Introduce "Predator" agents.
- Introduce "Seasons" (Variable Food).
- Observe Lotka-Volterra dynamics.
"""

import sys
import os
import csv
import math
import random
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.life.genesis import DigitalLifeform
from src.life.ecosystem import Ecosystem

class Predator(DigitalLifeform):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.is_predator = True
        self.is_prey = False
        self.name = f"Wolf-{self.id}"
        # Predators are better at hunting
        # Ensure genome has enough elements
        while len(self.genome) < 5:
            self.genome.append(0.5)
        self.genome[4] = 0.8 # High hunting efficiency

    def act(self):
        # Override act to prioritize hunting
        # If hungry, hunt. If full, maybe reproduce.
        
        # Threshold for reproduction
        if self.energy > 400:
             self.intent = 'reproduce'
        else:
             self.intent = 'hunt'
             
        return None

class Prey(DigitalLifeform):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.is_predator = False
        self.is_prey = True
        self.name = f"Sheep-{self.id}"

def run_garden():
    print("🌿 CYCLE 2487: THE GARDENER")
    
    # Setup
    capacity = 100
    duration = 500
    env = Ecosystem(capacity=capacity)
    
    # Seed Prey
    print("🐑 Seeding Prey...")
    for i in range(40):
        agent = Prey()
        agent.energy = 100
        env.add_agent(agent)
        
    # Seed Predators
    print("🐺 Seeding Predators...")
    for i in range(5):
        agent = Predator()
        agent.energy = 200 # Predators need a buffer
        env.add_agent(agent)
        
    # Prepare Output
    results_dir = Path("experiments/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    csv_path = results_dir / "cycle2487_garden.csv"
    
    print(f"📝 Logging to {csv_path}")
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["tick", "season_factor", "prey_pop", "pred_pop", "avg_prey_energy", "avg_pred_energy"])
        
        # Simulation Loop
        env.running = True
        for tick in range(1, duration + 1):
            # --- SEASONALITY ---
            # Sinusoidal food availability
            # Period = 100 ticks
            season_factor = 0.5 + 0.5 * math.sin(2 * math.pi * tick / 100)
            
            # Feed Prey (Plants grow based on season)
            # Base food = 20% of prey pop
            # Season factor modifies probability or amount
            
            prey_agents = [a for a in env.agents if a.is_prey]
            pred_agents = [a for a in env.agents if a.is_predator]
            
            if prey_agents:
                # Food abundance depends on season
                # Max 50% of pop gets food in high summer, 0% in deep winter
                food_abundance = int(len(prey_agents) * 0.5 * season_factor)
                for _ in range(food_abundance):
                    lucky_agent = random.choice(prey_agents)
                    lucky_agent.energy += 20 # Grass is nutritious
            
            env.update()
            
            # Collect Stats
            prey_pop = len([a for a in env.agents if a.is_prey])
            pred_pop = len([a for a in env.agents if a.is_predator])
            
            if prey_pop > 0:
                avg_prey_e = sum(a.energy for a in env.agents if a.is_prey) / prey_pop
            else:
                avg_prey_e = 0
                
            if pred_pop > 0:
                avg_pred_e = sum(a.energy for a in env.agents if a.is_predator) / pred_pop
            else:
                avg_pred_e = 0
                
            writer.writerow([tick, f"{season_factor:.2f}", prey_pop, pred_pop, f"{avg_prey_e:.1f}", f"{avg_pred_e:.1f}"])
            
            # Console Feedback
            if tick % 50 == 0:
                print(f"   Tick {tick} (Season {season_factor:.2f}): Prey={prey_pop}, Pred={pred_pop}")
            
            if len(env.agents) == 0:
                print("💀 TOTAL EXTINCTION.")
                break
                
    print("✅ GARDEN SIMULATION COMPLETE.")
    print(f"   Final: Prey={prey_pop}, Pred={pred_pop}")

if __name__ == "__main__":
    run_garden()
