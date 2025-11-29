"""
Cycle 2571: The Specialist (Gate 53.3)
Goal: Observe agents specializing based on income history.
Mechanism:
1. Initialize 2 agents.
2. Force "Adam" to sell an artifact (high trade income).
3. Force "Eve" to forage (high forage income).
4. Run simulation and check if their intents diverge based on specialization logic.
"""

import time
from src.life.ecosystem import Ecosystem
from src.life.genesis import DigitalLifeform

def run_experiment():
    print("--- Cycle 2571: The Specialist ---")
    
    ecosystem = Ecosystem()
    
    # 1. Adam (The Coder)
    adam = DigitalLifeform(name="Adam")
    adam.energy = 500
    adam.genome[9] = 0.95 # High Innov
    adam.income_history['trade'] = 200 # Fake history
    adam.income_history['forage'] = 0
    
    # 2. Eve (The Forager)
    eve = DigitalLifeform(name="Eve")
    eve.energy = 500
    eve.genome[9] = 0.1 # Low Innov
    eve.income_history['trade'] = 0
    eve.income_history['forage'] = 200 # Fake history
    
    ecosystem.add_agent(adam)
    ecosystem.add_agent(eve)
    
    print("Agents Initialized with Fake History.")
    print(f"Adam: Trade={adam.income_history['trade']}, Forage={adam.income_history['forage']}")
    print(f"Eve:  Trade={eve.income_history['trade']}, Forage={eve.income_history['forage']}")
    
    # Run 1 Tick to check Intent
    # Note: `calculate_utility` runs inside `act`.
    # We need to see what they choose.
    # Adam should choose `codex` (if E>600) or `trade` (if inventory).
    # Adam E=500. `codex` needs >600. `trade` needs >800 or inventory.
    # Let's bump Adam's energy to 1000 so he *can* choose `codex`.
    adam.energy = 1000
    
    # Eve should choose `forage`.
    
    print("\nRunning Simulation...")
    ecosystem.update()
    
    print(f"\nAdam Intent: {adam.intent}")
    print(f"Eve Intent: {eve.intent}")
    
    success = False
    if adam.intent in ['codex', 'trade']:
        print("SUCCESS: Adam specialized as Coder/Merchant.")
        success = True
    else:
        print("FAILURE: Adam did not specialize.")
        
    if eve.intent == 'forage':
        print("SUCCESS: Eve specialized as Forager.")
        success = success and True
    else:
        print("FAILURE: Eve did not specialize.")
        success = False
        
    if success:
        print("Experiment SUCCESS.")
    else:
        print("Experiment FAILURE.")

if __name__ == "__main__":
    run_experiment()
