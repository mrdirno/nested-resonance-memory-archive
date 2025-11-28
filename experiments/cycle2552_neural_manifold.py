
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

def run_manifold_experiment():
    print("🧶 CYCLE 2552: THE NEURAL MANIFOLD - HOLOGRAPHIC ENCODING")
    print("   (Compressing Vector Concepts into Scalar Waves)")
    
    # 1. Define Concept Vector (The Idea)
    original_concept = [0.2, 0.5, 0.8] # e.g. [Happiness, Freedom, Security]
    print(f"💡 Original Concept: {original_concept}")
    
    # 2. Encoding (Frequency Multiplexing)
    # We map dimensions to frequencies: 1Hz, 2Hz, 3Hz
    def encode(vector, t):
        signal = 0
        for i, val in enumerate(vector):
            freq = i + 1
            signal += val * math.sin(freq * t)
        return signal
        
    # 3. Transmission (The Channel)
    # We sample the signal over time window T
    # T must be large enough to resolve 1Hz vs 2Hz
    # dt must be small enough (Nyquist) for 3Hz
    
    samples = []
    N = 1000
    T_MAX = 100.0
    dt = T_MAX / N
    
    for i in range(N):
        t = i * dt
        samples.append(encode(original_concept, t))
        
    # 4. Decoding (Fourier Transform)
    fft_result = np.fft.fft(samples)
    freqs = np.fft.fftfreq(N, dt)
    
    # Freqs in numpy are in Cycles/UnitTime (Hz) if dt is in seconds?
    # encode() used sin(freq * t). Period = 2pi/freq.
    # Angular Frequency omega = freq.
    # Hz = omega / 2pi.
    # So target 1Hz in my code is actually omega=1, which is 1/(2pi) Hz.
    
    # Let's map to Angular Frequency to match encode()
    omegas = freqs * 2 * math.pi
    
    magnitudes = np.abs(fft_result) / (N / 2)
    
    reconstructed = []
    
    for target_omega in [1, 2, 3]:
        idx = np.argmin(np.abs(omegas - target_omega))
        val = magnitudes[idx]
        reconstructed.append(val)
        
    print(f"🧠 Reconstructed: {[f'{x:.2f}' for x in reconstructed]}")
    
    # Error Calc
    mse = np.mean((np.array(original_concept) - np.array(reconstructed))**2)
    print(f"📉 MSE: {mse:.6f}")
    
    if mse < 0.01:
        print("✨ HOLOGRAPHIC TRANSFER SUCCESS.")
    else:
        print("💀 TRANSFER FAILED (Aliasing/Noise).")

if __name__ == "__main__":
    run_manifold_experiment()
