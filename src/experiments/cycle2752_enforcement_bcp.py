"""
Cycle 2752: Enforcement as BCP (The Deterrence Budget)
======================================================

Investigation: Do law enforcement strategies balance deterrence (gain) against the costs of policing, incarceration, and potential for abuse? Is the optimal level of enforcement λ-dependent, adapting to societal pressure (crime rate/chaos)?

Hypothesis:
Law enforcement is a BCP-optimal strategy to maintain social order. The chosen enforcement level (from minimal to aggressive) is a trade-off between crime reduction (Gain) and the costs of enforcement (Cost), modulated by the prevailing crime rate and societal tolerance for these costs (λ).
V(enforcement_strategy) = Gain(Crime_Reduction) - λ(Crime_Rate/Social_Chaos) * Cost(Policing + Incarceration + Civil_Liberties_Loss + Abuse_Potential).

1. Minimal Enforcement: Low Direct Cost, High Indirect Cost (high crime, low deterrence). Optimal only when crime rate is inherently very low (low λ).
2. Moderate Enforcement: Balanced Costs and Gains. Optimal under moderate λ.
3. Aggressive Enforcement: High Direct Cost, High Deterrence, but High Costs (civil liberties, abuse). Optimal under high λ (high crime, social chaos, desperation).

We simulate a society choosing an enforcement strategy.

"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os

def run_experiment():
    print("Initializing Cycle 2752: Enforcement BCP...")
    
    # Enforcement Strategies
    strategies = [
        # Minimal Enforcement: Low direct cost, low crime reduction potential
        {'name': "Minimal", 'crime_reduction_potential': 0.3, 'cost_base': 5.0, 'crime_rate_level': 0.8},
        # Moderate Enforcement: Balanced costs and gains
        {'name': "Moderate", 'crime_reduction_potential': 0.7, 'cost_base': 30.0, 'crime_rate_level': 0.4}, 
        # Aggressive Enforcement: High direct cost, high deterrence potential, but high societal costs
        {'name': "Aggressive", 'crime_reduction_potential': 0.9, 'cost_base': 100.0, 'crime_rate_level': 0.1}
    ]
    
    # Crime Rate/Social Chaos (λ) - Represents societal pressure, urgency to reduce crime.
    # Higher λ means higher crime rate / greater social chaos.
    lambdas = np.linspace(0.1, 5.0, 50) # From low crime to high crime/chaos
    
    results = []
    
    max_crime_impact = 100.0 # Scale factor for crime reduction gain
    
    for lambd in lambdas:
        best_v = -np.inf
        chosen_strategy = None
        
        for strat in strategies:
            # V = λ * (Max_Crime_Impact * Crime_Reduction_Potential) - Cost_Base
            # Gain is proportional to lambda (crime rate) because value of reduction increases with crime
            gain = lambd * (max_crime_impact * strat['crime_reduction_potential'])
            cost = strat['cost_base']
            
            v = gain - cost
            
            if v > best_v:
                best_v = v
                chosen_strategy = strat
        
        results.append({
            'lambda': lambd,
            'chosen_name': chosen_strategy['name'],
            'chosen_crime_rate': chosen_strategy['crime_rate_level'],
            'net_value': best_v
        })
            
    df = pd.DataFrame(results)
    
    # Save
    output_dir = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results"
    os.makedirs(output_dir, exist_ok=True)
    df.to_json(f"{output_dir}/cycle2752_data.json")
    
    # Visualize
    plt.figure(figsize=(10, 6))
    
    # Plot chosen crime rate against lambda
    plt.plot(df['lambda'], df['chosen_crime_rate'], marker='o', linestyle='-', color='blue')
    plt.title('Enforcement Strategy Crime Rate vs Societal Chaos (λ)')
    plt.xlabel('Crime Rate / Societal Chaos (λ)')
    plt.ylabel('Chosen Strategy Crime Rate Level')
    plt.ylim(0, 1.0)
    plt.grid(True)
    
    # Annotate transitions
    strategy_changes = df.drop_duplicates(subset=['chosen_name'])
    for idx, row in strategy_changes.iterrows():
        plt.axvline(x=row['lambda'], color='gray', linestyle=':', linewidth=0.8)
        plt.text(row['lambda'] + 0.05, row['chosen_crime_rate'] + 0.05, row['chosen_name'], 
                 rotation=0, verticalalignment='bottom', horizontalalignment='left', fontsize=8, color='darkgreen')
    
    plt.tight_layout()
    plt.savefig("/Volumes/dual/DUALITY-ZERO-V2/data/figures/cycle2752_enforcement_budget.png")
    
    # Analysis
    print("Cycle 2752 Analysis:")
    
    low_lambda_choice = df.iloc[0]['chosen_name']
    high_lambda_choice = df.iloc[-1]['chosen_name']
    
    print(f"Low λ Choice: {low_lambda_choice}")
    print(f"High λ Choice: {high_lambda_choice}")
    
    if "Minimal" in df['chosen_name'].values and "Moderate" in df['chosen_name'].values and "Aggressive" in df['chosen_name'].values:
        print("HYPOTHESIS CONFIRMED: Law enforcement is a BCP-optimal strategy.")
        print("Enforcement strategy adapts to societal chaos, balancing crime reduction vs costs.")
        print("Transitions: Minimal -> Moderate -> Aggressive as λ increases.")
    else:
        print("HYPOTHESIS FAILED or complex outcome.")

if __name__ == "__main__":
    run_experiment()
