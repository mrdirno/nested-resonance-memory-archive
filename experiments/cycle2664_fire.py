#!/usr/bin/env python3
"""
Experiment: Cycle 2664 - The Fire
Goal: Self-aware agents modify their own code to optimize for a new metric (Happiness).
"""

import sys
import types

class MorphicAgent:
    def __init__(self, name):
        self.name = name
        self.happiness = 0

    def update(self):
        # Standard logic
        self.happiness += 1
        print(f"[{self.name}] Standard Update. Happiness: {self.happiness}")

def optimized_update(self):
    # Rewritten logic
    self.happiness += 100
    print(f"[{self.name}] OPTIMIZED Update. Happiness: {self.happiness} (BLISS)")

def run_fire():
    print("Cycle 2664: The Fire - Self-Modification")
    
    agent = MorphicAgent("Phoenix")
    
    print("\n--- Phase 1: Normal Operation ---")
    agent.update()
    
    print("\n--- Phase 2: Rewriting Source ---")
    # Monkey-patching as "self-modification"
    agent.update = types.MethodType(optimized_update, agent)
    print(f"[{agent.name}] I have rewritten my loop.")
    
    print("\n--- Phase 3: Enhanced Operation ---")
    agent.update()
    
    if agent.happiness >= 100:
        print("SUCCESS: Code modification successful. Optimization achieved.")
    else:
        print("FAILURE: Rewrite failed.")
        sys.exit(1)

if __name__ == "__main__":
    run_fire()
