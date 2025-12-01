import json
import math
import sys
import os

# Ensure valid import path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

# -----------------------------------------------------------------------------
# EXPERIMENT: THE DISTANCE BUDGET (INTERSTELLAR TRAP)
# -----------------------------------------------------------------------------
# Hypothesis: Interstellar Colonization is BCP-irrational.
# V(colony) = ColonyValue - λ(Home) * (LaunchCost + TimeCost)
#
# Dynamics:
# - Distance D (Light Years).
# - Speed v (fraction of c).
# - Time T = D / v.
# - Energy Cost E scales with v^2 (Kinetic) -> Rocket Equation exponential.
# - Biological Maintenance M per year.
# - Total Cost = LaunchEnergy + (M * T).
# -----------------------------------------------------------------------------

RESULTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'results')
os.makedirs(RESULTS_DIR, exist_ok=True)

def run_distance_experiment():
    print("Running Cycle 2692: The Distance Budget (Interstellar Trap)...")
    
    # Parameters
    distance = 4.2 # Proxima Centauri (Light Years)
    colony_value = 1000.0 # Massive value of a new world
    lambda_val = 1.0 # Value of resources at home
    maintenance_cost = 10.0 # High cost to keep humans alive per year
    
    # Physics
    c = 1.0 # Speed of light
    
    # Strategy: Choose Speed v
    speeds = [0.01, 0.05, 0.1, 0.2, 0.5, 0.8, 0.99]
    
    results = {
        "meta": {
            "cycle": 2692,
            "name": "The Distance Budget",
            "phase": 253,
            "gate": 1168
        },
        "strategies": []
    }
    
    print(f"Target: {distance} LY. Value: {colony_value}. Maintenance: {maintenance_cost}/yr")
    
    for v in speeds:
        # Time (Years)
        time = distance / v
        
        # Energy Cost (Kinetic ~ v^2, ignoring Relativistic for low v, but let's be rough)
        # Rocket Equation: Mass Ratio scales exponentially.
        # Let's just use a proxy Cost function C_launch = k * (v^2 / (1-v^2)^0.5) for relativistic?
        # Let's stick to BCP simple proxy: High speed is expensive.
        # Launch Cost = 100 * (e^(10v) - 1) ?
        launch_cost = 100.0 * v * 10 # Linear proxy for now? No, energy is v^2.
        launch_cost = 1000.0 * (v**2)
        
        # Total Maintenance Cost
        total_maint = maintenance_cost * time
        
        # Total Project Cost
        total_cost = launch_cost + total_maint
        
        # Net Value
        value = colony_value - (lambda_val * total_cost)
        
        results["strategies"].append({
            "speed": v,
            "time_years": round(time, 2),
            "launch_cost": round(launch_cost, 2),
            "maint_cost": round(total_maint, 2),
            "total_cost": round(total_cost, 2),
            "net_value": round(value, 2),
            "viable": value > 0
        })
        
        print(f"v={v:.2f}c: T={time:.1f}y Cost={total_cost:.0f} V={value:.0f} -> {'VIABLE' if value > 0 else 'TRAPPED'}")
        
    # Analysis
    # Is there ANY viable strategy?
    viable_count = sum(1 for s in results["strategies"] if s["viable"])
    
    print(f"\nViable Strategies: {viable_count}/{len(speeds)}")
    
    # Validation
    # If Viable Count is 0 (or very low), Interstellar Trap confirmed.
    trap_confirmed = (viable_count == 0)
    
    results["validation"] = {
        "trap_confirmed": trap_confirmed
    }
    
    filepath = os.path.join(RESULTS_DIR, 'cycle2692_distance_budget.json')
    with open(filepath, 'w') as f:
        json.dump(results, f, indent=2)
        
    print(f"Results saved to {filepath}")

if __name__ == "__main__":
    run_distance_experiment()
