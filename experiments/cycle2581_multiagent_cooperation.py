#!/usr/bin/env python3
"""
Cycle 2581: Multi-Agent BCP Cooperation Dynamics
=================================================
Gate 209: When do BCP agents benefit from cooperation?

Research Questions:
1. Does pooling resources improve total system gain?
2. Can agents form coalitions to overcome individual limitations?
3. What are the conditions for cooperation to outperform competition?

The Cooperation Model:
- N agents can choose to cooperate (pool budgets) or compete
- Cooperation creates a shared pool with shared access
- Competition maintains separate individual budgets
- Measure: Total gain, fairness, efficiency

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Authored-By: Claude <noreply@anthropic.com>
License: GPL-3.0
"""

import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Set, Optional
from enum import Enum
import json
from datetime import datetime


@dataclass
class CoopItem:
    """An item that an agent can attend to."""
    name: str
    gain: float
    cost: float
    priority: float = 0.0
    attended: bool = False
    owner: str = ""  # Which agent owns this item


class CoopAgent:
    """A BCP agent with cooperation capability."""

    def __init__(
        self,
        agent_id: str,
        items: List[Tuple[str, float, float]],  # (name, gain, cost)
        lambda_scale: float = 2.0,
        lambda_epsilon: float = 0.1
    ):
        self.agent_id = agent_id
        self.items = [
            CoopItem(name=n, gain=g, cost=c, owner=agent_id)
            for n, g, c in items
        ]
        self.lambda_scale = lambda_scale
        self.lambda_epsilon = lambda_epsilon

    def compute_lambda(self, budget: float) -> float:
        """Compute metabolic pressure."""
        return self.lambda_scale / (self.lambda_epsilon + budget)

    def compute_priorities(self, budget: float) -> List[CoopItem]:
        """Compute priorities for all items given budget."""
        lambda_ = self.compute_lambda(budget)
        for item in self.items:
            item.priority = item.gain - lambda_ * item.cost
            item.attended = False
        return self.items

    def allocate_individual(self, budget: float) -> Tuple[List[str], float]:
        """Allocate individually with given budget."""
        self.compute_priorities(budget)
        sorted_items = sorted(self.items, key=lambda x: x.priority, reverse=True)

        attended = []
        total_gain = 0.0
        remaining = budget

        for item in sorted_items:
            if item.priority > 0 and item.cost <= remaining:
                item.attended = True
                attended.append(item.name)
                total_gain += item.gain
                remaining -= item.cost

        return attended, total_gain


@dataclass
class CooperationResult:
    """Result of cooperation analysis."""
    mode: str  # "individual" or "cooperative"
    total_budget: float
    agent_results: Dict[str, Dict]
    total_gain: float
    efficiency: float  # gain per unit budget
    fairness: float  # how evenly distributed is gain


class CooperationModel:
    """
    Multi-Agent BCP Cooperation Model.

    Tests when cooperation outperforms individual allocation.
    """

    def __init__(self, agents: List[CoopAgent]):
        self.agents = agents

    def run_individual(self, total_budget: float) -> CooperationResult:
        """Each agent gets equal share of budget."""
        individual_budget = total_budget / len(self.agents)

        agent_results = {}
        total_gain = 0.0
        gains = []

        for agent in self.agents:
            attended, gain = agent.allocate_individual(individual_budget)
            agent_results[agent.agent_id] = {
                "budget": individual_budget,
                "attended": attended,
                "gain": gain
            }
            total_gain += gain
            gains.append(gain)

        efficiency = total_gain / total_budget if total_budget > 0 else 0

        # Fairness: 1 - coefficient of variation
        if len(gains) > 1 and np.mean(gains) > 0:
            cv = np.std(gains) / np.mean(gains)
            fairness = 1 - min(cv, 1)
        else:
            fairness = 1.0

        return CooperationResult(
            mode="individual",
            total_budget=total_budget,
            agent_results=agent_results,
            total_gain=total_gain,
            efficiency=efficiency,
            fairness=fairness
        )

    def run_cooperative(self, total_budget: float) -> CooperationResult:
        """All agents pool resources and items."""
        # Collect all items
        all_items = []
        for agent in self.agents:
            all_items.extend(agent.items)

        # Use average lambda
        avg_lambda_scale = np.mean([a.lambda_scale for a in self.agents])

        # Compute priorities with pooled budget
        lambda_ = avg_lambda_scale / (0.1 + total_budget)
        for item in all_items:
            item.priority = item.gain - lambda_ * item.cost
            item.attended = False

        # Sort by priority
        sorted_items = sorted(all_items, key=lambda x: x.priority, reverse=True)

        # Allocate greedily
        remaining = total_budget
        attended_by_owner = {a.agent_id: [] for a in self.agents}
        gains_by_owner = {a.agent_id: 0.0 for a in self.agents}

        for item in sorted_items:
            if item.priority > 0 and item.cost <= remaining:
                item.attended = True
                attended_by_owner[item.owner].append(item.name)
                gains_by_owner[item.owner] += item.gain
                remaining -= item.cost

        total_gain = sum(gains_by_owner.values())
        efficiency = total_gain / total_budget if total_budget > 0 else 0

        # Build results
        agent_results = {}
        for agent in self.agents:
            agent_results[agent.agent_id] = {
                "budget": "pooled",
                "attended": attended_by_owner[agent.agent_id],
                "gain": gains_by_owner[agent.agent_id]
            }

        gains = list(gains_by_owner.values())
        if len(gains) > 1 and np.mean(gains) > 0:
            cv = np.std(gains) / np.mean(gains)
            fairness = 1 - min(cv, 1)
        else:
            fairness = 1.0

        return CooperationResult(
            mode="cooperative",
            total_budget=total_budget,
            agent_results=agent_results,
            total_gain=total_gain,
            efficiency=efficiency,
            fairness=fairness
        )

    def compare(self, total_budget: float) -> Dict:
        """Compare individual vs cooperative allocation."""
        individual = self.run_individual(total_budget)
        cooperative = self.run_cooperative(total_budget)

        return {
            "budget": total_budget,
            "individual": {
                "total_gain": individual.total_gain,
                "efficiency": individual.efficiency,
                "fairness": individual.fairness,
                "details": individual.agent_results
            },
            "cooperative": {
                "total_gain": cooperative.total_gain,
                "efficiency": cooperative.efficiency,
                "fairness": cooperative.fairness,
                "details": cooperative.agent_results
            },
            "cooperation_benefit": cooperative.total_gain - individual.total_gain,
            "cooperation_wins": cooperative.total_gain > individual.total_gain
        }


def run_experiment():
    """Execute cooperation experiments."""
    print("=" * 70)
    print("CYCLE 2581: MULTI-AGENT BCP COOPERATION DYNAMICS")
    print("Gate 209: When do BCP agents benefit from cooperation?")
    print("=" * 70)

    results = {
        "experiment": "cycle2581_multiagent_cooperation",
        "timestamp": datetime.now().isoformat(),
        "gate": 209,
        "scenarios": []
    }

    # Scenario 1: Equal agents, equal items
    print("\n" + "-" * 50)
    print("SCENARIO 1: Equal Agents (Symmetric Resources)")
    print("-" * 50)

    agent1 = CoopAgent("Agent_A", [
        ("A1", 0.9, 0.15),
        ("A2", 0.7, 0.15),
        ("A3", 0.5, 0.15),
    ])

    agent2 = CoopAgent("Agent_B", [
        ("B1", 0.9, 0.15),
        ("B2", 0.7, 0.15),
        ("B3", 0.5, 0.15),
    ])

    model = CooperationModel([agent1, agent2])

    for budget in [1.5, 0.8, 0.4]:
        comparison = model.compare(budget)

        print(f"\nBudget: {budget}")
        print(f"  Individual: Gain={comparison['individual']['total_gain']:.2f}, "
              f"Efficiency={comparison['individual']['efficiency']:.2f}")
        print(f"  Cooperative: Gain={comparison['cooperative']['total_gain']:.2f}, "
              f"Efficiency={comparison['cooperative']['efficiency']:.2f}")
        print(f"  Cooperation Benefit: {comparison['cooperation_benefit']:+.2f}")
        print(f"  Cooperation Wins: {comparison['cooperation_wins']}")

        results["scenarios"].append({
            "scenario": "equal_symmetric",
            **comparison
        })

    # Scenario 2: Unequal agents (one has better items)
    print("\n" + "-" * 50)
    print("SCENARIO 2: Unequal Agents (Asymmetric Resources)")
    print("-" * 50)

    agent_strong = CoopAgent("Agent_Strong", [
        ("S1", 1.0, 0.1),  # Great items
        ("S2", 0.95, 0.1),
        ("S3", 0.9, 0.1),
    ])

    agent_weak = CoopAgent("Agent_Weak", [
        ("W1", 0.4, 0.2),  # Poor items
        ("W2", 0.3, 0.2),
        ("W3", 0.2, 0.2),
    ])

    model2 = CooperationModel([agent_strong, agent_weak])

    for budget in [1.0, 0.5, 0.3]:
        comparison = model2.compare(budget)

        print(f"\nBudget: {budget}")
        print(f"  Individual Total: {comparison['individual']['total_gain']:.2f}")
        for agent_id, detail in comparison['individual']['details'].items():
            print(f"    {agent_id}: {detail['attended']} -> Gain={detail['gain']:.2f}")
        print(f"  Cooperative Total: {comparison['cooperative']['total_gain']:.2f}")
        for agent_id, detail in comparison['cooperative']['details'].items():
            print(f"    {agent_id}: {detail['attended']} -> Gain={detail['gain']:.2f}")
        print(f"  Cooperation Benefit: {comparison['cooperation_benefit']:+.2f}")

        results["scenarios"].append({
            "scenario": "unequal_asymmetric",
            **comparison
        })

    # Scenario 3: Complementary agents (different specializations)
    print("\n" + "-" * 50)
    print("SCENARIO 3: Complementary Agents (Synergy Potential)")
    print("-" * 50)

    # Agent with expensive high-gain items (needs budget)
    agent_expensive = CoopAgent("Agent_Expensive", [
        ("E1", 1.0, 0.4),  # High gain but expensive
        ("E2", 0.9, 0.35),
    ])

    # Agent with cheap low-gain items (has spare budget)
    agent_cheap = CoopAgent("Agent_Cheap", [
        ("C1", 0.5, 0.05),  # Lower gain but very cheap
        ("C2", 0.4, 0.05),
        ("C3", 0.3, 0.05),
    ])

    model3 = CooperationModel([agent_expensive, agent_cheap])

    for budget in [1.0, 0.6, 0.3]:
        comparison = model3.compare(budget)

        print(f"\nBudget: {budget}")
        print(f"  Individual Total: {comparison['individual']['total_gain']:.2f}")
        for agent_id, detail in comparison['individual']['details'].items():
            print(f"    {agent_id}: {detail['attended']}")
        print(f"  Cooperative Total: {comparison['cooperative']['total_gain']:.2f}")
        for agent_id, detail in comparison['cooperative']['details'].items():
            print(f"    {agent_id}: {detail['attended']}")
        print(f"  Cooperation Benefit: {comparison['cooperation_benefit']:+.2f}")

        results["scenarios"].append({
            "scenario": "complementary_synergy",
            **comparison
        })

    # Analysis
    print("\n" + "=" * 70)
    print("ANALYSIS: KEY FINDINGS")
    print("=" * 70)

    # Count cooperation wins
    coop_wins = sum(1 for s in results["scenarios"] if s["cooperation_wins"])
    total = len(results["scenarios"])

    print(f"\nCooperation wins in {coop_wins}/{total} scenarios ({100*coop_wins/total:.0f}%)")

    # Find biggest benefit
    benefits = [s["cooperation_benefit"] for s in results["scenarios"]]
    best_idx = np.argmax(benefits)
    best_scenario = results["scenarios"][best_idx]

    print(f"\nBiggest cooperation benefit: {best_scenario['cooperation_benefit']:+.2f}")
    print(f"  Scenario: {best_scenario['scenario']}")
    print(f"  Budget: {best_scenario['budget']}")

    # Derive principle
    if coop_wins > total / 2:
        finding = "Cooperation generally outperforms individual allocation"
        mechanism = "Pooling allows budget to flow to highest-priority items globally"
    else:
        finding = "Cooperation benefits depend on agent asymmetry"
        mechanism = "Equal agents gain less from cooperation than unequal ones"

    results["analysis"] = {
        "coop_win_rate": coop_wins / total,
        "max_benefit": max(benefits),
        "finding": finding,
        "mechanism": mechanism
    }

    print(f"\n**FINDING:** {finding}")
    print(f"**MECHANISM:** {mechanism}")

    # Fairness analysis
    print("\n" + "-" * 50)
    print("FAIRNESS ANALYSIS")
    print("-" * 50)

    for s in results["scenarios"]:
        if s["scenario"] == "unequal_asymmetric":
            print(f"\nBudget: {s['budget']}")
            print(f"  Individual Fairness: {s['individual']['fairness']:.2f}")
            print(f"  Cooperative Fairness: {s['cooperative']['fairness']:.2f}")

    # Save results
    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/cycle2581_results.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to: {output_path}")

    return results


if __name__ == "__main__":
    run_experiment()
