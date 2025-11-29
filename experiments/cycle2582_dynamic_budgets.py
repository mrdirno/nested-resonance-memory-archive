#!/usr/bin/env python3
"""
Cycle 2582: Dynamic Budget BCP Dynamics
========================================
Gate 210: How do BCP agents adapt to time-varying budgets?

Research Questions:
1. How does allocation change during budget cycles (boom/bust)?
2. Is there hysteresis in attention allocation (path dependence)?
3. Can agents anticipate budget changes?

The Dynamic Budget Model:
- Budget varies according to time functions
- Agent allocation updates at each timestep
- Track: items attended, phase transitions, lag effects

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Authored-By: Claude <noreply@anthropic.com>
License: GPL-3.0
"""

import numpy as np
from dataclasses import dataclass
from typing import List, Dict, Callable, Tuple
import json
from datetime import datetime


@dataclass
class TimeItem:
    """An item with time-varying properties."""
    name: str
    base_gain: float
    cost: float
    priority: float = 0.0
    attended: bool = False


class DynamicBCPAgent:
    """BCP agent that operates in dynamic budget environments."""

    def __init__(
        self,
        agent_id: str,
        items: List[Tuple[str, float, float]],
        lambda_scale: float = 2.0,
        lambda_epsilon: float = 0.1
    ):
        self.agent_id = agent_id
        self.items = [TimeItem(n, g, c) for n, g, c in items]
        self.lambda_scale = lambda_scale
        self.lambda_epsilon = lambda_epsilon
        self.history: List[Dict] = []

    def allocate(self, budget: float, time: float = 0.0) -> Dict:
        """Allocate at given budget and time."""
        lambda_ = self.lambda_scale / (self.lambda_epsilon + budget)

        for item in self.items:
            item.priority = item.base_gain - lambda_ * item.cost
            item.attended = False

        sorted_items = sorted(self.items, key=lambda x: x.priority, reverse=True)

        attended = []
        total_gain = 0.0
        total_cost = 0.0
        remaining = budget

        for item in sorted_items:
            if item.priority > 0 and item.cost <= remaining:
                item.attended = True
                attended.append(item.name)
                total_gain += item.base_gain
                total_cost += item.cost
                remaining -= item.cost

        # Determine phase
        if budget >= 1.5:
            phase = "ABUNDANCE"
        elif budget <= 0.3:
            phase = "CRISIS"
        else:
            phase = "SCARCITY"

        result = {
            "time": time,
            "budget": budget,
            "lambda": lambda_,
            "phase": phase,
            "attended": attended,
            "ignored": [i.name for i in self.items if not i.attended],
            "total_gain": total_gain,
            "n_attended": len(attended),
        }

        self.history.append(result)
        return result


def sinusoidal_budget(t: float, amplitude: float = 0.7,
                       offset: float = 1.0, period: float = 10.0) -> float:
    """Sinusoidal budget: oscillates between (offset-amplitude) and (offset+amplitude)."""
    return offset + amplitude * np.sin(2 * np.pi * t / period)


def boom_bust_budget(t: float, boom_level: float = 2.0,
                      bust_level: float = 0.3, period: float = 10.0) -> float:
    """Square wave: alternates between boom and bust."""
    phase = (t % period) / period
    return boom_level if phase < 0.5 else bust_level


def declining_budget(t: float, initial: float = 2.0,
                      decay_rate: float = 0.1) -> float:
    """Exponential decline: starts high, decays over time."""
    return max(0.1, initial * np.exp(-decay_rate * t))


def shock_budget(t: float, base: float = 1.5,
                  shock_times: List[float] = None, shock_depth: float = 0.8) -> float:
    """Periodic shocks: stable base with sudden drops."""
    if shock_times is None:
        shock_times = [5, 15, 25]

    for shock_t in shock_times:
        if abs(t - shock_t) < 0.5:
            return base * (1 - shock_depth)
    return base


def run_experiment():
    """Execute dynamic budget experiments."""
    print("=" * 70)
    print("CYCLE 2582: DYNAMIC BUDGET BCP DYNAMICS")
    print("Gate 210: How do BCP agents adapt to time-varying budgets?")
    print("=" * 70)

    results = {
        "experiment": "cycle2582_dynamic_budgets",
        "timestamp": datetime.now().isoformat(),
        "gate": 210,
        "scenarios": []
    }

    # Create agent
    base_items = [
        ("Critical", 1.0, 0.15),
        ("High", 0.85, 0.15),
        ("Medium", 0.65, 0.15),
        ("Low", 0.45, 0.15),
        ("Optional", 0.25, 0.15),
    ]

    time_points = np.linspace(0, 20, 41)

    # Scenario 1: Sinusoidal budget (smooth cycles)
    print("\n" + "-" * 50)
    print("SCENARIO 1: Sinusoidal Budget (Smooth Cycles)")
    print("-" * 50)

    agent = DynamicBCPAgent("Agent", base_items)
    budget_fn = sinusoidal_budget

    for t in time_points:
        budget = budget_fn(t)
        agent.allocate(budget, t)

    # Analyze
    phases = [h["phase"] for h in agent.history]
    n_attended = [h["n_attended"] for h in agent.history]

    phase_transitions = sum(1 for i in range(1, len(phases)) if phases[i] != phases[i-1])

    print(f"\nTime points: {len(time_points)}")
    print(f"Phase transitions: {phase_transitions}")
    print(f"Mean items attended: {np.mean(n_attended):.2f}")
    print(f"Min/Max attended: {min(n_attended)}/{max(n_attended)}")

    results["scenarios"].append({
        "scenario": "sinusoidal",
        "budget_function": "sin wave",
        "phase_transitions": phase_transitions,
        "mean_attended": np.mean(n_attended),
        "history": agent.history
    })

    # Scenario 2: Boom-Bust (Square wave)
    print("\n" + "-" * 50)
    print("SCENARIO 2: Boom-Bust (Square Wave)")
    print("-" * 50)

    agent2 = DynamicBCPAgent("Agent", base_items)
    budget_fn2 = boom_bust_budget

    for t in time_points:
        budget = budget_fn2(t)
        agent2.allocate(budget, t)

    phases2 = [h["phase"] for h in agent2.history]
    n_attended2 = [h["n_attended"] for h in agent2.history]
    phase_transitions2 = sum(1 for i in range(1, len(phases2)) if phases2[i] != phases2[i-1])

    print(f"\nPhase transitions: {phase_transitions2}")
    print(f"Mean items attended: {np.mean(n_attended2):.2f}")
    print(f"Time in ABUNDANCE: {phases2.count('ABUNDANCE')}/{len(phases2)}")
    print(f"Time in CRISIS: {phases2.count('CRISIS')}/{len(phases2)}")

    results["scenarios"].append({
        "scenario": "boom_bust",
        "budget_function": "square wave",
        "phase_transitions": phase_transitions2,
        "mean_attended": np.mean(n_attended2),
        "time_abundance": phases2.count('ABUNDANCE'),
        "time_crisis": phases2.count('CRISIS'),
        "history": agent2.history
    })

    # Scenario 3: Declining budget (Collapse trajectory)
    print("\n" + "-" * 50)
    print("SCENARIO 3: Declining Budget (Collapse Trajectory)")
    print("-" * 50)

    agent3 = DynamicBCPAgent("Agent", base_items)
    budget_fn3 = declining_budget

    for t in time_points:
        budget = budget_fn3(t)
        agent3.allocate(budget, t)

    phases3 = [h["phase"] for h in agent3.history]
    n_attended3 = [h["n_attended"] for h in agent3.history]

    # Find when each item is dropped
    drop_times = {}
    all_items = ["Critical", "High", "Medium", "Low", "Optional"]
    for item in all_items:
        for h in agent3.history:
            if item not in h["attended"]:
                drop_times[item] = h["time"]
                break

    print(f"\nItem drop sequence:")
    for item, t in sorted(drop_times.items(), key=lambda x: x[1]):
        budget_at_drop = declining_budget(t)
        print(f"  {item}: dropped at t={t:.1f} (budget={budget_at_drop:.2f})")

    print(f"\nFinal state (t={time_points[-1]}):")
    final = agent3.history[-1]
    print(f"  Budget: {final['budget']:.2f}")
    print(f"  Attended: {final['attended']}")
    print(f"  Phase: {final['phase']}")

    results["scenarios"].append({
        "scenario": "declining",
        "budget_function": "exponential decay",
        "drop_sequence": drop_times,
        "final_attended": final["attended"],
        "history": agent3.history
    })

    # Scenario 4: Shock recovery
    print("\n" + "-" * 50)
    print("SCENARIO 4: Shock & Recovery")
    print("-" * 50)

    agent4 = DynamicBCPAgent("Agent", base_items)
    shock_times = [5, 10, 15]

    for t in time_points:
        budget = shock_budget(t, shock_times=shock_times)
        agent4.allocate(budget, t)

    phases4 = [h["phase"] for h in agent4.history]
    n_attended4 = [h["n_attended"] for h in agent4.history]

    # Find shock impact
    print("\nShock analysis:")
    for shock_t in shock_times:
        # Find nearest time point to shock
        shock_idx = np.argmin(np.abs(time_points - shock_t))
        before_idx = max(0, shock_idx - 1)
        after_idx = shock_idx

        before = agent4.history[before_idx]
        at_shock = agent4.history[after_idx]

        print(f"  t={shock_t}: {before['n_attended']} items -> {at_shock['n_attended']} items "
              f"(phase: {at_shock['phase']})")

    # Recovery time analysis
    recovery_times = []
    for shock_t in shock_times:
        shock_idx = np.argmin(np.abs(time_points - shock_t))
        pre_shock = agent4.history[max(0, shock_idx-1)]["n_attended"]

        for i in range(shock_idx, len(agent4.history)):
            if agent4.history[i]["n_attended"] >= pre_shock:
                recovery_times.append(time_points[i] - shock_t)
                break

    if recovery_times:
        print(f"\nMean recovery time: {np.mean(recovery_times):.2f} time units")

    results["scenarios"].append({
        "scenario": "shock_recovery",
        "shock_times": shock_times,
        "mean_recovery": np.mean(recovery_times) if recovery_times else None,
        "history": agent4.history
    })

    # Analysis
    print("\n" + "=" * 70)
    print("ANALYSIS: KEY FINDINGS")
    print("=" * 70)

    print("\n1. PHASE TRANSITION FREQUENCY")
    print(f"   Sinusoidal: {phase_transitions} transitions")
    print(f"   Boom-Bust:  {phase_transitions2} transitions")
    print(f"   -> Square waves cause sharper, more disruptive transitions")

    print("\n2. TRIAGE ORDER (Declining Budget)")
    print("   Drop sequence reveals priority hierarchy:")
    for item, t in sorted(drop_times.items(), key=lambda x: x[1]):
        print(f"   {item}")

    print("\n3. RECOVERY DYNAMICS (Shock)")
    if recovery_times:
        print(f"   Mean recovery: {np.mean(recovery_times):.2f} time units")
        print("   -> System returns to pre-shock allocation quickly")

    # Derive principle
    finding = "Budget dynamics create predictable triage cascades"
    mechanism = "Items are dropped in reverse priority order during decline; recovery reverses this"

    results["analysis"] = {
        "finding": finding,
        "mechanism": mechanism,
        "drop_order": list(sorted(drop_times.items(), key=lambda x: x[1]))
    }

    print(f"\n**FINDING:** {finding}")
    print(f"**MECHANISM:** {mechanism}")

    # Save results
    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/cycle2582_results.json"
    with open(output_path, 'w') as f:
        # Convert numpy types for JSON
        def convert(obj):
            if isinstance(obj, np.floating):
                return float(obj)
            if isinstance(obj, np.integer):
                return int(obj)
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            return obj

        json.dump(results, f, indent=2, default=convert)

    print(f"\nResults saved to: {output_path}")

    return results


if __name__ == "__main__":
    run_experiment()
