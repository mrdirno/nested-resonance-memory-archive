import json
import math
import sys
import os

# Ensure valid import path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

# -----------------------------------------------------------------------------
# EXPERIMENT: THE LANDAUER LIMIT (THERMAL BUDGET)
# -----------------------------------------------------------------------------
# Hypothesis: Heat Dissipation becomes the dominant Lambda (constraint) even if
# Energy is abundant. Intelligence is throttled by Physics.
#
# Equation: V(op) = Gain - λ(Temperature) * HeatCost
#
# Dynamics:
# - Computation generates Heat.
# - Cooling reduces Heat (at a fixed rate).
# - If Temp > Max, System Dies.
# - λ increases as Temp approaches Max.
# -----------------------------------------------------------------------------

RESULTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'results')
os.makedirs(RESULTS_DIR, exist_ok=True)

def run_landauer_experiment():
    print("Running Cycle 2686: The Landauer Limit (Thermal Budget)...")
    
    # Parameters
    max_temp = 100.0
    cooling_rate = 10.0 # Joules/sec dissipation capacity
    
    # Energy is infinite (we assume we have a nuclear reactor)
    # But Heat is the constraint.
    
    results = {
        "meta": {
            "cycle": 2686,
            "name": "The Landauer Limit",
            "phase": 252,
            "gate": 1163
        },
        "trace": []
    }
    
    current_temp = 20.0 # Ambient
    
    # Workload: Infinite queue of tasks
    # Each task: Gain=50, HeatGenerated=5.0
    task_gain = 50.0
    task_heat = 5.0
    
    epsilon = 1.0
    k = 10.0 # Sensitivity of Lambda to Heat Pressure
    
    print("\nStarting Thermal Simulation...")
    print(f"Max Temp: {max_temp}, Cooling: {cooling_rate}")
    
    for t in range(50): # 50 time steps
        # 1. Calculate Lambda based on Thermal Headroom
        # Budget = Headroom = Max_Temp - Current_Temp
        headroom = max_temp - current_temp
        if headroom <= 0:
            lambda_val = 1000.0 # Crisis
        else:
            lambda_val = k / (epsilon + headroom)
            
        # 2. Decide how many ops to run in this step
        # We assume we can run N ops.
        # V(n) = n*Gain - lambda * n*Heat
        # Marginal V > 0 condition: Gain > lambda * Heat
        # Threshold Lambda = Gain / Heat = 50 / 5 = 10.0
        
        max_possible_ops = 10 # Hardware limit per step
        ops_performed = 0
        
        marginal_value = task_gain - (lambda_val * task_heat)
        
        if marginal_value > 0:
            # It's profitable! Run max ops.
            ops_performed = max_possible_ops
        else:
            # Too hot! Throttle.
            ops_performed = 0
            
        # 3. Physics Update
        heat_in = ops_performed * task_heat
        current_temp += heat_in
        current_temp -= cooling_rate
        
        # Clamp to ambient
        if current_temp < 20.0:
            current_temp = 20.0
            
        results["trace"].append({
            "time": t,
            "temp": round(current_temp, 2),
            "headroom": round(headroom, 2),
            "lambda": round(lambda_val, 4),
            "ops": ops_performed,
            "heat_in": heat_in,
            "cooling": cooling_rate
        })
        
        status = "RUNNING" if ops_performed > 0 else "THROTTLED"
        print(f"T={t}: Temp={current_temp:.1f} λ={lambda_val:.2f} Ops={ops_performed} [{status}]")
        
    # Analysis
    # Did it oscillate? Did it avoid melting?
    # The equilibrium should be where Cooling = Heat_In
    # Max Sustained Ops = Cooling / Heat_In_Per_Op = 10 / 5 = 2 ops/step
    # But our policy is binary (All or Nothing) based on BCP.
    # So it should oscillate (Thermal Throttling).
    
    trace = results["trace"]
    final_temp = trace[-1]["temp"]
    melted = any(step["temp"] > max_temp for step in trace)
    throttled_count = sum(1 for step in trace if step["ops"] == 0)
    
    print("\n--- Analysis ---")
    print(f"Meltdown Occurred: {melted}")
    print(f"Throttled Steps: {throttled_count}/50")
    print(f"Final Temp: {final_temp}")
    
    # Validation: BCP prevented meltdown by raising lambda
    # If melted is False and we processed ops, success.
    success = (not melted) and (throttled_count > 0)
    
    print(f"BCP Throttling Validated: {success}")
    
    results["validation"] = {
        "success": success,
        "melted": melted
    }
    
    filepath = os.path.join(RESULTS_DIR, 'cycle2686_landauer_limit.json')
    with open(filepath, 'w') as f:
        json.dump(results, f, indent=2)
        
    print(f"Results saved to {filepath}")

if __name__ == "__main__":
    run_landauer_experiment()
