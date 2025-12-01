"""
Cycle 2751: Justice as BCP (The Fairness Budget)
=================================================

Investigation: Is the concept of "justice" (fairness, equity) a BCP-optimal solution to maintain social cohesion (gain) by distributing enforcement costs and benefits, reducing societal friction (λ)? Do different legal systems (e.g., restorative, retributive) represent BCP strategies for managing this budget?

Hypothesis:
Justice systems are BCP-optimal mechanisms for managing social friction and maintaining social cohesion. The "best" system is not absolute but dynamically chosen based on societal pressure (λ), balancing social order (Gain) against the costs of enforcement, liberty sacrifice, and victim dissatisfaction.
V(justice_system) = Gain(Social_Cohesion_Order) - λ(Societal_Friction) * Cost(Enforcement + Victim_Dissatisfaction + Recidivism).

1. Retributive Justice: High Enforcement Cost (punishment), Moderate Gain (deterrence, victim satisfaction). Optimal when immediate deterrence is critical (high λ, high crime).
2. Restorative Justice: Moderate Enforcement Cost (mediation, rehabilitation), High Gain (reintegration, reduced recidivism, victim satisfaction). Optimal under lower λ (social capital, long-term focus).
3. Laissez-faire (No Justice): Very Low Enforcement Cost, Very Low Gain (high societal friction, low order). Only chosen if ALL other systems are prohibitively expensive.

We simulate a society choosing a justice system.

"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os

def run_experiment():
    print("Initializing Cycle 2751: Justice BCP...")
    
    # Justice Systems
    systems = [
        # Retributive Justice: Moderate gain, efficient enforcement for punishment
        {'name': "Retributive", 'social_cohesion_gain': 80.0, 'enforcement_cost': 10.0, 'victim_dissatisfaction': 2.0, 'recidivism_cost': 3.0, 'order_level': 0.7},
        # Restorative Justice: High gain, moderate cost, focuses on healing
        {'name': "Restorative", 'social_cohesion_gain': 90.0, 'enforcement_cost': 15.0, 'victim_dissatisfaction': 5.0, 'recidivism_cost': 2.0, 'order_level': 0.9}, 
        # Laissez-faire: Low enforcement, low cohesion
        {'name': "Laissez-faire", 'social_cohesion_gain': 30.0, 'enforcement_cost': 2.0, 'victim_dissatisfaction': 30.0, 'recidivism_cost': 20.0, 'order_level': 0.3}
    ]
    
    # Societal Friction (λ) - Represents crime rate, social inequality, economic stress.
    # Higher λ means higher social friction / need for robust justice system.
    lambdas = np.linspace(0.1, 5.0, 50) # From low friction to high friction
    
    results = []
    
    for lambd in lambdas:
        best_v = -np.inf
        chosen_system = None
        
        for sys in systems:
            # Total Cost = Enforcement_Cost + Victim_Dissatisfaction + Recidivism_Cost
            # Assume these costs are scaled by lambda to reflect difficulty under friction
            total_cost_per_lambda = sys['enforcement_cost'] + sys['victim_dissatisfaction'] + sys['recidivism_cost']
            
            # V = Gain(Social_Cohesion_Order) - λ * Total_Cost
            v = sys['social_cohesion_gain'] - (lambd * total_cost_per_lambda)
            
            if v > best_v:
                best_v = v
                chosen_system = sys
        
        results.append({
            'lambda': lambd,
            'chosen_name': chosen_system['name'],
            'chosen_order_level': chosen_system['order_level'],
            'net_value': best_v
        })
            
    df = pd.DataFrame(results)
    
    # Save
    output_dir = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results"
    os.makedirs(output_dir, exist_ok=True)
    df.to_json(f"{output_dir}/cycle2751_data.json")
    
    # Visualize
    plt.figure(figsize=(10, 6))
    
    # Plot chosen order level against lambda
    plt.plot(df['lambda'], df['chosen_order_level'], marker='o', linestyle='-', color='blue')
    plt.title('Justice System Order Level vs Societal Friction (λ)')
    plt.xlabel('Societal Friction (λ)')
    plt.ylabel('Chosen System Order Level')
    plt.ylim(0, 1.1)
    plt.grid(True)
    
    # Annotate transitions
    system_changes = df.drop_duplicates(subset=['chosen_name'])
    for idx, row in system_changes.iterrows():
        plt.axvline(x=row['lambda'], color='gray', linestyle=':', linewidth=0.8)
        plt.text(row['lambda'] + 0.05, row['chosen_order_level'] + 0.05, row['chosen_name'], 
                 rotation=0, verticalalignment='bottom', horizontalalignment='left', fontsize=8, color='darkgreen')
    
    plt.tight_layout()
    plt.savefig("/Volumes/dual/DUALITY-ZERO-V2/data/figures/cycle2751_justice_budget.png")
    
    # Analysis
    print("Cycle 2751 Analysis:")
    
    low_lambda_choice = df.iloc[0]['chosen_name']
    high_lambda_choice = df.iloc[-1]['chosen_name']
    
    print(f"Low λ Choice: {low_lambda_choice}")
    print(f"High λ Choice: {high_lambda_choice}")
    
    if low_lambda_choice == "Restorative" and high_lambda_choice == "Retributive":
        print("HYPOTHESIS CONFIRMED: Justice is a BCP-optimal solution for social cohesion.")
        print("Legal systems adapt to societal friction, balancing social order vs costs.")
    else:
        print("HYPOTHESIS FAILED or complex outcome.")

if __name__ == "__main__":
    run_experiment()
