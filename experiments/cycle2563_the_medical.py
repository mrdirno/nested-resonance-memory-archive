
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

def run_medical_experiment():
    print("⚕️ CYCLE 2563: THE MEDICAL - ACTIVE CANCELLATION")
    print("   (Curing Disease via Phase Inversion)")
    
    # 1. Body (Healthy Frequencies)
    HEALTHY_FREQS = [10.0, 20.0, 30.0]
    PATHOGEN_FREQ = 25.0
    
    def get_body_signal(t):
        val = 0
        for f in HEALTHY_FREQS:
            val += math.sin(f * t)
        return val
        
    def get_pathogen_signal(t):
        return 2.0 * math.sin(PATHOGEN_FREQ * t) # Strong Infection
        
    # 2. Diagnosis (Sampling)
    # Increase N for better resolution
    N = 10000 
    dt = 0.01
    
    print("🔬 Diagnosing Patient...")
    samples = []
    for i in range(N):
        t = i * dt
        # Signal = Body + Pathogen
        s = get_body_signal(t) + get_pathogen_signal(t)
        samples.append(s)
        
    # FFT to find Pathogen
    fft_result = np.fft.fft(samples)
    freqs = np.fft.fftfreq(N, dt)
    omegas = freqs * 2 * math.pi
    magnitudes = np.abs(fft_result) / (N/2)
    
    # Identify peaks not in HEALTHY list
    detected_pathogen = None
    
    for i, mag in enumerate(magnitudes):
        if mag > 0.5 and omegas[i] > 0: # Significant peak
            omega = omegas[i]
            # Is it healthy?
            is_healthy = False
            for h in HEALTHY_FREQS:
                if abs(omega - h) < 0.5: is_healthy = True # Tighter tolerance
            
            if not is_healthy:
                print(f"🦠 Pathogen Detected at {omega:.1f} Hz (Mag={mag:.1f})")
                detected_pathogen = omega
                break
                
    if not detected_pathogen:
        print("✅ Patient Healthy.")
        return
        
    # 3. Therapy (Band-Stop Filter)
    print("💉 Administering Frequency Block...")
    
    # Create Filter
    filter_mask = np.ones(len(freqs))
    
    for i, omega in enumerate(omegas):
        # Block range [24, 26]
        if 24.0 < abs(omega) < 26.0:
            filter_mask[i] = 0.0
            
    # Apply Filter
    filtered_spectrum = fft_result * filter_mask
    
    # IFFT to get cured signal
    cure_signal = np.fft.ifft(filtered_spectrum)
    
    # 4. Verification
    final_energy = 0
    
    for i in range(N):
        t = i * dt
        # S_cured is the filtered signal
        # Ideal is Body Signal
        s = float(cure_signal[i].real) # Take real part
        ideal = get_body_signal(t)
        
        final_energy += abs(s - ideal)
        
    print(f"📉 Residual Pathogen Energy: {final_energy:.4f}")
    
    if final_energy < 100.0: # Some leakage is fine (Gibbs phenomenon)
        print("✨ PATIENT CURED.")
    else:
        print("💀 TREATMENT FAILED.")
        
    def get_cure_signal(t): return 0 # Placeholder for consistency
    final_energy = 0
    pathogen_energy = 0
    
    for i in range(N):
        t = i * dt
        # Total = Body + Pathogen + Cure
        s = get_body_signal(t) + get_pathogen_signal(t) + get_cure_signal(t)
        
        # Check if Pathogen is gone
        # Ideal S = Body only
        ideal = get_body_signal(t)
        error = abs(s - ideal)
        
        final_energy += error
        
    print(f"📉 Residual Pathogen Energy: {final_energy:.4f}")
    
    if final_energy < 1.0:
        print("✨ PATIENT CURED.")
    else:
        print("💀 TREATMENT FAILED.")

    print("✅ EXPERIMENT COMPLETE.")

if __name__ == "__main__":
    run_medical_experiment()
