"""
Cycle 2681: The Creative Temperature
====================================

Investigation: Is "Temperature" in Generative Models a proxy for Budget (λ)?

Hypothesis:
1. Low Temperature (T -> 0) = High λ (Scarcity).
   - The system cannot afford risk. It picks the most probable token (Max Likelihood).
   - Result: Repetitive, safe, boring.
2. High Temperature (T -> 1) = Low λ (Abundance).
   - The system can afford to be wrong. It explores the tail of the distribution.
   - Result: Creative, diverse, potentially incoherent.

Equation:
V(token) = Probability(token) - λ * Risk(token)
Where Risk = -log(Probability) (Surprisal/Entropy cost)

If λ is high, we penalize Surprisal heavily -> Pick high Probability.
If λ is low, we tolerate Surprisal -> Pick lower Probability (Creativity).

Let's simulate token selection under BCP and compare to Softmax Temperature.

"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
from scipy.special import softmax

def run_experiment():
    print("Initializing Cycle 2681: Creative Temperature BCP...")
    
    # Token Distribution (Zipfian)
    n_tokens = 100
    ranks = np.arange(1, n_tokens + 1)
    probs = 1 / ranks
    probs = probs / probs.sum() # Normalize
    
    # Surprisal (Risk)
    risk = -np.log(probs)
    
    # BCP Selection
    # V = Prob - λ * Risk
    # Or V = log(Prob) - λ * Risk ?
    # Standard Softmax: exp(logits / T). Logits are log(prob).
    # So P_new ~ exp(log(P) / T) = P^(1/T).
    
    # Let's test if BCP selection matches Temperature Scaling
    
    lambdas = [0.1, 0.5, 1.0, 2.0, 5.0]
    temperatures = [10.0, 2.0, 1.0, 0.5, 0.2] # Inverse relation expected
    
    results = []
    
    # BCP Approach
    for lambd in lambdas:
        # Calculate Value for each token
        # We assume Gain = Probability (Likelihood of being correct next token)
        # Cost = Risk (Surprisal)
        
        # Wait, if Gain = Prob, V = P - λ * (-log P).
        # Let's maximize this.
        
        v = probs - (lambd * risk)
        
        # Hard Selection: Pick token with max V (Greedy BCP)
        # Soft Selection: Sample proportional to V? No, BCP usually implies optimization.
        # Let's look at the distribution of V.
        
        # In Softmax Temperature, we re-normalize.
        
        # Let's compare the "Effective Distribution"
        # For BCP, maybe we just cut off tokens with V < Threshold?
        
        # Let's simplify:
        # Does λ map to T?
        
        # Calculate entropy of selection
        # If we pick max V:
        best_idx = np.argmax(v)
        max_v_prob = probs[best_idx]
        entropy = 0 # Deterministic
        
        results.append({
            'method': 'BCP',
            'param': lambd,
            'top_token_prob': max_v_prob,
            'entropy': 0,
            'selected_rank': best_idx + 1
        })

    # Softmax Temperature Approach
    for T in temperatures:
        # Logits = log(probs)
        logits = np.log(probs)
        scaled_logits = logits / T
        new_probs = softmax(scaled_logits)
        
        # Entropy of new distribution
        entropy = -np.sum(new_probs * np.log(new_probs))
        
        # Top token prob
        top_prob = new_probs[0]
        
        results.append({
            'method': 'Softmax',
            'param': T,
            'top_token_prob': top_prob,
            'entropy': entropy,
            'selected_rank': 1 # Always rank 1 is highest prob
        })
        
    df = pd.DataFrame(results)
    
    # Let's look at how BCP changes the RANK of the selected token.
    # If λ is negative (Risk Seeking), we might pick lower rank?
    # BCP equation: V = P + λ * log(P)
    # dV/dP = 1 + λ/P. 
    # If λ > 0 (Risk Averse): 1 + λ/P > 0 always. Monotonic with P.
    # So BCP with Gain=Prob always picks Rank 1.
    
    # What if Gain = Utility (which might not be Prob)?
    # Let's assume Utility is uncorrelated with Probability (Creativity).
    # Then High λ forces us to pick High Probability (Safe).
    # Low λ allows us to pick High Utility (Creative) even if Low Probability.
    
    # Simulation 2: Creativity vs Safety
    print("Running Simulation 2: Creativity vs Safety...")
    
    n_tokens = 1000
    # Probability (Safety)
    probs = np.random.dirichlet(np.ones(n_tokens))
    risk = -np.log(probs)
    
    # Utility (Creativity/Novelty) - uncorrelated with prob
    utility = np.random.uniform(0, 1, n_tokens)
    
    sim_results = []
    lambdas = np.linspace(0, 2.0, 50)
    
    for lambd in lambdas:
        # V = Utility - λ * Risk
        v = utility - (lambd * risk)
        best_idx = np.argmax(v)
        
        selected_utility = utility[best_idx]
        selected_prob = probs[best_idx]
        selected_risk = risk[best_idx]
        
        sim_results.append({
            'lambda': lambd,
            'utility': selected_utility,
            'probability': selected_prob,
            'risk': selected_risk
        })
        
    df_sim = pd.DataFrame(sim_results)
    
    # Save
    output_dir = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results"
    os.makedirs(output_dir, exist_ok=True)
    df_sim.to_json(f"{output_dir}/cycle2681_data.json")
    
    # Visualize
    plt.figure(figsize=(10, 6))
    
    plt.subplot(1, 2, 1)
    plt.plot(df_sim['lambda'], df_sim['utility'], label='Utility (Creativity)', color='green')
    plt.title('Creativity vs Scarcity (λ)')
    plt.xlabel('Risk Aversion (λ)')
    plt.ylabel('Selected Utility')
    plt.grid(True)
    
    plt.subplot(1, 2, 2)
    plt.plot(df_sim['lambda'], df_sim['risk'], label='Risk (Surprisal)', color='red')
    plt.title('Risk Taking vs Scarcity (λ)')
    plt.xlabel('Risk Aversion (λ)')
    plt.ylabel('Selected Risk (-log P)')
    plt.grid(True)
    
    plt.tight_layout()
    plt.savefig("/Volumes/dual/DUALITY-ZERO-V2/data/figures/cycle2681_creative_temp.png")
    
    # Analysis
    low_lambda_risk = df_sim.iloc[0]['risk']
    high_lambda_risk = df_sim.iloc[-1]['risk']
    
    print(f"Low Scarcity (λ=0.0) Risk: {low_lambda_risk:.2f}")
    print(f"High Scarcity (λ=2.0) Risk: {high_lambda_risk:.2f}")
    
    if high_lambda_risk < low_lambda_risk:
        print("HYPOTHESIS CONFIRMED: Scarcity kills Creativity. High λ forces safe, boring tokens.")
    else:
        print("HYPOTHESIS FAILED.")

if __name__ == "__main__":
    run_experiment()
