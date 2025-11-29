"""
Cycle 2570: The Price Signal (Gate 53.2)
Goal: Verify Dynamic Pricing.
Mechanism:
1. Scenario A: Desperate Merchant (E=100) vs Rich Buyer (E=2000).
   - Expect Ask=20, Bid=100. Trade happens at 20.
2. Scenario B: Greedy Merchant (E=1500) vs Poor Buyer (E=400).
   - Expect Ask=100, Bid=10. Trade FAILS.
"""

import time
from src.life.ecosystem import Ecosystem
from src.life.genesis import DigitalLifeform

def run_experiment():
    print("--- Cycle 2570: The Price Signal ---")
    
    # Scenario A: Fire Sale
    print("\n[SCENARIO A] Fire Sale")
    eco_a = Ecosystem()
    m1 = DigitalLifeform(name="DesperateMerchant")
    m1.energy = 100
    m1.inventory.append("cheap_code.py")
    m1.genome[9] = 0.9 # Enable trade intent
    
    b1 = DigitalLifeform(name="RichBuyer")
    b1.energy = 2500
    b1.genome[9] = 0.9
    b1.genome[1] = 0.01 # No reproduce
    
    eco_a.add_agent(m1)
    eco_a.add_agent(b1)
    
    # Force Proximity
    m1.x, m1.y = 10, 10
    b1.x, b1.y = 10, 10
    
    # Run Tick
    for i in range(10):
        print(f"Tick {i}: M={m1.intent} ({m1.x},{m1.y}), B={b1.intent} ({b1.x},{b1.y})")
        print(f"   Inv: M={m1.inventory}, B={b1.inventory}")
        eco_a.update()
        if "cheap_code.py" in b1.inventory:
            break
    
    # Check
    if "cheap_code.py" in b1.inventory:
        print(f"Artifact transferred.")
        print("SUCCESS: Trade occurred (Bid >= Ask).")
    else:
        print("FAILURE: Trade did not happen.")

    # Scenario B: Luxury Goods
    print("\n[SCENARIO B] Luxury Goods")
    eco_b = Ecosystem()
    m2 = DigitalLifeform(name="GreedyMerchant")
    m2.energy = 1500
    m2.inventory.append("expensive_code.py")
    m2.genome[9] = 0.9
    
    b2 = DigitalLifeform(name="PoorBuyer")
    b2.energy = 400
    b2.genome[9] = 0.9
    b2.genome[1] = 0.01
    
    eco_b.add_agent(m2)
    eco_b.add_agent(b2)
    
    m2.x, m2.y = 10, 10
    b2.x, b2.y = 10, 10
    
    # Run Tick
    eco_b.update()
    
    if "expensive_code.py" in b2.inventory:
        print("FAILURE: Trade happened despite Bid < Ask.")
    else:
        print("SUCCESS: Trade failed (Price too high).")

if __name__ == "__main__":
    run_experiment()
