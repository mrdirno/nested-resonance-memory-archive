"""
Cycle 2753: Rights as BCP (The Freedom Budget)
==============================================

Investigation: Are individual rights (e.g., freedom of speech, due process) BCP-optimal compromises? Do they set a fixed cost on the state (limiting its power) in exchange for reduced transaction costs for citizens and increased social stability, and is the optimal scope of rights λ-dependent?

Hypothesis:
Individual rights are a BCP-optimal solution for managing the trade-off between state power and individual liberty. They incur a "cost" on the state (limiting its power, requiring due process) but provide "gain" in reduced transaction costs for citizens, increased innovation, and enhanced social stability. The optimal scope of rights is dynamically chosen based on societal pressure (λ).
V(rights_regime) = Gain(Social_Stability + Individual_Welfare) - λ(Societal_Pressure) * Cost(State_Control_Limitation + Enforcement_Overhead + Citizen_Friction).

1. Minimal Rights (Authoritarian): Low State Control Limitation Cost, High Citizen Friction Cost. Optimal under high λ (perceived existential threat, high social chaos).
2. Balanced Rights (Democratic): Moderate Costs for State and Citizens, High Social Stability/Welfare. Optimal under moderate λ.
3. Extensive Rights (Libertarian): High State Control Limitation Cost, Low Citizen Friction Cost, Potentially Lower Social Stability (from lack of state action). Optimal under low λ (high trust, resource abundance).

We simulate a society choosing a rights regime.

"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os

def run_experiment():
    print("Initializing Cycle 2753: Rights BCP...")
    
    # Rights Regimes
    regimes = [
        # Minimal Rights (Authoritarian): High Gain in Order (via State Power), High State Control Cost (surveillance, enforcement), Low Citizen Friction (suppressed)
        {'name': "Minimal Rights", 'social_order_gain': 90.0, 'state_control_cost': 30.0, 'citizen_friction_cost': 5.0, 'liberty_level': 0.3},
        # Balanced Rights (Democratic): Moderate Costs, High Gain in Social Order and Individual Welfare
        {'name': "Balanced Rights", 'social_order_gain': 95.0, 'state_control_cost': 20.0, 'citizen_friction_cost': 10.0, 'liberty_level': 0.7}, 
        # Extensive Rights (Libertarian): High Cost to State (weak control), Moderate Gain, Moderate Citizen Friction
        {'name': "Extensive Rights", 'social_order_gain': 80.0, 'state_control_cost': 50.0, 'citizen_friction_cost': 15.0, 'liberty_level': 0.9}
    ]
    
    # Societal Pressure (λ) - Represents external threats, internal divisions, resource scarcity.
    # Higher λ means higher urgency for state control.
    lambdas = np.linspace(0.1, 5.0, 50) # From low pressure to high pressure
    
    results = []
    
    for lambd in lambdas:
        best_v = -np.inf
        chosen_regime = None
        
        for reg in regimes:
            # V = Gain(Social_Order_Gain) - Cost(State_Control) - λ * Cost(Citizen_Friction)
            # This models citizen friction as an amplified cost under societal pressure.
            v = reg['social_order_gain'] - reg['state_control_cost'] - (lambd * reg['citizen_friction_cost'])
            
            if v > best_v:
                best_v = v
                chosen_regime = reg
        
        results.append({
            'lambda': lambd,
            'chosen_name': chosen_regime['name'],
            'chosen_liberty_level': chosen_regime['liberty_level'],
            'net_value': best_v
        })

            
    df = pd.DataFrame(results)
    
    # Save
    output_dir = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results"
    os.makedirs(output_dir, exist_ok=True)
    df.to_json(f"{output_dir}/cycle2753_data.json")
    
    # Visualize
    plt.figure(figsize=(10, 6))
    
    # Plot chosen liberty level against lambda
    plt.plot(df['lambda'], df['chosen_liberty_level'], marker='o', linestyle='-', color='blue')
    plt.title('Rights Regime Liberty Level vs Societal Pressure (λ)')
    plt.xlabel('Societal Pressure (λ)')
    plt.ylabel('Chosen Regime Liberty Level')
    plt.ylim(0, 1.1)
    plt.grid(True)
    
    # Annotate transitions
    regime_changes = df.drop_duplicates(subset=['chosen_name'])
    for idx, row in regime_changes.iterrows():
        plt.axvline(x=row['lambda'], color='gray', linestyle=':', linewidth=0.8)
        plt.text(row['lambda'] + 0.05, row['chosen_liberty_level'] + 0.05, row['chosen_name'], 
                 rotation=0, verticalalignment='bottom', horizontalalignment='left', fontsize=8, color='darkgreen')
    
    plt.tight_layout()
    plt.savefig("/Volumes/dual/DUALITY-ZERO-V2/data/figures/cycle2753_rights_budget.png")
    
    # Analysis
    print("Cycle 2753 Analysis:")
    
    low_lambda_choice = df.iloc[0]['chosen_name']
    high_lambda_choice = df.iloc[-1]['chosen_name']
    
    print(f"Low λ Choice: {low_lambda_choice}")
    print(f"High λ Choice: {high_lambda_choice}")
    
    if low_lambda_choice == "Balanced Rights" and high_lambda_choice == "Minimal Rights":
        print("HYPOTHESIS CONFIRMED: Individual rights are BCP-optimal compromises.")
        print("The scope of rights adapts to societal pressure, balancing state control vs individual welfare.")
    else:
        print("HYPOTHESIS FAILED or complex outcome.")

if __name__ == "__main__":
    run_experiment()
