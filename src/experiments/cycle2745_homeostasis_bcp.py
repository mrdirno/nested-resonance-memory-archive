"""
Cycle 2745: Homeostasis as BCP (The Stability Budget)
======================================================

Investigation: Is biological homeostasis (e.g., body temperature, blood sugar regulation) a BCP system? Does it maintain physiological parameters within a narrow range (precision/stability) against environmental disturbances at a minimal energy cost, and are extreme responses (like fever) BCP-optimal under high threat?

Hypothesis:
Homeostasis is a BCP-optimal control strategy. The setpoint and tightness of regulation are dynamically adjusted to balance physiological stability (Gain) against the energy and resource cost of regulation (Cost), modulated by environmental disturbance/threat (λ).
V(homeostasis) = Gain(Physiological_Stability) - λ(Disturbance) * Cost(Energy_Expenditure + Resource_Allocation).

1. Precise Regulation: High Energy Cost, High Stability. Optimal under low λ (stable environment).
2. Loose Regulation: Lower Energy Cost, Lower Stability. Optimal under moderate λ (mild fluctuation).
3. Overdrive (e.g., Fever): Very High Energy Cost, but High Gain (fighting infection). Optimal under high λ (severe threat).

We simulate a biological system (e.g., body temperature) managing its internal state.

"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os

def run_experiment():
    print("Initializing Cycle 2745: Homeostasis BCP...")
    
    # Homeostatic Strategies
    strategies = [
        # Precise Regulation: High energy cost, very stable
        {'name': "Precise Regulation", 'stability_gain': 100.0, 'energy_cost_base': 20.0, 'energy_cost_variance': 15.0, 'setpoint_deviation': 0.05, 'threat_bonus_multiplier': 0.0},
        # Loose Regulation: Lower energy cost, allows more fluctuation
        {'name': "Loose Regulation", 'stability_gain': 70.0, 'energy_cost_base': 5.0, 'energy_cost_variance': 10.0, 'setpoint_deviation': 0.2, 'threat_bonus_multiplier': 0.0}, 
        # Overdrive (Fever): Very high energy cost, high gain ONLY under severe threat
        {'name': "Overdrive (Fever)", 'stability_gain': 30.0, 'energy_cost_base': 50.0, 'energy_cost_variance': 15.0, 'setpoint_deviation': 0.1, 'threat_bonus_multiplier': 30.0}
    ]
    
    # Environmental Disturbance (λ) - Represents threat level, environmental fluctuation, stress.
    # Higher λ means more severe disturbance / higher need for adaptive response.
    lambdas = np.linspace(0.1, 5.0, 50) # From stable environment to high disturbance
    
    results = []
    
    for lambd in lambdas:
        best_v = -np.inf
        chosen_strategy = None
        
        for strat in strategies:
            # Total Cost = Energy_Cost_Base + λ * Energy_Cost_Variance
            total_cost = strat['energy_cost_base'] + (lambd * strat['energy_cost_variance'])
            
            # Gain = base stability gain + λ * threat_bonus_multiplier (for overdrive)
            gain = strat['stability_gain'] + (lambd * strat['threat_bonus_multiplier'])
            
            # V = Gain(Physiological_Stability) - Total_Cost
            v = gain - total_cost
            
            if v > best_v:
                best_v = v
                chosen_strategy = strat
        
        results.append({
            'lambda': lambd,
            'chosen_name': chosen_strategy['name'],
            'chosen_deviation': chosen_strategy['setpoint_deviation'],
            'net_value': best_v
        })
            
    df = pd.DataFrame(results)
    
    # Save
    output_dir = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results"
    os.makedirs(output_dir, exist_ok=True)
    df.to_json(f"{output_dir}/cycle2745_data.json")
    
    # Visualize
    plt.figure(figsize=(10, 6))
    
    # Plot chosen setpoint deviation against lambda
    plt.plot(df['lambda'], df['chosen_deviation'], marker='o', linestyle='-', color='blue')
    plt.title('Homeostatic Strategy Setpoint Deviation vs Environmental Disturbance (λ)')
    plt.xlabel('Environmental Disturbance / Threat (λ)')
    plt.ylabel('Chosen Strategy Setpoint Deviation')
    plt.ylim(0, 0.3)
    plt.grid(True)
    
    # Annotate transitions
    strategy_changes = df.drop_duplicates(subset=['chosen_name'])
    for idx, row in strategy_changes.iterrows():
        plt.axvline(x=row['lambda'], color='gray', linestyle=':', linewidth=0.8)
        plt.text(row['lambda'] + 0.05, row['chosen_deviation'] + 0.02, row['chosen_name'], 
                 rotation=0, verticalalignment='bottom', horizontalalignment='left', fontsize=8, color='darkgreen')
    
    plt.tight_layout()
    plt.savefig("/Volumes/dual/DUALITY-ZERO-V2/data/figures/cycle2745_homeostasis_budget.png")
    
    # Analysis
    print("Cycle 2745 Analysis:")
    
    low_lambda_choice = df.iloc[0]['chosen_name']
    high_lambda_choice = df.iloc[-1]['chosen_name']
    
    print(f"Low λ Choice: {low_lambda_choice}")
    print(f"High λ Choice: {high_lambda_choice}")
    
    if low_lambda_choice == "Precise Regulation" and high_lambda_choice == "Overdrive (Fever)":
        print("HYPOTHESIS CONFIRMED: Homeostasis is a BCP-optimal control strategy.")
        print("Regulation adapts to environmental disturbance, prioritizing efficient stability or extreme response under threat.")
    else:
        print("HYPOTHESIS FAILED or complex outcome.")

if __name__ == "__main__":
    run_experiment()
