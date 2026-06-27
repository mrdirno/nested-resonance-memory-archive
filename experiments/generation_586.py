#!/usr/bin/env python3
"""
BCP Evolution: Generation 586 (The Holocron Genesis)
This script models Generation 586 of the BCP agent population under volatile environments.
It evaluates the evolutionary selection of "Temporal Memory Seeds" (The Holocron).
We compare:
1. Standard Hysteresis Lineage (Amnesiac, trapped by informational bottleneck at N=2 during recovery).
2. Holocron-Enabled Lineage (Saves structure during collapse, instantly re-complexifies to N=8 during recovery).
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
            return self.k / (self.epsilon + max(0.0001, self.budget))
        def evaluate(self, gain, cost):
            return gain - (self.lambda_val * cost)

class AdaptiveBCPAgent:
    def __init__(self, budget=100.0, k=1.0, epsilon_base=0.001, alpha_adapt=0.05, gamma_base=0.1, psi=2.0, complexity=1, budget_target=50.0):
        self.budget = budget
        self.k = k
        self.epsilon_base = epsilon_base
        self.alpha_adapt = alpha_adapt
        self.gamma_base = gamma_base
        self.psi = psi
        self.complexity = complexity
        self.budget_target = budget_target
        
        self.gamma_adapt = self.gamma_base * (float(self.complexity) ** self.psi)
        
        if self.budget < self.budget_target:
            self.epsilon = self.epsilon_base + self.alpha_adapt * (self.budget_target - self.budget)
            self.adaptation_cost = self.gamma_adapt * ((self.epsilon - self.epsilon_base) ** 2)
        else:
            self.epsilon = self.epsilon_base
            self.adaptation_cost = 0.0

    @property
    def lambda_val(self):
        return self.k / (self.epsilon + max(0.0001, self.budget))

    def evaluate(self, gain, cost, paid_cost=0.0):
        adjusted_cost = cost + self.adaptation_cost + paid_cost
        return gain - (self.lambda_val * adjusted_cost)

def evaluate_lineage(name, steps, initial_complexity, seed_cost=0.05, seed_trigger_B=5.0):
    random.seed(42)
    complexity = initial_complexity
    info_capacity_per_N = 10.0
    info_growth_rate = 2.5
    info = initial_complexity * info_capacity_per_N
    
    has_seed = False
    seed_template_N = 0
    
    base_gain = 50.0
    base_cost = 20.0
    coop_shielding_K = 1.5
    synergy_bonus = 0.1
    epsilon_base = 0.001
    alpha_adapt = 0.05
    gamma_base = 0.5
    psi = 2.0
    budget_target = 50.0
    
    total_cumulative_fitness = 0.0
    survival_steps = 0
    
    # Trace of the environment (Collapse -> Starvation -> Recovery)
    for t, b in enumerate(steps):
        paid_cost = 0.0
        
        # 1. Seed construction check for Holocron lineage
        if name == "holocron" and not has_seed and b <= seed_trigger_B and complexity > 2:
            has_seed = True
            seed_template_N = complexity
            paid_cost = seed_cost
            
        # 2. Seed retrieval check for Holocron lineage
        if name == "holocron" and has_seed and b > seed_trigger_B and t > len(steps)//2:
            info = max(info, seed_template_N * info_capacity_per_N)
            
        # 3. Determine optimal complexity under information limits
        best_v = -1e9
        best_n = 1
        
        # Candidate complexities up to 14
        for n in range(1, 15):
            if n * info_capacity_per_N <= info or n <= complexity:
                # Shielding calculations
                eff_cost = base_cost / (1.0 + coop_shielding_K * (n - 1))
                eff_gain = base_gain * (1.0 + synergy_bonus * (n - 1))
                
                # Simple average fitness evaluation
                temp_v = 0.0
                for i in range(n):
                    agent_b = b * random.uniform(0.8, 1.2)
                    agent = AdaptiveBCPAgent(
                        budget=agent_b,
                        k=1.0,
                        epsilon_base=epsilon_base,
                        alpha_adapt=alpha_adapt,
                        gamma_base=gamma_base,
                        psi=psi,
                        complexity=n,
                        budget_target=budget_target
                    )
                    temp_v += agent.evaluate(eff_gain, eff_cost, paid_cost=paid_cost)
                temp_v /= n
                
                if temp_v > best_v:
                    best_v = temp_v
                    best_n = n
                
        # Update Info State
        if best_n < complexity:
            info = min(info, best_n * info_capacity_per_N)
        else:
            info = min(info + info_growth_rate, best_n * info_capacity_per_N)
            
        complexity = best_n
        total_cumulative_fitness += best_v
        if best_v > 0:
            survival_steps += 1
            
    return {
        "cumulative_fitness": total_cumulative_fitness,
        "final_complexity": complexity,
        "survival_rate": survival_steps / len(steps),
        "info": info
    }

def run_generation():
    gen = 586
    
    # Environmental sequence (Volatility): Abundance (50) -> Collapse (0.001) -> Recovery (50)
    steps = [50.0, 20.0, 10.0, 5.0, 1.0, 0.1, 0.01, 0.001, 0.01, 0.1, 1.0, 5.0, 10.0, 20.0, 50.0]
    
    results = {
        "standard": evaluate_lineage("standard", steps, initial_complexity=8),
        "holocron": evaluate_lineage("holocron", steps, initial_complexity=8)
    }
    
    selected_name = "holocron" if results["holocron"]["cumulative_fitness"] > results["standard"]["cumulative_fitness"] else "standard"
    selected_data = results[selected_name]
    
    print(f"--- Natural Selection for Generation {gen} ---")
    print(f"Standard Hysteresis Lineage: Cum V={results['standard']['cumulative_fitness']:.2f} | Final N={results['standard']['final_complexity']} | Survival={results['standard']['survival_rate']*100:.1f}%")
    print(f"Holocron-Enabled Lineage:    Cum V={results['holocron']['cumulative_fitness']:.2f} | Final N={results['holocron']['final_complexity']} | Survival={results['holocron']['survival_rate']*100:.1f}%")
    print(f"Selected Lineage: {selected_name.upper()} (Final N={selected_data['final_complexity']})")
    
    result = {
        "generation": gen,
        "budget_avg": 50.0,
        "gain_base": 50.0,
        "cost_base": 20.0,
        "complexity": selected_data["final_complexity"],
        "value": selected_data["cumulative_fitness"] / len(steps), # Average fitness across volatile steps
        "survival_rate": selected_data["survival_rate"],
        "survived": selected_data["survival_rate"] > 0.5,
        "comparison": results,
        "params_used": {
            "budget_sequence": steps,
            "seed_cost": 0.05,
            "seed_trigger": 5.0,
            "selected_lineage": selected_name
        }
    }
    
    os.makedirs(os.path.join(os.path.dirname(__file__), '..', 'data', 'results'), exist_ok=True)
    result_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'results', f'gen_{gen}_fitness.json')
    with open(result_path, "w") as f:
        json.dump(result, f, indent=2)

    print(f"Gen {gen} (Complexity {selected_data['final_complexity']}): Selected Avg V={result['value']:.2f} Survival={result['survival_rate']*100:.1f}% -> {'SURVIVED' if result['survived'] else 'DIED'}")

if __name__ == "__main__":
    run_generation()
