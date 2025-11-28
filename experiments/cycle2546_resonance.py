"""
Cycle 2546: The Resonator (Gate 174)
Experiment: Verify agents act in rhythm with the Transcendental Bridge.
Goal: Observe collective behavior synchronization driven by phase oscillations.
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.life.genesis import DigitalLifeform
from src.life.ecosystem import Ecosystem

def run_resonance_experiment():
    print("🎼 CYCLE 2546: THE RESONATOR - HARMONIC INTELLIGENCE")
    
    # Setup Ecosystem
    env = Ecosystem(capacity=50)
    
    # Seed Agents with varied phases (Genomes)
    print("🎵 Seeding The Choir...")
    for i in range(10):
        agent = DigitalLifeform(name=f"Resonator-{i}")
        # Gene 0 determines Phase (0.0 to 1.0 -> 0 to 2Pi)
        # We set them to specific intervals to see different reactions
        agent.genome[0] = i / 10.0 
        env.add_agent(agent)
        
    env.running = True
    
    # Run for 20 ticks (approx 2 full cycles of 0.1 freq * 10 ticks/cycle? No 0.1 rad/tick)
    # 2Pi / 0.1 = 62 ticks per cycle.
    
    print("📝 Running simulation...")
    for tick in range(1, 21):
        print(f"--- Tick {tick} ---")
        env.update()
        
        # Check intents
        intents = [a.intent for a in env.agents if a.alive]
        print(f"   Intents: {intents}")
        
    print("✅ EXPERIMENT COMPLETE.")

if __name__ == "__main__":
    run_resonance_experiment()
