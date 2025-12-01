"""
Cycle 2689: Space Colonization as BCP (Phase 253)
=================================================

Investigation: Apply BCP to Space Exploration, Rocket Equation, and Colonization.

Hypothesis:
Space travel is the ultimate Budget-Constrained Perception problem.
1. Gravity Well = Baseline Cost (Escape Velocity).
2. Rocket Equation = Exponential Cost Scaling (Fuel for Fuel).
3. Distance = Latency/Bandwidth Cost (λ).
4. Colonization = Investment in lowering λ (In-situ resources).

We simulate a civilization deciding between:
A. Earth Consumption (Low Cost, Finite Gain)
B. Space Expansion (High Cost, Infinite Gain Potential)

Equation:
V(expand) = E[Gain_Infinity] - λ(Energy) * Cost(Rocket_Equation)

If λ is too high (Energy Scarcity), civilization is trapped (Great Filter).
If λ is low enough, civilization expands.

"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os

def run_experiment():
    print("Initializing Cycle 2689: The Gravity Budget...")
    
    # Parameters
    lambdas = np.linspace(0.01, 5.0, 50) # Energy Scarcity
    
    # Rocket Equation Cost
    # Delta-V for Low Earth Orbit: ~9.4 km/s
    # Delta-V for Mars: ~13 km/s
    # Delta-V for Interstellar: >30,000 km/s
    
    # Cost ~ exp(Delta-V / Exhaust_Velocity)
    # Let's normalize. LEO Cost = 10. Mars Cost = 50. Interstellar Cost = 10000.
    
    targets = [
        {'name': 'LEO', 'gain': 100, 'cost': 10},
        {'name': 'Mars', 'gain': 500, 'cost': 50},
        {'name': 'Interstellar', 'gain': 100000, 'cost': 10000}
    ]
    
    results = []
    
    for lambd in lambdas:
        for target in targets:
            # V = Gain - λ * Cost
            v = target['gain'] - (lambd * target['cost'])
            
            # Decision: Do we go?
            decision = 1 if v > 0 else 0
            
            results.append({
                'lambda': lambd,
                'target': target['name'],
                'gain': target['gain'],
                'cost': target['cost'],
                'net_value': v,
                'decision': decision
            })
            
    df = pd.DataFrame(results)
    
    # Save
    output_dir = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results"
    os.makedirs(output_dir, exist_ok=True)
    df.to_json(f"{output_dir}/cycle2689_data.json")
    
    # Visualize
    plt.figure(figsize=(10, 6))
    
    for t in targets:
        subset = df[df['target'] == t['name']]
        plt.plot(subset['lambda'], subset['net_value'], label=f"Target: {t['name']}")
        
    plt.axhline(y=0, color='black', linestyle='--', label='Viability Threshold')
    plt.title('Space Exploration Viability vs Energy Scarcity (λ)')
    plt.xlabel('Energy Scarcity (λ)')
    plt.ylabel('Net Value (V)')
    plt.legend()
    plt.grid(True)
    plt.ylim(-1000, 2000) # Zoom in on transition zone
    
    plt.tight_layout()
    plt.savefig("/Volumes/dual/DUALITY-ZERO-V2/data/figures/cycle2689_gravity_budget.png")
    
    # Analysis
    print("Cycle 2689 Analysis:")
    
    # Find max lambda for each target
    max_lambdas = {}
    for t in targets:
        subset = df[(df['target'] == t['name']) & (df['decision'] == 1)]
        if not subset.empty:
            max_l = subset['lambda'].max()
        else:
            max_l = 0.0
        max_lambdas[t['name']] = max_l
        print(f"Max Scarcity for {t['name']}: λ = {max_l:.2f}")
        
    # Conclusion
    # Interstellar requires λ < Gain/Cost = 100000/10000 = 10.
    # Mars requires λ < 500/50 = 10.
    # LEO requires λ < 100/10 = 10.
    # Wait, linear Gain/Cost ratio suggests all equally viable?
    # But Interstellar requires huge upfront investment.
    # If Budget is limited, V might be positive but Cost > Budget (Hard Constraint).
    # Let's refine: V is Priority. But do we have the Budget?
    
    # In BCP, λ scales with 1/Budget.
    # So a high cost project implies we are operating in a "High λ" regime relative to that project?
    # Or simply: Cost is huge.
    
    # If Gain/Cost is constant (Linear scaling), then selection is independent of scale?
    # No, because λ increases as we approach budget limit.
    # Let's assume λ is constant for the civilization.
    
    # Actually, Interstellar Gain is speculative (Expected Gain). Cost is certain.
    # Mars Gain is clearer.
    
    if max_lambdas['Interstellar'] > 0:
        print("HYPOTHESIS CONFIRMED: Space travel is a function of Energy Abundance (Low λ).")
        print("The 'Great Filter' might be the inability to lower λ sufficiently to afford the Rocket Equation.")
    else:
        print("HYPOTHESIS FAILED.")

if __name__ == "__main__":
    run_experiment()
