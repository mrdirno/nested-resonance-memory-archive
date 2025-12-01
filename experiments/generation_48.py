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
    gen = 48
    
    # Mutated parameters from previous generation or initial
    budget = random.uniform(592.1265855232292, 888.1898782848438)
    gain = random.uniform(95.30039438546554, 116.47825980445788)
    cost = random.uniform(37.37213233979884, 45.67705063753191)
    
    agent = BCPAgent(budget=budget, k=1.0, epsilon=0.1)
    
    val = agent.evaluate(gain, cost)
    
    result = {
        "generation": gen,
        "budget": budget,
        "gain": gain,
        "cost": cost,
        "lambda_val": agent.lambda_val,
        "value": val,
        "survived": val > 0,
        "params_used": {"budget_range": [592.1265855232292, 888.1898782848438], "gain_range": [95.30039438546554, 116.47825980445788], "cost_range": [37.37213233979884, 45.67705063753191], "k": 1.0, "epsilon": 0.1}
    }
    
    result_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'results', f'gen_{gen}_fitness.json')
    with open(result_path, "w") as f:
        json.dump(result, f, indent=2)

    print(f"Gen {gen}: B={budget:.2f} G={gain:.2f} C={cost:.2f} λ={agent.lambda_val:.2f} V={val:.2f} -> {'SURVIVED' if val > 0 else 'DIED'}")

if __name__ == "__main__":
    run_generation()