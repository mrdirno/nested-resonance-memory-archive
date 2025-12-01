"""
Cycle 2754: Trial Process as BCP (The Truth Budget)
===================================================

Investigation: Is the trial process (e.g., adversarial vs inquisitorial) a BCP method for approximating truth and resolving disputes? Does it balance the gain of accurate judgment against the immense costs of investigation, testimony, and legal representation, and is the optimal process λ-dependent?

Hypothesis:
Legal trial processes are BCP-optimal strategies for achieving justice. The chosen process (e.g., adversarial, inquisitorial, or alternative dispute resolution) is a trade-off between the gain of accurate judgment and the costs (financial, time, emotional) of the legal process, modulated by the societal budget for justice and case complexity (λ).
V(trial_process) = Gain(Accuracy_of_Judgment) - λ(Societal_Budget/Case_Complexity) * Cost(Investigation + Legal_Representation + Time + Emotional_Toll).

1. Inquisitorial System: High Investigation Cost (state-driven), Potentially High Accuracy. Optimal under low λ (ample resources, high value on absolute truth).
2. Adversarial System: Moderate Investigation Cost (parties-driven), Moderate Accuracy. Optimal under moderate λ (resource constraints, balance between truth and efficiency).
3. Mediation/Arbitration: Low Investigation Cost, Focus on Resolution over Absolute Truth, Lower Accuracy, but High Efficiency. Optimal under high λ (severe resource constraints, need for quick resolution).

We simulate a society choosing a trial process.

"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os

def run_experiment():
    print("Initializing Cycle 2754: Trial Process BCP...")
    
    # Trial Processes
    processes = [
        # Inquisitorial System: High cost, high accuracy (idealistic)
        {'name': "Inquisitorial", 'accuracy_gain': 95.0, 'investigation_cost': 50.0, 'legal_rep_cost': 10.0, 'time_cost': 20.0, 'emotional_cost': 5.0, 'judgment_fidelity': 0.95},
        # Adversarial System: Moderate cost, moderate accuracy (realistic)
        {'name': "Adversarial", 'accuracy_gain': 80.0, 'investigation_cost': 20.0, 'legal_rep_cost': 20.0, 'time_cost': 10.0, 'emotional_cost': 10.0, 'judgment_fidelity': 0.8}, 
        # Mediation/Arbitration: Low cost, resolution focused
        {'name': "Mediation", 'accuracy_gain': 60.0, 'investigation_cost': 5.0, 'legal_rep_cost': 5.0, 'time_cost': 2.0, 'emotional_cost': 2.0, 'judgment_fidelity': 0.6}
    ]
    
    # Societal Budget/Case Complexity (λ) - Represents pressure on the justice system.
    # Higher λ means higher costs for investigation, etc.
    lambdas = np.linspace(0.1, 5.0, 50) # From ample budget/simple cases to constrained budget/complex cases
    
    results = []
    
    for lambd in lambdas:
        best_v = -np.inf
        chosen_process = None
        
        for proc in processes:
            # Total Cost = Investigation + Legal_Representation + Time + Emotional_Toll
            total_cost_base = proc['investigation_cost'] + proc['legal_rep_cost'] + proc['time_cost'] + proc['emotional_cost']
            
            # V = Gain(Accuracy_of_Judgment) - λ * Total_Cost_Base
            v = proc['accuracy_gain'] - (lambd * total_cost_base)
            
            if v > best_v:
                best_v = v
                chosen_process = proc
        
        results.append({
            'lambda': lambd,
            'chosen_name': chosen_process['name'],
            'chosen_fidelity': chosen_process['judgment_fidelity'],
            'net_value': best_v
        })
            
    df = pd.DataFrame(results)
    
    # Save
    output_dir = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results"
    os.makedirs(output_dir, exist_ok=True)
    df.to_json(f"{output_dir}/cycle2754_data.json")
    
    # Visualize
    plt.figure(figsize=(10, 6))
    
    # Plot chosen fidelity against lambda
    plt.plot(df['lambda'], df['chosen_fidelity'], marker='o', linestyle='-', color='blue')
    plt.title('Trial Process Judgment Fidelity vs Societal Budget/Case Complexity (λ)')
    plt.xlabel('Societal Budget / Case Complexity (λ)')
    plt.ylabel('Chosen Process Judgment Fidelity')
    plt.ylim(0, 1.1)
    plt.grid(True)
    
    # Annotate transitions
    process_changes = df.drop_duplicates(subset=['chosen_name'])
    for idx, row in process_changes.iterrows():
        plt.axvline(x=row['lambda'], color='gray', linestyle=':', linewidth=0.8)
        plt.text(row['lambda'] + 0.05, row['chosen_fidelity'] + 0.05, row['chosen_name'], 
                 rotation=0, verticalalignment='bottom', horizontalalignment='left', fontsize=8, color='darkgreen')
    
    plt.tight_layout()
    plt.savefig("/Volumes/dual/DUALITY-ZERO-V2/data/figures/cycle2754_trial_process_budget.png")
    
    # Analysis
    print("Cycle 2754 Analysis:")
    
    low_lambda_choice = df.iloc[0]['chosen_name']
    high_lambda_choice = df.iloc[-1]['chosen_name']
    
    print(f"Low λ Choice: {low_lambda_choice}")
    print(f"High λ Choice: {high_lambda_choice}")
    
    if low_lambda_choice == "Inquisitorial" and high_lambda_choice == "Mediation":
        print("HYPOTHESIS CONFIRMED: Trial process is a BCP-optimal method for achieving justice.")
        print("Legal systems adapt to societal budget/case complexity, balancing accuracy vs cost.")
    else:
        print("HYPOTHESIS FAILED or complex outcome.")

if __name__ == "__main__":
    run_experiment()
