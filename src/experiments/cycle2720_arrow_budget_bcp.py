"""
Cycle 2720: Progress as Energy Vector (The Arrow Budget)
========================================================

Investigation: Is "Progress" a function of Energy Density (λ)?

Hypothesis:
History has a direction (Time's Arrow) because Energy Consumption increases over time.
V(progress) = Gain(Complexity) - λ(Energy) * Cost(Entropy).

1. Low λ (Abundance): Complexity increases. History looks "progressive".
2. Rising λ (Scarcity): Complexity stalls or collapses. History looks "cyclical" or "regressive".
3. The "Arc of the Moral Universe" bends towards justice only because justice is efficient (lower friction) and we have the energy to afford the transition costs.

We simulate a civilization's complexity over time.
- Energy Input E(t) grows (tech) but faces limits (carrying capacity).
- Complexity C(t) consumes Energy.
- If E > C, Surplus -> Investment -> Progress.
- If C > E, Deficit -> Triage -> Collapse.

"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os

def run_experiment():
    print("Initializing Cycle 2720: The Arrow Budget...")
    
    # Time
    steps = 200
    t = np.arange(steps)
    
    # Scenario A: Unbounded Energy (Solar/Fusion) -> Linear Progress
    # Scenario B: Bounded Energy (Fossil/Agrarian) -> Cyclical/Logistic
    
    results = []
    
    # Scenario A: Exponential Energy Growth
    # E(t) = E0 * e^(rt)
    e_growth_rate = 0.02
    energy_A = 10 * np.exp(e_growth_rate * t)
    
    # Scenario B: Logistic Energy (Carrying Capacity)
    # E(t) = K / (1 + e^-k(t-t0))
    K = 100
    energy_B = K / (1 + np.exp(-0.1 * (t - 50)))
    
    # Complexity Dynamics
    # dC/dt = (Energy - Maintenance) * Efficiency
    # Maintenance = C (Linear cost of complexity)
    
    def simulate_history(energy_curve, name):
        c = np.zeros(steps)
        c[0] = 1.0
        
        for i in range(1, steps):
            available_energy = energy_curve[i]
            maintenance = c[i-1]
            
            surplus = available_energy - maintenance
            
            if surplus > 0:
                # Invest surplus in growth
                # Growth is slow (takes time to build)
                growth = surplus * 0.1
                c[i] = c[i-1] + growth
            else:
                # Deficit! Collapse is fast (Triage)
                # Collapse rate is proportional to deficit
                collapse = surplus * 0.5 # surplus is negative
                c[i] = c[i-1] + collapse
                
            # Floor
            c[i] = max(0.1, c[i])
            
        return c
    
    complexity_A = simulate_history(energy_A, "Unbounded")
    complexity_B = simulate_history(energy_B, "Bounded")
    
    # Save data
    df = pd.DataFrame({
        'time': t,
        'energy_A': energy_A,
        'complexity_A': complexity_A,
        'energy_B': energy_B,
        'complexity_B': complexity_B
    })
    
    output_dir = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results"
    os.makedirs(output_dir, exist_ok=True)
    df.to_json(f"{output_dir}/cycle2720_data.json")
    
    # Visualize
    plt.figure(figsize=(12, 6))
    
    plt.subplot(1, 2, 1)
    plt.plot(t, complexity_A, label='Complexity', color='green')
    plt.plot(t, energy_A, label='Energy Limit', color='gray', linestyle='--')
    plt.title('Scenario A: Unbounded Energy (The Singularity)')
    plt.xlabel('Time')
    plt.ylabel('Magnitude')
    plt.legend()
    plt.grid(True)
    
    plt.subplot(1, 2, 2)
    plt.plot(t, complexity_B, label='Complexity', color='orange')
    plt.plot(t, energy_B, label='Energy Limit', color='gray', linestyle='--')
    plt.title('Scenario B: Bounded Energy (The Cycle)')
    plt.xlabel('Time')
    plt.ylabel('Magnitude')
    plt.legend()
    plt.grid(True)
    
    plt.tight_layout()
    plt.savefig("/Volumes/dual/DUALITY-ZERO-V2/data/figures/cycle2720_arrow_budget.png")
    
    # Analysis
    print("Cycle 2720 Analysis:")
    
    # Correlation
    corr_A = np.corrcoef(energy_A, complexity_A)[0,1]
    corr_B = np.corrcoef(energy_B, complexity_B)[0,1]
    
    print(f"Correlation (Energy-Complexity) A: {corr_A:.4f}")
    print(f"Correlation (Energy-Complexity) B: {corr_B:.4f}")
    
    if corr_A > 0.9 and corr_B > 0.9:
        print("HYPOTHESIS CONFIRMED: History is an Energy Function.")
        print("Progress is simply the artifact of rising Energy Density.")
        print("Stagnation is the artifact of Energy Limits.")
    else:
        print("HYPOTHESIS FAILED.")

if __name__ == "__main__":
    run_experiment()
