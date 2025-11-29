"""
Cycle 2577: The Corporation (Gate 55.1)
Goal: Verify agents can found a corporation.
Mechanism:
1. Initialize a Tycoon (High Innov, High Energy).
2. Run simulation.
3. Check if Tycoon founds a corp.
4. Check if Corp exists in Ecosystem.
"""

import time
from src.life.ecosystem import Ecosystem
from src.life.genesis import DigitalLifeform

def run_experiment():
    print("--- Cycle 2577: The Corporation ---")
    
    ecosystem = Ecosystem()
    
    # 1. Tycoon
    tycoon = DigitalLifeform(name="Tycoon")
    while len(tycoon.genome) < 11: tycoon.genome.append(0.5)
    tycoon.genome[9] = 0.99 # Innov
    tycoon.energy = 3000 # Rich
    tycoon.genome[1] = 0.01 # No kids
    
    ecosystem.add_agent(tycoon)
    
    print(f"Tycoon Initialized. E={tycoon.energy}")
    
    # Run
    found = False
    for i in range(5):
        ecosystem.update()
        # Check intents
        print(f"Tick {i}: Tycoon Intent={tycoon.intent}")
        
        if ecosystem.institutions:
            print(f"Institutions: {[i.name for i in ecosystem.institutions]}")
            found = True
            break
            
    if found:
        print("Experiment SUCCESS.")
    else:
        print("Experiment FAILURE.")

if __name__ == "__main__":
    run_experiment()
