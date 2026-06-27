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
    gen = 583
    complexity = 5 # Evolved complexity from 3 in Gen 582 to 5
    
    # Mutated parameters from Gen 582
    budget = random.uniform(50.0, 500.0)  # Evolved budget range (tighter bound)
    gain_base = random.uniform(100.0, 250.0)  # Evolved base gain
    cost_base = random.uniform(20.0, 60.0)   # Evolved base cost
    coop_shielding_K = 1.5                    # Stabilized shielding
    scarcity_beta = 0.05                      # Newly introduced carrying capacity constraint
    
    agents = []
    for i in range(complexity):
        b = budget * random.uniform(0.8, 1.2)
        agents.append(BCPAgent(budget=b, k=1.0, epsilon=0.1))
    
    total_value = 0.0
    survivors = 0
    
    # Evaluate with BOTH cooperative shielding AND scarcity division
    effective_cost = cost_base / (1.0 + coop_shielding_K * (complexity - 1))
    effective_gain = gain_base / (1.0 + scarcity_beta * (complexity - 1))
    
    for agent in agents:
        val = agent.evaluate(effective_gain, effective_cost)
        total_value += val
        if val > 0:
            survivors += 1
            
    avg_value = total_value / complexity if complexity > 0 else 0
    survival_rate = survivors / complexity if complexity > 0 else 0
    
    result = {
        "generation": gen,
        "budget_avg": budget,
        "gain_base": gain_base,
        "cost_base": cost_base,
        "coop_shielding_K": coop_shielding_K,
        "scarcity_beta": scarcity_beta,
        "complexity": complexity,
        "value": avg_value,
        "survival_rate": survival_rate,
        "survived": survival_rate > 0.5,
        "params_used": {
            "budget_range": [50.0, 500.0],
            "gain_range": [100.0, 250.0],
            "cost_range": [20.0, 60.0],
            "k": 1.0,
            "epsilon": 0.1,
            "coop_shielding_K": coop_shielding_K,
            "scarcity_beta": scarcity_beta,
            "complexity": complexity
        }
    }
    
    os.makedirs(os.path.join(os.path.dirname(__file__), '..', 'data', 'results'), exist_ok=True)
    result_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'results', f'gen_{gen}_fitness.json')
    with open(result_path, "w") as f:
        json.dump(result, f, indent=2)

    print(f"Gen {gen} (Complexity {complexity}): Avg V={avg_value:.2f} Survival={survival_rate*100:.1f}% -> {'SURVIVED' if survival_rate > 0.5 else 'DIED'}")

if __name__ == "__main__":
    run_generation()
