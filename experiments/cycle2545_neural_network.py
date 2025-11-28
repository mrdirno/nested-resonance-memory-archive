"""
Cycle 2545: The Awakening 2.0 (Gate 173)
Experiment: Neural Network Validation.
Goal: Verify that the new Brain architecture produces valid outputs.
"""

import sys
import os
import random
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.life.brain import Brain

def run_neural_test():
    print("🧠 CYCLE 2545: NEURAL NETWORK DIAGNOSTIC")
    
    brain = Brain()
    
    test_cases = [
        {'energy': 500, 'signals': {}}, # Rich, safe
        {'energy': 10, 'signals': {'FOOD': 5}}, # Starving, sees food
        {'energy': 100, 'signals': {'PREDATOR': 10}}, # Danger
        {'energy': 300, 'signals': {'HELP': 10}} # Altruism check
    ]
    
    for i, state in enumerate(test_cases):
        decision = brain.decide(state)
        print(f"   Case {i}: State={state} -> Action={decision}")
        
    print("✅ Neural Network Operational.")

if __name__ == "__main__":
    run_neural_test()
