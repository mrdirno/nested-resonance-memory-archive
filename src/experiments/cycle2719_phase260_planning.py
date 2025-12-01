"""
Cycle 2719: Phase 260 Planning - The Historical Budget
======================================================

Context:
We have unified 185 domains.
Phase 259 (Politics) confirmed Politics is Thermodynamics.
Phase 260 targets HISTORY (The Narrative Budget).

Objective:
Select Phase 260 domain using BCP.
Candidates:
1. HISTORIOGRAPHY (The Memory Budget): Why is history written by the victors?
   - Hypothesis: Victorious narratives are subsidized (Low Cost). Loser narratives are taxed (High Cost).
   - "History is what we can afford to remember."
2. CIVILIZATION CYCLES (The Rise/Fall Budget): Why do empires fall?
   - Hypothesis: Complexity Cost eventually exceeds Energy Income. (Tainter's Collapse).
3. MYTHOLOGY (The Legend Budget): Why do myths persist?
   - Hypothesis: Myths are compressed zip-files of cultural survival data. High Utility / Low Cost.
4. PROGRESS (The Arrow Budget): Is history linear or cyclical?
   - Hypothesis: Progress is a function of Energy Density. If E grows, history looks linear. If E stalls, it looks cyclical.

Current λ estimate: 0.2 (Abundance).

"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os

def run_planning():
    print("Initializing Cycle 2719: Phase 260 Planning...")
    
    candidates = [
        {'name': 'Historiography', 'novelty': 0.85, 'impact': 0.85, 'cost': 0.60},
        {'name': 'Civilization',   'novelty': 0.90, 'impact': 0.95, 'cost': 0.80},
        {'name': 'Mythology',      'novelty': 0.80, 'impact': 0.75, 'cost': 0.50},
        {'name': 'Progress',       'novelty': 0.95, 'impact': 0.90, 'cost': 0.75}
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
    df.to_json(f"{output_dir}/cycle2719_planning.json")
    
    # Current λ estimate: 0.2
    current_lambda = 0.2
    
    # Select winner
    winner_row = df.iloc[(df['lambda'] - current_lambda).abs().argsort()[:1]]
    winner = winner_row['selection'].values[0]
    score = winner_row['max_v'].values[0]
    
    print(f"\n--- PHASE 260 SELECTION ---")
    print(f"Current estimated Research Pressure λ: {current_lambda}")
    print(f"Selected Domain: {winner.upper()}")
    print(f"Score (V): {score:.4f}")
    
    print("\nRationale:")
    if winner == 'Civilization':
        print("Civilization selected. Tainter's Collapse is the ultimate BCP macro-pattern.")
    elif winner == 'Progress':
        print("Progress selected. The Arrow of Time is an Energy Vector.")
    
    return winner

if __name__ == "__main__":
    run_planning()
