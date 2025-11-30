#!/usr/bin/env python3
"""
Experiment: Cycle 2635 - The Bridge 2.0
Goal: Advanced Transcendental Bridge accepting complex feedback structures.
"""

import sys
import json
from pathlib import Path

# Add helios_one/src to path
sys.path.append(str(Path("helios_one/src").resolve()))

try:
    from bridge.transcendental_bridge import TranscendentalBridge, TranscendentalState
except ImportError:
    sys.exit(1)

class AdvancedBridge(TranscendentalBridge):
    """
    Bridge 2.0: Handles JSON state objects for deep resonance.
    """
    def reality_to_phase_complex(self, complex_state: dict) -> TranscendentalState:
        """
        Maps a complex JSON state (e.g. entire Swarm snapshot) to phase space.
        """
        # Flatten metrics
        # We need to extract scalar values from the complex structure
        # Example: Sum of all agent positions, or average velocities
        
        cpu_proxy = 0.0
        mem_proxy = 0.0
        disk_proxy = 0.0
        
        if "agents" in complex_state:
            count = len(complex_state["agents"])
            if count > 0:
                # CPU -> Average X
                cpu_proxy = sum(a['x'] for a in complex_state["agents"]) / count
                # MEM -> Average Y
                mem_proxy = sum(a['y'] for a in complex_state["agents"]) / count
                # DISK -> Count
                disk_proxy = float(count)
        
        metrics = {
            'cpu_percent': cpu_proxy % 100,
            'memory_percent': mem_proxy % 100,
            'disk_percent': disk_proxy
        }
        
        return self.reality_to_phase(metrics)

def run_bridge_v2_test():
    print("Cycle 2635: The Bridge 2.0 - Complex Grounding")
    
    bridge = AdvancedBridge()
    
    # Mock complex swarm state
    swarm_state = {
        "timestamp": 123456789,
        "target": {"x": 50, "y": 50},
        "agents": [
            {"id": "A1", "x": 10, "y": 10},
            {"id": "A2", "x": 20, "y": 20},
            {"id": "A3", "x": 30, "y": 30}
        ]
    }
    
    print("Input State: Complex JSON Object")
    state = bridge.reality_to_phase_complex(swarm_state)
    
    print(f"Output Phase: pi={state.pi_phase:.4f}, e={state.e_phase:.4f}")
    
    if state.magnitude > 0:
        print("SUCCESS: Complex state successfully mapped to Transcendental Phase.")
    else:
        print("FAILURE: Zero magnitude output.")
        sys.exit(1)

if __name__ == "__main__":
    run_bridge_v2_test()
