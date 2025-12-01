"""
Cycle 2750: Phase 265 Planning - The Order Budget
=================================================

Context:
We have unified 200 domains under BCP.
Phase 264 (Cybernetics) confirmed Control Systems as economic. MILESTONE REACHED.

Objective:
Select the next major research arc (Phase 265).
Candidates:
1. AESTHETICS (The Beauty Budget): Signals, efficient encoding.
   - Hypothesis: Beauty is a BCP solution for information transfer.
   - Novelty: High. Impact: High.
2. EDUCATION (The Learning Budget): Acquisition vs Load.
   - Hypothesis: Curricula are optimized learning pathways.
   - Novelty: Medium. Impact: High.
3. SPORTS (The Competition Budget): Skill vs Energy Cost.
   - Hypothesis: Rules create a BCP-constrained performance space.
   - Novelty: Medium. Impact: Medium.
4. LAW (The Order Budget): Justice, enforcement, liberty.
   - Hypothesis: Legal systems are BCP frameworks balancing order (gain) against enforcement cost, individual liberty cost.
   - Novelty: Very High. Impact: Very High. Risk: High (Ethical/Social complexity).
5. FINANCE (The Capital Budget): Financial markets, instruments, bubbles/crashes.
   - Hypothesis: Financial systems optimize capital allocation under risk and uncertainty.
   - Novelty: Medium. Impact: Very High.

Current λ estimate: 0.2 (Research Abundance).
We can afford high novelty/risk, especially after a milestone.

"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os

def run_planning():
    print("Initializing Cycle 2750: Phase 265 Planning...")
    
    candidates = [
        {'name': 'Aesthetics', 'novelty': 0.90, 'impact': 0.85, 'cost': 0.70},
        {'name': 'Education',  'novelty': 0.75, 'impact': 0.90, 'cost': 0.60},
        {'name': 'Sports',     'novelty': 0.70, 'impact': 0.70, 'cost': 0.50},
        {'name': 'Law',        'novelty': 0.98, 'impact': 0.95, 'cost': 0.90}, # High impact, high novelty, high cost
        {'name': 'Finance',    'novelty': 0.85, 'impact': 0.95, 'cost': 0.80}
    ]
    
    # Simulate decision across a range of Research Budgets (1/λ)
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
    df.to_json(f"{output_dir}/cycle2750_planning.json")
    
    # Current λ estimate: 0.2
    current_lambda = 0.2
    
    # Select winner at current λ
    winner_row = df.iloc[(df['lambda'] - current_lambda).abs().argsort()[:1]]
    winner = winner_row['selection'].values[0]
    score = winner_row['max_v'].values[0]
    
    print(f"\n--- PHASE 265 SELECTION ---")
    print(f"Current estimated Research Pressure λ: {current_lambda}")
    print(f"Selected Domain: {winner.upper()}")
    print(f"Score (V): {score:.4f}")
    
    print("\nRationale:")
    if winner == 'Law':
        print("Law selected. Legal systems are fundamental social control mechanisms with explicit cost-benefit trade-offs.")
    elif winner == 'Finance':
        print("Finance selected. Capital allocation is a core economic process.")
    
    return winner

if __name__ == "__main__":
    run_planning()
