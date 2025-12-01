"""
Cycle 2740: Treatment Choice as BCP (The Therapeutic Budget)
============================================================

Investigation: Does choosing a medical treatment involve BCP tradeoffs, where physicians and patients weigh efficacy (gain) against side effects, invasiveness, cost, and recovery time, with the optimal choice being λ-dependent?

Hypothesis:
Medical treatment decisions are BCP-optimal strategies. The "best" treatment is not absolute but depends on the patient's context (representing λ) and the balance between expected health gain and various costs.
V(treatment) = Gain(Health_Outcome) - λ(Patient_Context) * Cost(Side_Effects + Financial + Invasiveness + Recovery_Time).

1. Aggressive Treatment: High Gain, High Cost (side effects, invasiveness, financial). Optimal under low λ (young, healthy, good insurance, high risk tolerance).
2. Conservative Treatment: Moderate Gain, Low Cost. Optimal under moderate λ.
3. Palliative Care: Low Cost (comfort-focused), Moderate Gain (quality of life). Optimal under high λ (elderly, frail, limited resources, low risk tolerance).

We simulate a physician/patient choosing a treatment strategy.

"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os

def run_experiment():
    print("Initializing Cycle 2740: Treatment Choice BCP...")
    
    # Treatment Strategies
    strategies = [
        # Aggressive Treatment: High gain, high cost (chemo, major surgery)
        {'name': "Aggressive Treatment", 'health_gain': 90.0, 'side_effects': 30.0, 'financial_cost': 100.0, 'invasiveness': 20.0, 'recovery_time': 15.0, 'survival_rate_factor': 0.9},
        # Conservative Treatment: Moderate gain, moderate cost (lifestyle change, less invasive meds)
        {'name': "Conservative Treatment", 'health_gain': 60.0, 'side_effects': 10.0, 'financial_cost': 20.0, 'invasiveness': 5.0, 'recovery_time': 5.0, 'survival_rate_factor': 0.7}, 
        # Palliative Care: Low cost, focus on comfort (symptom management)
        {'name': "Palliative Care", 'health_gain': 30.0, 'side_effects': 2.0, 'financial_cost': 5.0, 'invasiveness': 1.0, 'recovery_time': 1.0, 'survival_rate_factor': 0.3}
    ]
    
    # Patient Context (λ) - Represents age, co-morbidities, financial resources, risk tolerance.
    # Higher λ means higher cost sensitivity (e.g., frail, poor, high risk aversion).
    lambdas = np.linspace(0.1, 5.0, 50) # From resource abundance to high scarcity
    
    results = []
    
    for lambd in lambdas:
        best_v = -np.inf
        chosen_strategy = None
        
        for strat in strategies:
            # Total Cost = Side_Effects + Financial + Invasiveness + Recovery_Time
            total_cost = strat['side_effects'] + strat['financial_cost'] + strat['invasiveness'] + strat['recovery_time']
            
            # V = Gain(Health_Outcome) - λ * Total_Cost
            v = strat['health_gain'] - (lambd * total_cost)
            
            if v > best_v:
                best_v = v
                chosen_strategy = strat
        
        results.append({
            'lambda': lambd,
            'chosen_name': chosen_strategy['name'],
            'chosen_survival_rate_factor': chosen_strategy['survival_rate_factor'],
            'net_value': best_v
        })
            
    df = pd.DataFrame(results)
    
    # Save
    output_dir = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results"
    os.makedirs(output_dir, exist_ok=True)
    df.to_json(f"{output_dir}/cycle2740_data.json")
    
    # Visualize
    plt.figure(figsize=(10, 6))
    
    # Plot chosen survival rate factor against lambda
    plt.plot(df['lambda'], df['chosen_survival_rate_factor'], marker='o', linestyle='-', color='blue')
    plt.title('Treatment Choice Survival Rate vs Patient Context (λ)')
    plt.xlabel('Patient Context / Resource Scarcity (λ)')
    plt.ylabel('Chosen Strategy Survival Rate Factor')
    plt.ylim(0, 1.1)
    plt.grid(True)
    
    # Annotate transitions
    strategy_changes = df.drop_duplicates(subset=['chosen_name'])
    for idx, row in strategy_changes.iterrows():
        plt.axvline(x=row['lambda'], color='gray', linestyle=':', linewidth=0.8)
        plt.text(row['lambda'] + 0.05, row['chosen_survival_rate_factor'] + 0.1, row['chosen_name'], 
                 rotation=0, verticalalignment='bottom', horizontalalignment='left', fontsize=8, color='darkgreen')
    
    plt.tight_layout()
    plt.savefig("/Volumes/dual/DUALITY-ZERO-V2/data/figures/cycle2740_treatment_budget.png")
    
    # Analysis
    print("Cycle 2740 Analysis:")
    
    low_lambda_choice = df.iloc[0]['chosen_name']
    high_lambda_choice = df.iloc[-1]['chosen_name']
    
    print(f"Low λ Choice: {low_lambda_choice}")
    print(f"High λ Choice: {high_lambda_choice}")
    
    if low_lambda_choice == "Aggressive Treatment" and high_lambda_choice == "Palliative Care":
        print("HYPOTHESIS CONFIRMED: Treatment choice is a BCP process.")
        print("Medical decisions adapt to patient context, prioritizing efficiency over aggressive interventions under scarcity.")
    else:
        print("HYPOTHESIS FAILED or complex outcome.")

if __name__ == "__main__":
    run_experiment()
