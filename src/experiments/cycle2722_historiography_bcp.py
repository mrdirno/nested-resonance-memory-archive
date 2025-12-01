"""
Cycle 2722: Historiography as BCP (The Memory Budget)
======================================================

Investigation: Is "History" (the recorded narrative) a product of budget-constrained perception?

Hypothesis:
Historical narratives are selected and propagated based on their V(narrative) = Gain - λ * Cost.
- Gain: Social cohesion, legitimizing power, inspiring action, providing simple explanations.
- Cost: Cognitive load (complexity), contradicting established beliefs, requiring resources to teach/maintain, challenging power.

1. "History is written by the victors": Victorious narratives have high Gain (legitimacy) and low Cost (supported by resources).
2. "History is what we can afford to remember": Complex or nuanced histories are expensive to maintain and transmit, especially under high λ. Simple, memorable narratives are preferred.
3. Collective Amnesia: When Cost > Gain, certain historical events/perspectives are rationally forgotten.

We simulate a society's "memory budget".
- Competing narratives about a past event.
- Narratives have varying Gain, Cost, and Truthfulness.
- Society (via λ) chooses which narratives to remember and transmit.

"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os

def run_experiment():
    print("Initializing Cycle 2722: Historiography BCP...")
    
    # Parameters
    generations = 50
    
    # Narratives (Hypothetical, simplified)
    narratives = [
        # The Nuanced Academic: Highest Truth, but Very High Cost
        {'name': "Nuanced Truth", 'gain': 150.0, 'cognitive_cost': 60.0, 'truthfulness': 1.0},
        # The Victor's Narrative: High Gain (legitimizes power), Medium Cost (supported by resources)
        {'name': "Victor's Glory", 'gain': 100.0, 'cognitive_cost': 10.0, 'truthfulness': 0.7},
        # The Loser's Lament: Low Gain (challenges power), High Cost (suppressed, complex)
        {'name': "Loser's Suffering", 'gain': 20.0, 'cognitive_cost': 30.0, 'truthfulness': 0.9},
        # The Propaganda: High Gain (simple, powerful), Low Cost (easy to disseminate), Low Truth
        {'name': "Propaganda Lie", 'gain': 120.0, 'cognitive_cost': 8.0, 'truthfulness': 0.3}
    ]
    
    # Societal Scarcity (λ)
    lambdas = np.linspace(0.1, 5.0, 50) # From abundance to high scarcity
    
    results = []
    
    for lambd in lambdas:
        best_v = -np.inf
        chosen_narrative = None
        
        for n in narratives:
            # V = Gain - λ * Cost
            # Total Cost = Cognitive Cost (for society to process/maintain)
            v = n['gain'] - (lambd * n['cognitive_cost'])
            
            if v > best_v:
                best_v = v
                chosen_narrative = n
        
        results.append({
            'lambda': lambd,
            'chosen_name': chosen_narrative['name'],
            'chosen_truthfulness': chosen_narrative['truthfulness'],
            'net_value': best_v
        })
            
    df = pd.DataFrame(results)
    
    # Save
    output_dir = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results"
    os.makedirs(output_dir, exist_ok=True)
    df.to_json(f"{output_dir}/cycle2722_data.json")
    
    # Visualize
    plt.figure(figsize=(10, 6))
    
    # Plot chosen truthfulness against lambda
    plt.plot(df['lambda'], df['chosen_truthfulness'], marker='o', linestyle='-', color='blue')
    plt.title('Truthfulness of History vs Societal Scarcity (λ)')
    plt.xlabel('Societal Scarcity (λ)')
    plt.ylabel('Chosen Narrative Truthfulness')
    plt.ylim(0, 1.1)
    plt.grid(True)
    
    # Annotate transitions
    narrative_changes = df.drop_duplicates(subset=['chosen_name'])
    for idx, row in narrative_changes.iterrows():
        plt.axvline(x=row['lambda'], color='gray', linestyle=':', linewidth=0.8)
        plt.text(row['lambda'] + 0.05, row['chosen_truthfulness'] + 0.1, row['chosen_name'], 
                 rotation=0, verticalalignment='bottom', horizontalalignment='left', fontsize=8, color='darkgreen')
    
    plt.tight_layout()
    plt.savefig("/Volumes/dual/DUALITY-ZERO-V2/data/figures/cycle2722_historiography_budget.png")
    
    # Analysis
    print("Cycle 2722 Analysis:")
    
    avg_truthfulness = df['chosen_truthfulness'].mean()
    print(f"Average Truthfulness across λ: {avg_truthfulness:.2f}")
    
    low_lambda_truth = df.iloc[0]['chosen_truthfulness']
    high_lambda_truth = df.iloc[-1]['chosen_truthfulness']
    
    print(f"Truthfulness at Low λ: {low_lambda_truth:.2f}")
    print(f"Truthfulness at High λ: {high_lambda_truth:.2f}")
    
    if low_lambda_truth > high_lambda_truth and 'Propaganda Lie' in df['chosen_name'].unique():
        print("HYPOTHESIS CONFIRMED: History is a BCP construction.")
        print("Under scarcity, truth is sacrificed for narratives with high gain/cost ratio (e.g., propaganda).")
        print("Narratives are chosen for their utility, not necessarily their veracity.")
    else:
        print("HYPOTHESIS FAILED or complex outcome.")

if __name__ == "__main__":
    run_experiment()
