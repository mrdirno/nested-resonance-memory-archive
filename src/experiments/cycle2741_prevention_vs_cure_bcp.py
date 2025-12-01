"""
Cycle 2741: Prevention vs Cure as BCP (The Lifecycle Budget)
=============================================================

Investigation: Do individuals and societies choose between investing in disease prevention (lower long-term cost, higher initial investment) and disease cure (higher immediate cost, lower initial investment) based on their time horizons and resource availability (λ)?

Hypothesis:
The "optimal" strategy for health management (prevention vs. cure) is a BCP decision. Under conditions of high scarcity (short time horizons, limited resources), the focus rationally shifts to immediate, reactive (cure-oriented) solutions, even if less efficient long-term.
V(health_strategy) = Gain(Long_Term_Health_Outcome) - λ(Resources_Time_Horizon) * Cost(Upfront_Investment + Future_Risk_Mitigation).

1. Prevention Strategy: Higher Upfront Investment, Lower Long-Term Cost, Higher Overall Health Gain. Optimal under low λ (resource abundance, long time horizon).
2. Cure Strategy: Lower Upfront Investment, Higher Long-Term Cost (recurring, severe), Lower Overall Health Gain (reactive). Optimal under high λ (resource scarcity, short time horizon).

We simulate a decision-maker choosing a health strategy over a lifecycle.

"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os

def run_experiment():
    print("Initializing Cycle 2741: Prevention vs Cure BCP...")
    
    # Health Strategies
    strategies = [
        # Prevention Strategy: High current cost, high long-term benefit
        {'name': "Prevention", 'current_cost': 200.0, 'long_term_benefit': 1000.0},
        # Cure Strategy: Low current cost, lower long-term benefit (as problems might recur or be worse)
        {'name': "Cure", 'current_cost': 50.0, 'long_term_benefit': 700.0}
    ]
    
    # Patient Context (λ) - Represents resource scarcity AND short time horizon (higher λ = more focus on immediate costs)
    lambdas = np.linspace(0.01, 5.0, 50) # λ directly acts as a discount factor (inverse relation to time horizon)
    
    results = []
    
    for lambd in lambdas:
        best_v = -np.inf
        chosen_strategy = None
        
        for strat in strategies:
            # V = long_term_benefit / (1 + lambd) - current_cost
            # A common way to model discounting: divide future value by (1 + discount_rate)
            v = strat['long_term_benefit'] / (1 + lambd) - strat['current_cost']
            
            if v > best_v:
                best_v = v
                chosen_strategy = strat
        
        results.append({
            'lambda': lambd,
            'chosen_name': chosen_strategy['name'],
            'chosen_health_gain': chosen_strategy['long_term_benefit'] / (1 + lambd), # Just for plotting effectively discounted benefit
            'net_value': best_v
        })
            
    df = pd.DataFrame(results)
    
    # Save
    output_dir = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results"
    os.makedirs(output_dir, exist_ok=True)
    df.to_json(f"{output_dir}/cycle2741_data.json")
    
    # Visualize
    plt.figure(figsize=(10, 6))
    
    # Plot chosen health gain against lambda
    plt.plot(df['lambda'], df['chosen_health_gain'], marker='o', linestyle='-', color='blue')
    plt.title('Health Strategy Gain vs Resource Scarcity/Time Horizon (λ)')
    plt.xlabel('Resource Scarcity / Short Time Horizon (λ)')
    plt.ylabel('Chosen Strategy Total Health Gain')
    plt.ylim(0, 1100)
    plt.grid(True)
    
    # Annotate transitions
    strategy_changes = df.drop_duplicates(subset=['chosen_name'])
    for idx, row in strategy_changes.iterrows():
        plt.axvline(x=row['lambda'], color='gray', linestyle=':', linewidth=0.8)
        plt.text(row['lambda'] + 0.05, row['chosen_health_gain'] + 50, row['chosen_name'], 
                 rotation=0, verticalalignment='bottom', horizontalalignment='left', fontsize=8, color='darkgreen')
    
    plt.tight_layout()
    plt.savefig("/Volumes/dual/DUALITY-ZERO-V2/data/figures/cycle2741_prevention_vs_cure_budget.png")
    
    # Analysis
    print("Cycle 2741 Analysis:")
    
    low_lambda_choice = df.iloc[0]['chosen_name']
    high_lambda_choice = df.iloc[-1]['chosen_name']
    
    print(f"Low λ Choice: {low_lambda_choice}")
    print(f"High λ Choice: {high_lambda_choice}")
    
    if low_lambda_choice == "Prevention" and high_lambda_choice == "Cure":
        print("HYPOTHESIS CONFIRMED: Health strategy (prevention vs. cure) is a BCP process.")
        print("Under scarcity, the focus shifts to immediate, reactive (cure-oriented) solutions, even if less efficient long-term.")
    else:
        print("HYPOTHESIS FAILED or complex outcome.")

if __name__ == "__main__":
    run_experiment()
