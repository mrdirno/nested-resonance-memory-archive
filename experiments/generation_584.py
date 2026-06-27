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

class AdaptiveBCPAgent:
    def __init__(self, budget=100.0, k=1.0, epsilon_base=0.001, alpha_adapt=0.05, gamma_adapt=0.1, budget_target=50.0):
        self.budget = budget
        self.k = k
        self.epsilon_base = epsilon_base
        self.alpha_adapt = alpha_adapt
        self.gamma_adapt = gamma_adapt
        self.budget_target = budget_target
        
        # Determine adapted epsilon and adaptation cost
        if self.budget < self.budget_target:
            self.epsilon = self.epsilon_base + self.alpha_adapt * (self.budget_target - self.budget)
            self.adaptation_cost = self.gamma_adapt * ((self.epsilon - self.epsilon_base) ** 2)
        else:
            self.epsilon = self.epsilon_base
            self.adaptation_cost = 0.0

    @property
    def lambda_val(self):
        return self.k / (self.epsilon + max(0.0, self.budget))

    def evaluate(self, gain, cost):
        # The adaptation cost is added as a second-order resource penalty to the metabolic cost
        total_cost = cost + self.adaptation_cost
        return gain - (self.lambda_val * total_cost)

def run_generation():
    gen = 584
    complexity = 6  # Evolved complexity from 5 in Gen 583 to 6
    
    # Mutated parameters from Gen 583 representing resource tightening
    budget = random.uniform(40.0, 450.0)  
    gain_base = random.uniform(110.0, 260.0)  
    cost_base = random.uniform(22.0, 62.0)   
    coop_shielding_K = 1.5                    
    scarcity_beta = 0.05                      
    
    # Epsilon adaptation parameters
    epsilon_base = 0.001
    alpha_adapt = 0.05
    gamma_adapt = 0.1
    budget_target = 50.0
    
    agents = []
    for i in range(complexity):
        b = budget * random.uniform(0.8, 1.2)
        agents.append(AdaptiveBCPAgent(
            budget=b, 
            k=1.0, 
            epsilon_base=epsilon_base,
            alpha_adapt=alpha_adapt,
            gamma_adapt=gamma_adapt,
            budget_target=budget_target
        ))
    
    total_value = 0.0
    survivors = 0
    
    # Evaluate with cooperative shielding, scarcity, and autopoietic adaptation
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
            "budget_range": [40.0, 450.0],
            "gain_range": [110.0, 260.0],
            "cost_range": [22.0, 62.0],
            "k": 1.0,
            "epsilon_base": epsilon_base,
            "alpha_adapt": alpha_adapt,
            "gamma_adapt": gamma_adapt,
            "budget_target": budget_target,
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
