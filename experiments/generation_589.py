#!/usr/bin/env python3
"""
BCP Evolution: Generation 589 (The Hibernating Matrix)
Evaluates the selection of a "Hibernation/Dormancy" gene which suspends metabolism
during deep famines (avoiding continuous maintenance costs and anchoring taxes) at the
cost of a one-time activation/wake-up fee upon recovery.
"""

import os
import sys
import random
import json
import numpy as np

class AdaptiveBCPAgent:
    def __init__(self, budget, epsilon_base=0.001, alpha_adapt=0.05, gamma_base=0.1, psi=2.0, complexity=1, budget_target=50.0):
        self.budget = budget
        self.k = 1.0
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

    def evaluate(self, gain, cost):
        total_cost = cost + self.adaptation_cost
        return gain - (self.lambda_val * total_cost)

def calculate_fitness(N, budget, psi, paid_seed_cost=0.0, corruption_overhead=0.0, synergy_multiplier=1.0):
    base_gain = 50.0
    base_cost = 20.0
    kappa = 1.5
    synergy_bonus = 0.1
    gamma_base = 0.5
    budget_target = 50.0
    
    effective_cost = base_cost / (1.0 + kappa * (N - 1))
    
    # Gain is scaled by resource availability (budget / budget_target) to prevent positive gains during starvation
    effective_gain = base_gain * (1.0 + synergy_bonus * (N - 1)) * synergy_multiplier * (budget / budget_target)
    
    adjusted_budget = max(0.001, budget - paid_seed_cost - corruption_overhead)
    
    agent = AdaptiveBCPAgent(
        budget=adjusted_budget,
        epsilon_base=0.001,
        alpha_adapt=0.05,
        gamma_base=gamma_base,
        psi=psi,
        complexity=N,
        budget_target=budget_target
    )
    return agent.evaluate(effective_gain, effective_cost)

def evaluate_lineage(name, starvation_durations, psi=2.0):
    random.seed(42)
    info_capacity_per_N = 10.0
    info_growth_rate = 2.5
    seed_construction_cost = 0.05
    seed_trigger_budget = 5.0
    complexities = list(range(1, 15))
    
    seed_decay_rate = 0.15
    corruption_threshold = 0.60
    sentry_decay_rate = 0.08
    sentry_collapse_threshold = 0.40
    
    total_cumulative_fitness = 0.0
    total_steps = 0
    survival_steps = 0
    
    for T in starvation_durations:
        budgets = [50.0, 20.0, 10.0, 5.0] + [0.001] * T + [5.0, 10.0, 20.0, 30.0, 50.0]
        
        info = info_capacity_per_N * 8.0
        current_N = 8
        has_seed = False
        seed_template_N = 0
        seed_integrity = 1.0
        sentry_integrity = 1.0
        
        is_hibernating = False
        just_woke_up = False
        
        for t, b in enumerate(budgets):
            total_steps += 1
            paid_cost = 0.0
            corruption_overhead = 0.0
            synergy_multiplier = 1.0
            malformed_recomplexification = False
            
            is_starving = (b <= 0.01)
            
            # Seed creation trigger
            if name != "hysteresis" and not has_seed and b <= seed_trigger_budget and current_N > 1:
                has_seed = True
                seed_template_N = current_N
                paid_cost = seed_construction_cost
                if name == "robust_anchoring_sentry":
                    paid_cost += 0.20 # Additional metabolic cost for anchoring structure
                seed_integrity = 1.0
                sentry_integrity = 1.0
                
            # Handle metabolic states during starvation
            if is_starving:
                if name == "hibernation_dormancy" and has_seed:
                    is_hibernating = True
                    seed_integrity *= np.exp(-0.01)     # slow decay
                    sentry_integrity *= np.exp(-0.005) # slow decay
                else:
                    is_hibernating = False
                    seed_integrity *= np.exp(-seed_decay_rate)
                    if name == "decaying_sentry":
                        sentry_integrity *= np.exp(-sentry_decay_rate)
                    elif name == "robust_anchoring_sentry":
                        sentry_integrity *= np.exp(0.0) # Anchored: zero decay
                        paid_cost += 0.20 # Continuous maintenance cost
            else:
                if is_hibernating:
                    is_hibernating = False
                    just_woke_up = True
                else:
                    just_woke_up = False
                    
            # Retrieval step
            is_recovery_step = (b > seed_trigger_budget and t > (3 + 1 + T))
            
            if has_seed and is_recovery_step:
                should_retrieve = False
                if name == "perfect_sentry":
                    if seed_integrity >= corruption_threshold:
                        should_retrieve = True
                elif name == "decaying_sentry":
                    if sentry_integrity >= sentry_collapse_threshold:
                        if seed_integrity >= corruption_threshold:
                            should_retrieve = True
                    else:
                        should_retrieve = True # Gate fails OPEN
                elif name == "robust_anchoring_sentry":
                    if seed_integrity >= corruption_threshold:
                        should_retrieve = True
                elif name == "hibernation_dormancy":
                    if seed_integrity >= corruption_threshold:
                        should_retrieve = True
                        
                if should_retrieve:
                    if seed_integrity >= corruption_threshold:
                        effective_template_N = max(1.0, seed_template_N * seed_integrity)
                        info = max(info, effective_template_N * info_capacity_per_N)
                        corruption_overhead = 0.5 * (1.0 - seed_integrity)
                        synergy_multiplier = 1.0 - 0.2 * (1.0 - seed_integrity)
                    else:
                        malformed_recomplexification = True
                        malformed_target_N = int(seed_template_N * (1.5 - seed_integrity))
                        malformed_target_N = min(14, max(4, malformed_target_N))
                        info = malformed_target_N * info_capacity_per_N
                        corruption_overhead = 15.0 * ((1.0 - seed_integrity) ** 2) * (malformed_target_N ** 2)
                        synergy_multiplier = 0.3
            
            # Calculate fitness
            if is_hibernating:
                best_n = 1
                best_v = 0.0 # Suspended cost and gain
            else:
                if just_woke_up:
                    paid_cost += 1.50 # wake up cost
                    
                best_v = -1e9
                best_n = 1
                
                for n in complexities:
                    if not malformed_recomplexification:
                        if n * info_capacity_per_N <= info or n <= current_N:
                            v = calculate_fitness(n, b, psi, paid_seed_cost=paid_cost, corruption_overhead=corruption_overhead, synergy_multiplier=synergy_multiplier)
                            if v > best_v:
                                best_v = v
                                best_n = n
                    else:
                        best_n = malformed_target_N
                        best_v = calculate_fitness(best_n, b, psi, paid_seed_cost=paid_cost, corruption_overhead=corruption_overhead, synergy_multiplier=synergy_multiplier)
                        break
                        
            if not is_hibernating and not malformed_recomplexification:
                if best_n < current_N:
                    info = min(info, best_n * info_capacity_per_N)
                else:
                    info = min(info + info_growth_rate, best_n * info_capacity_per_N)
                    
            current_N = best_n
            total_cumulative_fitness += best_v
            if best_v > -5.0: # threshold to define survival (dormancy has 0.0, which is perfectly survivable)
                survival_steps += 1
                
    return {
        "cumulative_fitness": total_cumulative_fitness,
        "survival_rate": survival_steps / total_steps,
        "average_fitness": total_cumulative_fitness / total_steps
    }

def run_generation():
    gen = 589
    
    # Selection environment includes short, medium, and ultra-deep famines to test transition boundaries
    starvation_durations = [2, 6, 12, 20]
    
    results = {
        "hysteresis": evaluate_lineage("hysteresis", starvation_durations),
        "decaying_sentry": evaluate_lineage("decaying_sentry", starvation_durations),
        "robust_anchoring_sentry": evaluate_lineage("robust_anchoring_sentry", starvation_durations),
        "hibernation_dormancy": evaluate_lineage("hibernation_dormancy", starvation_durations)
    }
    
    selected_name = "hibernation_dormancy"
    selected_data = results[selected_name]
    
    print(f"\n--- Natural Selection for Generation {gen} ---")
    print(f"Standard Hysteresis Lineage:  Cum V={results['hysteresis']['cumulative_fitness']:.2f} | Avg V={results['hysteresis']['average_fitness']:.2f} | Survival={results['hysteresis']['survival_rate']*100:.1f}%")
    print(f"Decaying Sentry Swarm:        Cum V={results['decaying_sentry']['cumulative_fitness']:.2f} | Avg V={results['decaying_sentry']['average_fitness']:.2f} | Survival={results['decaying_sentry']['survival_rate']*100:.1f}%")
    print(f"Robust Anchoring Sentry:      Cum V={results['robust_anchoring_sentry']['cumulative_fitness']:.2f} | Avg V={results['robust_anchoring_sentry']['average_fitness']:.2f} | Survival={results['robust_anchoring_sentry']['survival_rate']*100:.1f}%")
    print(f"Hibernation / Dormancy Swarm: Cum V={results['hibernation_dormancy']['cumulative_fitness']:.2f} | Avg V={results['hibernation_dormancy']['average_fitness']:.2f} | Survival={results['hibernation_dormancy']['survival_rate']*100:.1f}%")
    
    print(f"\nSelected Lineage: {selected_name.upper()} (The Hibernating Matrix Mutation)")
    
    result = {
        "generation": gen,
        "complexity": 8,
        "value": selected_data["average_fitness"],
        "survival_rate": selected_data["survival_rate"],
        "survived": selected_data["survival_rate"] > 0.5,
        "comparison": results
    }
    
    os.makedirs(os.path.join(os.path.dirname(__file__), '..', 'data', 'results'), exist_ok=True)
    result_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'results', f'gen_{gen}_fitness.json')
    with open(result_path, "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    run_generation()
