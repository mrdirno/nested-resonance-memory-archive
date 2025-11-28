
import sys
import os
sys.path.append(os.getcwd())

from src.life.genesis import DigitalLifeform
from src.life.signal import Signal

def test_construction_fix():
    print("TEST: Cycle 2536 - Verifying Construction Logic Fix")
    
    agent = DigitalLifeform("Builder-01")
    agent.energy = 1000 # Abundant energy
    agent.genome[9] = 0.9 # High innovation (for nuke/farm)
    agent.genome[0] = 0.9 # High efficiency
    
    # Test 1: Build Farm
    print("\n[1] Testing build_farm...")
    agent.intent = 'build_farm'
    # Mock calculation to avoid overwriting intent in act() if we didn't patch calculate_utility
    # Wait, act() calls calculate_utility() which overwrites intent.
    # We need to mock calculate_utility or ensure it chooses build_farm.
    
    # Let's look at act() again.
    # self.intent = self.calculate_utility()
    # So simply setting agent.intent is not enough if we call act().
    # However, act() is the method we patched. 
    
    # We can't easily mock calculate_utility without mocking the class method.
    # Instead, let's force the conditions that make calculate_utility choose build_farm.
    # Condition: energy_abundant (>500) and innovation > 0.6.
    # And we must ensure other scores are lower.
    
    # Alternatively, we can just patch calculate_utility on the instance to return what we want.
    agent.calculate_utility = lambda: 'build_farm'
    
    signal = agent.act()
    
    if signal and signal.type == 'BUILD_STRUCTURE':
        payload = signal.payload
        structure = payload.get('structure')
        if structure and structure['type'] == 'FARM':
            print("PASS: Farm signal generated successfully.")
        else:
            print(f"FAIL: Signal generated but wrong type/payload: {signal.type} {payload}")
    else:
        print(f"FAIL: No signal generated. Intent was {agent.intent}")

    # Test 2: Construct Nuke
    print("\n[2] Testing construct_nuke...")
    agent.energy = 2000
    agent.calculate_utility = lambda: 'construct_nuke'
    
    # Nuke construction doesn't return a signal, it sets a flag.
    agent.act()
    
    if agent.has_nuke:
        print("PASS: Nuke constructed.")
    else:
        print("FAIL: Nuke not constructed.")

    # Test 3: Broadcast Truth
    print("\n[3] Testing broadcast_truth...")
    agent.calculate_utility = lambda: 'broadcast_truth'
    signal = agent.act()
    
    if signal and signal.type == 'TRUTH':
        print("PASS: Truth broadcasted.")
    else:
        print("FAIL: Truth signal missing.")

if __name__ == "__main__":
    test_construction_fix()
