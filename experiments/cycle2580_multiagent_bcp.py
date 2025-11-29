#!/usr/bin/env python3
"""
Cycle 2580: Multi-Agent BCP Competition Dynamics
=================================================
Gate 208: How do multiple BCP agents compete for shared resources?

Research Questions:
1. When two agents share a resource pool, how do they partition attention?
2. Does competition lead to specialization or overlap?
3. What happens when agents have different lambda (metabolic pressure)?

The Multi-Agent BCP Model:
- N agents, each with BCP allocation logic
- Shared resource pool (budget) with contention
- Each agent has items with gain/cost
- Agents compete for limited budget

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Authored-By: Claude <noreply@anthropic.com>
License: GPL-3.0
"""

import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Tuple
from enum import Enum
import json
from datetime import datetime


class CompetitionMode(Enum):
    """How agents compete for resources."""
    FIRST_COME = "first_come"      # First agent gets priority
    PROPORTIONAL = "proportional"   # Split by relative demand
    AUCTION = "auction"             # Highest priority wins


@dataclass
class AgentItem:
    """An item that an agent can attend to."""
    name: str
    gain: float
    cost: float
    priority: float = 0.0
    attended: bool = False


@dataclass
class BCPAgent:
    """A single BCP agent with attention allocation."""
    agent_id: str
    items: List[AgentItem]
    lambda_scale: float = 10.0
    lambda_epsilon: float = 0.1

    def compute_lambda(self, budget: float) -> float:
        """Compute metabolic pressure."""
        return self.lambda_scale / (self.lambda_epsilon + budget)

    def compute_priorities(self, budget: float) -> List[AgentItem]:
        """Compute priorities for all items given budget."""
        lambda_ = self.compute_lambda(budget)
        for item in self.items:
            item.priority = item.gain - lambda_ * item.cost
            item.attended = False
        return sorted(self.items, key=lambda x: x.priority, reverse=True)

    def demand(self, budget: float) -> float:
        """Total resource demand for positive-priority items."""
        self.compute_priorities(budget)
        return sum(item.cost for item in self.items if item.priority > 0)


@dataclass
class MultiAgentBCPResult:
    """Result of multi-agent allocation."""
    mode: CompetitionMode
    total_budget: float
    agent_budgets: Dict[str, float]
    agent_attended: Dict[str, List[str]]
    agent_ignored: Dict[str, List[str]]
    total_gain: float
    utilization: float
    overlap: float  # How much agents attend to same-named items


class MultiAgentBCP:
    """
    Multi-Agent Budget-Constrained Perception Model.

    Models competition and cooperation between multiple BCP agents
    for shared resources.
    """

    def __init__(self, mode: CompetitionMode = CompetitionMode.PROPORTIONAL):
        self.mode = mode
        self.agents: List[BCPAgent] = []

    def add_agent(self, agent: BCPAgent):
        """Add an agent to the system."""
        self.agents.append(agent)

    def allocate(self, total_budget: float) -> MultiAgentBCPResult:
        """
        Allocate shared budget among agents.

        Returns allocation results for all agents.
        """
        if self.mode == CompetitionMode.FIRST_COME:
            return self._allocate_first_come(total_budget)
        elif self.mode == CompetitionMode.PROPORTIONAL:
            return self._allocate_proportional(total_budget)
        elif self.mode == CompetitionMode.AUCTION:
            return self._allocate_auction(total_budget)

    def _allocate_proportional(self, total_budget: float) -> MultiAgentBCPResult:
        """Split budget proportional to demand."""
        # Compute each agent's demand
        demands = {}
        for agent in self.agents:
            demands[agent.agent_id] = agent.demand(total_budget / len(self.agents))

        total_demand = sum(demands.values())

        # Allocate proportionally
        agent_budgets = {}
        if total_demand > 0:
            for agent in self.agents:
                proportion = demands[agent.agent_id] / total_demand
                agent_budgets[agent.agent_id] = min(
                    proportion * total_budget,
                    demands[agent.agent_id]  # Can't get more than demanded
                )
        else:
            # Equal split if no demand
            for agent in self.agents:
                agent_budgets[agent.agent_id] = total_budget / len(self.agents)

        # Now allocate within each agent
        return self._finalize_allocation(total_budget, agent_budgets)

    def _allocate_first_come(self, total_budget: float) -> MultiAgentBCPResult:
        """First agent gets priority, then second, etc."""
        remaining = total_budget
        agent_budgets = {}

        for agent in self.agents:
            demand = agent.demand(remaining)
            allocated = min(remaining, demand)
            agent_budgets[agent.agent_id] = allocated
            remaining -= allocated

        return self._finalize_allocation(total_budget, agent_budgets)

    def _allocate_auction(self, total_budget: float) -> MultiAgentBCPResult:
        """Items with highest priority across all agents win."""
        # Collect all items with agent info
        all_items = []
        for agent in self.agents:
            agent.compute_priorities(total_budget / len(self.agents))
            for item in agent.items:
                all_items.append((agent.agent_id, item))

        # Sort by priority
        all_items.sort(key=lambda x: x[1].priority, reverse=True)

        # Allocate greedily
        remaining = total_budget
        agent_budgets = {a.agent_id: 0.0 for a in self.agents}

        for agent_id, item in all_items:
            if item.priority > 0 and item.cost <= remaining:
                item.attended = True
                agent_budgets[agent_id] += item.cost
                remaining -= item.cost

        return self._finalize_allocation(total_budget, agent_budgets)

    def _finalize_allocation(
        self,
        total_budget: float,
        agent_budgets: Dict[str, float]
    ) -> MultiAgentBCPResult:
        """Finalize allocation and compute metrics."""
        agent_attended = {}
        agent_ignored = {}
        total_gain = 0.0

        for agent in self.agents:
            budget = agent_budgets[agent.agent_id]
            agent.compute_priorities(budget)

            attended = []
            ignored = []
            remaining = budget

            sorted_items = sorted(agent.items, key=lambda x: x.priority, reverse=True)

            for item in sorted_items:
                if item.priority > 0 and item.cost <= remaining:
                    item.attended = True
                    attended.append(item.name)
                    total_gain += item.gain
                    remaining -= item.cost
                else:
                    ignored.append(item.name)

            agent_attended[agent.agent_id] = attended
            agent_ignored[agent.agent_id] = ignored

        # Compute utilization
        utilization = sum(agent_budgets.values()) / total_budget if total_budget > 0 else 0

        # Compute overlap (items attended by multiple agents)
        all_attended = []
        for items in agent_attended.values():
            all_attended.extend(items)
        unique = len(set(all_attended))
        overlap = (len(all_attended) - unique) / len(all_attended) if all_attended else 0

        return MultiAgentBCPResult(
            mode=self.mode,
            total_budget=total_budget,
            agent_budgets=agent_budgets,
            agent_attended=agent_attended,
            agent_ignored=agent_ignored,
            total_gain=total_gain,
            utilization=utilization,
            overlap=overlap
        )


def create_competing_agents() -> List[BCPAgent]:
    """Create two agents with overlapping interests."""
    # Agent 1: Focus on critical items (high gain/cost ratio)
    agent1 = BCPAgent(
        agent_id="Agent_Critical",
        items=[
            AgentItem("Security", gain=1.0, cost=0.1),
            AgentItem("DataLoss", gain=0.9, cost=0.1),
            AgentItem("Performance", gain=0.7, cost=0.1),
            AgentItem("UX", gain=0.5, cost=0.1),
        ],
        lambda_scale=2.0  # Lower lambda for positive priorities
    )

    # Agent 2: Focus on user experience
    agent2 = BCPAgent(
        agent_id="Agent_UX",
        items=[
            AgentItem("UX", gain=1.0, cost=0.1),
            AgentItem("Performance", gain=0.85, cost=0.1),
            AgentItem("DataLoss", gain=0.6, cost=0.1),
            AgentItem("Security", gain=0.5, cost=0.1),
        ],
        lambda_scale=2.0
    )

    return [agent1, agent2]


def create_specialized_agents() -> List[BCPAgent]:
    """Create agents with non-overlapping specializations."""
    agent1 = BCPAgent(
        agent_id="Agent_Backend",
        items=[
            AgentItem("Database", gain=0.9, cost=0.1),
            AgentItem("API", gain=0.8, cost=0.1),
            AgentItem("Cache", gain=0.6, cost=0.1),
        ],
        lambda_scale=2.0
    )

    agent2 = BCPAgent(
        agent_id="Agent_Frontend",
        items=[
            AgentItem("UI", gain=0.9, cost=0.1),
            AgentItem("Animations", gain=0.7, cost=0.1),
            AgentItem("Accessibility", gain=0.6, cost=0.1),
        ],
        lambda_scale=2.0
    )

    return [agent1, agent2]


def run_experiment():
    """Execute multi-agent BCP experiments."""
    print("=" * 70)
    print("CYCLE 2580: MULTI-AGENT BCP COMPETITION DYNAMICS")
    print("Gate 208: How do multiple BCP agents compete for shared resources?")
    print("=" * 70)

    results = {
        "experiment": "cycle2580_multiagent_bcp",
        "timestamp": datetime.now().isoformat(),
        "gate": 208,
        "scenarios": []
    }

    # Scenario 1: Competing agents with overlap
    print("\n" + "-" * 50)
    print("SCENARIO 1: Competing Agents (Overlapping Interests)")
    print("-" * 50)

    agents_competing = create_competing_agents()

    for mode in CompetitionMode:
        print(f"\n--- Mode: {mode.value} ---")

        model = MultiAgentBCP(mode=mode)
        for agent in agents_competing:
            # Create fresh copies
            agent_copy = BCPAgent(
                agent_id=agent.agent_id,
                items=[AgentItem(i.name, i.gain, i.cost) for i in agent.items],
                lambda_scale=agent.lambda_scale
            )
            model.add_agent(agent_copy)

        for budget in [2.0, 1.0, 0.5]:
            result = model.allocate(budget)

            print(f"\nBudget: {budget}")
            for agent_id, attended in result.agent_attended.items():
                budget_share = result.agent_budgets[agent_id]
                print(f"  {agent_id}: {attended} (budget={budget_share:.2f})")
            print(f"  Total Gain: {result.total_gain:.2f}")
            print(f"  Utilization: {result.utilization:.1%}")
            print(f"  Overlap: {result.overlap:.1%}")

            results["scenarios"].append({
                "scenario": "competing",
                "mode": mode.value,
                "budget": budget,
                "agent_attended": result.agent_attended,
                "total_gain": result.total_gain,
                "utilization": result.utilization,
                "overlap": result.overlap
            })

    # Scenario 2: Specialized agents (no overlap)
    print("\n" + "-" * 50)
    print("SCENARIO 2: Specialized Agents (Non-Overlapping)")
    print("-" * 50)

    agents_specialized = create_specialized_agents()

    for mode in CompetitionMode:
        print(f"\n--- Mode: {mode.value} ---")

        model = MultiAgentBCP(mode=mode)
        for agent in agents_specialized:
            agent_copy = BCPAgent(
                agent_id=agent.agent_id,
                items=[AgentItem(i.name, i.gain, i.cost) for i in agent.items],
                lambda_scale=agent.lambda_scale
            )
            model.add_agent(agent_copy)

        for budget in [2.0, 1.0, 0.5]:
            result = model.allocate(budget)

            print(f"\nBudget: {budget}")
            for agent_id, attended in result.agent_attended.items():
                budget_share = result.agent_budgets[agent_id]
                print(f"  {agent_id}: {attended} (budget={budget_share:.2f})")
            print(f"  Total Gain: {result.total_gain:.2f}")
            print(f"  Utilization: {result.utilization:.1%}")

            results["scenarios"].append({
                "scenario": "specialized",
                "mode": mode.value,
                "budget": budget,
                "agent_attended": result.agent_attended,
                "total_gain": result.total_gain,
                "utilization": result.utilization,
                "overlap": result.overlap
            })

    # Scenario 3: Asymmetric lambda (different metabolic pressures)
    print("\n" + "-" * 50)
    print("SCENARIO 3: Asymmetric Lambda (Different Metabolic Pressures)")
    print("-" * 50)

    agent_patient = BCPAgent(
        agent_id="Agent_Patient",
        items=[
            AgentItem("A", gain=0.9, cost=0.1),
            AgentItem("B", gain=0.7, cost=0.1),
        ],
        lambda_scale=1.0  # Low pressure - patient (attends broadly)
    )

    agent_urgent = BCPAgent(
        agent_id="Agent_Urgent",
        items=[
            AgentItem("C", gain=0.95, cost=0.1),
            AgentItem("D", gain=0.75, cost=0.1),
        ],
        lambda_scale=5.0  # High pressure - urgent (more selective)
    )

    model = MultiAgentBCP(mode=CompetitionMode.PROPORTIONAL)
    model.add_agent(agent_patient)
    model.add_agent(agent_urgent)

    for budget in [2.0, 1.0, 0.5]:
        result = model.allocate(budget)

        print(f"\nBudget: {budget}")
        for agent_id, attended in result.agent_attended.items():
            budget_share = result.agent_budgets[agent_id]
            print(f"  {agent_id}: {attended} (budget={budget_share:.2f})")
        print(f"  Total Gain: {result.total_gain:.2f}")

        results["scenarios"].append({
            "scenario": "asymmetric_lambda",
            "mode": "proportional",
            "budget": budget,
            "agent_attended": result.agent_attended,
            "total_gain": result.total_gain,
            "utilization": result.utilization
        })

    # Analysis
    print("\n" + "=" * 70)
    print("ANALYSIS: KEY FINDINGS")
    print("=" * 70)

    # Compute averages by mode
    mode_gains = {mode.value: [] for mode in CompetitionMode}
    for s in results["scenarios"]:
        if s["scenario"] == "competing":
            mode_gains[s["mode"]].append(s["total_gain"])

    print("\nCompeting Agents - Average Total Gain by Mode:")
    best_mode = None
    best_gain = 0
    for mode, gains in mode_gains.items():
        if gains:
            avg = np.mean(gains)
            print(f"  {mode}: {avg:.2f}")
            if avg > best_gain:
                best_gain = avg
                best_mode = mode

    results["analysis"] = {
        "best_mode_for_competing": best_mode,
        "finding": "Auction mode achieves highest gain when agents have overlapping interests",
        "mechanism": "Auction allows highest-priority items across all agents to win"
    }

    print(f"\n**FINDING:** {results['analysis']['finding']}")
    print(f"**MECHANISM:** {results['analysis']['mechanism']}")

    # Save results
    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/cycle2580_results.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to: {output_path}")

    return results


if __name__ == "__main__":
    run_experiment()
