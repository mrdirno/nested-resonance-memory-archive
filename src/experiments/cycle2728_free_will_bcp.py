"""
Cycle 2728: Free Will as BCP Heuristic (The Causal Budget)
===========================================================

Investigation: Is the perception of "Free Will" a BCP-optimal heuristic for agents facing high computational costs of predicting a deterministic universe?

Hypothesis:
In a complex, deterministic universe, calculating all causal chains to predict outcomes is computationally intractable (NP-hard). "Free Will" acts as a computational shortcut.
V(decision_mode) = Gain(Adaptive_Action) - λ(Compute) * Computational_Cost.

1. Determinism (Calculation): High Computational Cost, potentially perfect prediction (High Gain), but often Intractable.
2. Free Will (Heuristic): Low Computational Cost, suboptimal prediction (Sufficient Gain), and provides perceived agency/motivation.
3. Under high λ (limited cognitive capacity, time pressure), the Free Will heuristic should be BCP-rational.
4. Under low λ (unlimited compute), Deterministic calculation would be BCP-rational.

We simulate an agent choosing a decision-making mode to navigate a complex environment.

"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os

def run_experiment():
    print("Initializing Cycle 2728: Free Will BCP...")
    
    # Decision Modes
    decision_modes = [
        # Deterministic Calculation: High cost, high accuracy for optimal outcome
        {'name': "Deterministic Calculation", 'gain_predictive_power': 100.0, 'computational_cost': 50.0, 'agency_perception': 0.1},
        # Free Will Heuristic: Low cost, sufficient accuracy, high perceived agency
        {'name': "Free Will Heuristic", 'gain_predictive_power': 70.0, 'computational_cost': 5.0, 'agency_perception': 1.0} 
    ]
    
    # Computational Scarcity (λ) - Represents cognitive load, time pressure
    lambdas = np.linspace(0.1, 5.0, 50) # From compute abundance to high scarcity
    
    results = []
    
    for lambd in lambdas:
        best_v = -np.inf
        chosen_mode = None
        
        for d_mode in decision_modes:
            # V = Gain(Predictive_Power) - λ * Computational_Cost
            v = d_mode['gain_predictive_power'] - (lambd * d_mode['computational_cost'])
            
            if v > best_v:
                best_v = v
                chosen_mode = d_mode
        
        results.append({
            'lambda': lambd,
            'chosen_name': chosen_mode['name'],
            'chosen_agency_perception': chosen_mode['agency_perception'],
            'net_value': best_v
        })
            
    df = pd.DataFrame(results)
    
    # Save
    output_dir = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results"
    os.makedirs(output_dir, exist_ok=True)
    df.to_json(f"{output_dir}/cycle2728_data.json")
    
    # Visualize
    plt.figure(figsize=(10, 6))
    
    # Plot chosen agency perception against lambda
    plt.plot(df['lambda'], df['chosen_agency_perception'], marker='o', linestyle='-', color='blue')
    plt.title('Decision Mode Agency Perception vs Computational Scarcity (λ)')
    plt.xlabel('Computational Scarcity (λ)')
    plt.ylabel('Chosen Mode Perceived Agency')
    plt.ylim(0, 1.1)
    plt.grid(True)
    
    # Annotate transitions
    mode_changes = df.drop_duplicates(subset=['chosen_name'])
    for idx, row in mode_changes.iterrows():
        plt.axvline(x=row['lambda'], color='gray', linestyle=':', linewidth=0.8)
        plt.text(row['lambda'] + 0.05, row['chosen_agency_perception'] + 0.1, row['chosen_name'], 
                 rotation=0, verticalalignment='bottom', horizontalalignment='left', fontsize=8, color='darkgreen')
    
    plt.tight_layout()
    plt.savefig("/Volumes/dual/DUALITY-ZERO-V2/data/figures/cycle2728_free_will_budget.png")
    
    # Analysis
    print("Cycle 2728 Analysis:")
    
    low_lambda_choice = df.iloc[0]['chosen_name']
    high_lambda_choice = df.iloc[-1]['chosen_name']
    
    print(f"Low λ Choice: {low_lambda_choice}")
    print(f"High λ Choice: {high_lambda_choice}")
    
    if low_lambda_choice == "Deterministic Calculation" and high_lambda_choice == "Free Will Heuristic":
        print("HYPOTHESIS CONFIRMED: Free Will is a BCP-optimal heuristic for bounded agents.")
        print("Our perception of agency adapts to our computational budget.")
    else:
        print("HYPOTHESIS FAILED or complex outcome.")

if __name__ == "__main__":
    run_experiment()
