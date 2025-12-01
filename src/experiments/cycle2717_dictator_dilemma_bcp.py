"""
Cycle 2717: The Dictator's Dilemma (Phase 259)
==============================================

Investigation: Is Autocracy a BCP Failure Mode?

Hypothesis:
Autocracy minimizes Coordination Cost (1 Ruler vs N Voters) but maximizes Information Cost.
V(autocracy) = Control - λ * (Enforcement + Information_Loss).

1. The Dictator's Dilemma: To rule, the dictator needs information. But truth is costly to speak (Fear).
2. Sycophancy Cost: Subordinates report Gain > 0 to survive, hiding Cost > 0.
3. Result: Dictator makes decisions on Hallucinated Data. V < 0. Collapse.

We simulate a Hierarchy.
- Ruler needs to allocate resources based on signals from N subordinates.
- Subordinates have a "Fear" parameter (Cost of Truth).
- If Fear is high, they lie.
- Ruler allocates resources based on lies.
- We measure System Efficiency vs Fear.

"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os

def run_experiment():
    print("Initializing Cycle 2717: The Dictator's Dilemma...")
    
    # Parameters
    n_subordinates = 100
    n_rounds = 50
    
    # Fear Levels (λ for Subordinates)
    # High Fear = High Cost of Truth
    fear_levels = np.linspace(0, 1.0, 20)
    
    results = []
    
    for fear in fear_levels:
        # System State
        real_needs = np.random.uniform(0, 100, n_subordinates)
        total_resources = 5000 # Enough for average needs
        
        # Reporting Phase
        reported_needs = []
        for real in real_needs:
            # Cost of Truth = Fear * (If need is high, maybe Ruler gets mad?)
            # Actually, Sycophancy means "Everything is fine" or "I need more".
            # Dictator's Dilemma usually means "Hiding Bad News".
            
            # Scenario: Subordinates manage a sector.
            # Real status: 100 (Great) to 0 (Collapse).
            # If status < 50, Dictator punishes.
            
            status = real # Reusing variable
            
            # Decision to Lie
            # V(truth) = -Punishment (if status bad) - λ * Fear
            # V(lie) = 0 (Safe) - Risk_of_discovery
            
            # Simple model:
            # If Status < Threshold and Fear > 0:
            # Lie = Status + Fear * 50 (Inflation)
            
            if status < 50:
                lie_magnitude = fear * 50.0
                report = min(100, status + lie_magnitude)
            else:
                report = status
                
            reported_needs.append(report)
            
        # Allocation Phase
        # Ruler allocates resources to fix problems.
        # If Report says "100" (Perfect), Ruler sends 0 resources.
        # If Report says "0" (Crisis), Ruler sends max resources.
        
        # In this model, lying "Everything is fine" means NO RESOURCES sent.
        # So the sector collapses further.
        
        # Real outcome calculation
        system_health = 0
        for i in range(n_subordinates):
            report = reported_needs[i]
            real = real_needs[i]
            
            # Ruler logic: 
            # Allocation = 100 - Report. (Fill the gap).
            allocation = 100 - report
            
            # New Real Status = Old Real + Allocation - Decay
            # Decay = 10
            decay = 10
            new_real = real + allocation - decay
            new_real = max(0, min(100, new_real))
            
            system_health += new_real
            
        avg_health = system_health / n_subordinates
        
        results.append({
            'fear': fear,
            'avg_health': avg_health,
            'lie_magnitude': np.mean(np.array(reported_needs) - np.array(real_needs))
        })
            
    df = pd.DataFrame(results)
    
    # Save
    output_dir = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results"
    os.makedirs(output_dir, exist_ok=True)
    df.to_json(f"{output_dir}/cycle2717_data.json")
    
    # Visualize
    plt.figure(figsize=(10, 6))
    
    plt.subplot(1, 2, 1)
    plt.plot(df['fear'], df['avg_health'], label='System Health', color='red')
    plt.title("Dictator's Dilemma: Health vs Fear")
    plt.xlabel('Fear / Cost of Truth (λ)')
    plt.ylabel('Average Sector Health')
    plt.grid(True)
    
    plt.subplot(1, 2, 2)
    plt.plot(df['fear'], df['lie_magnitude'], label='Information Distortion', color='purple')
    plt.title('The Sycophancy Curve')
    plt.xlabel('Fear (λ)')
    plt.ylabel('Magnitude of Lies')
    plt.grid(True)
    
    plt.tight_layout()
    plt.savefig("/Volumes/dual/DUALITY-ZERO-V2/data/figures/cycle2717_dictator_dilemma.png")
    
    # Analysis
    print("Cycle 2717 Analysis:")
    
    low_fear_health = df.iloc[0]['avg_health']
    high_fear_health = df.iloc[-1]['avg_health']
    
    print(f"Low Fear Health: {low_fear_health:.2f}")
    print(f"High Fear Health: {high_fear_health:.2f}")
    
    if high_fear_health < low_fear_health * 0.8:
        print("HYPOTHESIS CONFIRMED: Autocracy fails because High Fear (λ) increases the Cost of Truth.")
        print("The Dictator operates on hallucinated data, leading to resource misallocation and collapse.")
    else:
        print("HYPOTHESIS FAILED.")

if __name__ == "__main__":
    run_experiment()
