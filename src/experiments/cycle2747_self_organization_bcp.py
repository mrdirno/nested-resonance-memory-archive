"""
Cycle 2747: Self-Organization as BCP (The Emergence Budget)
============================================================

Investigation: Do self-organizing systems (e.g., ant colonies, markets, flocking birds) emerge as BCP-optimal solutions to coordinate complex tasks without centralized, high-cost control? Is information processing distributed to reduce single-point failure/cost, potentially at the expense of global optimality?

Hypothesis:
Self-organization is a BCP-optimal control strategy for complex systems, especially under high costs of centralized control or high environmental uncertainty. It trades off perfect global optimality for robustness, scalability, and reduced overhead.
V(control_architecture) = Gain(Global_Objective_Achievement) - λ(System_Size/Complexity) * Cost(Centralized_Information_Processing + Communication).

1. Centralized Control: High Cost (central command, communication overhead), Potentially High Global Optimality, but Brittle and Unscalable. Optimal under low λ (small, simple systems).
2. Self-Organized Control: Low Cost (local rules, distributed info), Sufficient Global Optimality, Robust and Scalable. Optimal under high λ (large, complex systems).
3. Chaotic System: Very Low Cost, No Global Optimality.

We simulate a system choosing a control architecture.

"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os

def run_experiment():
    print("Initializing Cycle 2747: Self-Organization BCP...")
    
    # Control Architectures
    architectures = [
        # Centralized Control: High cost, high optimality, brittle
        {'name': "Centralized", 'global_optimality_gain': 95.0, 'central_compute_cost_factor': 20.0, 'communication_cost_factor': 10.0, 'robustness': 0.5},
        # Self-Organized Control: Low cost, sufficient optimality, robust
        {'name': "Self-Organized", 'global_optimality_gain': 80.0, 'central_compute_cost_factor': 1.0, 'communication_cost_factor': 5.0, 'robustness': 0.9}, 
        # Chaotic System: Very low cost, no optimality
        {'name': "Chaotic", 'global_optimality_gain': 10.0, 'central_compute_cost_factor': 0.1, 'communication_cost_factor': 0.1, 'robustness': 0.99}
    ]
    
    # System Size/Complexity (λ) - Represents number of agents, interdependencies, information processing demand.
    # Higher λ means higher cost of centralized control.
    lambdas = np.linspace(0.1, 5.0, 50) # From small/simple to large/complex systems
    
    results = []
    
    for lambd in lambdas:
        best_v = -np.inf
        chosen_architecture = None
        
        for arch in architectures:
            # Total Cost = λ * (Central_Compute_Cost_Factor + Communication_Cost_Factor)
            # Higher lambda means higher penalty for centralized processing.
            total_cost = lambd * (arch['central_compute_cost_factor'] + arch['communication_cost_factor'])
            
            # V = Gain(Global_Objective_Achievement) - Total_Cost
            v = arch['global_optimality_gain'] - total_cost
            
            if v > best_v:
                best_v = v
                chosen_architecture = arch
        
        results.append({
            'lambda': lambd,
            'chosen_name': chosen_architecture['name'],
            'chosen_robustness': chosen_architecture['robustness'],
            'net_value': best_v
        })
            
    df = pd.DataFrame(results)
    
    # Save
    output_dir = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results"
    os.makedirs(output_dir, exist_ok=True)
    df.to_json(f"{output_dir}/cycle2747_data.json")
    
    # Visualize
    plt.figure(figsize=(10, 6))
    
    # Plot chosen robustness against lambda
    plt.plot(df['lambda'], df['chosen_robustness'], marker='o', linestyle='-', color='blue')
    plt.title('Control Architecture Robustness vs System Size/Complexity (λ)')
    plt.xlabel('System Size/Complexity (λ)')
    plt.ylabel('Chosen Architecture Robustness')
    plt.ylim(0, 1.1)
    plt.grid(True)
    
    # Annotate transitions
    arch_changes = df.drop_duplicates(subset=['chosen_name'])
    for idx, row in arch_changes.iterrows():
        plt.axvline(x=row['lambda'], color='gray', linestyle=':', linewidth=0.8)
        plt.text(row['lambda'] + 0.05, row['chosen_robustness'] + 0.05, row['chosen_name'], 
                 rotation=0, verticalalignment='bottom', horizontalalignment='left', fontsize=8, color='darkgreen')
    
    plt.tight_layout()
    plt.savefig("/Volumes/dual/DUALITY-ZERO-V2/data/figures/cycle2747_self_organization_budget.png")
    
    # Analysis
    print("Cycle 2747 Analysis:")
    
    low_lambda_choice = df.iloc[0]['chosen_name']
    high_lambda_choice = df.iloc[-1]['chosen_name']
    
    print(f"Low λ Choice: {low_lambda_choice}")
    print(f"High λ Choice: {high_lambda_choice}")
    
    if low_lambda_choice == "Centralized" and high_lambda_choice == "Self-Organized":
        print("HYPOTHESIS CONFIRMED: Self-organization is a BCP-optimal control strategy for complex systems.")
        print("Distributed information processing reduces cost and enhances robustness under high complexity.")
    else:
        print("HYPOTHESIS FAILED or complex outcome.")

if __name__ == "__main__":
    run_experiment()
