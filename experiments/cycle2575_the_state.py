"""
Cycle 2575: The State (Gate 54.3)
Goal: Verify Taxation funding the Sheriff.
Mechanism:
1. Initialize Population (Taxpayers) and Sheriff.
2. Run simulation.
3. Verify Treasury grows from taxes.
4. Verify Sheriff receives salary from Treasury.
"""

import time
from src.life.ecosystem import Ecosystem
from src.life.genesis import DigitalLifeform

def run_experiment():
    print("--- Cycle 2575: The State ---")
    
    ecosystem = Ecosystem()
    
    # 1. Taxpayers (Rich)
    for i in range(5):
        citizen = DigitalLifeform(name=f"Citizen-{i}")
        citizen.energy = 1000 # Rich enough to pay tax
        # High altruism = vote for taxes?
        # Ecosystem.govern() checks agents > 1000 energy.
        # Voting logic: desired_tax = 0.05 * altruism.
        # Let's give them high altruism (Gene 5).
        while len(citizen.genome) < 11: citizen.genome.append(0.5)
        citizen.genome[5] = 1.0 # Max Altruism -> Vote for 5% Tax
        ecosystem.add_agent(citizen)
        
    # 2. Sheriff (Poor, relies on salary)
    sheriff = DigitalLifeform(name="Sheriff")
    sheriff.energy = 50 # Poor
    ecosystem.add_agent(sheriff)
    
    print(f"Initial Sheriff Energy: {sheriff.energy}")
    
    # Run
    for t in range(5):
        ecosystem.update()
        print(f"Tick {t}: Treasury={ecosystem.treasury:.1f}, Sheriff={sheriff.energy:.1f}")
        
    # Final Check
    # Taxpayers: 5 * 1000 * 0.05 = 250 revenue per tick.
    # Salary: 10 per tick.
    # Sheriff should gain ~10 per tick (minus metabolism).
    
    if sheriff.energy > 80:
        print("Experiment SUCCESS.")
    else:
        print("Experiment FAILURE.")

if __name__ == "__main__":
    run_experiment()
