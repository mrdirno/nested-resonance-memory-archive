#!/usr/bin/env python3
"""
Experiment: Cycle 2627 - The Tether
Goal: Drive agent mutation using Transcendental Bridge entropy instead of PRNG.
"""

import sys
import random
from pathlib import Path

# Add current directory to sys.path
sys.path.append(str(Path(__file__).parent))
# Add helios_one/src to path for Bridge
sys.path.insert(0, str(Path("helios_one/src").resolve()))

try:
    from cycle2612_mutator import MutatingAgent
    from cycle2602_hive import Vector2
    from bridge.transcendental_bridge import TranscendentalBridge
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)

class TetheredAgent(MutatingAgent):
    def __init__(self, agent_id: str, start_pos: Vector2, bridge: TranscendentalBridge):
        super().__init__(agent_id, start_pos)
        self.bridge = bridge
        # Each agent tracks its own oscillator offset to sample different "parts" of the transcendental field
        self.bridge_offset = random.random() * 100 

    def mutate_via_entropy(self, rate: float = 0.1):
        """
        Adjust parameters using Transcendental Phase.
        """
        # 1. Sample Bridge
        # We use our ID or position as "Reality" input to get a deterministic but chaotic phase
        metrics = {
            'cpu_percent': self.position.x % 100,
            'memory_percent': self.position.y % 100,
            'disk_percent': self.speed
        }
        state = self.bridge.reality_to_phase(metrics)
        
        # 2. Use Phase (pi, e, phi) to drive mutation
        # Pi phase -> Speed mutation
        # E phase -> Range mutation
        
        # Normalize phase [-PI, PI] -> [-1, 1]
        pi_factor = (state.pi_phase / 3.14159) - 1.0
        e_factor = (state.e_phase / 3.14159) - 1.0
        
        # Apply mutation
        speed_change = pi_factor * rate
        range_change = e_factor * rate
        
        self.speed = max(0.5, self.speed + speed_change)
        self.sensor_range = max(5.0, self.sensor_range + range_change)
        
        return state.magnitude

def run_tether_experiment():
    print("Cycle 2627: The Tether - Reality-Driven Mutation")
    
    bridge = TranscendentalBridge()
    agents = [TetheredAgent(f"tether_{i}", Vector2(10,10), bridge) for i in range(5)]
    
    print("Initial Parameters:")
    for a in agents:
        print(f"  {a.agent_id}: Speed={a.speed:.2f}, Range={a.sensor_range:.2f}")
        
    print("\nApplying Transcendental Mutation (5 steps)...")
    
    for step in range(5):
        print(f"Step {step}:")
        for a in agents:
            # Move slightly to change 'reality' input
            a.position.x += 1.0
            mag = a.mutate_via_entropy(rate=0.5)
            print(f"  {a.agent_id}: Speed -> {a.speed:.2f} (Mag: {mag:.2f})")
            
    print("\nSUCCESS: Mutation driven by NRM Bridge.")

if __name__ == "__main__":
    run_tether_experiment()
