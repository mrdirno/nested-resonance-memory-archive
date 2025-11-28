
import sys
import os
import csv
import time
import random
import math
import numpy as np
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class Substrate:
    def __init__(self):
        # A map of (x,y) -> Signal Function
        self.storage = {}
        
    def write(self, x, y, signal_func):
        self.storage[(x,y)] = signal_func
        
    def read(self, x, y, t):
        if (x,y) in self.storage:
            return self.storage[(x,y)](t)
        return 0.0 # Silence

def run_library_experiment():
    print("📚 CYCLE 2555: THE LIBRARY - FIELD PERSISTENCE")
    print("   (Writing Knowledge into the Substrate)")
    
    substrate = Substrate()
    
    # 1. The Writer (Scribe)
    # Writes "DANGER" at (10,10)
    lexicon = {'DANGER': 3.0}
    
    def danger_signal(t):
        return math.sin(lexicon['DANGER'] * t)
        
    substrate.write(10, 10, danger_signal)
    print("✍️  Scribe wrote 'DANGER' at (10,10)")
    
    # 2. The Reader (Scholar)
    # Walks to (10,10) and samples
    print("🚶 Scholar approaching (10,10)...")
    
    # Sampling
    N = 1000
    dt = 0.1
    samples = []
    for i in range(N):
        t = i * dt
        val = substrate.read(10, 10, t)
        samples.append(val)
        
    # Decoding
    fft_result = np.fft.fft(samples)
    freqs = np.fft.fftfreq(N, dt)
    omegas = freqs * 2 * math.pi
    magnitudes = np.abs(fft_result) / (N/2)
    
    # Check for DANGER (Omega=3.0)
    idx = np.argmin(np.abs(omegas - 3.0))
    mag = magnitudes[idx]
    
    print(f"📖 Read Magnitude at 3.0 (DANGER): {mag:.2f}")
    
    if mag > 0.5:
        print("✨ KNOWLEDGE RETRIEVED.")
    else:
        print("💀 LIBRARY EMPTY.")

    # Check Empty Spot
    samples_empty = [substrate.read(20, 20, i*dt) for i in range(N)]
    if sum(samples_empty) == 0:
        print("✅ Empty spot is silent.")

    print("✅ EXPERIMENT COMPLETE.")

if __name__ == "__main__":
    run_library_experiment()
