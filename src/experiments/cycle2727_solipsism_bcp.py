"""
Cycle 2727: Solipsism as BCP (The Social Budget)
=================================================

Investigation: Is Solipsism (the belief that only one's mind is sure to exist) a BCP-rational retreat from the high social costs of maintaining a shared objective reality?

Hypothesis:
Maintaining a belief in a shared, objective external reality requires significant "Social Coordination Cost" (communication, trust, resolving disagreements). Solipsism avoids these costs entirely.
V(reality_mode) = Gain(Social_Cohesion) - λ(Social) * Social_Coordination_Cost.

1. Objective Reality: High Social Coordination Cost, but High Gain (collective action, shared knowledge).
2. Solipsism: Near-zero Social Coordination Cost, but Low Gain (isolation, lack of external validation).
3. Under high λ (social distrust, communication breakdown, high cost of consensus), Solipsism should become BCP-rational.
4. Under low λ (high trust, cheap communication), Objective Reality should dominate.

We simulate an agent choosing a "reality mode" based on the prevailing social environment.

"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os

def run_experiment():
    print("Initializing Cycle 2727: Solipsism BCP...")
    
    # Reality Modes
    reality_modes = [
        # Objective Reality: High social cohesion, but significant coordination cost
        {'name': "Objective Reality", 'social_gain': 100.0, 'social_coordination_cost': 50.0, 'cohesion_level': 1.0},
        # Solipsism: Zero coordination cost, but no social gain (isolation)
        {'name': "Solipsism", 'social_gain': 10.0, 'social_coordination_cost': 1.0, 'cohesion_level': 0.1} # Minimal internal cost
    ]
    
    # Social Scarcity (λ) - Represents social distrust, communication breakdown, cost of consensus
    lambdas = np.linspace(0.1, 5.0, 50) # From social abundance to high social scarcity
    
    results = []
    
    for lambd in lambdas:
        best_v = -np.inf
        chosen_mode = None
        
        for r_mode in reality_modes:
            # V = Social_Gain - λ * Social_Coordination_Cost
            v = r_mode['social_gain'] - (lambd * r_mode['social_coordination_cost'])
            
            if v > best_v:
                best_v = v
                chosen_mode = r_mode
        
        results.append({
            'lambda': lambd,
            'chosen_name': chosen_mode['name'],
            'chosen_cohesion_level': chosen_mode['cohesion_level'],
            'net_value': best_v
        })
            
    df = pd.DataFrame(results)
    
    # Save
    output_dir = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results"
    os.makedirs(output_dir, exist_ok=True)
    df.to_json(f"{output_dir}/cycle2727_data.json")
    
    # Visualize
    plt.figure(figsize=(10, 6))
    
    # Plot chosen cohesion level against lambda
    plt.plot(df['lambda'], df['chosen_cohesion_level'], marker='o', linestyle='-', color='blue')
    plt.title('Reality Mode Cohesion vs Social Scarcity (λ)')
    plt.xlabel('Social Scarcity (λ)')
    plt.ylabel('Chosen Mode Cohesion')
    plt.ylim(0, 1.1)
    plt.grid(True)
    
    # Annotate transitions
    mode_changes = df.drop_duplicates(subset=['chosen_name'])
    for idx, row in mode_changes.iterrows():
        plt.axvline(x=row['lambda'], color='gray', linestyle=':', linewidth=0.8)
        plt.text(row['lambda'] + 0.05, row['chosen_cohesion_level'] + 0.1, row['chosen_name'], 
                 rotation=0, verticalalignment='bottom', horizontalalignment='left', fontsize=8, color='darkgreen')
    
    plt.tight_layout()
    plt.savefig("/Volumes/dual/DUALITY-ZERO-V2/data/figures/cycle2727_solipsism_budget.png")
    
    # Analysis
    print("Cycle 2727 Analysis:")
    
    low_lambda_choice = df.iloc[0]['chosen_name']
    high_lambda_choice = df.iloc[-1]['chosen_name']
    
    print(f"Low λ Choice: {low_lambda_choice}")
    print(f"High λ Choice: {high_lambda_choice}")
    
    if low_lambda_choice == "Objective Reality" and high_lambda_choice == "Solipsism":
        print("HYPOTHESIS CONFIRMED: Solipsism is a BCP-rational retreat from high social coordination costs.")
        print("The belief in a shared reality is an economic choice.")
    else:
        print("HYPOTHESIS FAILED or complex outcome.")

if __name__ == "__main__":
    run_experiment()
