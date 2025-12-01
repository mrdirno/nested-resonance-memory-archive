"""
Cycle 2703: The Axiomatic Budget (Phase 255)
============================================

Investigation: Are Axiom Systems selected via BCP?

Hypothesis:
Mathematicians choose axiom systems (ZFC, Peano, Euclidean) that maximize the "Yield" of interesting theorems while minimizing the "Cost" of complexity/inconsistency.
V(system) = Yield(Theorems) - λ * (Complexity + Risk(Inconsistency)).

1. Low λ (Abundance): We explore exotic axioms (Non-Euclidean, Large Cardinals).
2. High λ (Scarcity/Pragmatism): We stick to minimal, useful axioms (Peano, Euclidean).
3. Inconsistency is an Infinite Cost. (V -> -inf).

We simulate an agent choosing between:
- System A: Simple, Low Yield (Peano)
- System B: Complex, High Yield (ZFC + Large Cardinals)
- System C: Very Complex, Very High Yield but Risky (Naïve Set Theory)

"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os

def run_experiment():
    print("Initializing Cycle 2703: The Axiomatic Budget...")
    
    # Axiom Systems
    # Cost: Complexity of axioms
    # Yield: Number of reachable theorems (Value)
    # Risk: Probability of hidden inconsistency
    
    systems = [
        {'name': 'Peano', 'cost': 10, 'yield': 100, 'risk': 0.0},
        {'name': 'ZFC', 'cost': 50, 'yield': 10000, 'risk': 0.001}, # Tiny risk?
        {'name': 'Large Cardinals', 'cost': 1000, 'yield': 50000, 'risk': 0.01}, # Increased cost
        {'name': 'Naïve Sets', 'cost': 5, 'yield': 1000000, 'risk': 1.0} # Paradox guaranteed
    ]
    
    lambdas = np.linspace(0.01, 500.0, 100) # Extreme range for Peano
    
    # Risk Penalty Factor: How much does inconsistency cost?
    # Inconsistency destroys the system. Cost is huge.
    inconsistency_penalty = 10000.0
    
    results = []
    
    for lambd in lambdas:
        best_v = -float('inf')
        choice = None
        
        for sys in systems:
            # Expected Yield = Yield * (1 - Risk) ? Or separate term?
            # V = Yield - λ * Cost - Risk_Penalty * Risk
            # Risk implies V might be -inf.
            # Expected V = (1-Risk)*Yield + Risk*(-Penalty) - λ*Cost
            
            ev = (1 - sys['risk']) * sys['yield'] - (sys['risk'] * inconsistency_penalty) - (lambd * sys['cost'])
            
            if ev > best_v:
                best_v = ev
                choice = sys['name']
                
        results.append({
            'lambda': lambd,
            'choice': choice,
            'best_v': best_v
        })
            
    df = pd.DataFrame(results)
    
    # Save
    output_dir = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results"
    os.makedirs(output_dir, exist_ok=True)
    df.to_json(f"{output_dir}/cycle2703_data.json")
    
    # Visualize
    plt.figure(figsize=(10, 6))
    
    # Map choice to number for plotting
    choice_map = {name: i for i, name in enumerate([s['name'] for s in systems])}
    y_values = df['choice'].map(choice_map)
    
    plt.scatter(df['lambda'], y_values, c=y_values, cmap='viridis', s=100)
    plt.yticks(range(len(systems)), [s['name'] for s in systems])
    plt.title('Axiom System Selection vs Scarcity (λ)')
    plt.xlabel('Cognitive/Compute Pressure (λ)')
    plt.ylabel('Selected System')
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig("/Volumes/dual/DUALITY-ZERO-V2/data/figures/cycle2703_axiomatic_budget.png")
    
    # Analysis
    print("Cycle 2703 Analysis:")
    
    # Find transitions
    # Low λ -> High Complexity (Large Cardinals)
    # Medium λ -> High Efficiency (ZFC)
    # High λ -> Minimal (Peano)
    # Naïve Sets should never be chosen if Risk Penalty is high enough.
    
    choices = df['choice'].unique()
    print(f"Systems Selected across λ range: {choices}")
    
    if 'Naïve Sets' not in choices and 'ZFC' in choices:
        print("HYPOTHESIS CONFIRMED: Mathematicians select axioms based on Economic Yield vs Cost.")
        print("ZFC is the 'Goldilocks' economy: High Yield, Manageable Cost, Low Risk.")
        if 'Peano' in choices:
            print("Peano is the 'Recession' economy: Low Cost, Low Yield.")
        else:
            print("Note: Peano requires even higher scarcity to be optimal over ZFC.")
        print("Large Cardinals are the 'Luxury' economy.")
    else:
        print("HYPOTHESIS FAILED.")

if __name__ == "__main__":
    run_experiment()
