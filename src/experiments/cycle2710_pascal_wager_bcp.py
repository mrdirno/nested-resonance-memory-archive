"""
Cycle 2710: The Pascal's Wager Budget (Phase 257)
=================================================

Investigation: Is Pascal's Wager BCP-rational?

Hypothesis:
Pascal's Wager is a BCP edge case where Gain is Infinite and Cost is Finite.
V(belief) = P(God) * Gain(Heaven) - λ(World) * Cost(Piety).

If Gain -> Infinity, then for any P(God) > 0 and any Finite Cost, V -> Infinity.
Therefore, belief is ALWAYS rational.

BUT: Why are there atheists?
1. High λ: Cost(Piety) is too high in the present (Immediate Scarcity).
2. Discounting: Future Gain is discounted heavily (γ -> 0).
3. P(God) = 0: Absolute Atheism.
4. Multiple Infinite Gains: Competing religions (Which Infinity?).

We simulate agents with different λ and Discount Factors facing the Wager.

"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os

def run_experiment():
    print("Initializing Cycle 2710: The Pascal's Wager Budget...")
    
    # Parameters
    n_agents = 1000
    
    # Agent Properties
    lambdas = np.random.exponential(1.0, n_agents) # Scarcity
    discounts = np.random.uniform(0, 1.0, n_agents) # Future orientation
    prob_god = np.random.beta(1, 5, n_agents) # Belief probability (mostly low)
    
    # Wager Parameters
    gain_heaven = 1e9 # Effective Infinity
    cost_piety = 100.0 # Cost of rituals/restrictions
    
    results = []
    
    for i in range(n_agents):
        l = lambdas[i]
        gamma = discounts[i]
        p = prob_god[i]
        
        # V = (P * Gain * Gamma) - (λ * Cost)
        # Note: Gain is in future, Cost is now.
        
        gain_term = p * gain_heaven * gamma
        cost_term = l * cost_piety
        
        v = gain_term - cost_term
        
        choice = 'Believer' if v > 0 else 'Atheist'
        
        results.append({
            'agent_id': i,
            'lambda': l,
            'discount': gamma,
            'prob_god': p,
            'net_value': v,
            'choice': choice
        })
            
    df = pd.DataFrame(results)
    
    # Save
    output_dir = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results"
    os.makedirs(output_dir, exist_ok=True)
    df.to_json(f"{output_dir}/cycle2710_data.json")
    
    # Visualize
    plt.figure(figsize=(10, 6))
    
    # Scatter plot: Lambda vs Prob(God)
    # Color by Choice
    
    believers = df[df['choice'] == 'Believer']
    atheists = df[df['choice'] == 'Atheist']
    
    plt.scatter(atheists['lambda'], atheists['prob_god'], color='red', alpha=0.5, label='Atheist')
    plt.scatter(believers['lambda'], believers['prob_god'], color='blue', alpha=0.5, label='Believer')
    
    plt.title("Pascal's Wager: Faith vs Scarcity")
    plt.xlabel('Scarcity (λ)')
    plt.ylabel('Probability of God (P)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig("/Volumes/dual/DUALITY-ZERO-V2/data/figures/cycle2710_pascal_wager.png")
    
    # Analysis
    print("Cycle 2710 Analysis:")
    
    believer_rate = len(believers) / n_agents
    print(f"Believer Rate: {believer_rate:.2%}")
    
    # Check High Cost Sensitivity
    # High λ agents should reject Wager even if P > 0.
    high_lambda_atheists = df[(df['lambda'] > 2.0) & (df['choice'] == 'Atheist')]
    print(f"High Scarcity Atheists: {len(high_lambda_atheists)}")
    
    # Hypothesis Check
    # If Gain is effectively infinite, why do High λ reject?
    # Because 1e9 * tiny_gamma * tiny_p might still be < λ * 100.
    # Or in the simulation, 1e9 dominates unless gamma or p are effectively zero.
    
    # With 1e9, almost everyone should believe unless P or Gamma is 0.
    # Let's check the data.
    
    if believer_rate > 0.9:
        print("HYPOTHESIS CONFIRMED: Infinite Gain dominates. Almost everyone believes.")
        print("Atheism implies P(God) ≈ 0 or Discount ≈ 0.")
    else:
        print("HYPOTHESIS REFINED: Finite Constraints (Scarcity) can override Infinite Gain if Probability or Discount is low enough.")
        print("Faith requires Affordability.")

if __name__ == "__main__":
    run_experiment()
