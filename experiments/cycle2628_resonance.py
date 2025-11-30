#!/usr/bin/env python3
"""
Experiment: Cycle 2628 - The Resonance
Goal: Agents grouping based on Phase Resonance (Bridge Similarity) rather than just spatial distance.
"""

import sys
import math
from pathlib import Path

# Add current directory to sys.path
sys.path.append(str(Path(__file__).parent))
sys.path.insert(0, str(Path("helios_one/src").resolve()))

try:
    from cycle2627_tether import TetheredAgent
    from cycle2602_hive import Vector2
    from bridge.transcendental_bridge import TranscendentalBridge, TranscendentalState
except ImportError:
    sys.exit(1)

class ResonantAgent(TetheredAgent):
    def __init__(self, agent_id: str, start_pos: Vector2, bridge: TranscendentalBridge):
        super().__init__(agent_id, start_pos, bridge)
        self.current_phase_state = None

    def update_phase(self):
        """Update internal phase state based on current position/status."""
        metrics = {
            'cpu_percent': self.position.x % 100,
            'memory_percent': self.position.y % 100,
            'disk_percent': self.speed
        }
        self.current_phase_state = self.bridge.reality_to_phase(metrics)

    def check_resonance(self, neighbor: 'ResonantAgent') -> float:
        """Calculate resonance with a neighbor."""
        if not self.current_phase_state or not neighbor.current_phase_state:
            return 0.0
            
        match = self.bridge.detect_resonance(self.current_phase_state, neighbor.current_phase_state)
        return match.similarity

def run_resonance_test():
    print("Cycle 2628: The Resonance - Phase Grouping")
    
    bridge = TranscendentalBridge()
    
    # Create two groups of agents with similar "Reality" (Position)
    # Group A: Near (10, 10)
    # Group B: Near (90, 90)
    
    group_a = [ResonantAgent(f"A_{i}", Vector2(10+i, 10+i), bridge) for i in range(3)]
    group_b = [ResonantAgent(f"B_{i}", Vector2(90+i, 90+i), bridge) for i in range(3)]
    
    all_agents = group_a + group_b
    
    # Update Phases
    for a in all_agents: a.update_phase()
    
    print("\nCalculating Resonance Matrix:")
    
    # Check resonance between A_0 and A_1 (Should be high)
    res_a_a = group_a[0].check_resonance(group_a[1])
    print(f"Resonance (A_0 <-> A_1): {res_a_a:.4f}")
    
    # Check resonance between A_0 and B_0 (Should be lower, different reality inputs)
    res_a_b = group_a[0].check_resonance(group_b[0])
    print(f"Resonance (A_0 <-> B_0): {res_a_b:.4f}")
    
    if res_a_a > res_a_b:
        print("SUCCESS: Resonance is spatially coherent (Reality-Grounded).")
    else:
        print("FAILURE: Resonance logic unclear.")
        sys.exit(1)

if __name__ == "__main__":
    run_resonance_test()
