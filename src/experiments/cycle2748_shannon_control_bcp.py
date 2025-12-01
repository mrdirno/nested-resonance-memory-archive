"""
Cycle 2748: Information Theory in Control as BCP (The Shannon Budget)
======================================================================

Investigation: Is the amount of information needed for control a BCP-constrained resource? Do control strategies trade off the fidelity of information (bandwidth) against its cost of acquisition and processing, adhering to an "Information Budget"?

Hypothesis:
All control systems operate under an "Information Budget." The quality and quantity of information acquired and processed are optimized to achieve desired control performance (Gain) against the cost of information (Cost), modulated by channel noise and system complexity (λ).
V(control_info) = Gain(Control_Performance) - λ(Channel_Noise/Complexity) * Cost(Sensor_Bandwidth + Communication_Overhead + Processing_Time).

1. High Bandwidth Control: High Information Cost, High Precision/Stability. Optimal under low λ (clean channels, simple systems).
2. Low Bandwidth Control: Low Information Cost, Lower Precision/Stability. Optimal under high λ (noisy channels, complex systems).
3. Minimum Information Control: There's a fundamental lower bound of information needed for control (related to Shannon's Channel Capacity Theorem and the Water-Filling algorithm).

We simulate a control system choosing an information acquisition strategy for a noisy plant.

"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os

def run_experiment():
    print("Initializing Cycle 2748: Shannon Control BCP...")
    
    # Information Acquisition Strategies
    strategies = [
        # High Bandwidth Control: High cost, high performance
        {'name': "High Bandwidth", 'control_performance': 95.0, 'sensor_bandwidth_cost': 20.0, 'comm_overhead_cost': 10.0, 'processing_cost': 15.0, 'control_precision': 0.05},
        # Low Bandwidth Control: Low cost, lower performance
        {'name': "Low Bandwidth", 'control_performance': 70.0, 'sensor_bandwidth_cost': 5.0, 'comm_overhead_cost': 2.0, 'processing_cost': 3.0, 'control_precision': 0.2}, 
        # Adaptive Bandwidth Control (ideal BCP): Medium costs, adapts to environment
        {'name': "Adaptive Bandwidth", 'control_performance': 85.0, 'sensor_bandwidth_cost': 12.0, 'comm_overhead_cost': 6.0, 'processing_cost': 8.0, 'control_precision': 0.1}
    ]
    
    # Channel Noise/Complexity (λ) - Represents information loss, system uncertainty.
    # Higher λ means more challenging information environment.
    lambdas = np.linspace(0.1, 5.0, 50) # From clean/simple to noisy/complex
    
    results = []
    
    for lambd in lambdas:
        best_v = -np.inf
        chosen_strategy = None
        
        for strat in strategies:
            # Total Cost = Sensor_Bandwidth_Cost + Communication_Overhead_Cost + Processing_Cost
            # Assume costs are directly multiplied by lambda to reflect difficulty of operating in noisy/complex env
            total_cost = (strat['sensor_bandwidth_cost'] + strat['comm_overhead_cost'] + strat['processing_cost']) * lambd
            
            # V = Gain(Control_Performance) - Total_Cost
            v = strat['control_performance'] - total_cost
            
            if v > best_v:
                best_v = v
                chosen_strategy = strat
        
        results.append({
            'lambda': lambd,
            'chosen_name': chosen_strategy['name'],
            'chosen_precision': chosen_strategy['control_precision'],
            'net_value': best_v
        })
            
    df = pd.DataFrame(results)
    
    # Save
    output_dir = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results"
    os.makedirs(output_dir, exist_ok=True)
    df.to_json(f"{output_dir}/cycle2748_data.json")
    
    # Visualize
    plt.figure(figsize=(10, 6))
    
    # Plot chosen precision against lambda
    plt.plot(df['lambda'], df['chosen_precision'], marker='o', linestyle='-', color='blue')
    plt.title('Control Strategy Precision vs Information Environment (λ)')
    plt.xlabel('Channel Noise / System Complexity (λ)')
    plt.ylabel('Chosen Strategy Precision')
    plt.ylim(0, 0.3)
    plt.grid(True)
    
    # Annotate transitions
    strategy_changes = df.drop_duplicates(subset=['chosen_name'])
    for idx, row in strategy_changes.iterrows():
        plt.axvline(x=row['lambda'], color='gray', linestyle=':', linewidth=0.8)
        plt.text(row['lambda'] + 0.05, row['chosen_precision'] + 0.02, row['chosen_name'], 
                 rotation=0, verticalalignment='bottom', horizontalalignment='left', fontsize=8, color='darkgreen')
    
    plt.tight_layout()
    plt.savefig("/Volumes/dual/DUALITY-ZERO-V2/data/figures/cycle2748_shannon_control_budget.png")
    
    # Analysis
    print("Cycle 2748 Analysis:")
    
    low_lambda_choice = df.iloc[0]['chosen_name']
    high_lambda_choice = df.iloc[-1]['chosen_name']
    
    print(f"Low λ Choice: {low_lambda_choice}")
    print(f"High λ Choice: {high_lambda_choice}")
    
    if low_lambda_choice == "High Bandwidth" and high_lambda_choice == "Low Bandwidth":
        print("HYPOTHESIS CONFIRMED: Information theory in control is a BCP optimization.")
        print("Control strategies adapt to the information environment, trading precision for cost efficiency.")
    else:
        print("HYPOTHESIS FAILED or complex outcome.")

if __name__ == "__main__":
    run_experiment()
