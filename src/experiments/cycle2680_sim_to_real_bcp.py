"""
Cycle 2680: The Sim-to-Real BCP Gap
===================================

Investigation: Does BCP explain the "Sim-to-Real Gap" as a budget-constrained 
fidelity trade-off?

Hypothesis:
1. High-Fidelity simulation (Physics-Accurate) is exponentially expensive.
2. Low-Fidelity simulation (Approximation) is cheap.
3. Transfer Learning Gain depends on Fidelity.
4. Agents under High λ (Scarcity) rationally choose Low Fidelity, accepting 
   poor transfer performance (the Gap) to save compute cost.

Dynamics:
- Fidelity (F) in [0, 1].
- Cost(F) = exp(k * F). (Exponential cost for perfection).
- Transfer_Gain(F) = F (Linear? Or Sigmoidal? Let's assume Linear for simplicity first).
- V(F) = Transfer_Gain(F) - λ * Cost(F).

We expect a phase transition where optimal F drops sharply as λ increases.

"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os

def run_experiment():
    print("Initializing Cycle 2680: Sim-to-Real BCP...")
    
    # Parameters
    lambdas = np.linspace(0.01, 2.0, 50)
    fidelity_levels = np.linspace(0.0, 1.0, 100)
    
    # Cost Function parameters
    # Cost = base_cost + exp(k * F)
    # Let's say F=0 cost is 1, F=1 cost is 100.
    # 100 = exp(k * 1) -> k = ln(100) ≈ 4.6
    k = 4.6
    
    results = []
    
    for lambd in lambdas:
        # Evaluate V for all Fidelity levels
        # Gain: F * 10 (Value of perfect transfer)
        # Cost: np.exp(k * F)
        
        gain = fidelity_levels * 10.0
        cost = np.exp(k * fidelity_levels)
        
        # Net Value
        v = gain - (lambd * cost)
        
        # Optimal Fidelity
        best_idx = np.argmax(v)
        optimal_fidelity = fidelity_levels[best_idx]
        optimal_v = v[best_idx]
        optimal_cost = cost[best_idx]
        
        # Sim-to-Real Gap
        # Gap = 1.0 - Optimal Fidelity
        gap = 1.0 - optimal_fidelity
        
        results.append({
            'lambda': lambd,
            'optimal_fidelity': optimal_fidelity,
            'sim_to_real_gap': gap,
            'cost_paid': optimal_cost,
            'net_value': optimal_v
        })
        
    df = pd.DataFrame(results)
    
    # Save results
    output_dir = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results"
    os.makedirs(output_dir, exist_ok=True)
    df.to_json(f"{output_dir}/cycle2680_data.json")
    
    # Visualize
    plt.figure(figsize=(10, 6))
    
    plt.subplot(1, 2, 1)
    plt.plot(df['lambda'], df['optimal_fidelity'], label='Optimal Fidelity', color='blue')
    plt.title('Optimal Simulation Fidelity vs Scarcity (λ)')
    plt.xlabel('Compute Cost Pressure (λ)')
    plt.ylabel('Fidelity (0-1)')
    plt.grid(True)
    
    plt.subplot(1, 2, 2)
    plt.plot(df['lambda'], df['sim_to_real_gap'], label='Sim-to-Real Gap', color='red')
    plt.title('Sim-to-Real Gap vs Scarcity (λ)')
    plt.xlabel('Compute Cost Pressure (λ)')
    plt.ylabel('Gap Magnitude')
    plt.grid(True)
    
    plt.tight_layout()
    plt.savefig("/Volumes/dual/DUALITY-ZERO-V2/data/figures/cycle2680_sim_to_real.png")
    
    # Analysis
    print("Cycle 2680 Analysis:")
    low_lambda_fidelity = df.iloc[0]['optimal_fidelity']
    high_lambda_fidelity = df.iloc[-1]['optimal_fidelity']
    
    print(f"Low Scarcity (λ={df.iloc[0]['lambda']:.2f}) Fidelity: {low_lambda_fidelity:.4f}")
    print(f"High Scarcity (λ={df.iloc[-1]['lambda']:.2f}) Fidelity: {high_lambda_fidelity:.4f}")
    
    if low_lambda_fidelity > 0.9 and high_lambda_fidelity < 0.5:
        print("HYPOTHESIS CONFIRMED: The Sim-to-Real Gap is a budget decision. High λ forces low fidelity.")
    else:
        print("HYPOTHESIS FAILED or dynamics complex.")

if __name__ == "__main__":
    run_experiment()
