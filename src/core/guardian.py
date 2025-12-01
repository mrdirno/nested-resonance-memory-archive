import os
import sys
import json
import time
import math
import random
import subprocess
import statistics

# Ensure valid import path for internal modules. This allows dynamic loading
# when generated experiment code runs.
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..')) # Add root for bootstrap
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))      # Add src for core
sys.path.append(os.path.join(os.path.dirname(__file__)))           # Add core

from monitor import BCPMonitor
# from agent import BCPAgent # Not directly imported here, but by generated code

class BCPGuardian:
    def __init__(self, start_generation=1, max_generations=10):
        self.monitor = BCPMonitor()
        self.current_generation = start_generation
        self.max_generations = max_generations
        self.last_params = None
        
        print("\n--- BCP Guardian Activated ---")

    def generate_experiment_code(self, generation, params=None):
        # Base parameters for the first generation
        if params is None:
            params = {
                "budget_range": [10.0, 1000.0],
                "gain_range": [50.0, 200.0],
                "cost_range": [5.0, 50.0],
                "k": 1.0,
                "epsilon": 0.1
            }

        return f"""
import sys
import os
import random
import json

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
try:
    from core.agent import BCPAgent
except ImportError:
    class BCPAgent:
        def __init__(self, budget=100.0, k=1.0, epsilon=0.1):
            self.budget = budget
            self.k = k
            self.epsilon = epsilon
        @property
        def lambda_val(self):
            return self.k / (self.epsilon + max(0.0, self.budget))
        def evaluate(self, gain, cost):
            return gain - (self.lambda_val * cost)

def run_generation():
    gen = {generation}
    
    # Mutated parameters from previous generation or initial
    budget = random.uniform({params["budget_range"][0]}, {params["budget_range"][1]})
    gain = random.uniform({params["gain_range"][0]}, {params["gain_range"][1]})
    cost = random.uniform({params["cost_range"][0]}, {params["cost_range"][1]})
    
    agent = BCPAgent(budget=budget, k={params["k"]}, epsilon={params["epsilon"]})
    
    val = agent.evaluate(gain, cost)
    
    result = {{
        "generation": gen,
        "budget": budget,
        "gain": gain,
        "cost": cost,
        "lambda_val": agent.lambda_val,
        "value": val,
        "survived": val > 0,
        "params_used": {json.dumps(params)}
    }}
    
    result_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'results', f'gen_{{gen}}_fitness.json')
    with open(result_path, "w") as f:
        json.dump(result, f, indent=2)

    print(f"Gen {{gen}}: B={{budget:.2f}} G={{gain:.2f}} C={{cost:.2f}} \u03BB={{agent.lambda_val:.2f}} V={{val:.2f}} -> {{'SURVIVED' if val > 0 else 'DIED'}}")

if __name__ == "__main__":
    run_generation()
"""
    def write_file(self, path, content):
        with open(path, 'w') as f:
            f.write(content.strip())

    def run_infinite_loop(self):
        print(f"\n🚀 Initiating Infinite Loop: Generation {self.current_generation} to {self.max_generations}")
        
        while self.current_generation <= self.max_generations:
            print(f"\n--- Running Generation {self.current_generation} ---")
            
            # 1. Generate Experiment Code
            exp_filename = os.path.join("experiments", f"generation_{self.current_generation}.py")
            exp_code = self.generate_experiment_code(self.current_generation, self.last_params)
            self.write_file(exp_filename, exp_code)
            
            # 2. Execute Experiment
            try:
                result = subprocess.run(
                    ["python3", exp_filename],
                    capture_output=True, text=True, check=True
                )
                print(result.stdout.strip())
                
                # 3. Read Fitness
                result_path = os.path.join("data", "results", f"gen_{self.current_generation}_fitness.json")
                with open(result_path, 'r') as f:
                    fitness_data = json.load(f)
                
                self.monitor.record_generation(fitness_data) # Record for monitoring
                
                fitness = fitness_data.get("value", 0.0)
                
                # 4. Check Stagnation (Cambrian Explosion)
                stagnant = False
                if self.monitor.total_generations >= 3:
                    if self.monitor.get_stats()["stagnation_variance"] < 5.0:
                        stagnant = True
                        print(f"⚠️ Stagnation Detected (Variance {self.monitor.get_stats()['stagnation_variance']:.2f}). Triggering CAMBRIAN EXPLOSION.")
                
                # 5. Update Parameters
                if stagnant:
                    self.last_params = {
                        "budget_range": [1.0, 10000.0], 
                        "gain_range": [10.0, 1000.0],   
                        "cost_range": [1.0, 100.0],
                        "k": random.uniform(0.1, 10.0),
                        "epsilon": random.uniform(0.01, 1.0)
                    }
                elif fitness_data["survived"]:
                    print(f"Gen {self.current_generation} SURVIVED. Refining parameters.")
                    self.last_params = {
                        "budget_range": [max(10.0, fitness_data["budget"] * 0.8), min(10000.0, fitness_data["budget"] * 1.2)], 
                        "gain_range": [max(10.0, fitness_data["gain"] * 0.9), min(1000.0, fitness_data["gain"] * 1.1)], 
                        "cost_range": [max(1.0, fitness_data["cost"] * 0.9), min(100.0, fitness_data["cost"] * 1.1)], 
                        "k": fitness_data["params_used"].get("k", 1.0),
                        "epsilon": fitness_data["params_used"].get("epsilon", 0.1)
                    }
                else:
                    print(f"Gen {self.current_generation} DIED. Backtracking.")
                    self.last_params = None
                
            except subprocess.CalledProcessError as e:
                print(f"Error running generation {self.current_generation}: {e.stderr}")
                self.last_params = None
                
            self.current_generation += 1
            time.sleep(0.1)

            # Guardian Report
            if self.current_generation % 5 == 0: # Report every 5 generations
                print(self.monitor.report_status(5))