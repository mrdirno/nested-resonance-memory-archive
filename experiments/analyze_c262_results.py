"""
Analysis script for C262 (H1xH2xH5) 3-way Factorial Experiment.
Calculates the 3-way interaction term to detect synergy.
"""
import json
import numpy as np
from pathlib import Path

def analyze_c262():
    results_path = Path("experiments/results/cycle262_h1h2h5_3way_factorial_results.json")
    if not results_path.exists():
        print(f"Error: Results file not found at {results_path}")
        return

    with open(results_path, 'r') as f:
        data = json.load(f)

    print(f"Analysis for C262: {data.get('experiment_id', 'Unknown')}")
    print("-" * 50)

    # Extract mean population for each condition
    conditions = data.get('conditions', {})
    means = {}
    
    # Map condition keys to simplified names
    # Keys in JSON are like "OFF-OFF-OFF", "ON-OFF-OFF", etc.
    # Order is H1, H2, H5
    
    key_map = {
        "OFF-OFF-OFF": "0",
        "H1-only": "A",
        "H2-only": "B",
        "H5-only": "C",
        "H1×H2": "AB",
        "H1×H5": "AC",
        "H2×H5": "BC",
        "H1×H2×H5": "ABC"
    }
    
    print("Population Means per Condition:")
    for cond_name, metrics in conditions.items():
        # Handle both list of runs and aggregated stats
        if 'mean_population' in metrics:
             val = metrics['mean_population']
        elif 'runs' in metrics:
             # Calculate mean from runs if not pre-calculated
             pops = [r['final_population'] for r in metrics['runs']]
             val = np.mean(pops)
        else:
             val = 0.0
             
        mapped_key = key_map.get(cond_name, cond_name)
        means[mapped_key] = val
        print(f"  {cond_name:12} ({mapped_key:3}): {val:.4f}")

    # Calculate 3-way Interaction Term
    # I3 = ABC - (AB + AC + BC) + (A + B + C) - Control
    # Wait, let's check the sign convention.
    # Standard expansion:
    # ABC = Control + A_eff + B_eff + C_eff + AB_int + AC_int + BC_int + ABC_int
    # A_eff = A - Control
    # AB_int = AB - A - B + Control
    # ABC_int = ABC - AB - AC - BC + A + B + C - Control
    
    A = means.get('A', 0)
    B = means.get('B', 0)
    C = means.get('C', 0)
    AB = means.get('AB', 0)
    AC = means.get('AC', 0)
    BC = means.get('BC', 0)
    ABC = means.get('ABC', 0)
    Ctrl = means.get('0', 0)
    
    interaction_term = ABC - AB - AC - BC + A + B + C - Ctrl
    
    print("-" * 50)
    print(f"3-way Interaction Term (Synergy): {interaction_term:.4f}")
    
    if interaction_term > 0.5:
        print("Result: STRONG SYNERGY detected.")
    elif interaction_term > 0.0:
        print("Result: WEAK SYNERGY detected.")
    elif interaction_term > -0.5:
        print("Result: ADDITIVE / NEUTRAL.")
    else:
        print("Result: INTERFERENCE / ANTAGONISM.")

if __name__ == "__main__":
    analyze_c262()
