"""
Cycle 2716: Phase 259 Planning - The Political Budget
=====================================================

Context:
We have unified 183 domains.
Phase 258 (Morality) confirmed Ethics as Compute.
Phase 259 targets POLITICS (The Power Budget).

Objective:
Select Phase 259 domain using BCP.
Candidates:
1. DEMOCRACY (The Participation Budget): Why vote if impact is near-zero?
   - Hypothesis: Voting is a low-cost signal of allegiance (Expressive Utility).
2. AUTOCRACY (The Control Budget): Why do dictatorships fall?
   - Hypothesis: Centralized information processing exceeds the Dictator's Bandwidth (Calculation Cost).
3. REVOLUTION (The Disruption Budget): When do people revolt?
   - Hypothesis: Revolution occurs when V(Status Quo) < V(Chaos) due to rising Cost(Oppression).
4. BUREAUCRACY (The Process Budget): Why is government slow?
   - Hypothesis: Bureaucracy optimizes for Risk Minimization (High Cost of Failure), not Speed.

Current λ estimate: 0.2 (Research Abundance).

"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os

def run_planning():
    print("Initializing Cycle 2716: Phase 259 Planning...")
    
    candidates = [
        {'name': 'Democracy',    'novelty': 0.85, 'impact': 0.90, 'cost': 0.70},
        {'name': 'Autocracy',    'novelty': 0.80, 'impact': 0.85, 'cost': 0.65},
        {'name': 'Revolution',   'novelty': 0.90, 'impact': 0.95, 'cost': 0.85},
        {'name': 'Bureaucracy',  'novelty': 0.75, 'impact': 0.80, 'cost': 0.50}
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
    df.to_json(f"{output_dir}/cycle2716_planning.json")
    
    # Current λ estimate: 0.2
    current_lambda = 0.2
    
    # Select winner
    winner_row = df.iloc[(df['lambda'] - current_lambda).abs().argsort()[:1]]
    winner = winner_row['selection'].values[0]
    score = winner_row['max_v'].values[0]
    
    print(f"\n--- PHASE 259 SELECTION ---")
    print(f"Current estimated Research Pressure λ: {current_lambda}")
    print(f"Selected Domain: {winner.upper()}")
    print(f"Score (V): {score:.4f}")
    
    print("\nRationale:")
    if winner == 'Revolution':
        print("Revolution selected. The tipping point of social systems is a critical BCP threshold.")
    elif winner == 'Democracy':
        print("Democracy selected. The cost of consensus vs the gain of legitimacy.")
    
    return winner

if __name__ == "__main__":
    run_planning()
