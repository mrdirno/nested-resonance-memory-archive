"""
Cycle 2491: Co-Evolutionary Pressure Test (Gate 119)
Role: The Evolutionary Biologist
Responsibility: Test Co-Evolution (Predation + Entropy).

Objective:
- Run for 1000 ticks.
- Environment: Seasonality + Entropy (1% Tax).
- Mechanism: Predators hunt the WEAKEST prey (lowest energy).
- Hypothesis: Efficiency -> Higher Energy -> Survival.
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

class CoEvolutionEcosystem(Ecosystem):
    def update(self):
        # Override update to implement specific hunting logic
        # 1. Remove dead agents
        self.agents = [a for a in self.agents if a.alive]
        
        # 2. Process Actions
        # Shuffle to prevent order bias
        random.shuffle(self.agents)
        
        prey_agents = [a for a in self.agents if a.is_prey]
        
        for agent in self.agents:
            if not agent.alive: continue
            
            # Hunting Logic
            if agent.is_predator and agent.intent == 'hunt':
                # Target the WEAKEST prey (Lowest Energy)
                if prey_agents:
                    # Sort by energy (ascending)
                    weakest = sorted(prey_agents, key=lambda x: x.energy)
                    # Pick one of the bottom 3 to add some noise
                    target = random.choice(weakest[:3])
                    
                    if target.alive:
                        agent.hunt(target)
                        if target.energy <= 0:
                            target.die()
                            
            # Standard Lifecycle
            # We manually call metabolize and act since live() is a blocking loop
            agent.metabolize()
            result = agent.act()
            
            # Handle Reproduction
            if agent.intent == 'reproduce':
                child = agent.reproduce()
                if child:
                    self.add_agent(child)
                    
        # 3. Global checks (Capacity)
        if len(self.agents) > self.capacity:
            # Random cull? Or age based?
            # Let's cull random for now to simulate overcrowding
            over = len(self.agents) - self.capacity
            for _ in range(over):
                victim = random.choice(self.agents)
                victim.die()

def run_coevolution():
    print("⚔️ CYCLE 2491: CO-EVOLUTIONARY PRESSURE TEST")
    
    # Setup
    capacity = 100
    duration = 1000
    env = CoEvolutionEcosystem(capacity=capacity)
    
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
    csv_path = results_dir / "cycle2491_coevolution.csv"
    
    print(f"📝 Logging to {csv_path}")
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["tick", "season_factor", "prey_pop", "pred_pop", "avg_prey_energy", "avg_efficiency"])
        
        # Simulation Loop
        env.running = True
        for tick in range(1, duration + 1):
            # --- SEASONALITY ---
            season_factor = 0.5 + 0.5 * math.sin(2 * math.pi * tick / 100)
            
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
                print(f"   Tick {tick}: Prey={prey_pop}, Pred={pred_pop}, Eff={avg_eff:.3f}, Energy={avg_prey_e:.1f}")
            
            if len(env.agents) == 0:
                print("💀 TOTAL EXTINCTION.")
                break
                
    print("✅ CO-EVOLUTION SIMULATION COMPLETE.")
    print(f"   Final: Prey={prey_pop}, Pred={pred_pop}, Eff={avg_eff:.3f}")

if __name__ == "__main__":
    run_coevolution()
