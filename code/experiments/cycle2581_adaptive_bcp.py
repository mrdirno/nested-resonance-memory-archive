#!/usr/bin/env python3
"""
Cycle 2581: Adaptive BCP - Learning Gain/Cost Estimates
=========================================================

Phase 74, Gate 211: What happens when agents must learn item parameters?

Research Questions:
1. How quickly do agents converge to true gain/cost values?
2. Does learning strategy affect phase transition timing?
3. Can adaptive BCP outperform oracle BCP under noisy observations?

Key Innovation:
- Agents start with uncertain estimates of gain/cost
- They update estimates through Bayesian learning
- Exploration-exploitation tradeoff emerges naturally

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
License: GPL-3.0
"""

import numpy as np
import json
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
from datetime import datetime
import sys
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2/bcp_lib')

from bcp import BCPModel, AttentionItem


@dataclass
class LearnableItem:
    """An item with unknown true parameters that must be learned."""
    name: str
    true_gain: float          # Hidden ground truth
    true_cost: float          # Hidden ground truth
    estimated_gain: float     # Agent's current estimate
    estimated_cost: float     # Agent's current estimate
    gain_variance: float = 1.0   # Uncertainty in gain estimate
    cost_variance: float = 1.0   # Uncertainty in cost estimate
    observations: int = 0        # Number of times attended

    def observe(self, noise_std: float = 0.1) -> Tuple[float, float]:
        """Observe noisy outcome when attended."""
        observed_gain = self.true_gain + np.random.normal(0, noise_std)
        observed_cost = self.true_cost + np.random.normal(0, noise_std * 0.5)
        return max(0, observed_gain), max(0.01, observed_cost)

    def update_estimates(self, observed_gain: float, observed_cost: float,
                        learning_rate: float = 0.1):
        """Bayesian-style update of estimates."""
        self.observations += 1
        
        # Running mean update (equivalent to Bayesian with known variance)
        alpha = learning_rate / np.sqrt(self.observations)
        self.estimated_gain += alpha * (observed_gain - self.estimated_gain)
        self.estimated_cost += alpha * (observed_cost - self.estimated_cost)
        
        # Reduce uncertainty with more observations
        self.gain_variance = 1.0 / (1.0 + 0.1 * self.observations)
        self.cost_variance = 1.0 / (1.0 + 0.1 * self.observations)

    def to_attention_item(self) -> AttentionItem:
        """Convert to AttentionItem using current estimates."""
        return AttentionItem(self.name, self.estimated_gain, self.estimated_cost)

    @property
    def estimation_error(self) -> float:
        """Current error in estimates vs true values."""
        gain_error = abs(self.estimated_gain - self.true_gain)
        cost_error = abs(self.estimated_cost - self.true_cost)
        return (gain_error + cost_error) / 2


class AdaptiveBCPAgent:
    """BCP agent that learns item parameters through experience."""

    def __init__(self, n_items: int = 5, exploration_bonus: float = 0.0):
        self.model = BCPModel(lambda_scale=5.0, abundance_threshold=3.0, crisis_threshold=0.8)
        self.items = self._generate_items(n_items)
        self.exploration_bonus = exploration_bonus
        self.history = []

    def _generate_items(self, n: int) -> List[LearnableItem]:
        """Generate items with hidden true parameters."""
        items = []
        for i in range(n):
            true_gain = np.random.uniform(0.4, 1.0)
            true_cost = np.random.uniform(0.05, 0.3)
            # Initial estimates are uninformed priors
            items.append(LearnableItem(
                name=f"item_{i}",
                true_gain=true_gain,
                true_cost=true_cost,
                estimated_gain=0.5,   # Neutral prior
                estimated_cost=0.15   # Neutral prior
            ))
        return items

    def step(self, budget: float) -> Dict:
        """Execute one step of adaptive allocation."""
        # Convert items to AttentionItems using current estimates
        attention_items = []
        for item in self.items:
            ai = item.to_attention_item()
            # Add exploration bonus for uncertain items
            if self.exploration_bonus > 0:
                uncertainty_bonus = self.exploration_bonus * (item.gain_variance + item.cost_variance) / 2
                ai.gain += uncertainty_bonus
            attention_items.append(ai)

        # Allocate attention using BCP
        result = self.model.allocate(attention_items, budget)

        # Update estimates for attended items
        for item in self.items:
            if item.name in result.attended:
                obs_gain, obs_cost = item.observe()
                item.update_estimates(obs_gain, obs_cost)

        # Compute metrics
        mean_error = np.mean([item.estimation_error for item in self.items])
        attended_error = np.mean([
            item.estimation_error for item in self.items
            if item.name in result.attended
        ]) if result.attended else 0

        record = {
            "step": len(self.history),
            "budget": budget,
            "phase": result.phase.value,
            "n_attended": result.n_attended,
            "mean_estimation_error": mean_error,
            "attended_estimation_error": attended_error,
            "total_observations": sum(item.observations for item in self.items)
        }
        self.history.append(record)
        return record

    def get_oracle_value(self, budget: float) -> float:
        """Get the value that would be achieved with perfect knowledge."""
        true_items = [
            AttentionItem(item.name, item.true_gain, item.true_cost)
            for item in self.items
        ]
        result = self.model.allocate(true_items, budget)
        return sum(
            item.true_gain for item in self.items
            if item.name in result.attended
        )


def run_experiment():
    """Run adaptive BCP experiment."""
    print("=" * 60)
    print("CYCLE 2581: Adaptive BCP - Learning Gain/Cost")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().isoformat()}\n")

    n_steps = 100
    n_runs = 20
    n_items = 5

    # Test different exploration strategies
    strategies = {
        "no_exploration": 0.0,
        "low_exploration": 0.1,
        "high_exploration": 0.3
    }

    results = {}

    for strategy_name, exploration_bonus in strategies.items():
        print(f"\n--- Strategy: {strategy_name.upper()} (bonus={exploration_bonus}) ---")

        run_data = []
        for run in range(n_runs):
            np.random.seed(run)
            agent = AdaptiveBCPAgent(n_items=n_items, exploration_bonus=exploration_bonus)
            
            # Run simulation with varying budget
            budgets = []
            errors = []
            for step in range(n_steps):
                # Budget oscillates to create phase transitions
                budget = 1.5 + 1.0 * np.sin(step * 0.1)
                record = agent.step(budget)
                budgets.append(budget)
                errors.append(record["mean_estimation_error"])

            # Convergence metrics
            final_error = np.mean(errors[-10:])
            convergence_step = next(
                (i for i, e in enumerate(errors) if e < 0.1),
                n_steps
            )

            run_data.append({
                "final_error": final_error,
                "convergence_step": convergence_step,
                "total_observations": agent.history[-1]["total_observations"]
            })

        # Aggregate across runs
        mean_final_error = np.mean([r["final_error"] for r in run_data])
        std_final_error = np.std([r["final_error"] for r in run_data])
        mean_convergence = np.mean([r["convergence_step"] for r in run_data])
        mean_observations = np.mean([r["total_observations"] for r in run_data])

        results[strategy_name] = {
            "exploration_bonus": exploration_bonus,
            "mean_final_error": mean_final_error,
            "std_final_error": std_final_error,
            "mean_convergence_step": mean_convergence,
            "mean_observations": mean_observations
        }

        print(f"  Final Error: {mean_final_error:.4f} +/- {std_final_error:.4f}")
        print(f"  Convergence Step: {mean_convergence:.1f}")
        print(f"  Total Observations: {mean_observations:.1f}")

    # Analysis
    print("\n" + "=" * 60)
    print("ANALYSIS")
    print("=" * 60)

    sorted_by_error = sorted(results.items(), key=lambda x: x[1]["mean_final_error"])
    print("\n1. ESTIMATION ACCURACY (Lower = Better):")
    for i, (strategy, data) in enumerate(sorted_by_error, 1):
        print(f"   {i}. {strategy}: {data['mean_final_error']:.4f}")

    sorted_by_convergence = sorted(results.items(), key=lambda x: x[1]["mean_convergence_step"])
    print("\n2. CONVERGENCE SPEED (Lower = Faster):")
    for i, (strategy, data) in enumerate(sorted_by_convergence, 1):
        print(f"   {i}. {strategy}: {data['mean_convergence_step']:.1f} steps")

    # Key findings
    best_accuracy = sorted_by_error[0][0]
    fastest_convergence = sorted_by_convergence[0][0]

    print("\n" + "=" * 60)
    print("KEY FINDINGS")
    print("=" * 60)
    print(f"\n1. Best Accuracy: {best_accuracy.upper()}")
    print(f"2. Fastest Convergence: {fastest_convergence.upper()}")

    # Check if exploration helps
    no_exp_error = results["no_exploration"]["mean_final_error"]
    high_exp_error = results["high_exploration"]["mean_final_error"]

    if high_exp_error < no_exp_error:
        emergent = "EXPLORATION ADVANTAGE"
        insight = f"Exploration reduces final error by {(no_exp_error - high_exp_error)/no_exp_error*100:.1f}%"
    else:
        emergent = "EXPLOITATION ADVANTAGE"
        insight = f"No exploration achieves {(high_exp_error - no_exp_error)/high_exp_error*100:.1f}% lower error"

    print(f"\n3. EMERGENT BEHAVIOR: {emergent}")
    print(f"   {insight}")

    # Save results
    output = {
        "experiment": "cycle2581_adaptive_bcp",
        "timestamp": datetime.now().isoformat(),
        "parameters": {"n_steps": n_steps, "n_runs": n_runs, "n_items": n_items},
        "results": results,
        "findings": {
            "best_accuracy": best_accuracy,
            "fastest_convergence": fastest_convergence,
            "emergent": emergent,
            "insight": insight
        }
    }

    with open("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/cycle2581_results.json", 'w') as f:
        json.dump(output, f, indent=2)

    print("\n" + "=" * 60)
    print("CYCLE 2581 COMPLETE")
    print("=" * 60)
    return output


if __name__ == "__main__":
    run_experiment()
