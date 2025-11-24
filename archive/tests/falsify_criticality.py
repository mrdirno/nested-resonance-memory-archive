import sys
import os
import json
import numpy as np
import random
from pathlib import Path

# Add project root to path
sys.path.append('/Volumes/dual/DUALITY-ZERO-V2')

from fractal.fractal_swarm import FractalSwarm
from fractal.fractal_agent import FractalAgent

def run_falsification_test():
    print("=== MOG v2 AGENTIC FALSIFICATION: CRITICALITY TEST ===")
    
    # 1. Setup Simulation (Longer Duration, Higher Initial Pop)
    DURATION = 300
    INITIAL_AGENTS = 20
    print(f"Running Simulation: {DURATION} cycles, {INITIAL_AGENTS} agents...")
    
    swarm = FractalSwarm(max_agents=100)
    for i in range(INITIAL_AGENTS):
        swarm.add_agent(FractalAgent(i))
        
    history = []
    bursts = []
    
    # 2. Execution Loop
    for cycle in range(DURATION):
        metrics = swarm.evolve_cycle()
        history.append(metrics)
        
        if metrics['bursts'] > 0:
            bursts.append(metrics['bursts'])
            
        if metrics['active_agents'] == 0:
            print(f"!! EXTINCTION EVENT at Cycle {cycle} !!")
            break
            
    # 3. Analysis
    final_agents = history[-1]['active_agents'] if history else 0
    total_bursts = len(bursts)
    
    print(f"\nResults:")
    print(f"- Final Agents: {final_agents}")
    print(f"- Total Bursts: {total_bursts}")
    
    # 4. Falsification Checks
    
    # Check 1: Viability (Must survive)
    if final_agents == 0:
        print("\n[FAIL] VIABILITY CHECK: Population collapsed.")
        print("Conclusion: System is in 'Sub-Critical' regime (Extinction).")
        return False
        
    # Check 2: Burst Significance (Surrogate Test)
    if total_bursts < 5:
        print("\n[FAIL] STATISTICAL POWER: Insufficient bursts for analysis.")
        return False
        
    # Simple Power Law Check (Log-Log Linearity)
    # If SOC, log(frequency) vs log(size) should be linear
    burst_sizes = np.array(bursts)
    hist, bins = np.histogram(burst_sizes, bins='auto')
    
    # Filter zeros
    valid_idx = hist > 0
    log_size = np.log10(bins[:-1][valid_idx])
    log_freq = np.log10(hist[valid_idx])
    
    # Linear Fit
    if len(log_size) > 2:
        slope, intercept = np.polyfit(log_size, log_freq, 1)
        r_squared = 1 - (np.sum((log_freq - (slope * log_size + intercept))**2) / np.sum((log_freq - np.mean(log_freq))**2))
        
        print(f"\nPower Law Fit:")
        print(f"- Slope (alpha): {slope:.4f}")
        print(f"- R^2: {r_squared:.4f}")
        
        if r_squared > 0.8 and slope < -0.5:
            print("\n[PASS] CRITICALITY CHECK: Burst distribution consistent with Power Law.")
            return True
        else:
            print("\n[FAIL] CRITICALITY CHECK: Burst distribution NOT Power Law.")
            return False
    else:
        print("\n[FAIL] DATA QUALITY: Insufficient binning for Power Law fit.")
        return False

if __name__ == "__main__":
    success = run_falsification_test()
    sys.exit(0 if success else 1)
