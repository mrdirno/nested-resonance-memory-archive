"""
Cycle 2739: Diagnosis as BCP (The Diagnostic Budget)
=====================================================

Investigation: Is medical diagnosis a BCP process, where doctors balance diagnostic accuracy (gain) against the cost of tests (financial, time, risk of false positives/negatives), modulated by the patient's condition and resources (λ)?

Hypothesis:
Medical diagnosis operates under a budget constraint. Optimal diagnostic strategy changes based on the patient's situation (representing λ) and the available resources.
V(diagnostic_action) = Gain(Diagnostic_Accuracy) - λ(Patient_Context) * Cost(Test_Financial + Test_Time + Risk_False_Positive).

1. Minimal Testing (Heuristic): Low Cost, Sufficient Accuracy, Fast. Optimal under high λ (urgent care, limited resources).
2. Comprehensive Testing (Optimal): High Cost, Higher Accuracy, Slower. Optimal under low λ (non-urgent, ample resources).
3. Over-testing: Occurs when λ is artificially low (e.g., defensive medicine).
4. Under-testing: Occurs when λ is artificially high (e.g., resource-poor settings).

We simulate a doctor choosing a diagnostic strategy.

"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os

def run_experiment():
    print("Initializing Cycle 2739: Diagnosis BCP...")
    
    # Diagnostic Strategies
    strategies = [
        # Minimal Testing (Heuristic): Low cost, sufficient accuracy
        {'name': "Minimal Testing", 'diagnostic_accuracy': 70.0, 'test_cost_financial': 10.0, 'test_cost_time': 2.0, 'risk_false_positive': 5.0, 'patient_satisfaction': 0.6},
        # Comprehensive Testing (Optimal): High cost, higher accuracy
        {'name': "Comprehensive Testing", 'diagnostic_accuracy': 95.0, 'test_cost_financial': 100.0, 'test_cost_time': 10.0, 'risk_false_positive': 15.0, 'patient_satisfaction': 0.9} 
    ]
    
    # Patient Context (λ) - Represents urgency, financial constraints, resource scarcity
    # Higher λ means higher cost sensitivity (e.g., patient can't afford, emergency room)
    lambdas = np.linspace(0.1, 5.0, 50) # From resource abundance to high scarcity
    
    results = []
    
    for lambd in lambdas:
        best_v = -np.inf
        chosen_strategy = None
        
        for strat in strategies:
            # Total Cost = Financial + Time + Risk
            total_cost = strat['test_cost_financial'] + strat['test_cost_time'] + strat['risk_false_positive']
            
            # V = Gain(Diagnostic_Accuracy) - λ * Total_Cost
            v = strat['diagnostic_accuracy'] - (lambd * total_cost)
            
            if v > best_v:
                best_v = v
                chosen_strategy = strat
        
        results.append({
            'lambda': lambd,
            'chosen_name': chosen_strategy['name'],
            'chosen_accuracy': chosen_strategy['diagnostic_accuracy'],
            'net_value': best_v
        })
            
    df = pd.DataFrame(results)
    
    # Save
    output_dir = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results"
    os.makedirs(output_dir, exist_ok=True)
    df.to_json(f"{output_dir}/cycle2739_data.json")
    
    # Visualize
    plt.figure(figsize=(10, 6))
    
    # Plot chosen accuracy against lambda
    plt.plot(df['lambda'], df['chosen_accuracy'], marker='o', linestyle='-', color='blue')
    plt.title('Diagnostic Strategy Accuracy vs Patient Context (λ)')
    plt.xlabel('Patient Context / Resource Scarcity (λ)')
    plt.ylabel('Chosen Strategy Accuracy')
    plt.ylim(0, 100)
    plt.grid(True)
    
    # Annotate transitions
    strategy_changes = df.drop_duplicates(subset=['chosen_name'])
    for idx, row in strategy_changes.iterrows():
        plt.axvline(x=row['lambda'], color='gray', linestyle=':', linewidth=0.8)
        plt.text(row['lambda'] + 0.05, row['chosen_accuracy'] + 5, row['chosen_name'], 
                 rotation=0, verticalalignment='bottom', horizontalalignment='left', fontsize=8, color='darkgreen')
    
    plt.tight_layout()
    plt.savefig("/Volumes/dual/DUALITY-ZERO-V2/data/figures/cycle2739_diagnosis_budget.png")
    
    # Analysis
    print("Cycle 2739 Analysis:")
    
    low_lambda_choice = df.iloc[0]['chosen_name']
    high_lambda_choice = df.iloc[-1]['chosen_name']
    
    print(f"Low λ Choice: {low_lambda_choice}")
    print(f"High λ Choice: {high_lambda_choice}")
    
    if low_lambda_choice == "Comprehensive Testing" and high_lambda_choice == "Minimal Testing":
        print("HYPOTHESIS CONFIRMED: Medical diagnosis is a BCP process.")
        print("Diagnostic strategy adapts to patient context, prioritizing efficiency over perfect accuracy under scarcity.")
    else:
        print("HYPOTHESIS FAILED or complex outcome.")

if __name__ == "__main__":
    run_experiment()
