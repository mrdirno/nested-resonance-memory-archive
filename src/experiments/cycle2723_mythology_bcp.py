"""
Cycle 2723: Mythology as BCP (The Legend Budget)
=================================================

Investigation: Do Myths persist and spread due to their BCP-optimal design?

Hypothesis:
Myths are highly compressed cultural algorithms for survival. They provide high "Survival Utility" (Gain) at low "Cognitive Cost" (easy to understand, remember, transmit).
V(myth) = Survival_Utility - λ(Cognitive) * Cognitive_Cost.

1. High Utility: Explaining natural phenomena, teaching moral lessons, fostering group cohesion, cultural identity.
2. Low Cognitive Cost: Simple narratives, memorable characters, emotional resonance, lack of internal contradictions (from a narrative, not logical, perspective).
3. Under high λ (scarcity, stress), myths with the highest V will be selected and persist, even if less "truthful" in a scientific sense.

We simulate the competition of cultural information.
- Competing pieces of cultural knowledge.
- Some are scientific explanations (High Utility, High Cognitive Cost, High Truth).
- Others are myths (High Utility, Low Cognitive Cost, Low Truth).
- Others are complex philosophical treatises (Low Utility, Very High Cognitive Cost, Medium Truth).

"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os

def run_experiment():
    print("Initializing Cycle 2723: Mythology BCP...")
    
    # Cultural Information Units (Hypothetical, simplified)
    knowledge_units = [
        # Scientific Explanation: High utility, High cognitive cost
        {'name': "Scientific Theory (e.g., Evolution)", 'survival_utility': 100.0, 'cognitive_cost': 50.0, 'truthfulness': 1.0},
        # Myth: High utility, Low cognitive cost
        {'name': "Creation Myth (e.g., Genesis)", 'survival_utility': 80.0, 'cognitive_cost': 10.0, 'truthfulness': 0.2},
        # Philosophical Treatise: Low utility (for general populace), Very high cognitive cost
        {'name': "Philosophical Treatise (e.g., Kant)", 'survival_utility': 30.0, 'cognitive_cost': 100.0, 'truthfulness': 0.8},
        # Historical Fact: Medium utility, Medium cognitive cost
        {'name': "Historical Fact (e.g., Battle Date)", 'survival_utility': 60.0, 'cognitive_cost': 25.0, 'truthfulness': 1.0}
    ]
    
    # Societal Scarcity (λ)
    lambdas = np.linspace(0.1, 5.0, 50) # From abundance to high scarcity
    
    results = []
    
    for lambd in lambdas:
        best_v = -np.inf
        chosen_knowledge = None
        
        for k_unit in knowledge_units:
            # V = Survival_Utility - λ * Cognitive_Cost
            v = k_unit['survival_utility'] - (lambd * k_unit['cognitive_cost'])
            
            if v > best_v:
                best_v = v
                chosen_knowledge = k_unit
        
        results.append({
            'lambda': lambd,
            'chosen_name': chosen_knowledge['name'],
            'chosen_truthfulness': chosen_knowledge['truthfulness'],
            'net_value': best_v
        })
            
    df = pd.DataFrame(results)
    
    # Save
    output_dir = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results"
    os.makedirs(output_dir, exist_ok=True)
    df.to_json(f"{output_dir}/cycle2723_data.json")
    
    # Visualize
    plt.figure(figsize=(10, 6))
    
    # Plot chosen truthfulness against lambda
    plt.plot(df['lambda'], df['chosen_truthfulness'], marker='o', linestyle='-', color='blue')
    plt.title('Truthfulness of Cultural Knowledge vs Societal Scarcity (λ)')
    plt.xlabel('Societal Scarcity (λ)')
    plt.ylabel('Chosen Knowledge Truthfulness')
    plt.ylim(0, 1.1)
    plt.grid(True)
    
    # Annotate transitions
    knowledge_changes = df.drop_duplicates(subset=['chosen_name'])
    for idx, row in knowledge_changes.iterrows():
        plt.axvline(x=row['lambda'], color='gray', linestyle=':', linewidth=0.8)
        plt.text(row['lambda'] + 0.05, row['chosen_truthfulness'] + 0.1, row['chosen_name'], 
                 rotation=0, verticalalignment='bottom', horizontalalignment='left', fontsize=8, color='darkgreen')
    
    plt.tight_layout()
    plt.savefig("/Volumes/dual/DUALITY-ZERO-V2/data/figures/cycle2723_mythology_budget.png")
    
    # Analysis
    print("Cycle 2723 Analysis:")
    
    low_lambda_choice = df.iloc[0]['chosen_name']
    high_lambda_choice = df.iloc[-1]['chosen_name']
    
    print(f"Low λ Choice: {low_lambda_choice}")
    print(f"High λ Choice: {high_lambda_choice}")
    
    if low_lambda_choice == "Scientific Theory (e.g., Evolution)" and high_lambda_choice == "Creation Myth (e.g., Genesis)":
        print("HYPOTHESIS CONFIRMED: Myths are BCP-optimal for cultural transmission under scarcity.")
        print("They prioritize survival utility and low cognitive cost over complex truth.")
    else:
        print("HYPOTHESIS FAILED or complex outcome.")

if __name__ == "__main__":
    run_experiment()
