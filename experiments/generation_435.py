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
    gen = 435
    complexity = 2
    
    # Mutated parameters from previous generation or initial
    budget = random.uniform(4175.648943197112, 6263.473414795669)
    gain_base = random.uniform(891.9906604250242, 1000.0)
    cost_base = random.uniform(44.983741541046975, 54.98012855016853)
    
    # Simulation: Multiple Agents interacting
    # Complexity = Number of Agents
    agents = []
    for i in range(complexity):
        # Heterogeneity: Each agent has slightly different budget
        b = budget * random.uniform(0.8, 1.2)
        agents.append(BCPAgent(budget=b, k=3.3136398384246877, epsilon=0.47667923498748715))
    
    total_value = 0.0
    survivors = 0
    
    for agent in agents:
        # Task: Perform Action
        val = agent.evaluate(gain_base, cost_base)
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
        "complexity": complexity,
        "value": avg_value,
        "survival_rate": survival_rate,
        "survived": survival_rate > 0.5, # Survival if >50% agents thrive
        "params_used": {"budget_range": [4175.648943197112, 6263.473414795669], "gain_range": [891.9906604250242, 1000.0], "cost_range": [44.983741541046975, 54.98012855016853], "k": 3.3136398384246877, "epsilon": 0.47667923498748715, "complexity": 2}
    }
    
    result_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'results', f'gen_{gen}_fitness.json')
    with open(result_path, "w") as f:
        json.dump(result, f, indent=2)

    print(f"Gen {gen} (Complexity {complexity}): Avg V={avg_value:.2f} Survival={survival_rate*100:.1f}% -> {'SURVIVED' if survival_rate > 0.5 else 'DIED'}")

if __name__ == "__main__":
    run_generation()