import json
import math
import sys
import os
import statistics

# Ensure valid import path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from core.bcp_core import BCPContext, BCPAgent, BCPResource
except ImportError:
    # Fallback if not running from standard path
    class BCPContext:
        pass
    class BCPAgent:
        pass
    class BCPResource:
        pass

# -----------------------------------------------------------------------------
# EXPERIMENT: THE EFFICIENCY PARADOX (JEVONS PARADOX IN AI)
# -----------------------------------------------------------------------------
# Hypothesis: Increasing Efficiency (E) leads to INCREASED Total Consumption (C)
# if Demand Elasticity > 1.
#
# Equation: V(task) = Gain(task) - λ * (BaseCost(task) / Efficiency)
#
# Scenarios:
# 1. Inelastic Demand (Fixed Task List) -> Efficiency saves Budget
# 2. Elastic Demand (Infinite Task Queue) -> Efficiency increases Consumption
# -----------------------------------------------------------------------------

RESULTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'results')
os.makedirs(RESULTS_DIR, exist_ok=True)

def run_efficiency_experiment():
    print("Running Cycle 2685: The Efficiency Paradox (Jevons in AI)...")
    
    # Parameters
    budget = 100.0
    lambda_val = 0.1 # Initial low pressure
    
    # Task Queue (Infinite potential utility)
    # Tasks have diminishing returns: Gain = 100 / (1 + index)
    # Tasks have constant base cost: Cost = 10.0
    
    efficiency_levels = [1.0, 2.0, 5.0, 10.0, 20.0, 50.0, 100.0]
    
    results = {
        "meta": {
            "cycle": 2685,
            "name": "The Efficiency Paradox",
            "phase": 252,
            "gate": 1162
        },
        "scenarios": []
    }
    
    # Scenario 1: Inelastic Demand (Fixed set of 5 critical tasks)
    print("\nScenario 1: Inelastic Demand (Fixed 5 Tasks)")
    s1_data = []
    fixed_tasks = 5
    base_cost = 10.0
    
    for eff in efficiency_levels:
        cost_per_task = base_cost / eff
        tasks_performed = fixed_tasks # Always do 5 if affordable
        total_cost = tasks_performed * cost_per_task
        
        # Check affordability
        if total_cost > budget:
            tasks_performed = math.floor(budget / cost_per_task)
            total_cost = tasks_performed * cost_per_task
            
        s1_data.append({
            "efficiency": eff,
            "cost_per_unit": cost_per_unit(base_cost, eff),
            "total_consumption": total_cost,
            "tasks_done": tasks_performed,
            "surplus": budget - total_cost
        })
    
    results["scenarios"].append({
        "name": "Inelastic Demand",
        "data": s1_data
    })

    # Scenario 2: Elastic Demand (Infinite potential tasks)
    # Agent will execute tasks as long as V > 0
    # V = (100 / (i+1)) - lambda * (10 / eff)
    # Assuming lambda stays constant for the decision (micro-view) or
    # more realistically, total consumption is limited by Budget, but we want to see
    # if they "spend it all" or "save it".
    
    print("\nScenario 2: Elastic Demand (The Jevons Paradox)")
    s2_data = []
    
    for eff in efficiency_levels:
        current_cost = base_cost / eff
        
        # Calculate how many tasks have V > 0
        # Gain(i) > lambda * Cost
        # 100 / (i+1) > 0.1 * current_cost
        # 100 / (0.1 * current_cost) > i + 1
        # max_i = (1000 / current_cost) - 1
        
        # Let's simulate the execution loop until budget exhausted or V < 0
        spent = 0.0
        tasks = 0
        
        for i in range(10000): # Arbitrary large limit
            gain = 100.0 / (i + 1)
            
            # Value decision
            value = gain - (lambda_val * current_cost)
            
            if value > 0:
                if spent + current_cost <= budget:
                    spent += current_cost
                    tasks += 1
                else:
                    break # Budget hard constraint
            else:
                break # Not worth it
        
        s2_data.append({
            "efficiency": eff,
            "cost_per_unit": current_cost,
            "total_consumption": spent,
            "tasks_done": tasks,
            "tasks_per_efficiency": tasks / eff
        })
        
    results["scenarios"].append({
        "name": "Elastic Demand",
        "data": s2_data
    })
    
    # Analysis
    print("\n--- Results Analysis ---")
    
    # Check Scenario 1 (Savings)
    s1_low = s1_data[0] # Eff=1
    s1_high = s1_data[-1] # Eff=100
    print(f"Inelastic: Eff {s1_low['efficiency']} -> Consumed {s1_low['total_consumption']}")
    print(f"Inelastic: Eff {s1_high['efficiency']} -> Consumed {s1_high['total_consumption']}")
    
    # Check Scenario 2 (Paradox)
    s2_low = s2_data[0]
    s2_high = s2_data[-1]
    print(f"Elastic: Eff {s2_low['efficiency']} -> Consumed {s2_low['total_consumption']}")
    print(f"Elastic: Eff {s2_high['efficiency']} -> Consumed {s2_high['total_consumption']}")
    print(f"Elastic Tasks: {s2_low['tasks_done']} -> {s2_high['tasks_done']}")
    
    # Validation Logic
    # Paradox is validated if Elastic Consumption stays High (near Budget) despite Efficiency increase
    # While Tasks Done increases massively.
    # Ideally, if demand was truly infinite and budget limited, consumption stays at 100% (Max Budget).
    # This confirms that Efficiency gains are fully absorbed by increased throughput.
    
    paradox_confirmed = s2_high['total_consumption'] > 90.0 # Still spending nearly full budget
    task_explosion = s2_high['tasks_done'] > (s2_low['tasks_done'] * 50) # 100x eff -> >50x tasks
    
    print(f"\nJevons Paradox Confirmed: {paradox_confirmed}")
    print(f"Task Explosion Confirmed: {task_explosion}")
    
    results["validation"] = {
        "paradox_confirmed": paradox_confirmed,
        "task_explosion": task_explosion
    }
    
    # Save Results
    filepath = os.path.join(RESULTS_DIR, 'cycle2685_efficiency_paradox.json')
    with open(filepath, 'w') as f:
        json.dump(results, f, indent=2)
        
    print(f"Results saved to {filepath}")

def cost_per_unit(base, eff):
    return base / eff

if __name__ == "__main__":
    run_efficiency_experiment()
