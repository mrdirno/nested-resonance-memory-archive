import json
import math
import sys
import os

# Ensure valid import path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

# -----------------------------------------------------------------------------
# EXPERIMENT: THE FABRICATION BUDGET (3D PRINT OPTIMIZATION)
# -----------------------------------------------------------------------------
# Hypothesis: 3D Printing parameters (Infill, Speed, Layer Height) are BCP allocations.
# V(print) = Strength * Quality - λ(Filament/Time) * Cost.
#
# Dynamics:
# - Infill % increases Strength (Gain) but also Time & Material (Cost).
# - Speed increases Throughput (Gain?) but decreases Quality (Gain).
#   Actually, Speed reduces Time Cost, but risks Failure (Cost).
# -----------------------------------------------------------------------------

RESULTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'results')
os.makedirs(RESULTS_DIR, exist_ok=True)

def run_fabrication_experiment():
    print("Running Cycle 2909: The Fabrication Budget...")
    
    # Parameters
    filament_budget = 1000.0 # grams
    time_budget = 600.0 # minutes
    part_utility = 500.0
    
    # Scenarios
    scenarios = [
        {"name": "Scarcity", "lambda_mat": 1.0, "lambda_time": 0.5},
        {"name": "Abundance", "lambda_mat": 0.1, "lambda_time": 0.1},
        {"name": "Urgency", "lambda_mat": 0.1, "lambda_time": 2.0} # Material cheap, Time expensive
    ]
    
    # Options: Infill %
    infills = [10, 20, 40, 60, 80, 100]
    
    results = {
        "meta": {
            "cycle": 2909,
            "name": "The Fabrication Budget",
            "phase": 267,
            "gate": 1200
        },
        "scenarios": []
    }
    
    print(f"Budgets: {filament_budget}g, {time_budget}m. Utility: {part_utility}")
    
    for scen in scenarios:
        print(f"\n--- Scenario: {scen['name']} ---")
        s_data = []
        
        for infill in infills:
            strength = 100.0 * math.pow(infill / 100.0, 0.8)
            material_cost = 10.0 * infill
            time_cost = 20.0 + (infill * 2.0)
            
            # Total Cost weighted by Lambda
            total_cost_score = (scen["lambda_mat"] * material_cost) + (scen["lambda_time"] * time_cost)
            
            # Value = Utility * Quality - Cost
            quality = strength / 100.0
            value = (part_utility * quality) - total_cost_score
            
            feasible = (material_cost <= filament_budget) and (time_cost <= time_budget)
            
            s_data.append({
                "infill": infill,
                "value": round(value, 2),
                "feasible": feasible
            })
            
            print(f"Infill {infill}%: V={value:.1f} -> {'YES' if value > 0 else 'NO'}")
            
        results["scenarios"].append({
            "name": scen["name"],
            "data": s_data
        })
        
        best = max(s_data, key=lambda x: x["value"])
        print(f"Optimal: {best['infill']}% (Value {best['value']})")
    
    filepath = os.path.join(RESULTS_DIR, 'cycle2909_fabrication_bcp.json')
    with open(filepath, 'w') as f:
        json.dump(results, f, indent=2)
        
    print(f"Results saved to {filepath}")

if __name__ == "__main__":
    run_fabrication_experiment()
