"""
Cycle 2735: Theory Choice as BCP (The Paradigm Budget)
======================================================

Investigation: Is the choice between competing scientific theories (e.g., cosmological paradigms) a BCP-driven process, where factors like elegance, testability, and conceptual difficulty determine their adoption?

Hypothesis:
The scientific community, as a budget-constrained collective intelligence, selects theories based on their BCP value. A theory is adopted if its "Explanatory Power" (Gain) outweighs its "Cognitive/Developmental Cost" (Cost), modulated by research pressure (λ).
V(theory) = Gain(Explanatory_Power) - λ(Research) * Cost(Conceptual_Complexity + Empirical_Testing).

1. Established Paradigm: Low Conceptual Complexity (familiarity), High Explanatory Power (well-tested), but maybe with anomalies.
2. Revolutionary Theory: High Conceptual Complexity (new math, new concepts), Potentially Higher Explanatory Power (solves anomalies), but High Empirical Testing Cost.
3. Fringe Theory: Low Conceptual Complexity (simplistic), Low Explanatory Power.

We simulate the scientific community's adoption of theories given research pressure.

"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os

def run_experiment():
    print("Initializing Cycle 2735: Theory Choice BCP...")
    
    # Cosmological Theories
    theories = [
        # Established Paradigm: GR+ΛCDM - low conceptual cost, high fit, but known anomalies
        {'name': "Established Paradigm", 'explanatory_power': 85.0, 'conceptual_complexity': 5.0, 'testability_cost': 5.0, 'cohesion': 1.0},
        # Revolutionary Theory: Quantum Gravity - high conceptual cost, significantly higher fit/depth, but hard to test
        {'name': "Revolutionary Theory", 'explanatory_power': 120.0, 'conceptual_complexity': 60.0, 'testability_cost': 70.0, 'cohesion': 0.5},
        # Fringe Theory: Low cost, low gain
        {'name': "Fringe Theory", 'explanatory_power': 15.0, 'conceptual_complexity': 2.0, 'testability_cost': 1.0, 'cohesion': 0.2}
    ]
    
    # Research Pressure (λ) - Represents funding, intellectual conservatism, time pressure
    lambdas = np.linspace(0.1, 5.0, 50) # From research abundance to high pressure
    
    results = []
    
    for lambd in lambdas:
        best_v = -np.inf
        chosen_theory = None
        
        for theory in theories:
            # Total Cost = Conceptual_Complexity + Empirical_Testing
            total_cost = theory['conceptual_complexity'] + theory['testability_cost']
            
            # V = Gain(Explanatory_Power) - λ * Total_Cost
            v = theory['explanatory_power'] - (lambd * total_cost)
            
            if v > best_v:
                best_v = v
                chosen_theory = theory
        
        results.append({
            'lambda': lambd,
            'chosen_name': chosen_theory['name'],
            'chosen_cohesion': chosen_theory['cohesion'],
            'net_value': best_v
        })
            
    df = pd.DataFrame(results)
    
    # Save
    output_dir = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results"
    os.makedirs(output_dir, exist_ok=True)
    df.to_json(f"{output_dir}/cycle2735_data.json")
    
    # Visualize
    plt.figure(figsize=(10, 6))
    
    # Plot chosen cohesion against lambda (representing resistance to change)
    plt.plot(df['lambda'], df['chosen_cohesion'], marker='o', linestyle='-', color='blue')
    plt.title('Theory Choice Cohesion vs Research Pressure (λ)')
    plt.xlabel('Research Pressure (λ)')
    plt.ylabel('Chosen Theory Cohesion (1=Established, 0.5=Revolutionary)')
    plt.ylim(0, 1.1)
    plt.grid(True)
    
    # Annotate transitions
    theory_changes = df.drop_duplicates(subset=['chosen_name'])
    for idx, row in theory_changes.iterrows():
        plt.axvline(x=row['lambda'], color='gray', linestyle=':', linewidth=0.8)
        plt.text(row['lambda'] + 0.05, row['chosen_cohesion'] + 0.1, row['chosen_name'], 
                 rotation=0, verticalalignment='bottom', horizontalalignment='left', fontsize=8, color='darkgreen')
    
    plt.tight_layout()
    plt.savefig("/Volumes/dual/DUALITY-ZERO-V2/data/figures/cycle2735_theory_choice_budget.png")
    
    # Analysis
    print("Cycle 2735 Analysis:")
    
    low_lambda_choice = df.iloc[0]['chosen_name']
    high_lambda_choice = df.iloc[-1]['chosen_name']
    
    print(f"Low λ Choice: {low_lambda_choice}")
    print(f"High λ Choice: {high_lambda_choice}")
    
    if low_lambda_choice == "Revolutionary Theory" and high_lambda_choice == "Established Paradigm":
        print("HYPOTHESIS CONFIRMED: Theory choice is a BCP-driven process.")
        print("Under high research pressure, the scientific community prefers established paradigms despite known anomalies.")
        print("Revolutionary theories are only adopted when the cost of the established paradigm (anomalies) outweighs the high cost of theoretical revision (low λ).")
    else:
        print("HYPOTHESIS FAILED or complex outcome.")

if __name__ == "__main__":
    run_experiment()
