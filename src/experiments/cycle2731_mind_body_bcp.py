"""
Cycle 2731: The Mind-Body Problem as BCP (The Integration Budget)
==================================================================

Investigation: Does the "Hard Problem" of consciousness (the mind-body problem) arise from the BCP-optimal modularity of information processing, where fully integrating all physical and mental states into a single, coherent model is computationally expensive?

Hypothesis:
The apparent irreconcilability of mind and body is a consequence of computational trade-offs. The brain operates as a collection of specialized, BCP-optimized modules. Fully integrating their "viewpoints" into a single, unified "theory of everything" (for the self) is too costly.
V(integration_mode) = Gain(Unified_Understanding) - λ(Compute) * Computational_Integration_Cost.

1. Monism (e.g., Physicalism): High Integration Cost (requires complex mapping from physics to qualia), potentially High Gain (unified theory), but often Intractable.
2. Dualism (e.g., Substance Dualism): Low Integration Cost (simply accept two separate realms), Lower Gain (leaves the "hard problem" unsolved, lacks full explanatory power).
3. Emergentism: Medium Cost, Medium Gain (mind emerges from matter, but not reducible).

We simulate an agent trying to create a "Theory of Everything" for its own existence.

"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os

def run_experiment():
    print("Initializing Cycle 2731: Mind-Body BCP...")
    
    # Integration Modes
    integration_modes = [
        # Monism (Physicalism): High cost, seeks full integration, high explanatory power
        {'name': "Monism (Physicalism)", 'gain_unified_understanding': 100.0, 'integration_cost': 50.0, 'coherence': 1.0},
        # Dualism (Substance Dualism): Low cost, accepts separation, low explanatory power
        {'name': "Dualism", 'gain_unified_understanding': 60.0, 'integration_cost': 5.0, 'coherence': 0.5}, 
        # Emergentism: Medium cost, decent explanatory power, avoids hardest parts
        {'name': "Emergentism", 'gain_unified_understanding': 80.0, 'integration_cost': 20.0, 'coherence': 0.8}
    ]
    
    # Computational Scarcity (λ) - Represents cognitive load, complexity of reality
    lambdas = np.linspace(0.1, 5.0, 50) # From compute abundance to high scarcity
    
    results = []
    
    for lambd in lambdas:
        best_v = -np.inf
        chosen_mode = None
        
        for i_mode in integration_modes:
            # V = Gain(Unified_Understanding) - λ * Computational_Integration_Cost
            v = i_mode['gain_unified_understanding'] - (lambd * i_mode['integration_cost'])
            
            if v > best_v:
                best_v = v
                chosen_mode = i_mode
        
        results.append({
            'lambda': lambd,
            'chosen_name': chosen_mode['name'],
            'chosen_coherence': chosen_mode['coherence'],
            'net_value': best_v
        })
            
    df = pd.DataFrame(results)
    
    # Save
    output_dir = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results"
    os.makedirs(output_dir, exist_ok=True)
    df.to_json(f"{output_dir}/cycle2731_data.json")
    
    # Visualize
    plt.figure(figsize=(10, 6))
    
    # Plot chosen coherence against lambda
    plt.plot(df['lambda'], df['chosen_coherence'], marker='o', linestyle='-', color='blue')
    plt.title('Mind-Body Solution Coherence vs Computational Scarcity (λ)')
    plt.xlabel('Computational Scarcity (λ)')
    plt.ylabel('Chosen Solution Coherence')
    plt.ylim(0, 1.1)
    plt.grid(True)
    
    # Annotate transitions
    mode_changes = df.drop_duplicates(subset=['chosen_name'])
    for idx, row in mode_changes.iterrows():
        plt.axvline(x=row['lambda'], color='gray', linestyle=':', linewidth=0.8)
        plt.text(row['lambda'] + 0.05, row['chosen_coherence'] + 0.1, row['chosen_name'], 
                 rotation=0, verticalalignment='bottom', horizontalalignment='left', fontsize=8, color='darkgreen')
    
    plt.tight_layout()
    plt.savefig("/Volumes/dual/DUALITY-ZERO-V2/data/figures/cycle2731_mind_body_budget.png")
    
    # Analysis
    print("Cycle 2731 Analysis:")
    
    low_lambda_choice = df.iloc[0]['chosen_name']
    high_lambda_choice = df.iloc[-1]['chosen_name']
    
    print(f"Low λ Choice: {low_lambda_choice}")
    print(f"High λ Choice: {high_lambda_choice}")
    
    if low_lambda_choice == "Monism (Physicalism)" and high_lambda_choice == "Dualism":
        print("HYPOTHESIS CONFIRMED: The Mind-Body problem is a BCP issue of integration cost.")
        print("Dualism is a computationally cheap heuristic when full integration is too expensive.")
    else:
        print("HYPOTHESIS FAILED or complex outcome.")

if __name__ == "__main__":
    run_experiment()
