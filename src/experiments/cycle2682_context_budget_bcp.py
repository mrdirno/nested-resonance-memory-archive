"""
Cycle 2682: Prompt Engineering as BCP (The Context Budget)
==========================================================

Investigation: Is Prompt Engineering functionally equivalent to reducing Search Cost in a BCP system?

Hypothesis:
1. "In-Context Learning" (Providing examples/instructions) reduces the internal search cost 
   required to locate the correct response pattern.
2. Under High λ (Scarcity/Latency Constraint), models fail complex tasks because the 
   Search Cost (without context) > V_threshold.
3. Providing Context lowers Cost, raising V above threshold even at High λ.

Equation:
V(response) = Gain(Correctness) - λ * (Base_Search_Cost - Context_Reduction)

If Context_Reduction is high (good prompt), V stays positive even if λ is high.
If Context is missing, Cost is high. If λ is high, V < 0 -> Failure/Hallucination.

We simulate a "Task" that requires finding a specific needle in a haystack.
- Base Search Cost: High (finding needle without hints).
- Prompt Quality (0-1): Reduces search cost linearly or exponentially.
- λ: Compute/Time pressure.

"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os

def run_experiment():
    print("Initializing Cycle 2682: The Context Budget...")
    
    # Parameters
    lambdas = np.linspace(0.1, 5.0, 50) # Pressure
    prompt_qualities = [0.0, 0.2, 0.5, 0.8, 1.0] # 0=Zero-shot, 1=Perfect Instruction
    
    base_search_cost = 10.0
    gain_correct = 20.0
    
    # Cost Function:
    # Effective Cost = Base_Search_Cost * (1 - Prompt_Quality) + Processing_Cost_of_Prompt
    # Note: Processing prompt adds a small cost (reading time), but saves massive search cost.
    # Let's assume Reading Cost is small constant per unit of quality.
    
    reading_cost_factor = 1.0 # Cost to read the prompt
    
    results = []
    
    for lambd in lambdas:
        for quality in prompt_qualities:
            # Calculate Costs
            search_reduction = quality # 0 to 1 reduction
            remaining_search_cost = base_search_cost * (1.0 - search_reduction)
            
            prompt_reading_cost = quality * reading_cost_factor
            
            total_cost = remaining_search_cost + prompt_reading_cost
            
            # Net Value
            v = gain_correct - (lambd * total_cost)
            
            # Outcome: Success if V > 0 (Rational to attempt and succeed)
            # If V < 0, agent gives up or hallucinates (Failure)
            success = 1.0 if v > 0 else 0.0
            
            results.append({
                'lambda': lambd,
                'prompt_quality': quality,
                'total_cost': total_cost,
                'net_value': v,
                'success': success
            })
            
    df = pd.DataFrame(results)
    
    # Save
    output_dir = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results"
    os.makedirs(output_dir, exist_ok=True)
    df.to_json(f"{output_dir}/cycle2682_data.json")
    
    # Visualize
    plt.figure(figsize=(10, 6))
    
    # Plot Success Regions
    # We want to see the "Success Boundary" in Lambda-Quality space
    
    # Pivot for heatmap
    pivot_table = df.pivot(index='lambda', columns='prompt_quality', values='success')
    
    # Using imshow directly or contour
    # Or just line plots of Value vs Lambda for different Qualities
    
    for q in prompt_qualities:
        subset = df[df['prompt_quality'] == q]
        plt.plot(subset['lambda'], subset['net_value'], label=f'Prompt Quality={q}')
        
    plt.axhline(y=0, color='black', linestyle='--', label='Success Threshold')
    plt.title('Net Value vs Scarcity (λ) for different Prompt Qualities')
    plt.xlabel('Compute Pressure (λ)')
    plt.ylabel('Net Value (V)')
    plt.legend()
    plt.grid(True)
    
    plt.tight_layout()
    plt.savefig("/Volumes/dual/DUALITY-ZERO-V2/data/figures/cycle2682_context_budget.png")
    
    # Analysis
    print("Cycle 2682 Analysis:")
    
    # Find max lambda where Success is possible for each quality
    max_lambdas = {}
    for q in prompt_qualities:
        subset = df[(df['prompt_quality'] == q) & (df['success'] == 1.0)]
        if not subset.empty:
            max_l = subset['lambda'].max()
        else:
            max_l = 0.0
        max_lambdas[q] = max_l
        
    print("Max Survivable Scarcity (λ) by Prompt Quality:")
    for q, l in max_lambdas.items():
        print(f"Quality {q}: λ_max = {l:.2f}")
        
    # Confirmation logic
    # We expect Quality 1.0 to survive much higher λ than Quality 0.0
    if max_lambdas[1.0] > max_lambdas[0.0] * 2.0:
        print("HYPOTHESIS CONFIRMED: Prompt Engineering buys 'Lambda Tolerance'. High quality context enables success under high scarcity.")
    else:
        print("HYPOTHESIS FAILED.")

if __name__ == "__main__":
    run_experiment()
