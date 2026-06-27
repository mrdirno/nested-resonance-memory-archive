#!/usr/bin/env python3
"""
BCP Evolution: Generation 585
This script models Generation 585 of the BCP agent population.
Under severe budget deprivation (budget dropping from 214.56 to 120.0) and the activation of
complexity-scaled autopoietic adaptation overhead (psi = 1.0), the parent complexity (N=6 from Gen 584)
undergoes metabolic strain. We evaluate if a mutated/adapted lineage of lower complexity (N=2)
emerges to survive the Thermodynamic Ceiling of Autopoietic Complexity (TCAC).
"""

import os
import sys
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
    def __init__(self, budget=100.0, k=1.0, epsilon_base=0.001, alpha_adapt=0.05, gamma_base=0.1, psi=1.0, complexity=1, budget_target=50.0):
        self.budget = budget
        self.k = k
        self.epsilon_base = epsilon_base
        self.alpha_adapt = alpha_adapt
        self.gamma_base = gamma_base
        self.psi = psi
        self.complexity = complexity
        self.budget_target = budget_target
        
        # Scale adaptation overhead with complexity
        self.gamma_adapt = self.gamma_base * (float(self.complexity) ** self.psi)
        
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
    gen = 585
    
    # Environment deprivation parameters (Resource tightening)
    budget = 120.0  # Dropped from 214.56 (Gen 584) to 120.0
    gain_base = 150.0
    cost_base = 35.0
    coop_shielding_K = 1.5
    scarcity_beta = 0.04
    
    # Epsilon adaptation parameters with linear complexity overhead (psi = 1.0)
    epsilon_base = 0.001
    alpha_adapt = 0.05
    gamma_base = 0.1
    psi = 1.0
    budget_target = 50.0
    
    # We compare two lineages:
    # 1. Parent Lineage (N=6): Continuing with the complexity of Gen 584
    # 2. Mutated/Adapted Lineage (N=2): Dynamically downscaling complexity to survive TCAC
    lineages = {
        "parent": 6,
        "adapted": 2
    }
    
    results_comparison = {}
    
    random.seed(42)
    
    for name, complexity in lineages.items():
        agents = []
        for i in range(complexity):
            # Heterogeneous budgets centered around 120.0
            b = budget * random.uniform(0.8, 1.2)
            agents.append(AdaptiveBCPAgent(
                budget=b,
                k=1.0,
                epsilon_base=epsilon_base,
                alpha_adapt=alpha_adapt,
                gamma_base=gamma_base,
                psi=psi,
                complexity=complexity,
                budget_target=budget_target
            ))
            
        total_value = 0.0
        survivors = 0
        
        # Evaluate with cooperative shielding and scarcity scaling
        effective_cost = cost_base / (1.0 + coop_shielding_K * (complexity - 1))
        effective_gain = gain_base / (1.0 + scarcity_beta * (complexity - 1))
        
        for agent in agents:
            val = agent.evaluate(effective_gain, effective_cost)
            total_value += val
            if val > 0:
                survivors += 1
                
        avg_value = total_value / complexity if complexity > 0 else 0
        survival_rate = survivors / complexity if complexity > 0 else 0
        
        results_comparison[name] = {
            "complexity": complexity,
            "avg_value": avg_value,
            "survival_rate": survival_rate,
            "survived": survival_rate > 0.5
        }
        
    # Natural selection: The lineage with higher average fitness survives and is recorded as the main result
    selected_name = "adapted" if results_comparison["adapted"]["avg_value"] > results_comparison["parent"]["avg_value"] else "parent"
    selected_data = results_comparison[selected_name]
    
    print(f"--- Natural Selection for Generation {gen} ---")
    print(f"Parent Lineage  (N={lineages['parent']}): Avg V={results_comparison['parent']['avg_value']:.2f} | Survival={results_comparison['parent']['survival_rate']*100:.1f}%")
    print(f"Adapted Lineage (N={lineages['adapted']}): Avg V={results_comparison['adapted']['avg_value']:.2f} | Survival={results_comparison['adapted']['survival_rate']*100:.1f}%")
    print(f"Selected Lineage: {selected_name.upper()} (N={selected_data['complexity']})\n")
    
    result = {
        "generation": gen,
        "budget_avg": budget,
        "gain_base": gain_base,
        "cost_base": cost_base,
        "coop_shielding_K": coop_shielding_K,
        "scarcity_beta": scarcity_beta,
        "complexity": selected_data["complexity"],
        "value": selected_data["avg_value"],
        "survival_rate": selected_data["survival_rate"],
        "survived": selected_data["survived"],
        "comparison": results_comparison,
        "params_used": {
            "budget_range": [budget * 0.8, budget * 1.2],
            "gain_range": [gain_base, gain_base],
            "cost_range": [cost_base, cost_base],
            "k": 1.0,
            "epsilon_base": epsilon_base,
            "alpha_adapt": alpha_adapt,
            "gamma_base": gamma_base,
            "psi": psi,
            "budget_target": budget_target,
            "coop_shielding_K": coop_shielding_K,
            "scarcity_beta": scarcity_beta,
            "complexity": selected_data["complexity"]
        }
    }
    
    os.makedirs(os.path.join(os.path.dirname(__file__), '..', 'data', 'results'), exist_ok=True)
    result_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'results', f'gen_{gen}_fitness.json')
    with open(result_path, "w") as f:
        json.dump(result, f, indent=2)

    print(f"Gen {gen} (Complexity {selected_data['complexity']}): Selected Avg V={selected_data['avg_value']:.2f} Survival={selected_data['survival_rate']*100:.1f}% -> {'SURVIVED' if selected_data['survived'] else 'DIED'}")

if __name__ == "__main__":
    run_generation()
