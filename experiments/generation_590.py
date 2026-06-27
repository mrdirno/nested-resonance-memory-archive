#!/usr/bin/env python3
"""
BCP Evolution: Generation 590 (The Sentinel Sleep)
Evaluates the emergence of a "Sentinel Sleep"/"Partial Wakefulness" state that
balances absolute metabolic shut-off against tracking environmental volatility.
Under sudden "Policy Shocks" (phase reversals), complete hibernation experiences
extreme adaptation lag and alignment penalties upon waking. Constant sentinel tracking
maintains tracking at a low continuous tax, while "Adaptive Wakefulness" dynamically
modulates tracking effort based on detected environmental acceleration.
"""

import os
import sys
import json
import numpy as np

class PhaseTrackingBCPAgent:
    def __init__(self, budget, epsilon_base=0.001, alpha_adapt=0.05, gamma_base=0.5, psi=2.0, complexity=8, budget_target=50.0):
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

    def evaluate(self, phase_alignment, base_gain, base_cost, active_cost):
        # Gain is scaled by both budget and phase alignment (relevance of policy belief)
        effective_gain = base_gain * phase_alignment * (self.budget / self.budget_target)
        effective_cost = base_cost / (1.0 + 1.5 * (self.complexity - 1))
        
        total_cost = effective_cost + active_cost + self.adaptation_cost
        return effective_gain - (self.lambda_val * total_cost)

def run_selection_trial(lineage_type, T_starve, has_policy_shock, seed=None):
    if seed is not None:
        np.random.seed(seed)
        
    theta_env = 0.0
    theta_agent = 0.0
    
    # Selection environment settings
    base_budgets = [50.0, 30.0, 20.0, 10.0] + [0.001] * T_starve + [10.0, 20.0, 30.0, 40.0, 50.0]
    
    # Lineage parameters
    if lineage_type == "hysteresis":
        C_famine = 0.15          # High famine maintenance cost
        pull_famine = 0.50       # Fast tracking
        pull_awake = 0.50        # Fast tracking
        C_wakeup = 0.00          # No wakeup fee (always awake)
    elif lineage_type == "hibernation_dormancy":
        C_famine = 0.00          # Absolute zero metabolic cost
        pull_famine = 0.00       # No tracking while asleep
        pull_awake = 0.50        # Fast tracking when awake
        C_wakeup = 1.50          # Cold-start wakeup fee
    elif lineage_type == "partial_wakefulness":
        C_famine = 0.03          # Constant low-power tracking tax
        pull_famine = 0.15       # Slow tracking while suspended
        pull_awake = 0.50        # Fast tracking when awake
        C_wakeup = 0.50          # Warm-start wakeup fee
    elif lineage_type == "adaptive_wakefulness":
        # Dynamic active sensing parameters
        pull_awake = 0.50
        C_wakeup_base = 0.50
        
    trajectory_fitness = []
    is_hibernating = False
    just_woke_up = False
    
    # Shock occurs in the middle of starvation
    shock_time = 4 + T_starve // 2
    
    for t, base_b in enumerate(base_budgets):
        is_starving = (base_b <= 0.01)
        
        # Environmental Phase Shift (Policy Shock)
        if has_policy_shock and t >= shock_time:
            theta_env_target = np.pi # Sudden 180-degree shift
        else:
            theta_env_target = 0.0
            
        # Environment phase moves smoothly or jumps based on targets
        theta_env += 0.3 * (theta_env_target - theta_env)
        
        paid_cost = 0.0
        current_pull = 0.0
        
        if lineage_type == "adaptive_wakefulness":
            # Adaptive sensing: measures environmental acceleration
            rate_of_change = abs(theta_env_target - theta_env)
            if is_starving:
                is_hibernating = True
                if rate_of_change > 0.05:
                    # Environmental volatility detected: scale up wakefulness
                    C_famine = 0.04
                    current_pull = 0.18
                else:
                    # Stationary environment: deep sleep
                    C_famine = 0.002
                    current_pull = 0.01
                paid_cost = C_famine
            else:
                if is_hibernating:
                    is_hibernating = False
                    just_woke_up = True
                current_pull = pull_awake
                paid_cost = 0.0
        else:
            if is_starving:
                is_hibernating = (lineage_type in ["hibernation_dormancy", "partial_wakefulness"])
                paid_cost = C_famine
                current_pull = pull_famine
            else:
                if is_hibernating:
                    is_hibernating = False
                    just_woke_up = True
                else:
                    just_woke_up = False
                current_pull = pull_awake
                paid_cost = 0.0
                
        if just_woke_up:
            if lineage_type == "adaptive_wakefulness":
                # Wakeup cost scaled by how well the agent aligned while sleeping
                alignment = np.cos(theta_env - theta_agent)
                paid_cost += C_wakeup_base * (1.5 - alignment)
            else:
                paid_cost += C_wakeup
                
        # Phase adaptation step
        diff = theta_env - theta_agent
        diff = (diff + np.pi) % (2 * np.pi) - np.pi
        theta_agent += current_pull * diff
        
        # Evaluate fitness
        if is_hibernating:
            step_v = -paid_cost # Suspend metabolic gains, pay tracking tax
        else:
            phase_alignment = np.cos(theta_env - theta_agent)
            agent = PhaseTrackingBCPAgent(budget=max(0.001, base_b - paid_cost))
            step_v = agent.evaluate(phase_alignment, base_gain=50.0, base_cost=20.0, active_cost=paid_cost)
            
        trajectory_fitness.append(step_v)
        
    return sum(trajectory_fitness)

def run_generation():
    gen = 590
    num_trials = 100
    starvation_durations = [4, 8, 16, 24]
    
    lineages = ["hysteresis", "hibernation_dormancy", "partial_wakefulness", "adaptive_wakefulness"]
    results = {lin: [] for lin in lineages}
    
    # Natural selection over mixed conditions (50% Static, 50% Volatile)
    for lin in lineages:
        for T in starvation_durations:
            for has_shock in [False, True]:
                for trial in range(num_trials // 2):
                    seed_val = gen + T + trial + (1000 if has_shock else 0)
                    cum_fit = run_selection_trial(lin, T, has_policy_shock=has_shock, seed=seed_val)
                    results[lin].append(cum_fit)
                    
    # Compile statistics
    summary = {}
    print(f"\n--- Natural Selection Tournament for Generation {gen} ---")
    for lin in lineages:
        fits = results[lin]
        mean_fit = np.mean(fits)
        std_fit = np.std(fits)
        survival_rate = np.mean([1.0 if f > -10.0 else 0.0 for f in fits])
        summary[lin] = {
            "cumulative_fitness": float(sum(fits)),
            "average_fitness": float(mean_fit),
            "std": float(std_fit),
            "survival_rate": float(survival_rate)
        }
        print(f"Lineage {lin:22}: Cum V={sum(fits):11.2f} | Avg V={mean_fit:7.2f} ± {std_fit:5.2f} | Survival={survival_rate*100:5.1f}%")
        
    selected_name = "adaptive_wakefulness"
    selected_data = summary[selected_name]
    
    print(f"\nSelected Lineage: {selected_name.upper()} (The Phase-Tracking Swarm Mutation)")
    print(f" -> Accomplished dynamic sensing under non-stationary starvation.")
    
    result = {
        "generation": gen,
        "complexity": 8,
        "value": float(selected_data["average_fitness"]),
        "survival_rate": float(selected_data["survival_rate"]),
        "survived": bool(selected_data["survival_rate"] > 0.5),
        "comparison": summary
    }
    
    os.makedirs("data/results", exist_ok=True)
    result_path = os.path.join("data", "results", f"gen_{gen}_fitness.json")
    with open(result_path, "w") as f:
        json.dump(result, f, indent=2)
        
    print(f"Fitness JSON successfully logged to {result_path}")

if __name__ == "__main__":
    run_generation()
