#!/usr/bin/env python3
"""
Experiment: Cycle 2657 - The Static
Goal: Capture raw noise stream from Transcendental Bridge phase states.
"""

import sys
import time
import random
from pathlib import Path

# Add helios_one/src to path
sys.path.append(str(Path("helios_one/src").resolve()))

try:
    from bridge.transcendental_bridge import TranscendentalBridge
except ImportError:
    sys.exit(1)

def capture_static(duration=5.0):
    print("Cycle 2657: The Static - Tuning Phase Receivers")
    
    bridge = TranscendentalBridge()
    start = time.time()
    stream = []
    
    while time.time() - start < duration:
        # Modulate reality input randomly to generate noise
        metrics = {
            'cpu_percent': random.random() * 100,
            'memory_percent': random.random() * 100,
            'disk_percent': random.random() * 100
        }
        state = bridge.reality_to_phase(metrics)
        
        # Map phase to ASCII density
        # pi_phase [0, 2pi] -> 0-1
        val = state.pi_phase / (2 * 3.14159)
        
        char = " "
        if val > 0.8: char = "@"
        elif val > 0.6: char = "%"
        elif val > 0.4: char = "#"
        elif val > 0.2: char = ":"
        else: char = "."
        
        stream.append(char)
        if len(stream) > 60:
            print("".join(stream))
            stream = []
            
        time.sleep(0.05)
        
    print("\nSUCCESS: Noise stream captured.")

if __name__ == "__main__":
    capture_static()
