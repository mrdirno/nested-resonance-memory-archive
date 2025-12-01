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

def run_mutation():
    gen = 2
    parent_fit = 150.0
    print(f"Running BCP Mutation Experiment (Gen {gen})...")
    
    # Evolution: Mutate parameters based on parent success?
    # For now, random drift.
    budget = random.uniform(10.0, 1000.0)
    agent = BCPAgent(budget=budget)
    
    gain = random.uniform(50.0, 200.0) + (gen * 10) # Evolution improves gain?
    cost = random.uniform(5.0, 50.0)
    
    print(f"Mutation: Budget={budget:.2f}, Gain={gain:.2f}, Cost={cost:.2f}")
    
    val = agent.evaluate(gain, cost)
    print(f"Value: {val:.2f}")
    
    result = {
        "generation": gen,
        "fitness": val,
        "survived": val > 0
    }
    
    # Persistence
    with open(f"data/results/gen_{gen}_fitness.json", "w") as f:
        json.dump(result, f)

    if val > 0:
        print("Mutation SURVIVED.")
    else:
        print("Mutation DIED.")

if __name__ == "__main__":
    run_mutation()