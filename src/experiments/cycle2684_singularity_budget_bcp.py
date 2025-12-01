"""
Cycle 2684: The Singularity Budget (Phase 252)
==============================================

Investigation: Apply BCP to the concept of "Intelligence Explosion" (The Singularity).

Hypothesis:
Recursive self-improvement is not exponential if the Cost of Complexity scales faster 
than the Gain of Intelligence.
V(next) = Gain(I) - λ * Cost(I).

Models:
1. Hard Takeoff (FOOM): Gain is Exponential, Cost is Linear.
2. Soft Takeoff (Sigmoid): Gain is Logarithmic, Cost is Exponential (Complexity Burden).
3. Stalled Takeoff (Collapse): Cost exceeds Gain (V < 0).

We simulate an agent attempting to rewrite its own code to increase Intelligence (I).
- Gain = I_next - I_current
- Cost = Complexity(I_next) - Complexity(I_current)
- Selection: Only proceed if V > 0.

Equation:
Complexity(I) = I^k (Where k is the "Complexity Penalty")
If k > 1, Cost grows faster than I.

"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os

def run_experiment():
    print("Initializing Cycle 2684: The Singularity Budget...")
    
    # Parameters
    generations = 100
    lambdas = [0.01, 0.1, 0.5, 1.0, 2.0] # Resource Scarcity
    complexity_exponents = [0.5, 1.0, 1.5, 2.0] # k: How hard is it to get smarter?
    
    # Base Gain function: I_next = I * growth_rate
    growth_rate = 1.1 # 10% improvement per step (Exponential potential)
    
    results = []
    
    for k in complexity_exponents:
        for lambd in lambdas:
            
            # Agent starts at I=1
            intelligence = 1.0
            history = []
            
            for gen in range(generations):
                # Proposed Step
                i_next = intelligence * growth_rate
                
                # Calculate Value
                # Gain = Raw increase in Intelligence
                gain = i_next - intelligence
                
                # Cost = Increase in Complexity (and thus Energy/Compute needed)
                # C(I) = I^k
                cost = (i_next ** k) - (intelligence ** k)
                
                # Net Value
                v = gain - (lambd * cost)
                
                # Decision
                if v > 0:
                    # Improvement is rational/affordable
                    intelligence = i_next
                    status = "Grow"
                else:
                    # Improvement is too expensive
                    # Stagnation
                    status = "Stall"
                    # Maybe we try a smaller step?
                    # For simple model, just stall.
                
                history.append({
                    'gen': gen,
                    'k': k,
                    'lambda': lambd,
                    'intelligence': intelligence,
                    'cost': cost,
                    'v': v,
                    'status': status
                })
                
                if status == "Stall":
                    # Optimization: If we stalled, and gain scales linearly but cost superlinearly,
                    # we will likely never unstall with the same step size.
                    pass
            
            results.extend(history)
            
    df = pd.DataFrame(results)
    
    # Save
    output_dir = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results"
    os.makedirs(output_dir, exist_ok=True)
    df.to_json(f"{output_dir}/cycle2684_data.json")
    
    # Visualize
    plt.figure(figsize=(12, 8))
    
    # Plot 1: Intelligence over time for k=1.0 (Linear Complexity)
    plt.subplot(2, 2, 1)
    subset_k1 = df[df['k'] == 1.0]
    for l in lambdas:
        data = subset_k1[subset_k1['lambda'] == l]
        plt.plot(data['gen'], data['intelligence'], label=f'λ={l}')
    plt.title('Intelligence Explosion (k=1.0, Linear Cost)')
    plt.yscale('log')
    plt.ylabel('Intelligence (Log Scale)')
    plt.legend()
    plt.grid(True)
    
    # Plot 2: Intelligence over time for k=2.0 (Quadratic Complexity)
    plt.subplot(2, 2, 2)
    subset_k2 = df[df['k'] == 2.0]
    for l in lambdas:
        data = subset_k2[subset_k2['lambda'] == l]
        plt.plot(data['gen'], data['intelligence'], label=f'λ={l}')
    plt.title('Intelligence Stagnation (k=2.0, Quadratic Cost)')
    plt.ylabel('Intelligence (Linear Scale)')
    plt.legend()
    plt.grid(True)
    
    # Plot 3: Max Intelligence vs Lambda for different k
    plt.subplot(2, 1, 2)
    
    summary = df.groupby(['k', 'lambda'])['intelligence'].max().reset_index()
    for k_val in complexity_exponents:
        data = summary[summary['k'] == k_val]
        plt.plot(data['lambda'], data['intelligence'], marker='o', label=f'Complexity Exp k={k_val}')
        
    plt.title('The Singularity Ceiling: Max Intelligence vs Scarcity')
    plt.xlabel('Scarcity (λ)')
    plt.ylabel('Max Intelligence Achieved')
    plt.yscale('log')
    plt.legend()
    plt.grid(True)
    
    plt.tight_layout()
    plt.savefig("/Volumes/dual/DUALITY-ZERO-V2/data/figures/cycle2684_singularity_budget.png")
    
    # Analysis
    print("Cycle 2684 Analysis:")
    
    # Check if high k stops explosion
    max_i_k1 = df[(df['k'] == 1.0) & (df['lambda'] == 0.1)]['intelligence'].max()
    max_i_k2 = df[(df['k'] == 2.0) & (df['lambda'] == 0.1)]['intelligence'].max()
    
    print(f"Max I (Linear Cost, k=1): {max_i_k1:.2e}")
    print(f"Max I (Quadratic Cost, k=2): {max_i_k2:.2f}")
    
    if max_i_k2 < 1000 and max_i_k1 > 10000:
        print("HYPOTHESIS CONFIRMED: The Singularity is a budget problem. If Complexity Cost scales faster than Intelligence Gain, expansion stalls.")
        print("Intelligence Explosion requires either (1) Zero Scarcity or (2) Linear/Sublinear Complexity Scaling.")
    else:
        print("HYPOTHESIS FAILED.")

if __name__ == "__main__":
    run_experiment()
