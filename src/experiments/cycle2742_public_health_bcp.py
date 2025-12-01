"""
Cycle 2742: Public Health Policy as BCP (The Population Budget)
================================================================

Investigation: Do public health interventions (e.g., vaccination campaigns, lockdowns) represent BCP-optimal decisions, balancing population health gain against societal costs (economic disruption, individual liberties), given the prevailing societal "health budget" (λ)?

Hypothesis:
Public health policy is a complex BCP optimization problem. The "optimal" intervention strategy is not absolute but dynamically chosen based on epidemic severity, societal resources, public trust (representing λ), and the trade-off between population health and societal costs.
V(policy) = Gain(Population_Health) - λ(Societal_Context) * Cost(Economic_Disruption + Individual_Liberties + Social_Cohesion_Loss).

1. Minimal Intervention: Low Direct Cost, High Indirect Cost (mortality, morbidity). Optimal under very low λ (mild disease, high trust).
2. Moderate Intervention (e.g., Vaccination): Moderate Direct Cost, High Health Gain. Optimal under moderate λ.
3. Aggressive Intervention (e.g., Lockdowns): High Direct Cost, Potentially Very High Health Gain (if effective). Optimal under high λ (severe epidemic, desperate measures).
4. No Intervention: Very high cost from disease, very low direct cost.

We simulate a public health agency choosing an intervention strategy during an epidemic.

"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os

def run_experiment():
    print("Initializing Cycle 2742: Public Health Policy BCP...")
    
    # Public Health Interventions
    interventions = [
        # Minimal Intervention: Low direct cost, high disease cost
        {'name': "Minimal", 'population_health_gain': 40.0, 'economic_disruption': 10.0, 'liberty_cost': 5.0, 'disease_cost_factor': 50.0},
        # Vaccination Campaign: Moderate direct cost, high health gain
        {'name': "Vaccination", 'population_health_gain': 90.0, 'economic_disruption': 30.0, 'liberty_cost': 10.0, 'disease_cost_factor': 10.0}, 
        # Aggressive Intervention (Lockdowns): High direct cost, very high health gain potential
        {'name': "Lockdown", 'population_health_gain': 95.0, 'economic_disruption': 100.0, 'liberty_cost': 50.0, 'disease_cost_factor': 5.0}
    ]
    
    # Societal Context (λ) - Represents epidemic severity, public trust, economic resilience.
    # Higher λ means higher cost sensitivity (e.g., severe epidemic, low trust, fragile economy).
    lambdas = np.linspace(0.1, 5.0, 50) # From resilient society to fragile/severe epidemic
    
    results = []
    
    for lambd in lambdas:
        best_v = -np.inf
        chosen_policy = None
        
        for policy in interventions:
            # Total Cost = Economic_Disruption + Individual_Liberties + (Disease_Cost_Factor * λ_disease_severity)
            # The disease_cost_factor is already scaled by lambda in the hypothesis
            # Let's define the overall cost as direct costs + lambda * disease_cost_factor
            
            # Cost = Direct_Cost + λ * Disease_Cost_Factor
            # Direct_Cost = Economic_Disruption + Liberty_Cost
            
            direct_cost = policy['economic_disruption'] + policy['liberty_cost']
            disease_cost = policy['disease_cost_factor'] * 10.0 # Scale disease cost
            
            total_effective_cost = direct_cost + (lambd * disease_cost)
            
            # V = Gain(Population_Health) - Total_Effective_Cost
            v = policy['population_health_gain'] - total_effective_cost
            
            if v > best_v:
                best_v = v
                chosen_policy = policy
        
        results.append({
            'lambda': lambd,
            'chosen_name': chosen_policy['name'],
            'chosen_health_gain': chosen_policy['population_health_gain'],
            'net_value': best_v
        })
            
    df = pd.DataFrame(results)
    
    # Save
    output_dir = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results"
    os.makedirs(output_dir, exist_ok=True)
    df.to_json(f"{output_dir}/cycle2742_data.json")
    
    # Visualize
    plt.figure(figsize=(10, 6))
    
    # Plot chosen health gain against lambda
    plt.plot(df['lambda'], df['chosen_health_gain'], marker='o', linestyle='-', color='blue')
    plt.title('Public Health Policy Gain vs Societal Context (λ)')
    plt.xlabel('Societal Context / Epidemic Severity (λ)')
    plt.ylabel('Chosen Policy Population Health Gain')
    plt.ylim(0, 100)
    plt.grid(True)
    
    # Annotate transitions
    policy_changes = df.drop_duplicates(subset=['chosen_name'])
    for idx, row in policy_changes.iterrows():
        plt.axvline(x=row['lambda'], color='gray', linestyle=':', linewidth=0.8)
        plt.text(row['lambda'] + 0.05, row['chosen_health_gain'] + 5, row['chosen_name'], 
                 rotation=0, verticalalignment='bottom', horizontalalignment='left', fontsize=8, color='darkgreen')
    
    plt.tight_layout()
    plt.savefig("/Volumes/dual/DUALITY-ZERO-V2/data/figures/cycle2742_public_health_budget.png")
    
    # Analysis
    print("Cycle 2742 Analysis:")
    
    low_lambda_choice = df.iloc[0]['chosen_name']
    high_lambda_choice = df.iloc[-1]['chosen_name']
    
    print(f"Low λ Choice: {low_lambda_choice}")
    print(f"High λ Choice: {high_lambda_choice}")
    
    if low_lambda_choice == "Vaccination" and high_lambda_choice == "Lockdown":
        print("HYPOTHESIS CONFIRMED: Public health policy is a BCP optimization.")
        print("Intervention strategy adapts to societal context, balancing health gain vs societal costs.")
    else:
        print("HYPOTHESIS FAILED or complex outcome.")

if __name__ == "__main__":
    run_experiment()
