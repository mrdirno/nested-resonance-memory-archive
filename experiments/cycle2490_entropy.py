"""
Cycle 2490: The Great Depression (Gate 118)
Role: The Economist
Responsibility: Test Entropy (Metabolic Tax).

Objective:
- Run for 1000 ticks.
- Tick 0-500: Abundance (Seasonality) + Entropy.
- Tick 500-1000: Drought (80% reduction) + Entropy.
- Hypothesis: Entropy prevents hoarding, making the Drought lethal for inefficient agents.
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
        while len(self.genome) < 5:
            self.genome.append(0.5)
        self.genome[4] = 0.8 

    def act(self):
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

def run_entropy():
    print("📉 CYCLE 2490: THE GREAT DEPRESSION (ENTROPY)")
    
    # Setup
    capacity = 100
    duration = 1000
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
        agent.energy = 200
        env.add_agent(agent)
        
    # Prepare Output
    results_dir = Path("experiments/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    csv_path = results_dir / "cycle2490_entropy.csv"
    
    print(f"📝 Logging to {csv_path}")
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["tick", "season_factor", "prey_pop", "pred_pop", "avg_prey_energy", "avg_efficiency"])
        
        # Simulation Loop
        env.running = True
        for tick in range(1, duration + 1):
            # --- SEASONALITY & DROUGHT ---
            
            if tick < 500:
                # Normal Seasonality
                season_factor = 0.5 + 0.5 * math.sin(2 * math.pi * tick / 100)
            else:
                # THE DROUGHT
                # Reduce to 20% of normal seasonality
                season_factor = (0.5 + 0.5 * math.sin(2 * math.pi * tick / 100)) * 0.2
            
            # Feed Prey
            prey_agents = [a for a in env.agents if a.is_prey]
            
            if prey_agents:
                food_abundance = int(len(prey_agents) * 0.5 * season_factor)
                for _ in range(food_abundance):
                    lucky_agent = random.choice(prey_agents)
                    lucky_agent.energy += 20 
            
            env.update()
            
            # Collect Stats
            prey_pop = len([a for a in env.agents if a.is_prey])
            pred_pop = len([a for a in env.agents if a.is_predator])
            
            if prey_pop > 0:
                avg_prey_e = sum(a.energy for a in env.agents if a.is_prey) / prey_pop
                avg_eff = sum(a.genome[0] for a in env.agents if a.is_prey) / prey_pop
            else:
                avg_prey_e = 0
                avg_eff = 0
                
            writer.writerow([tick, f"{season_factor:.2f}", prey_pop, pred_pop, f"{avg_prey_e:.1f}", f"{avg_eff:.4f}"])
            
            # Console Feedback
            if tick % 100 == 0:
                status = "ABUNDANCE" if tick < 500 else "DROUGHT"
                print(f"   Tick {tick} ({status}): Prey={prey_pop}, Eff={avg_eff:.3f}, Energy={avg_prey_e:.1f}")
            
            if len(env.agents) == 0:
                print("💀 TOTAL EXTINCTION.")
                break
                
    print("✅ ENTROPY SIMULATION COMPLETE.")
    print(f"   Final: Prey={prey_pop}, Eff={avg_eff:.3f}")

if __name__ == "__main__":
    run_entropy()
