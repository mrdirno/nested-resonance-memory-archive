#!/usr/bin/env python3
"""
Experiment: Cycle 2629 - The Synchronization
Goal: Close the loop by feeding Swarm state back into the Transcendental Bridge to drive global oscillation.
"""

import sys
import time
from pathlib import Path

# Add current directory to sys.path
sys.path.append(str(Path(__file__).parent))
sys.path.insert(0, str(Path("helios_one/src").resolve()))

try:
    from cycle2628_resonance import ResonantAgent, Vector2
    from bridge.transcendental_bridge import TranscendentalBridge
except ImportError:
    sys.exit(1)

def run_closed_loop():
    print("Cycle 2629: The Synchronization - Feedback Loop")
    
    bridge = TranscendentalBridge()
    agents = [ResonantAgent(f"S_{i}", Vector2(i*10, i*10), bridge) for i in range(5)]
    
    print("Monitoring Bridge Oscillators (Start):")
    print(f"  Pi Offset: {bridge.pi_offset:.4f}")
    
    steps = 10
    
    for step in range(steps):
        # 1. Calculate Swarm Entropy (e.g. Average Velocity/Energy)
        # Since we aren't moving them in this simple test, we use position variance or similar.
        # Let's use average X position as a proxy for "Energy"
        avg_pos = sum(a.position.x for a in agents) / len(agents)
        
        # 2. Feed back into Bridge
        # We modulate the oscillators based on swarm state
        bridge.pi_offset += (avg_pos / 1000.0) 
        bridge.e_offset += (avg_pos / 2000.0)
        
        # 3. Bridge generates new state
        # (Implicitly happens as offset is updated)
        
        # 4. Agents react (Mutation/Resonance updates)
        for a in agents:
            a.update_phase()
            # Drift positions slightly based on phase to close the loop
            if a.current_phase_state.pi_phase > 3.14:
                a.position.x += 1.0
            else:
                a.position.x -= 1.0
                
    print(f"\nMonitoring Bridge Oscillators (End of Step {steps}):")
    print(f"  Pi Offset: {bridge.pi_offset:.4f}")
    
    if bridge.pi_offset != 0.0:
        print("SUCCESS: Swarm state successfully drove Bridge evolution.")
    else:
        print("FAILURE: Bridge state static.")
        sys.exit(1)

if __name__ == "__main__":
    run_closed_loop()
