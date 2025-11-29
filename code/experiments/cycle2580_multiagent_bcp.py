#!/usr/bin/env python3
"""
Cycle 2580: Multi-Agent BCP Dynamics
=====================================

Phase 74, Gate 208: What happens when multiple BCP agents share resources?

Research Questions:
1. Do agents converge on similar triage patterns?
2. Does competition for resources accelerate phase transitions?
3. Can cooperative behavior emerge under shared scarcity?

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
License: GPL-3.0
"""

import numpy as np
import json
from dataclasses import dataclass, field
from typing import List, Dict
from datetime import datetime
import sys
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2/bcp_lib')

from bcp import BCPModel, AttentionItem


@dataclass
class Agent:
    """A BCP-governed agent competing for shared resources."""
    id: str
    model: BCPModel = field(default_factory=lambda: BCPModel(
        lambda_scale=5.0,        # Lower pressure for more variance
        abundance_threshold=3.0,  # Easier to reach abundance
        crisis_threshold=0.8      # Lower crisis threshold
    ))
    items: List[AttentionItem] = field(default_factory=list)
    history: List[Dict] = field(default_factory=list)

    def generate_items(self, n: int = 5) -> List[AttentionItem]:
        """Generate random attention items for this agent."""
        items = []
        for i in range(n):
            gain = np.random.uniform(0.5, 1.0)  # Higher gains
            cost = np.random.uniform(0.05, 0.2)  # Lower costs
            items.append(AttentionItem(f"{self.id}_task_{i}", gain, cost))
        return items

    def step(self, available_budget: float) -> Dict:
        """Execute one step of attention allocation."""
        # Use full available budget - no arbitrary cap
        self.items = self.generate_items()
        result = self.model.allocate(self.items, available_budget)

        record = {
            "step": len(self.history),
            "budget": available_budget,
            "phase": result.phase.value,
            "n_attended": result.n_attended,
            "n_ignored": result.n_ignored,
            "lambda": result.lambda_,
            "total_cost": result.total_cost
        }
        self.history.append(record)
        return record


@dataclass
class SharedResourcePool:
    """A shared resource pool that agents compete for."""
    total_budget: float = 8.0      # Scarce pool
    regeneration_rate: float = 0.3  # Slow regeneration
    current_budget: float = 8.0
    depletion_history: List[float] = field(default_factory=list)

    def consume(self, amount: float) -> float:
        consumed = min(amount, self.current_budget)
        self.current_budget -= consumed
        return consumed

    def regenerate(self):
        self.current_budget = min(self.total_budget, self.current_budget + self.regeneration_rate)

    def get_per_agent_budget(self, n_agents: int) -> float:
        return self.current_budget / n_agents if n_agents > 0 else 0


class MultiAgentBCPSimulation:
    def __init__(self, n_agents: int = 5, scenario: str = "cooperative"):
        self.n_agents = n_agents
        self.scenario = scenario
        self.agents = [Agent(id=f"agent_{i}") for i in range(n_agents)]
        self.pool = SharedResourcePool()
        self.step_count = 0
        self.aggregate_history = []

    def step(self) -> Dict:
        step_results = []

        if self.scenario == "cooperative":
            per_agent = self.pool.get_per_agent_budget(self.n_agents)
            for agent in self.agents:
                result = agent.step(per_agent)
                self.pool.consume(result["total_cost"])
                step_results.append(result)

        elif self.scenario == "competitive":
            agents_shuffled = list(self.agents)
            np.random.shuffle(agents_shuffled)
            for agent in agents_shuffled:
                result = agent.step(self.pool.current_budget)
                self.pool.consume(result["total_cost"])
                step_results.append(result)

        elif self.scenario == "hierarchical":
            for agent in sorted(self.agents, key=lambda a: a.id):
                result = agent.step(self.pool.current_budget)
                self.pool.consume(result["total_cost"])
                step_results.append(result)

        self.pool.regenerate()
        self.pool.depletion_history.append(self.pool.current_budget)

        aggregate = {
            "step": self.step_count,
            "pool_budget": self.pool.current_budget,
            "mean_budget": np.mean([r["budget"] for r in step_results]),
            "mean_attended": np.mean([r["n_attended"] for r in step_results]),
            "mean_lambda": np.mean([r["lambda"] for r in step_results]),
            "phase_distribution": self._count_phases(step_results),
            "total_consumption": sum(r["total_cost"] for r in step_results)
        }
        self.aggregate_history.append(aggregate)
        self.step_count += 1
        return aggregate

    def _count_phases(self, results: List[Dict]) -> Dict[str, int]:
        phases = [r["phase"] for r in results]
        return {p: phases.count(p) for p in set(phases)}

    def run(self, n_steps: int = 100) -> List[Dict]:
        for _ in range(n_steps):
            self.step()
        return self.aggregate_history

    def get_summary(self) -> Dict:
        if not self.aggregate_history:
            return {"error": "No simulation run yet"}

        budgets = [h["mean_budget"] for h in self.aggregate_history]
        attended = [h["mean_attended"] for h in self.aggregate_history]
        lambdas = [h["mean_lambda"] for h in self.aggregate_history]
        pool_history = self.pool.depletion_history

        total_transitions = 0
        for agent in self.agents:
            for i in range(1, len(agent.history)):
                if agent.history[i]["phase"] != agent.history[i-1]["phase"]:
                    total_transitions += 1

        return {
            "scenario": self.scenario,
            "n_agents": self.n_agents,
            "n_steps": self.step_count,
            "budget": {"mean": np.mean(budgets), "std": np.std(budgets), "min": np.min(budgets), "max": np.max(budgets)},
            "attended": {"mean": np.mean(attended), "std": np.std(attended)},
            "lambda": {"mean": np.mean(lambdas), "std": np.std(lambdas)},
            "pool": {"final": pool_history[-1] if pool_history else 0, "mean": np.mean(pool_history), "depleted_steps": sum(1 for p in pool_history if p < 1.0)},
            "phase_transitions": total_transitions
        }


def run_experiment():
    print("=" * 60)
    print("CYCLE 2580: Multi-Agent BCP Dynamics")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().isoformat()}\n")

    scenarios = ["cooperative", "competitive", "hierarchical"]
    n_agents, n_steps, n_runs = 5, 100, 10
    results = {}

    for scenario in scenarios:
        print(f"\n--- Scenario: {scenario.upper()} ---")
        run_summaries = []
        for run in range(n_runs):
            np.random.seed(run)
            sim = MultiAgentBCPSimulation(n_agents=n_agents, scenario=scenario)
            sim.run(n_steps)
            run_summaries.append(sim.get_summary())

        mean_budget = np.mean([s["budget"]["mean"] for s in run_summaries])
        std_budget = np.std([s["budget"]["mean"] for s in run_summaries])
        mean_attended = np.mean([s["attended"]["mean"] for s in run_summaries])
        mean_lambda = np.mean([s["lambda"]["mean"] for s in run_summaries])
        mean_transitions = np.mean([s["phase_transitions"] for s in run_summaries])
        mean_depleted = np.mean([s["pool"]["depleted_steps"] for s in run_summaries])

        results[scenario] = {
            "mean_budget": mean_budget, "std_budget": std_budget,
            "mean_attended": mean_attended, "mean_lambda": mean_lambda,
            "mean_phase_transitions": mean_transitions, "mean_depleted_steps": mean_depleted
        }

        print(f"  Mean Budget: {mean_budget:.3f} +/- {std_budget:.3f}")
        print(f"  Mean Attended: {mean_attended:.2f}")
        print(f"  Mean Lambda: {mean_lambda:.2f}")
        print(f"  Phase Transitions: {mean_transitions:.1f}")

    print("\n" + "=" * 60)
    print("ANALYSIS")
    print("=" * 60)

    sorted_by_budget = sorted(results.items(), key=lambda x: x[1]["mean_budget"], reverse=True)
    print("\n1. RESOURCE EFFICIENCY:")
    for i, (s, d) in enumerate(sorted_by_budget, 1):
        print(f"   {i}. {s}: {d['mean_budget']:.3f}")

    sorted_by_transitions = sorted(results.items(), key=lambda x: x[1]["mean_phase_transitions"])
    print("\n2. PHASE STABILITY:")
    for i, (s, d) in enumerate(sorted_by_transitions, 1):
        print(f"   {i}. {s}: {d['mean_phase_transitions']:.1f} transitions")

    best_efficiency = sorted_by_budget[0][0]
    most_stable = sorted_by_transitions[0][0]

    coop = results["cooperative"]["mean_budget"]
    comp = results["competitive"]["mean_budget"]
    hier = results["hierarchical"]["mean_budget"]

    if coop > comp and coop > hier:
        emergent, insight = "COOPERATION ADVANTAGE", "Fair sharing outperforms competition"
    elif hier > coop:
        emergent, insight = "HIERARCHY ADVANTAGE", "Priority access creates efficiency"
    else:
        emergent, insight = "COMPETITION EQUIVALENCE", "Competition matches cooperation"

    print(f"\n3. EMERGENT: {emergent}")
    print(f"   {insight}")

    output = {
        "experiment": "cycle2580_multiagent_bcp",
        "timestamp": datetime.now().isoformat(),
        "parameters": {"n_agents": n_agents, "n_steps": n_steps, "n_runs": n_runs},
        "results": results,
        "findings": {"best_efficiency": best_efficiency, "most_stable": most_stable, "emergent": emergent, "insight": insight}
    }

    with open("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/cycle2580_results.json", 'w') as f:
        json.dump(output, f, indent=2)

    print("\n" + "=" * 60)
    print("CYCLE 2580 COMPLETE")
    print("=" * 60)
    return output


if __name__ == "__main__":
    run_experiment()
