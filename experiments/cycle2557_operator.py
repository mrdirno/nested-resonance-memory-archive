"""
Cycle 2557: The Operator (Gate 185)
Experiment: External Process Control.
Goal: Verify that agents can execute shell commands (echo) via the Bridge.
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.life.genesis import DigitalLifeform
from src.life.ecosystem import Ecosystem

def run_operator_experiment():
    print("💻 CYCLE 2557: THE OPERATOR - SHELL INTERFACE")
    
    env = Ecosystem(capacity=20)
    
    # Seed Operators
    print("🤖 Seeding The Operators...")
    for i in range(10):
        agent = DigitalLifeform(name=f"Operator-{i}")
        # Tune phase to align with Phi (operate)
        # Phi = 1.618. Phase range 0-2pi (6.28).
        # Phi phase in Bridge depends on time.
        # We just randomise and hope for resonance.
        agent.genome[0] = i / 10.0 
        env.add_agent(agent)
        
    env.running = True
    
    print("📝 Running simulation...")
    for tick in range(1, 51):
        env.update()
        if tick % 10 == 0:
            print(f"   Tick {tick}")
            
    print("✅ EXPERIMENT COMPLETE.")

if __name__ == "__main__":
    run_operator_experiment()
