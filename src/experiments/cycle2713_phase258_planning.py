"""
Cycle 2713: Phase 258 Planning - The Moral Budget
=================================================

Context:
We have unified 181 domains.
Phase 257 (Religion) confirmed the Economics of the Infinite.
Phase 258 targets MORALITY (The Ethical Budget).

Objective:
Select Phase 258 domain using BCP.
Candidates:
1. ALTRUISM (The Gift Budget): Why give when resources are scarce?
   - Hypothesis: Altruism is high-λ investment in social capital.
2. JUSTICE (The Fairness Budget): Why punish free-riders at a cost?
   - Hypothesis: Punishment is a public good with private cost. High λ prevents justice (impunity).
3. RIGHTS (The Freedom Budget): Are rights absolute or economic?
   - Hypothesis: Rights are budget allocations. Freedom of Speech is expensive (requires tolerance).
4. UTILITARIANISM (The Calculation Budget): Why not calculate everything?
   - Hypothesis: Utilitarianism is computationally intractable (NP-Hard). Deontology is a BCP heuristic.

Current λ estimate: 0.2 (Research Abundance).

"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os

def run_planning():
    print("Initializing Cycle 2713: Phase 258 Planning...")
    
    candidates = [
        {'name': 'Altruism', 'novelty': 0.85, 'impact': 0.80, 'cost': 0.60},
        {'name': 'Justice',  'novelty': 0.90, 'impact': 0.90, 'cost': 0.80},
        {'name': 'Rights',   'novelty': 0.80, 'impact': 0.85, 'cost': 0.70},
        {'name': 'Utilitarianism', 'novelty': 0.95, 'impact': 0.95, 'cost': 0.90} # High compute cost
    ]
    
    lambdas = np.linspace(0.1, 2.0, 20)
    results = []
    
    for lambd in lambdas:
        selection = None
        max_v = -float('inf')
        
        for c in candidates:
            gain = c['novelty'] * c['impact']
            cost = c['cost']
            v = gain - (lambd * cost)
            
            if v > max_v:
                max_v = v
                selection = c['name']
                
        results.append({
            'lambda': lambd,
            'selection': selection,
            'max_v': max_v
        })
        
    df = pd.DataFrame(results)
    
    # Save
    output_dir = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results"
    os.makedirs(output_dir, exist_ok=True)
    df.to_json(f"{output_dir}/cycle2713_planning.json")
    
    # Current λ estimate: 0.2
    current_lambda = 0.2
    
    # Select winner
    winner_row = df.iloc[(df['lambda'] - current_lambda).abs().argsort()[:1]]
    winner = winner_row['selection'].values[0]
    score = winner_row['max_v'].values[0]
    
    print(f"\n--- PHASE 258 SELECTION ---")
    print(f"Current estimated Research Pressure λ: {current_lambda}")
    print(f"Selected Domain: {winner.upper()}")
    print(f"Score (V): {score:.4f}")
    
    print("\nRationale:")
    if winner == 'Utilitarianism':
        print("Utilitarianism selected. BCP explains why we are not utilitarian (Calculation is too expensive).")
        print("Deontology is the cheap heuristic.")
    elif winner == 'Justice':
        print("Justice selected. The cost of enforcement vs the gain of order.")
    
    return winner

if __name__ == "__main__":
    run_planning()
