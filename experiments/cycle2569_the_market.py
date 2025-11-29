"""
Cycle 2569: The Market (Gate 53.1)
Goal: Verify agents can trade Energy for Artifacts.
Mechanism:
1. Initialize "Merchant" (Has Artifact, Wants Energy) and "Buyer" (Has Energy, Wants Artifact).
2. Run simulation.
3. Verify artifact transfer and energy transfer.
"""

import time
from src.life.ecosystem import Ecosystem
from src.life.genesis import DigitalLifeform

def run_experiment():
    print("--- Cycle 2569: The Market ---")
    
    ecosystem = Ecosystem()
    
    # 1. Merchant (Has Artifact, Low Energy)
    merchant = DigitalLifeform(name="Merchant")
    while len(merchant.genome) < 11: merchant.genome.append(0.5)
    merchant.genome[9] = 0.99 # High Innov
    merchant.energy = 100 # Low Energy (Needs to sell)
    # Give artifact
    merchant.inventory.append("rare_algorithm.py")
    
    # 2. Buyer (High Energy)
    buyer = DigitalLifeform(name="Buyer")
    while len(buyer.genome) < 11: buyer.genome.append(0.5)
    buyer.genome[9] = 0.99 # High Innov (Appreciates Art)
    buyer.genome[1] = 0.01 # Low Fertility
    buyer.energy = 3000 # High Energy (Rich)
    
    ecosystem.add_agent(merchant)
    ecosystem.add_agent(buyer)
    
    # Force position overlap
    merchant.x = 10
    merchant.y = 10
    buyer.x = 10
    buyer.y = 10
    
    print(f"Initial State:")
    print(f"Merchant: E={merchant.energy}, Inv={merchant.inventory}")
    print(f"Buyer:    E={buyer.energy}, Inv={buyer.inventory}")
    
    # Run
    print("\nRunning Simulation...")
    for i in range(20):
        ecosystem.update()
        print(f"Tick {i}: M.Intent={merchant.intent}, B.Intent={buyer.intent}")
        
        # Check for success
        if "rare_algorithm.py" in buyer.inventory:
            print("\nSUCCESS: Artifact transferred!")
            break
            
    print(f"\nFinal State:")
    print(f"Merchant: E={merchant.energy}, Inv={merchant.inventory}")
    print(f"Buyer:    E={buyer.energy}, Inv={buyer.inventory}")
    
    if "rare_algorithm.py" in buyer.inventory and merchant.energy > 100:
        print("Experiment SUCCESS.")
    else:
        print("Experiment FAILURE.")

if __name__ == "__main__":
    run_experiment()
