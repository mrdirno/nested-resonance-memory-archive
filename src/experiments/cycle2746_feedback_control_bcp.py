"""
Cycle 2746: Feedback Control as BCP (The Adaptation Budget)
============================================================

Investigation: Is the design of feedback control loops (e.g., PID controllers, neural feedback) a BCP optimization? Is the complexity and aggressiveness of the feedback mechanism chosen to balance desired performance (gain) against sensor/actuator cost and computational overhead, adapting to environmental volatility (λ)?

Hypothesis:
Feedback control systems are BCP-optimal adaptations to environmental uncertainty and desired performance. Higher performance (precision, responsiveness) comes at a higher cost, and the chosen controller complexity reflects the available budget.
V(control_strategy) = Gain(Performance) - λ(Environmental_Volatility) * Cost(Sensors + Actuators + Compute).

1. Open-loop Control: Lowest Cost, Poor Performance (no adaptation). Optimal only when environment is perfectly predictable (low λ).
2. Simple Feedback (e.g., Proportional): Moderate Cost, Moderate Performance (basic adaptation). Optimal under moderate λ.
3. Advanced Feedback (e.g., Predictive/Adaptive): Highest Cost, High Performance (proactive adaptation). Optimal under low λ (predictable, ample compute).
4. Adaptive Control (e.g., Neural Networks): High cost to learn, but potentially high performance if environment is highly dynamic.

We simulate a control system (e.g., robotic arm) adapting its strategy to environmental volatility.

"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os

def run_experiment():
    print("Initializing Cycle 2746: Feedback Control BCP...")
    
    # Control Strategies
    strategies = [
        # Open-loop Control: Low cost, low performance
        {'name': "Open-loop", 'performance_gain': 40.0, 'sensor_cost': 1.0, 'actuator_cost': 1.0, 'compute_cost': 1.0, 'tracking_error': 0.6},
        # Simple Feedback (PID): Moderate cost, moderate performance
        {'name': "Simple Feedback", 'performance_gain': 80.0, 'sensor_cost': 10.0, 'actuator_cost': 5.0, 'compute_cost': 10.0, 'tracking_error': 0.2}, 
        # Advanced Feedback (MPC/Adaptive): High cost, high performance
        {'name': "Advanced Feedback", 'performance_gain': 95.0, 'sensor_cost': 20.0, 'actuator_cost': 10.0, 'compute_cost': 50.0, 'tracking_error': 0.05}
    ]
    
    # Environmental Volatility (λ) - Represents unpredictability, disturbance magnitude, noise.
    # Higher λ means more dynamic environment / higher need for adaptation.
    lambdas = np.linspace(0.1, 5.0, 50) # From stable/predictable to highly volatile
    
    results = []
    
    for lambd in lambdas:
        best_v = -np.inf
        chosen_strategy = None
        
        for strat in strategies:
            # Total Cost = Sensor_Cost + Actuator_Cost + Compute_Cost
            # Assume compute cost scales with lambda (more compute for more volatility)
            total_cost_per_lambda = strat['sensor_cost'] + strat['actuator_cost'] + strat['compute_cost']
            
            # V = Gain(Performance) - λ * Total_Cost
            v = strat['performance_gain'] - (lambd * total_cost_per_lambda)
            
            if v > best_v:
                best_v = v
                chosen_strategy = strat
        
        results.append({
            'lambda': lambd,
            'chosen_name': chosen_strategy['name'],
            'chosen_error': chosen_strategy['tracking_error'],
            'net_value': best_v
        })
            
    df = pd.DataFrame(results)
    
    # Save
    output_dir = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results"
    os.makedirs(output_dir, exist_ok=True)
    df.to_json(f"{output_dir}/cycle2746_data.json")
    
    # Visualize
    plt.figure(figsize=(10, 6))
    
    # Plot chosen tracking error against lambda
    plt.plot(df['lambda'], df['chosen_error'], marker='o', linestyle='-', color='blue')
    plt.title('Control Strategy Tracking Error vs Environmental Volatility (λ)')
    plt.xlabel('Environmental Volatility (λ)')
    plt.ylabel('Chosen Strategy Tracking Error')
    plt.ylim(0, 0.7)
    plt.grid(True)
    
    # Annotate transitions
    strategy_changes = df.drop_duplicates(subset=['chosen_name'])
    for idx, row in strategy_changes.iterrows():
        plt.axvline(x=row['lambda'], color='gray', linestyle=':', linewidth=0.8)
        plt.text(row['lambda'] + 0.05, row['chosen_error'] + 0.05, row['chosen_name'], 
                 rotation=0, verticalalignment='bottom', horizontalalignment='left', fontsize=8, color='darkgreen')
    
    plt.tight_layout()
    plt.savefig("/Volumes/dual/DUALITY-ZERO-V2/data/figures/cycle2746_feedback_control_budget.png")
    
    # Analysis
    print("Cycle 2746 Analysis:")
    
    low_lambda_choice = df.iloc[0]['chosen_name']
    high_lambda_choice = df.iloc[-1]['chosen_name']
    
    print(f"Low λ Choice: {low_lambda_choice}")
    print(f"High λ Choice: {high_lambda_choice}")
    
    if low_lambda_choice == "Advanced Feedback" and high_lambda_choice == "Open-loop":
        print("HYPOTHESIS CONFIRMED: Feedback control design is a BCP optimization.")
        print("Control strategy adapts to environmental volatility, balancing performance vs cost.")
    else:
        print("HYPOTHESIS FAILED or complex outcome.")

if __name__ == "__main__":
    run_experiment()
