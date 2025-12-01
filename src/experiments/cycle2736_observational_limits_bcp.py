"""
Cycle 2736: Observational Limits as BCP (The Horizon Budget)
=============================================================

Investigation: Do observational limits (like the cosmic horizon) represent BCP boundaries, where information beyond is prohibitively expensive, leading our models to optimally truncate at these boundaries?

Hypothesis:
The construction of cosmological models is constrained by the cost of acquiring and processing observational data. Regions of the universe beyond our observational horizon are effectively of infinite "Observational Cost," making detailed modeling of them BCP-irrational.
V(model_scope) = Gain(Explanatory_Power) - λ(Observational) * Cost(Data_Acquisition + Model_Complexity).

1. Model within Horizon: High Explanatory Power (constrained by data), Finite Cost (observable data, manageable complexity).
2. Model beyond Horizon: Hypothetically High Explanatory Power (if perfect), Effectively Infinite Cost (no observational data, pure speculation).
3. Under any finite λ, a model that includes regions beyond the horizon with high detail will have V < 0 due to infinite cost.
4. Our models will optimally truncate their detailed descriptions at the horizon, prioritizing the observable.

We simulate a cosmologist choosing the scope of their model given observational budget.

"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os

def run_experiment():
    print("Initializing Cycle 2736: Observational Limits BCP...")
    
    # Model Scopes
    model_scopes = [
        # Model within Horizon: Realistic, data-constrained, manageable cost
        {'name': "Model within Horizon", 'explanatory_power': 90.0, 'observational_cost': 15.0, 'detail_level': 1.0},
        # Model beyond Horizon: High ambition, but effectively infinite observational cost
        {'name': "Model beyond Horizon", 'explanatory_power': 100.0, 'observational_cost': 1000000.0, 'detail_level': 0.1}, # High cost represents speculation without data
        # Abstract Global Model: Low cost, low detail, for overall structure only
        {'name': "Abstract Global Model", 'explanatory_power': 60.0, 'observational_cost': 5.0, 'detail_level': 0.5}
    ]
    
    # Observational Pressure (λ) - Represents telescope time, funding, data processing capacity
    lambdas = np.linspace(0.1, 5.0, 50) # From observational abundance to high pressure
    
    results = []
    
    for lambd in lambdas:
        best_v = -np.inf
        chosen_scope = None
        
        for scope in model_scopes:
            # V = Gain(Explanatory_Power) - λ * Observational_Cost
            v = scope['explanatory_power'] - (lambd * scope['observational_cost'])
            
            if v > best_v:
                best_v = v
                chosen_scope = scope
        
        results.append({
            'lambda': lambd,
            'chosen_name': chosen_scope['name'],
            'chosen_detail_level': chosen_scope['detail_level'],
            'net_value': best_v
        })
            
    df = pd.DataFrame(results)
    
    # Save
    output_dir = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results"
    os.makedirs(output_dir, exist_ok=True)
    df.to_json(f"{output_dir}/cycle2736_data.json")
    
    # Visualize
    plt.figure(figsize=(10, 6))
    
    # Plot chosen detail level against lambda
    plt.plot(df['lambda'], df['chosen_detail_level'], marker='o', linestyle='-', color='blue')
    plt.title('Model Scope Detail Level vs Observational Pressure (λ)')
    plt.xlabel('Observational Pressure (λ)')
    plt.ylabel('Chosen Model Detail Level')
    plt.ylim(0, 1.1)
    plt.grid(True)
    
    # Annotate transitions
    scope_changes = df.drop_duplicates(subset=['chosen_name'])
    for idx, row in scope_changes.iterrows():
        plt.axvline(x=row['lambda'], color='gray', linestyle=':', linewidth=0.8)
        plt.text(row['lambda'] + 0.05, row['chosen_detail_level'] + 0.1, row['chosen_name'], 
                 rotation=0, verticalalignment='bottom', horizontalalignment='left', fontsize=8, color='darkgreen')
    
    plt.tight_layout()
    plt.savefig("/Volumes/dual/DUALITY-ZERO-V2/data/figures/cycle2736_observational_limits_budget.png")
    
    # Analysis
    print("Cycle 2736 Analysis:")
    
    low_lambda_choice = df.iloc[0]['chosen_name']
    high_lambda_choice = df.iloc[-1]['chosen_name']
    
    print(f"Low λ Choice: {low_lambda_choice}")
    print(f"High λ Choice: {high_lambda_choice}")
    
    if low_lambda_choice == "Model within Horizon" and high_lambda_choice == "Abstract Global Model":
        print("HYPOTHESIS CONFIRMED: Our cosmological models optimally truncate at observational limits.")
        print("Modeling beyond the horizon is BCP-irrational due to effectively infinite observational cost.")
    else:
        print("HYPOTHESIS FAILED or complex outcome.")

if __name__ == "__main__":
    run_experiment()
