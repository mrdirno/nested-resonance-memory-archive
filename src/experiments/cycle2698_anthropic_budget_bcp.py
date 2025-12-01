"""
Cycle 2698: The Anthropic Budget (Phase 254)
============================================

Investigation: Apply BCP to the Anthropic Principle.

Hypothesis:
We exist in a universe tuned for complexity because complex observers (Us) can only 
afford to exist in a Low-λ (Low Entropy/Cost) universe.
V(observer) = Gain(Consciousness) - λ(Universe) * Cost(Biology)

If λ(Universe) were slightly higher (different constants), Cost(Biology) > Gain.
Result: V < 0. No observers.

We simulate a multiverse of different λ values.
- Only Low-λ universes produce observers.
- Therefore, any observer will measure Low λ, even if most universes are High λ.

"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os

def run_experiment():
    print("Initializing Cycle 2698: The Anthropic Budget...")
    
    # Parameters
    n_universes = 1000
    
    # Generate Multiverse: Random distribution of Scarcity (λ)
    # Most universes are chaotic/high-entropy (High λ)
    # Some are structured (Low λ)
    universe_lambdas = np.random.exponential(scale=5.0, size=n_universes)
    
    # Observer Cost Function
    # Cost of maintaining a brain/biology
    observer_cost = 10.0 
    observer_gain = 20.0 # Value of existence
    
    results = []
    
    for i, lambd in enumerate(universe_lambdas):
        # Can an observer exist here?
        # V = Gain - λ * Cost
        v = observer_gain - (lambd * observer_cost)
        
        # Existence condition: V > 0
        exists = 1 if v > 0 else 0
        
        results.append({
            'universe_id': i,
            'lambda': lambd,
            'net_value': v,
            'observer_exists': exists
        })
            
    df = pd.DataFrame(results)
    
    # Save
    output_dir = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results"
    os.makedirs(output_dir, exist_ok=True)
    df.to_json(f"{output_dir}/cycle2698_data.json")
    
    # Visualize
    plt.figure(figsize=(10, 6))
    
    # Histogram of All Universes vs Observed Universes
    plt.hist(df['lambda'], bins=50, alpha=0.5, label='All Universes (Objective)', color='gray')
    plt.hist(df[df['observer_exists'] == 1]['lambda'], bins=50, alpha=0.8, label='Observed Universes (Anthropic)', color='green')
    
    plt.title('The Anthropic Selection Effect')
    plt.xlabel('Universe Scarcity (λ)')
    plt.ylabel('Count')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig("/Volumes/dual/DUALITY-ZERO-V2/data/figures/cycle2698_anthropic_budget.png")
    
    # Analysis
    print("Cycle 2698 Analysis:")
    
    total_mean_lambda = df['lambda'].mean()
    observed_mean_lambda = df[df['observer_exists'] == 1]['lambda'].mean()
    
    print(f"Objective Mean λ: {total_mean_lambda:.2f}")
    print(f"Observed Mean λ: {observed_mean_lambda:.2f}")
    
    if observed_mean_lambda < total_mean_lambda * 0.5:
        print("HYPOTHESIS CONFIRMED: Observers necessarily find themselves in a Low-Scarcity (Low-λ) universe, regardless of the objective probability.")
        print("The Anthropic Principle is a BCP selection bias.")
    else:
        print("HYPOTHESIS FAILED.")

if __name__ == "__main__":
    run_experiment()
