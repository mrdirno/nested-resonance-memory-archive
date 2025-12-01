"""
Cycle 2679: Model Collapse as BCP Bankruptcy
============================================

Investigation: Does BCP explain Model Collapse as a rational market failure?

Hypothesis:
Model Collapse is a "Tragedy of the Commons" where agents rationally choose
Low-Cost/Medium-Quality Synthetic Data (Pyrite) over High-Cost/High-Quality Real Data (Gold),
leading to a recursive degradation of the Synthetic Data quality itself.

Dynamics:
1. Real Data (Gold): Cost = 10, Quality = 1.0 (Constant)
2. Synthetic Data (Pyrite): Cost = 1, Quality = f(Previous Generation Mix)
3. Agent Decision: Choose mix to Maximize V = Quality - λ * Cost

If λ is high (Scarcity), agents choose Synthetic.
If everyone chooses Synthetic, next gen Synthetic Quality drops.
Collapse occurs when Synthetic Quality < Threshold, but agents can't afford Real.

"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os

def run_experiment():
    print("Initializing Cycle 2679: Model Collapse BCP...")
    
    # Parameters
    generations = 20
    lambdas = [0.01, 0.1, 0.5, 1.0, 5.0] # Extreme Abundance to Scarcity
    
    cost_real = 3.0  # Truth is expensive, but affordable for the elite
    cost_synth = 1.0
    
    quality_real = 1.0 # Gold standard
    
    results = []
    
    for lambd in lambdas:
        # Initial State
        current_synth_quality = 0.95 # Starts good
        
        history = []
        
        for gen in range(generations):
            # Agent Decision: Evaluate V(Real) vs V(Synth)
            # V = Gain - λ * Cost
            # We assume agents can estimate current quality
            
            v_real = quality_real - (lambd * cost_real)
            v_synth = current_synth_quality - (lambd * cost_synth)
            
            # Selection Probability (Softmax-like or deterministic)
            # Let's use deterministic for clarity, or a mix based on V difference?
            # Let's use a population of agents.
            
            if v_synth > v_real:
                # Rational choice is Synthetic
                pct_synth_adoption = 1.0
            elif v_real > v_synth:
                # Rational choice is Real
                pct_synth_adoption = 0.0
            else:
                pct_synth_adoption = 0.5
                
            # Reality Check: Even with low V, some agents might be forced?
            # Let's keep it simple: Market Share = Sigmoid(V_synth - V_real)
            # If V_synth is much better (cheaper), adoption is high.
            
            delta_v = v_synth - v_real
            # Adoption function
            adoption = 1 / (1 + np.exp(-5 * delta_v)) 
            
            # Outcome: Next Gen Quality
            # Quality degrades proportional to Synthetic adoption
            # Decay factor: How much info is lost?
            # Q(t+1) = Q(t) * (1 - decay * adoption) + recovery * (1 - adoption)
            # If adoption = 0 (All Real), Quality resets to max (trained on Gold).
            # If adoption = 1 (All Synth), Quality decays.
            
            decay_rate = 0.1 # 10% loss per gen if pure synthetic
            recovery_rate = 1.0 # Instant recovery if training on gold
            
            # Calculate effective training mix quality
            # The NEW model is trained on the weighted average of data consumed
            mix_quality = (adoption * current_synth_quality) + ((1 - adoption) * quality_real)
            
            # The NEXT generation's synthetic data will be based on THIS model's output.
            # But synthetic data inherently has variance loss.
            # So Next Synth Quality = Mix Quality * (1 - Intrinsic_Entropy_Loss)
            
            intrinsic_loss = 0.05
            next_synth_quality = mix_quality * (1 - intrinsic_loss)
            
            # Record
            history.append({
                'gen': gen,
                'lambda': lambd,
                'synth_quality': current_synth_quality,
                'adoption': adoption,
                'v_real': v_real,
                'v_synth': v_synth
            })
            
            # Update
            current_synth_quality = next_synth_quality
            
        results.extend(history)
        
    df = pd.DataFrame(results)
    
    # Save
    output_dir = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results"
    os.makedirs(output_dir, exist_ok=True)
    df.to_json(f"{output_dir}/cycle2679_data.json")
    
    # Visualize
    plt.figure(figsize=(12, 6))
    
    # Plot 1: Quality over Time
    plt.subplot(1, 2, 1)
    for l in lambdas:
        subset = df[df['lambda'] == l]
        plt.plot(subset['gen'], subset['synth_quality'], label=f'λ={l}')
    plt.title('Model Quality vs Generations (By Scarcity)')
    plt.xlabel('Generation')
    plt.ylabel('Synthetic Quality')
    plt.legend()
    
    # Plot 2: Adoption Rate
    plt.subplot(1, 2, 2)
    for l in lambdas:
        subset = df[df['lambda'] == l]
        plt.plot(subset['gen'], subset['adoption'], label=f'λ={l}')
    plt.title('Synthetic Adoption vs Generations')
    plt.xlabel('Generation')
    plt.ylabel('Adoption Rate (1.0 = All Synth)')
    
    plt.tight_layout()
    plt.savefig("/Volumes/dual/DUALITY-ZERO-V2/data/figures/cycle2679_model_collapse.png")
    
    # Findings
    print("Cycle 2679 Analysis:")
    high_scarcity = df[df['lambda'] == 5.0].iloc[-1]
    low_scarcity = df[df['lambda'] == 0.01].iloc[-1]
    
    print(f"High Scarcity (λ=5.0) Final Quality: {high_scarcity['synth_quality']:.4f}")
    print(f"Low Scarcity (λ=0.01) Final Quality: {low_scarcity['synth_quality']:.4f}")
    
    if high_scarcity['synth_quality'] < 0.5 and low_scarcity['synth_quality'] > 0.9:
        print("HYPOTHESIS CONFIRMED: Only extreme abundance (λ=0.01) preserves Truth. The middle class consumes Slop.")
    else:
        print("HYPOTHESIS FAILED or dynamics complex.")

if __name__ == "__main__":
    run_experiment()
