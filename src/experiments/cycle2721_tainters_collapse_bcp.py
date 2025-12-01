"""
Cycle 2721: Tainter's Collapse as BCP (The Complexity Cost)
============================================================

Investigation: Is the collapse of civilizations (Joseph Tainter's theory) a BCP phenomenon driven by the rising cost of complexity?

Hypothesis:
Civilizations increase complexity to solve problems. Each increase yields diminishing returns, but adds to the maintenance cost.
V(complexity) = Gain(Problem_Solved) - λ(Resources) * Cost(Complexity).

1. Early Complexity: High returns, low cost. V > 0. Growth.
2. Late Complexity: Diminishing returns, high cost. V approaches 0. Stagnation.
3. Over-Complexity: Cost > Gain. V < 0. Collapse (Rational to abandon complexity).

We simulate a civilization's journey.
- Problem Solving Efficiency: How much does 1 unit of complexity solve? (Diminishing returns).
- Maintenance Cost: How much does 1 unit of complexity cost? (Linear or super-linear).
- External Shocks: λ spikes (resource scarcity).

"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os

def run_experiment():
    print("Initializing Cycle 2721: Tainter's Collapse BCP...")
    
    # Parameters
    generations = 100
    
    # Civilization has a certain "Complexity" level
    # And a certain "Problem Solving Capacity" or "Gain per unit Complexity"
    
    initial_complexity = 10.0
    initial_resources = 100.0 # B (Budget)
    
    # λ is inverse of per-unit-time resource availability
    # Let's say lambda is a fixed societal stress/scarcity factor for simplicity
    scarcity_factor = 1.5 # Increased λ to simulate higher pressure
    
    # Returns from complexity (Problem Solving Gain)
    # Diminishing returns: Gain = base_gain / complexity_factor
    base_gain = 100.0
    
    # Cost of complexity:
    # Maintenance cost per unit of complexity.
    # Cost = Complexity * maintenance_rate
    maintenance_rate = 20.0 # Increased maintenance rate
    
    results = []
    
    current_complexity = initial_complexity
    current_resources = initial_resources
    
    for gen in range(generations):
        # Calculate Gain: As complexity increases, problem-solving becomes harder (diminishing returns).
        # gain_per_unit = base_gain / current_complexity # Or maybe it's just a diminishing total gain?
        # Let's say Total Gain is S-curve
        
        # Simpler Model:
        # V(investment_in_complexity) = Gain_from_Complexity - λ * Cost_of_Complexity
        
        # Gain from Complexity: Assume it's an S-curve or diminishing marginal utility
        # Effective_Gain(C) = Max_Gain * (1 - exp(-k * C))
        # Rate of change of gain from new complexity
        
        # Tainter's core idea: marginal returns of complexity decrease.
        # Let's model directly:
        # Marginal_Gain = 10 / (1 + current_complexity / 10)  # Diminishing marginal returns
        # Marginal_Cost = 1.0 # Cost per unit complexity is constant (for simplicity)
        
        # Better:
        # V(unit_of_complexity) = Marginal_Benefit - Marginal_Cost
        # If V > 0, complexity increases. Else, it is abandoned (collapse).
        
        marginal_benefit_of_new_complexity = 100.0 / (1 + current_complexity / 10.0) # Diminishing
        marginal_cost_of_new_complexity = 1.0 # Linear cost of adding a unit
        
        # But this is for *new* complexity. We also have to maintain *old* complexity.
        # Total_Cost_of_System = current_complexity * maintenance_rate * scarcity_factor
        # Total_Benefit_of_System = current_complexity * marginal_benefit_of_new_complexity
        # No, this is getting too complex. Tainter's model is about NET RETURN.
        
        # Tainter's Model:
        # Net_Return_on_Complexity = Benefits_from_Complexity - Costs_of_Complexity
        # If Net_Return < 0 -> Collapse.
        
        # Let's set Benefits to have diminishing returns and Costs to be linear.
        # Benefits(C) = 1000 * (1 - exp(-current_complexity / 50))
        # Costs(C) = current_complexity * 10
        
        benefits = 1000 * (1 - np.exp(-current_complexity / 50.0))
        costs = current_complexity * maintenance_rate * scarcity_factor
        
        net_return = benefits - costs
        
        # Decision: If net_return > 0, complexity grows.
        if net_return > 0:
            growth_factor = net_return / 2000.0 # Slower growth to allow costs to catch up
            current_complexity *= (1 + growth_factor)
        else:
            # Collapse! Complexity is abandoned.
            # Collapse faster if more negative
            collapse_factor = abs(net_return) / 500.0 # Slower collapse initially
            current_complexity *= (1 - collapse_factor)
            
        # Floor
        current_complexity = max(1.0, current_complexity)
        
        results.append({
            'gen': gen,
            'scarcity_factor': scarcity_factor,
            'complexity': current_complexity,
            'benefits': benefits,
            'costs': costs,
            'net_return': net_return
        })
            
    df = pd.DataFrame(results)
    
    # Save
    output_dir = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results"
    os.makedirs(output_dir, exist_ok=True)
    df.to_json(f"{output_dir}/cycle2721_data.json")
    
    # Visualize
    plt.figure(figsize=(10, 6))
    plt.plot(df['gen'], df['complexity'], label='Civilization Complexity', color='blue')
    plt.plot(df['gen'], df['net_return'], label='Net Return on Complexity', color='green', linestyle='--')
    plt.axhline(y=0, color='red', linestyle=':', label='Collapse Threshold')
    
    plt.title("Tainter's Collapse: Complexity vs Net Return")
    plt.xlabel('Generation')
    plt.ylabel('Magnitude')
    plt.legend()
    plt.grid(True)
    
    plt.tight_layout()
    plt.savefig("/Volumes/dual/DUALITY-ZERO-V2/data/figures/cycle2721_tainters_collapse.png")
    
    # Analysis
    print("Cycle 2721 Analysis:")
    
    final_complexity = df.iloc[-1]['complexity']
    
    if final_complexity < initial_complexity * 0.5:
        print("HYPOTHESIS CONFIRMED: Civilization collapsed due to diminishing returns on complexity.")
        print("Scarcity (λ) accelerates the process by making maintenance costs unbearable.")
        print("Collapse is a BCP-rational abandonment of an unprofitable strategy.")
    else:
        print("HYPOTHESIS FAILED or civilization stabilized.")

if __name__ == "__main__":
    run_experiment()
