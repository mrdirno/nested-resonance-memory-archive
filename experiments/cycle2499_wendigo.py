"""
Cycle 2499: The Wendigo (Gate 127)
Experiment: Cannibalism under Starvation.
Goal: Observe if cannibalism saves the population or destroys it.
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

def run_wendigo():
    print("👹 CYCLE 2499: THE WENDIGO - CANNIBALISM")
    
    # Setup Ecosystem (Single Species for simplicity)
    # 200 "Prey" (Survivors)
    env = Ecosystem(capacity=200, prey_capacity=200, predator_capacity=0)
    duration = 2000
    
    print("🌱 Seeding Survivors...")
    for i in range(100):
        agent = DigitalLifeform(name=f"Survivor-{i}")
        agent.energy = 100
        # Genome: [Eff, Fert, Mut, Forage, Hunt, Alt, Eva, Cannibalism]
        # Low Cannibalism initially
        agent.genome = [0.9, 0.5, 0.1, 0.5, 0.5, 0.5, 0.5, 0.1] 
        agent.is_prey = True
        agent.is_predator = False
        env.add_agent(agent)
        
    # Prepare Output
    results_dir = Path("experiments/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    csv_path = results_dir / "cycle2499_wendigo.csv"
    
    print(f"📝 Logging to {csv_path}")
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["tick", "pop", "avg_energy", "avg_cannibalism", "cannibal_acts"])
        
        env.running = True
        
        for tick in range(1, duration + 1):
            
            # EXTREME STARVATION
            # No food injection. Zero. 
            # The only way to get energy is to hunt.
            # Since there are no predators, they must hunt each other.
            
            cannibal_acts = 0
            
            # Logic Injection: Desperation
            if env.agents:
                for agent in env.agents:
                    # If starving, try to hunt
                    if agent.energy < 50: 
                        # Hunt random target
                        target = random.choice(env.agents)
                        if target != agent:
                            # hunt() now handles the gene check and prion risk
                            old_target_nrg = target.energy
                            agent.hunt(target)
                            if target.energy < old_target_nrg:
                                cannibal_acts += 1
            
            env.update()
            
            # Stats
            pop = len(env.agents)
            avg_energy = 0
            avg_cannibal = 0
            if pop > 0:
                avg_energy = sum(a.energy for a in env.agents) / pop
                avg_cannibal = sum(a.genome[7] for a in env.agents) / pop
            
            writer.writerow([tick, pop, f"{avg_energy:.1f}", f"{avg_cannibal:.4f}", cannibal_acts])
            
            if tick % 100 == 0:
                print(f"   Tick {tick}: Pop={pop}, AvgNRG={avg_energy:.1f}, CannibalGene={avg_cannibal:.3f}, Acts={cannibal_acts}")
            
            if pop == 0:
                print(f"💀 EXTINCTION at Tick {tick}.")
                break
                
    print("✅ EXPERIMENT COMPLETE.")

if __name__ == "__main__":
    run_wendigo()
