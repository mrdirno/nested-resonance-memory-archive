"""
Cycle 2730: Qualia as BCP (The Subjective Budget)
=================================================

Investigation: Are Qualia (subjective conscious experiences like "the redness of red" or "the feeling of pain") BCP-optimal data compression and prioritization mechanisms for complex sensory information, guiding action without explicit, expensive processing?

Hypothesis:
In a high-bandwidth, complex sensory environment, processing all raw data for decision-making is computationally intractable. Qualia serve as efficient, low-cost signals that integrate vast amounts of information into immediately actionable "feels."
V(sensory_processing) = Gain(Adaptive_Response) - λ(Cognitive) * Computational_Cost.

1. Raw Data Processing: High Computational Cost (analyze every pixel, every frequency), High Fidelity, but Slow and Intractable for real-time decisions.
2. Qualia-based Processing: Low Computational Cost (simple "feel"), Sufficient Gain (fast adaptive response), Lower Fidelity (lossy compression).
3. Under high λ (immediate threat, information overload), Qualia-based processing should be BCP-rational.
4. Under low λ (relaxed state, focused analysis), Raw Data Processing might be affordable for specific tasks.

We simulate an agent choosing a sensory processing mode to react to a dynamic environment.

"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os

def run_experiment():
    print("Initializing Cycle 2730: Qualia BCP...")
    
    # Sensory Processing Modes
    processing_modes = [
        # Raw Data Processing: High cost, high fidelity, for ultimate analysis
        {'name': "Raw Data Processing", 'gain_adaptive_response': 100.0, 'computational_cost': 50.0, 'speed': 0.1},
        # Qualia-based Processing: Low cost, sufficient adaptive response, high speed
        {'name': "Qualia-based Processing", 'gain_adaptive_response': 70.0, 'computational_cost': 5.0, 'speed': 1.0} 
    ]
    
    # Cognitive Scarcity (λ) - Represents threat level, information overload, cognitive load
    lambdas = np.linspace(0.1, 5.0, 50) # From cognitive abundance to high scarcity
    
    results = []
    
    for lambd in lambdas:
        best_v = -np.inf
        chosen_mode = None
        
        for p_mode in processing_modes:
            # V = Gain(Adaptive_Response) - λ * Computational_Cost
            v = p_mode['gain_adaptive_response'] - (lambd * p_mode['computational_cost'])
            
            if v > best_v:
                best_v = v
                chosen_mode = p_mode
        
        results.append({
            'lambda': lambd,
            'chosen_name': chosen_mode['name'],
            'chosen_speed': chosen_mode['speed'],
            'net_value': best_v
        })
            
    df = pd.DataFrame(results)
    
    # Save
    output_dir = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results"
    os.makedirs(output_dir, exist_ok=True)
    df.to_json(f"{output_dir}/cycle2730_data.json")
    
    # Visualize
    plt.figure(figsize=(10, 6))
    
    # Plot chosen speed against lambda
    plt.plot(df['lambda'], df['chosen_speed'], marker='o', linestyle='-', color='blue')
    plt.title('Sensory Processing Mode Speed vs Cognitive Scarcity (λ)')
    plt.xlabel('Cognitive Scarcity (λ)')
    plt.ylabel('Chosen Mode Speed')
    plt.ylim(0, 1.1)
    plt.grid(True)
    
    # Annotate transitions
    mode_changes = df.drop_duplicates(subset=['chosen_name'])
    for idx, row in mode_changes.iterrows():
        plt.axvline(x=row['lambda'], color='gray', linestyle=':', linewidth=0.8)
        plt.text(row['lambda'] + 0.05, row['chosen_speed'] + 0.1, row['chosen_name'], 
                 rotation=0, verticalalignment='bottom', horizontalalignment='left', fontsize=8, color='darkgreen')
    
    plt.tight_layout()
    plt.savefig("/Volumes/dual/DUALITY-ZERO-V2/data/figures/cycle2730_qualia_budget.png")
    
    # Analysis
    print("Cycle 2730 Analysis:")
    
    low_lambda_choice = df.iloc[0]['chosen_name']
    high_lambda_choice = df.iloc[-1]['chosen_name']
    
    print(f"Low λ Choice: {low_lambda_choice}")
    print(f"High λ Choice: {high_lambda_choice}")
    
    if low_lambda_choice == "Raw Data Processing" and high_lambda_choice == "Qualia-based Processing":
        print("HYPOTHESIS CONFIRMED: Qualia are BCP-optimal data compression for adaptive response.")
        print("Subjective experience is an efficiency hack for the brain.")
    else:
        print("HYPOTHESIS FAILED or complex outcome.")

if __name__ == "__main__":
    run_experiment()
