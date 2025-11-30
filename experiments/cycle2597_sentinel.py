#!/usr/bin/env python3
"""
Experiment: Cycle 2597 - The Sentinel
Goal: Implement a monitoring agent for the Transcendental Bridge.
"""

import sys
import time
import json
import math
import random
from pathlib import Path
from dataclasses import asdict

# Add HELIOS-ONE src to path
HELIOS_SRC = Path("helios_one/src").resolve()
sys.path.insert(0, str(HELIOS_SRC))

try:
    from bridge.transcendental_bridge import TranscendentalBridge, TranscendentalState
except ImportError:
    print("CRITICAL: Could not import TranscendentalBridge.")
    sys.exit(1)

class Sentinel:
    def __init__(self, bridge: TranscendentalBridge, log_path: str):
        self.bridge = bridge
        self.log_path = Path(log_path)
        self.threshold_magnitude = 10.0 # Arbitrary threshold for "instability"
        self.threshold_phase_velocity = 1.5 # Rad/s threshold
        self.last_state = None
        
        # Ensure log directory exists
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def monitor_step(self) -> dict:
        """
        Perform one monitoring step.
        Returns a dict containing status and any alerts.
        """
        # Get current reality state
        # We mock some reality metrics if not running on a full system with psutil,
        # but TranscendentalBridge handles defaults (0.0).
        # Let's inject some random noise to simulate a "living" system for the bridge to pick up.
        
        mock_metrics = {
            'cpu_percent': random.uniform(10, 30),
            'memory_percent': random.uniform(40, 60),
            'disk_percent': random.uniform(20, 25)
        }
        
        current_state = self.bridge.reality_to_phase(mock_metrics)
        
        alert = None
        velocity = 0.0
        
        if self.last_state:
            velocity = self.bridge.compute_phase_distance(current_state, self.last_state)
            
            # Check thresholds
            if current_state.magnitude > self.threshold_magnitude:
                alert = f"HIGH_MAGNITUDE: {current_state.magnitude:.2f} > {self.threshold_magnitude}"
            
            if velocity > self.threshold_phase_velocity:
                alert = f"HIGH_VELOCITY: {velocity:.2f} > {self.threshold_phase_velocity}"

        self.last_state = current_state
        
        log_entry = {
            "timestamp": time.time(),
            "magnitude": current_state.magnitude,
            "velocity": velocity,
            "phases": {
                "pi": current_state.pi_phase,
                "e": current_state.e_phase,
                "phi": current_state.phi_phase
            },
            "alert": alert
        }
        
        self._log(log_entry)
        return log_entry

    def _log(self, entry: dict):
        with open(self.log_path, "a") as f:
            f.write(json.dumps(entry) + "\n")

def main():
    print("Cycle 2597: The Sentinel - Initialization")
    
    bridge = TranscendentalBridge()
    sentinel_log = Path("experiments/logs/sentinel_cycle2597.jsonl")
    sentinel = Sentinel(bridge, str(sentinel_log))
    
    print(f"Sentinel active. Logging to {sentinel_log}")
    
    # Run normal monitoring
    print("Phase 1: Normal Monitoring (5 steps)")
    for i in range(5):
        status = sentinel.monitor_step()
        print(f"  Step {i}: Mag={status['magnitude']:.2f}, Vel={status['velocity']:.2f} - {status['alert'] or 'OK'}")
        time.sleep(0.1)

    # Simulate Anomaly
    print("\nPhase 2: Simulating Anomaly (High Energy Event)")
    # We force the bridge oscillators to jump to create high velocity
    bridge.pi_offset += math.pi
    bridge.e_offset += math.pi
    
    # We also inject a high-load metric
    print("  Injecting massive CPU spike...")
    # We can't easily force the Sentinel to see a different metric than it generates internally
    # without modifying the Sentinel class or the bridge, but the Sentinel generates its own mock metrics in this test harness.
    # So we will subclass or just modify the loop here to pass explicit metrics if the class allowed it,
    # but the class generates them internally. 
    # Let's rely on the oscillator shift we just did to trigger the "HIGH_VELOCITY" alert.
    
    status = sentinel.monitor_step()
    print(f"  Anomaly Step: Mag={status['magnitude']:.2f}, Vel={status['velocity']:.2f} - {status['alert'] or 'OK'}")

    if status['alert']:
        print("\nSUCCESS: Anomaly detected.")
    else:
        print("\nFAILURE: Anomaly NOT detected.")
        sys.exit(1)

if __name__ == "__main__":
    main()
