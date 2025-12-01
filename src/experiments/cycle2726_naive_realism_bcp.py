"""
Cycle 2726: Naive Realism as BCP (The Observational Budget)
============================================================

Investigation: Is Naive Realism (believing what you see directly) a BCP-optimal strategy for everyday survival, compared to Scientific Realism (complex, theory-laden observation)?

Hypothesis:
Our default mode of perceiving reality (Naive Realism) is a BCP-rational heuristic. It maximizes "Survival Utility" (Gain) while minimizing "Cognitive Processing Cost" (Cost).
V(perception_mode) = Survival_Utility - λ(Cognitive) * Cognitive_Processing_Cost.

1. Naive Realism: High Gain (quick action), Low Cost (minimal processing), but Lower Accuracy.
2. Scientific Realism: Higher Gain (deeper understanding, predictive power), High Cost (complex models, experimentation), Higher Accuracy.
3. Under high λ (immediate threat, cognitive overload), Naive Realism should dominate.
4. Under low λ (leisure, research), Scientific Realism should dominate.

We simulate an agent choosing a perception mode to navigate a world with varying levels of complexity and immediate threats.

"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os

def run_experiment():
    print("Initializing Cycle 2726: Naive Realism BCP...")
    
    # Perception Modes
    perception_modes = [
        # Naive Realism: Low cost, Quick action (sufficient utility for survival), but less accurate
        {'name': "Naive Realism", 'survival_utility': 80.0, 'cognitive_cost': 5.0, 'accuracy': 0.7},
        # Scientific Realism: High cost, High accuracy, high predictive power (higher utility)
        {'name': "Scientific Realism", 'survival_utility': 120.0, 'cognitive_cost': 50.0, 'accuracy': 1.0}
    ]
    
    # Cognitive Scarcity (λ) - Represents pressure on cognitive resources (e.g., immediate threat, hunger)
    lambdas = np.linspace(0.1, 5.0, 50) # From cognitive abundance to high scarcity
    
    results = []
    
    for lambd in lambdas:
        best_v = -np.inf
        chosen_mode = None
        
        for p_mode in perception_modes:
            # V = Survival_Utility - λ * Cognitive_Cost
            v = p_mode['survival_utility'] - (lambd * p_mode['cognitive_cost'])
            
            if v > best_v:
                best_v = v
                chosen_mode = p_mode
        
        results.append({
            'lambda': lambd,
            'chosen_name': chosen_mode['name'],
            'chosen_accuracy': chosen_mode['accuracy'],
            'net_value': best_v
        })
            
    df = pd.DataFrame(results)
    
    # Save
    output_dir = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results"
    os.makedirs(output_dir, exist_ok=True)
    df.to_json(f"{output_dir}/cycle2726_data.json")
    
    # Visualize
    plt.figure(figsize=(10, 6))
    
    # Plot chosen accuracy against lambda
    plt.plot(df['lambda'], df['chosen_accuracy'], marker='o', linestyle='-', color='blue')
    plt.title('Perception Mode Accuracy vs Cognitive Scarcity (λ)')
    plt.xlabel('Cognitive Scarcity (λ)')
    plt.ylabel('Chosen Mode Accuracy')
    plt.ylim(0, 1.1)
    plt.grid(True)
    
    # Annotate transitions
    mode_changes = df.drop_duplicates(subset=['chosen_name'])
    for idx, row in mode_changes.iterrows():
        plt.axvline(x=row['lambda'], color='gray', linestyle=':', linewidth=0.8)
        plt.text(row['lambda'] + 0.05, row['chosen_accuracy'] + 0.1, row['chosen_name'], 
                 rotation=0, verticalalignment='bottom', horizontalalignment='left', fontsize=8, color='darkgreen')
    
    plt.tight_layout()
    plt.savefig("/Volumes/dual/DUALITY-ZERO-V2/data/figures/cycle2726_naive_realism_budget.png")
    
    # Analysis
    print("Cycle 2726 Analysis:")
    
    low_lambda_choice = df.iloc[0]['chosen_name']
    high_lambda_choice = df.iloc[-1]['chosen_name']
    
    print(f"Low λ Choice: {low_lambda_choice}")
    print(f"High λ Choice: {high_lambda_choice}")
    
    if low_lambda_choice == "Scientific Realism" and high_lambda_choice == "Naive Realism":
        print("HYPOTHESIS CONFIRMED: Naive Realism is a BCP-optimal heuristic for survival under high scarcity.")
        print("Our perception of reality adapts to our cognitive budget.")
    else:
        print("HYPOTHESIS FAILED or complex outcome.")

if __name__ == "__main__":
    run_experiment()
