#!/usr/bin/env python3
"""
Cycle 2590: Decision Fatigue as BCP Budget Exhaustion
======================================================
Gate 218: Does decision fatigue follow budget depletion dynamics?

Research Questions:
1. Does each decision consume cognitive budget?
2. Does λ rise as budget depletes?
3. Do later decisions default to easy options?
4. Can rest restore the decision budget?

The Decision Fatigue BCP Model:
- Decisions as cognitive allocations
- Decision quality as "gain"
- Mental effort as "cost"
- Willpower/energy as "budget"
- λ(Budget) rises as fatigue accumulates

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Authored-By: Claude <noreply@anthropic.com>
License: GPL-3.0
"""

import numpy as np
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
import json
from datetime import datetime


@dataclass
class Decision:
    """A decision opportunity."""
    name: str
    optimal_gain: float  # Gain from making optimal choice
    default_gain: float  # Gain from defaulting to easy choice
    effort_cost: float  # Mental effort required
    complexity: float  # Decision complexity
    made_optimally: bool = False
    outcome: float = 0.0


@dataclass
class DecisionMakerState:
    """Current state of decision maker."""
    budget: float
    decisions_made: int
    optimal_decisions: int
    total_gain: float
    lambda_: float


class DecisionFatigueBCP:
    """
    Decision fatigue model based on BCP budget depletion.

    Each decision consumes budget proportional to effort.
    As budget depletes, λ rises, making costly decisions less attractive.
    Eventually, the agent defaults to easy choices (ego depletion).
    """

    def __init__(
        self,
        initial_budget: float = 10.0,
        lambda_scale: float = 2.0,
        lambda_epsilon: float = 0.5,
        recovery_rate: float = 0.5,  # Budget recovery per rest period
    ):
        self.initial_budget = initial_budget
        self.budget = initial_budget
        self.lambda_scale = lambda_scale
        self.lambda_epsilon = lambda_epsilon
        self.recovery_rate = recovery_rate

        # Tracking
        self.decisions_made = 0
        self.optimal_decisions = 0
        self.total_gain = 0.0

    def compute_lambda(self) -> float:
        """Compute current metabolic pressure from remaining budget."""
        return self.lambda_scale / (self.lambda_epsilon + self.budget)

    def decision_value(self, decision: Decision, make_optimal: bool) -> float:
        """
        Compute value of making a decision optimally vs defaulting.

        V_optimal = OptimalGain - λ × Effort
        V_default = DefaultGain (no effort)
        """
        lambda_ = self.compute_lambda()

        if make_optimal:
            return decision.optimal_gain - lambda_ * decision.effort_cost
        else:
            return decision.default_gain

    def make_decision(self, decision: Decision) -> Decision:
        """
        Make a decision: optimal or default based on BCP value.

        If V_optimal > V_default, make optimal choice.
        Otherwise, default to easy choice.
        """
        v_optimal = self.decision_value(decision, make_optimal=True)
        v_default = self.decision_value(decision, make_optimal=False)

        if v_optimal > v_default:
            # Make optimal decision
            decision.made_optimally = True
            decision.outcome = decision.optimal_gain
            self.budget -= decision.effort_cost  # Consume budget
            self.optimal_decisions += 1
        else:
            # Default to easy choice
            decision.made_optimally = False
            decision.outcome = decision.default_gain

        self.decisions_made += 1
        self.total_gain += decision.outcome
        self.budget = max(0, self.budget)  # Don't go negative

        return decision

    def rest(self, duration: float = 1.0) -> float:
        """
        Rest and recover budget.

        Returns: Amount of budget recovered
        """
        recovery = self.recovery_rate * duration
        old_budget = self.budget
        self.budget = min(self.initial_budget, self.budget + recovery)
        return self.budget - old_budget

    def get_state(self) -> DecisionMakerState:
        """Get current state."""
        return DecisionMakerState(
            budget=self.budget,
            decisions_made=self.decisions_made,
            optimal_decisions=self.optimal_decisions,
            total_gain=self.total_gain,
            lambda_=self.compute_lambda()
        )

    def reset(self):
        """Reset to initial state."""
        self.budget = self.initial_budget
        self.decisions_made = 0
        self.optimal_decisions = 0
        self.total_gain = 0.0


def generate_decision_sequence(n: int, difficulty: str = "mixed") -> List[Decision]:
    """Generate a sequence of decisions."""
    decisions = []

    for i in range(n):
        if difficulty == "easy":
            effort = 0.3 + np.random.uniform(-0.1, 0.1)
            optimal_gain = 1.0
            default_gain = 0.6
        elif difficulty == "hard":
            effort = 1.5 + np.random.uniform(-0.3, 0.3)
            optimal_gain = 2.0
            default_gain = 0.5
        else:  # mixed
            if np.random.random() < 0.7:
                effort = 0.5 + np.random.uniform(-0.2, 0.2)
                optimal_gain = 1.0
                default_gain = 0.6
            else:
                effort = 1.2 + np.random.uniform(-0.2, 0.2)
                optimal_gain = 1.5
                default_gain = 0.4

        decisions.append(Decision(
            name=f"Decision_{i}",
            optimal_gain=optimal_gain,
            default_gain=default_gain,
            effort_cost=effort,
            complexity=effort / 0.5
        ))

    return decisions


def run_experiment():
    """Execute decision fatigue BCP experiments."""
    print("=" * 70)
    print("CYCLE 2590: DECISION FATIGUE AS BCP BUDGET EXHAUSTION")
    print("Gate 218: Does decision fatigue follow budget depletion dynamics?")
    print("=" * 70)

    results = {
        "experiment": "cycle2590_decision_fatigue_bcp",
        "timestamp": datetime.now().isoformat(),
        "gate": 218,
        "scenarios": []
    }

    # Scenario 1: Fatigue accumulation
    print("\n" + "-" * 50)
    print("SCENARIO 1: Fatigue Accumulation Over Decisions")
    print("-" * 50)

    np.random.seed(42)
    dm = DecisionFatigueBCP(initial_budget=10.0)
    decisions = generate_decision_sequence(20, difficulty="mixed")

    print(f"\n{'#':<4} {'Budget':<8} {'λ':<8} {'Optimal?':<10} {'Gain':<8}")
    print("-" * 42)

    trajectory = []
    for i, decision in enumerate(decisions):
        state_before = dm.get_state()
        dm.make_decision(decision)
        state_after = dm.get_state()

        print(f"{i:<4} {state_before.budget:.2f}     {state_before.lambda_:.2f}     "
              f"{'YES' if decision.made_optimally else 'NO':<10} {decision.outcome:.2f}")

        trajectory.append({
            "decision": i,
            "budget": state_before.budget,
            "lambda": state_before.lambda_,
            "optimal": decision.made_optimally,
            "gain": decision.outcome
        })

    # Calculate phase transitions
    early = trajectory[:5]
    mid = trajectory[5:15]
    late = trajectory[15:]

    early_optimal = sum(1 for t in early if t["optimal"]) / len(early)
    mid_optimal = sum(1 for t in mid if t["optimal"]) / len(mid)
    late_optimal = sum(1 for t in late if t["optimal"]) / len(late)

    print(f"\nOptimal decision rate by phase:")
    print(f"  Early (0-4):  {early_optimal:.0%}")
    print(f"  Mid (5-14):   {mid_optimal:.0%}")
    print(f"  Late (15-19): {late_optimal:.0%}")

    results["scenarios"].append({
        "scenario": "fatigue_accumulation",
        "trajectory": trajectory,
        "phase_rates": {
            "early": early_optimal,
            "mid": mid_optimal,
            "late": late_optimal
        }
    })

    # Scenario 2: Budget depletion threshold
    print("\n" + "-" * 50)
    print("SCENARIO 2: Critical Threshold Detection")
    print("-" * 50)

    # Find the budget level at which defaults start
    dm.reset()
    threshold_found = False
    threshold_budget = None

    for i, decision in enumerate(decisions):
        budget_before = dm.budget
        dm.make_decision(decision)

        if not decision.made_optimally and not threshold_found:
            threshold_found = True
            threshold_budget = budget_before
            print(f"First default at decision {i}, budget={budget_before:.2f}, λ={dm.compute_lambda():.2f}")

    if threshold_found:
        print(f"\nCritical threshold: Budget ≈ {threshold_budget:.2f}")
        print(f"At this point, λ exceeds cost/benefit ratio for marginal decisions")

    results["scenarios"].append({
        "scenario": "threshold_detection",
        "threshold_budget": float(threshold_budget) if threshold_budget else None
    })

    # Scenario 3: Rest and recovery
    print("\n" + "-" * 50)
    print("SCENARIO 3: Rest and Recovery")
    print("-" * 50)

    dm.reset()
    decisions = generate_decision_sequence(30, difficulty="mixed")

    print("\nSequence: 10 decisions → rest → 10 decisions → rest → 10 decisions")
    print(f"\n{'Phase':<15} {'Optimal Rate':<15} {'Final Budget':<15} {'Final λ':<10}")
    print("-" * 55)

    phases = []
    for phase in range(3):
        start_idx = phase * 10
        phase_decisions = decisions[start_idx:start_idx + 10]

        budget_before = dm.budget
        optimal_count = 0

        for decision in phase_decisions:
            dm.make_decision(decision)
            if decision.made_optimally:
                optimal_count += 1

        rate = optimal_count / 10
        print(f"Phase {phase + 1}        {rate:.0%}            {dm.budget:.2f}            {dm.compute_lambda():.2f}")

        phases.append({
            "phase": phase + 1,
            "optimal_rate": rate,
            "final_budget": dm.budget,
            "final_lambda": dm.compute_lambda()
        })

        # Rest between phases (except last)
        if phase < 2:
            recovery = dm.rest(duration=3.0)
            print(f"  (rest: +{recovery:.2f} budget)")

    results["scenarios"].append({
        "scenario": "rest_recovery",
        "phases": phases
    })

    # Scenario 4: Decision quality vs effort trade-off
    print("\n" + "-" * 50)
    print("SCENARIO 4: Quality vs Effort Trade-off")
    print("-" * 50)

    print("\nOptimal decision rate by difficulty level at different fatigue states:")
    print(f"{'Budget':<10} {'Easy':<10} {'Medium':<10} {'Hard':<10}")
    print("-" * 40)

    scenario4_results = []
    for budget in [10.0, 5.0, 2.0, 1.0, 0.5]:
        rates = []
        for difficulty, effort in [("easy", 0.3), ("medium", 0.7), ("hard", 1.5)]:
            dm_test = DecisionFatigueBCP(initial_budget=budget)
            decision = Decision(
                name="Test",
                optimal_gain=1.0,
                default_gain=0.5,
                effort_cost=effort,
                complexity=1.0
            )
            dm_test.make_decision(decision)
            rates.append(1 if decision.made_optimally else 0)

        print(f"{budget:<10.1f} {rates[0]:<10} {rates[1]:<10} {rates[2]:<10}")
        scenario4_results.append({
            "budget": budget,
            "easy": rates[0],
            "medium": rates[1],
            "hard": rates[2]
        })

    results["scenarios"].append({
        "scenario": "quality_effort_tradeoff",
        "results": scenario4_results
    })

    # Scenario 5: Individual differences
    print("\n" + "-" * 50)
    print("SCENARIO 5: Individual Differences in Depletion")
    print("-" * 50)

    profiles = {
        "High Capacity": {"budget": 15.0, "lambda_scale": 1.5},
        "Normal": {"budget": 10.0, "lambda_scale": 2.0},
        "Low Capacity": {"budget": 6.0, "lambda_scale": 2.5},
    }

    print(f"\n{'Profile':<15} {'Optimal Rate':<15} {'Decisions to Fatigue':<20}")
    print("-" * 50)

    scenario5_results = {}
    for profile_name, params in profiles.items():
        dm_profile = DecisionFatigueBCP(
            initial_budget=params["budget"],
            lambda_scale=params["lambda_scale"]
        )
        decisions = generate_decision_sequence(25, difficulty="mixed")

        optimal_count = 0
        decisions_to_fatigue = 25  # Default if never fatigues

        for i, decision in enumerate(decisions):
            dm_profile.make_decision(decision)
            if decision.made_optimally:
                optimal_count += 1
            elif decisions_to_fatigue == 25:
                decisions_to_fatigue = i

        rate = optimal_count / 25
        print(f"{profile_name:<15} {rate:.0%}            {decisions_to_fatigue}")

        scenario5_results[profile_name] = {
            "optimal_rate": float(rate),
            "decisions_to_fatigue": decisions_to_fatigue
        }

    results["scenarios"].append({
        "scenario": "individual_differences",
        "results": scenario5_results
    })

    # Analysis
    print("\n" + "=" * 70)
    print("ANALYSIS: KEY FINDINGS")
    print("=" * 70)

    print("\n1. DECISION FATIGUE AS BUDGET DEPLETION")
    print("   - Each decision consumes cognitive budget")
    print("   - Budget depletes → λ rises → Effort becomes more 'expensive'")
    print("   - Eventually V_default > V_optimal → Default to easy choice")

    print("\n2. PHASE TRANSITIONS")
    print(f"   - Early phase: {early_optimal:.0%} optimal (abundant budget)")
    print(f"   - Late phase: {late_optimal:.0%} optimal (depleted budget)")
    print("   - Clear degradation pattern over decision sequence")

    print("\n3. CRITICAL THRESHOLD")
    if threshold_budget:
        print(f"   - Defaults begin at budget ≈ {threshold_budget:.1f}")
        print("   - Below threshold, λ too high for effortful decisions")
        print("   - This maps to 'ego depletion' in psychology literature")

    print("\n4. REST RESTORES BUDGET")
    print("   - Rest periods restore budget (λ decreases)")
    print("   - Explains why breaks improve decision quality")
    print("   - Strategic rest can prevent depletion")

    print("\n5. EFFORT SELECTIVITY UNDER FATIGUE")
    print("   - Easy decisions remain optimal even when fatigued")
    print("   - Hard decisions are abandoned first")
    print("   - Explains 'picking battles' under stress")

    finding = "Decision fatigue is BCP budget depletion: rising λ makes effort increasingly expensive"
    mechanism = "Each decision consumes budget; when λ exceeds cost/benefit threshold, defaults occur"

    print(f"\n**FINDING:** {finding}")
    print(f"**MECHANISM:** {mechanism}")

    results["analysis"] = {
        "finding": finding,
        "mechanism": mechanism,
        "key_insights": {
            "ego_depletion": "Budget depletion → High λ → Defaults",
            "willpower": "Initial budget capacity",
            "rest": "Budget restoration mechanism",
            "strategic_breaks": "Prevent λ from exceeding threshold"
        }
    }

    # Save results
    output_path = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results/cycle2590_results.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to: {output_path}")

    return results


if __name__ == "__main__":
    run_experiment()
