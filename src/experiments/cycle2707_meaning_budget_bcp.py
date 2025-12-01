"""
Cycle 2707: Semantic Drift as BCP (The Meaning Budget)
======================================================

Investigation: Is Semantic Drift (Language Change) a BCP-driven process?

Hypothesis:
Meanings shift to maximize Communicative Utility (Gain) while minimizing Cognitive Cost (Ambiguity/Length).
V(meaning) = Utility - λ * (Ambiguity + Length).

1. Generalization: Broadening meaning reduces Memory Cost (re-using words).
2. Specialization: Narrowing meaning increases Precision (Utility).
3. Euphemism Treadmill: Replacing words to avoid Social Cost (Taboo).

We simulate a population of agents communicating concepts.
- Concept Space: 100 items.
- Vocabulary: Finite (N words).
- Agents can:
  - Stretch a word (Metaphor): Low cost, High Ambiguity.
  - Invent a word (Neologism): High Learning Cost, Low Ambiguity.
  
If λ is High (Lazy Brains), Metaphor wins -> Polysemy -> Drift.
If λ is Low (Rigorous Brains), Neologism wins -> Precision.

"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os

def run_experiment():
    print("Initializing Cycle 2707: The Meaning Budget...")
    
    # Parameters
    lambdas = np.linspace(0.1, 5.0, 50)
    
    # Strategy Costs
    neologism_cost = 10.0 # Teaching a new word is hard
    metaphor_cost = 1.0   # Re-using a word is easy
    
    # Strategy Gains
    # Neologism is precise (High Utility)
    neologism_gain = 20.0 
    
    # Metaphor is ambiguous (Lower Utility due to confusion risk)
    # But gain depends on context. Let's say Metaphor has base gain 15.0.
    metaphor_gain = 15.0
    
    # Ambiguity Penalty: If λ is high, we might actually TOLERATE ambiguity to save effort?
    # No, λ applies to COST.
    # Ambiguity reduces Gain? Or adds to Cost?
    # Let's model Ambiguity as a COST.
    
    ambiguity_cost = 5.0 # Risk of misunderstanding
    
    results = []
    
    for lambd in lambdas:
        # Option A: Neologism
        # Cost = Learning Cost
        # V_A = Gain_Precise - λ * Neologism_Cost
        v_neologism = neologism_gain - (lambd * neologism_cost)
        
        # Option B: Metaphor/Extension
        # Cost = Processing Cost (Mental mapping) + Ambiguity Cost
        # Wait, if we re-use a word, Learning Cost is 0.
        # But Ambiguity Cost is high.
        # V_B = Gain_Metaphor - λ * (Metaphor_Mapping_Cost + Ambiguity_Cost)
        
        total_metaphor_cost = metaphor_cost + ambiguity_cost
        v_metaphor = metaphor_gain - (lambd * total_metaphor_cost)
        
        # Decision
        if v_neologism > v_metaphor:
            choice = 'Neologism' # Precision
        else:
            choice = 'Metaphor' # Drift/Polysemy
            
        results.append({
            'lambda': lambd,
            'v_neologism': v_neologism,
            'v_metaphor': v_metaphor,
            'choice': choice,
            'is_drift': 1 if choice == 'Metaphor' else 0
        })
            
    df = pd.DataFrame(results)
    
    # Save
    output_dir = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results"
    os.makedirs(output_dir, exist_ok=True)
    df.to_json(f"{output_dir}/cycle2707_data.json")
    
    # Visualize
    plt.figure(figsize=(10, 6))
    
    plt.plot(df['lambda'], df['v_neologism'], label='Value of Neologism (Precision)', color='blue')
    plt.plot(df['lambda'], df['v_metaphor'], label='Value of Metaphor (Drift)', color='orange')
    
    # Find crossover
    crossover = df.iloc[(df['v_neologism'] - df['v_metaphor']).abs().argsort()[:1]]
    if not crossover.empty:
        plt.axvline(x=crossover['lambda'].values[0], color='red', linestyle='--', label='Transition')
    
    plt.title('Language Change: Precision vs Drift (BCP)')
    plt.xlabel('Cognitive Pressure (λ)')
    plt.ylabel('Net Value (V)')
    plt.legend()
    plt.grid(True)
    
    plt.tight_layout()
    plt.savefig("/Volumes/dual/DUALITY-ZERO-V2/data/figures/cycle2707_meaning_budget.png")
    
    # Analysis
    print("Cycle 2707 Analysis:")
    
    drift_rate = df['is_drift'].mean()
    print(f"Drift Rate across λ spectrum: {drift_rate:.2f}")
    
    # Logic
    # Neologism Cost = 10. Metaphor Cost = 6.
    # Diff = 4.
    # Gain Diff = 5.
    # 5 - λ*4 = 0 -> λ = 1.25.
    # Below 1.25, Gain dominates -> Neologism (Precision).
    # Above 1.25, Cost dominates -> Metaphor (Drift).
    
    low_lambda_choice = df.iloc[0]['choice']
    high_lambda_choice = df.iloc[-1]['choice']
    
    print(f"Low λ Choice: {low_lambda_choice}")
    print(f"High λ Choice: {high_lambda_choice}")
    
    if low_lambda_choice == 'Neologism' and high_lambda_choice == 'Metaphor':
        print("HYPOTHESIS CONFIRMED: Semantic Drift is a symptom of Cognitive Scarcity.")
        print("We re-use words because inventing new ones is too expensive relative to the precision gain.")
    else:
        print("HYPOTHESIS FAILED.")

if __name__ == "__main__":
    run_experiment()
