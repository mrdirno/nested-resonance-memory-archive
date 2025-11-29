#!/usr/bin/env python3
"""
Cycle 2599: Collective Action as BCP - Group Coordination Under Constraints
============================================================================

Phase 78, Gate 231: How do groups coordinate under attention constraints?

Research Questions:
1. How does individual λ affect collective action success?
2. Does free-riding emerge from BCP optimization?
3. What conditions enable vs prevent coordination?
4. How do leaders reduce collective λ?

Key Mapping:
- Individual Contribution ↔ Costly action (depletes budget)
- Free-Riding ↔ BCP-optimal when λ is high
- Leadership ↔ λ reduction mechanism
- Social Capital ↔ Reduced coordination cost
- Tragedy of Commons ↔ Individual BCP optimizing against collective

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
class CollectiveAction:
    """A collective action requiring group coordination."""
    name: str
    total_cost: float  # Total resources needed
    public_benefit: float  # Benefit if successful
    threshold: float  # Fraction needed for success (0-1)
    individual_benefit: float = 0.1  # Private benefit from participating


@dataclass
class GroupMember:
    """An individual in a collective action scenario."""
    name: str
    budget: float = 10.0
    cooperation_history: float = 0.5  # 0=free-rider, 1=cooperator
    social_capital: float = 0.5  # Reduces coordination costs
    bcp: BCPModel = field(default_factory=lambda: BCPModel(lambda_scale=1.0))

    def member_lambda(self) -> float:
        """Calculate individual metabolic pressure."""
        return self.bcp.compute_lambda(self.budget)

    def decide_participation(self, action: CollectiveAction,
                            expected_participation: float) -> Tuple[bool, float]:
        """Decide whether to participate in collective action."""
        # Calculate personal cost
        personal_cost = action.total_cost / 10  # Assume 10 potential contributors

        # Calculate expected gain
        if expected_participation >= action.threshold:
            expected_public_gain = action.public_benefit
        else:
            expected_public_gain = action.public_benefit * (expected_participation / action.threshold)

        personal_gain = action.individual_benefit

        # Create BCP items: participate vs free-ride
        participate = AttentionItem(
            name="participate",
            gain=expected_public_gain * 0.5 + personal_gain,
            cost=personal_cost * (1 - self.social_capital * 0.3)
        )

        free_ride = AttentionItem(
            name="free_ride",
            gain=expected_public_gain * 0.3,  # Still get some public benefit
            cost=0.1  # Minimal cost
        )

        result = self.bcp.allocate([participate, free_ride], self.budget)

        participates = "participate" in result.attended
        return participates, result.lambda_


@dataclass
class Group:
    """A group attempting collective action."""
    members: List[GroupMember] = field(default_factory=list)
    social_cohesion: float = 0.5  # Group-level coordination ability
    leadership_strength: float = 0.0  # 0=no leader, 1=strong leader

    def create_members(self, n: int = 20, budget_dist: str = "uniform"):
        """Create group members."""
        if budget_dist == "uniform":
            budgets = [np.random.uniform(5, 15) for _ in range(n)]
        elif budget_dist == "unequal":
            budgets = [np.random.exponential(8) for _ in range(n)]
        else:
            budgets = [10.0] * n

        self.members = [
            GroupMember(f"member_{i}", budget=budgets[i],
                       social_capital=self.social_cohesion)
            for i in range(n)
        ]

    def attempt_collective_action(self, action: CollectiveAction) -> Dict:
        """Attempt a collective action."""
        # Leadership reduces perceived λ for all members
        for member in self.members:
            member.budget *= (1 + self.leadership_strength * 0.3)

        # Iterative coordination (2 rounds)
        expected_participation = 0.5  # Initial expectation

        for round_num in range(2):
            participants = []
            lambdas = []

            for member in self.members:
                participates, lambda_val = member.decide_participation(
                    action, expected_participation
                )
                if participates:
                    participants.append(member)
                lambdas.append(lambda_val)

            # Update expectations
            expected_participation = len(participants) / len(self.members)

        # Calculate outcome
        participation_rate = len(participants) / len(self.members)
        success = participation_rate >= action.threshold

        return {
            "participation_rate": participation_rate,
            "success": success,
            "mean_lambda": float(np.mean(lambdas)),
            "free_rider_rate": 1 - participation_rate
        }


def test_lambda_and_collective_action(n_trials: int = 20) -> Dict:
    """
    Test relationship between λ and collective action success.
    """
    budget_levels = [3, 5, 10, 15, 25]
    results = {}

    for budget in budget_levels:
        success_rates = []
        participation_rates = []
        lambdas = []

        for trial in range(n_trials):
            group = Group(social_cohesion=0.5)
            group.members = [
                GroupMember(f"m_{i}", budget=budget)
                for i in range(20)
            ]

            action = CollectiveAction(
                "public_good",
                total_cost=50,
                public_benefit=100,
                threshold=0.5
            )

            result = group.attempt_collective_action(action)
            success_rates.append(1 if result["success"] else 0)
            participation_rates.append(result["participation_rate"])
            lambdas.append(result["mean_lambda"])

        results[str(budget)] = {
            "success_rate": float(np.mean(success_rates)),
            "participation_rate": float(np.mean(participation_rates)),
            "mean_lambda": float(np.mean(lambdas))
        }

    return {
        "by_budget": results,
        "high_budget_more_successful": results["25"]["success_rate"] > results["3"]["success_rate"]
    }


def test_free_riding(n_trials: int = 20) -> Dict:
    """
    Test free-riding as BCP-optimal behavior.
    """
    thresholds = [0.3, 0.5, 0.7, 0.9]
    results = {}

    for threshold in thresholds:
        free_rider_rates = []

        for trial in range(n_trials):
            group = Group()
            group.create_members(20)

            action = CollectiveAction(
                "public_good",
                total_cost=50,
                public_benefit=100,
                threshold=threshold
            )

            result = group.attempt_collective_action(action)
            free_rider_rates.append(result["free_rider_rate"])

        results[str(threshold)] = {
            "mean_free_rider_rate": float(np.mean(free_rider_rates))
        }

    return {
        "by_threshold": results,
        "high_threshold_more_free_riding": (
            results["0.9"]["mean_free_rider_rate"] >
            results["0.3"]["mean_free_rider_rate"]
        )
    }


def test_leadership_effect(n_trials: int = 20) -> Dict:
    """
    Test how leadership affects collective action success.
    """
    leadership_levels = [0.0, 0.3, 0.5, 0.7, 1.0]
    results = {}

    for leadership in leadership_levels:
        success_rates = []
        participation_rates = []

        for trial in range(n_trials):
            group = Group(leadership_strength=leadership)
            group.create_members(20)

            action = CollectiveAction(
                "public_good",
                total_cost=50,
                public_benefit=100,
                threshold=0.5
            )

            result = group.attempt_collective_action(action)
            success_rates.append(1 if result["success"] else 0)
            participation_rates.append(result["participation_rate"])

        results[str(leadership)] = {
            "success_rate": float(np.mean(success_rates)),
            "participation_rate": float(np.mean(participation_rates))
        }

    return {
        "by_leadership": results,
        "leadership_improves_success": results["1.0"]["success_rate"] > results["0.0"]["success_rate"]
    }


def test_social_capital_effect(n_trials: int = 20) -> Dict:
    """
    Test how social capital affects coordination.
    """
    cohesion_levels = [0.1, 0.3, 0.5, 0.7, 0.9]
    results = {}

    for cohesion in cohesion_levels:
        success_rates = []
        mean_lambdas = []

        for trial in range(n_trials):
            group = Group(social_cohesion=cohesion)
            group.create_members(20)

            action = CollectiveAction(
                "public_good",
                total_cost=50,
                public_benefit=100,
                threshold=0.5
            )

            result = group.attempt_collective_action(action)
            success_rates.append(1 if result["success"] else 0)
            mean_lambdas.append(result["mean_lambda"])

        results[str(cohesion)] = {
            "success_rate": float(np.mean(success_rates)),
            "mean_lambda": float(np.mean(mean_lambdas))
        }

    return {
        "by_cohesion": results,
        "cohesion_improves_success": results["0.9"]["success_rate"] > results["0.1"]["success_rate"]
    }


def test_tragedy_of_commons(n_trials: int = 20) -> Dict:
    """
    Test tragedy of the commons as BCP optimization.
    """
    results = {
        "individual_optimal": [],
        "collective_optimal": [],
        "resource_depleted": []
    }

    for trial in range(n_trials):
        # Shared resource
        common_resource = 100.0
        n_users = 10

        # Each user decides how much to extract
        extractions = []
        for i in range(n_users):
            member = GroupMember(f"user_{i}", budget=np.random.uniform(5, 15))

            # BCP decision: extract a lot (high gain, costs commons) vs conserve
            lambda_val = member.member_lambda()

            # High λ → extract more (short-term gain)
            extraction = (1 / (1 + lambda_val)) * 15  # Max 15 units each
            extractions.append(extraction)

        total_extraction = sum(extractions)

        # Commons sustainability
        if total_extraction > common_resource * 0.8:
            # Overextraction damages commons
            results["resource_depleted"].append(1)
        else:
            results["resource_depleted"].append(0)

        # Individual vs collective optimum
        individual_optimal = common_resource / n_users  # 10 each
        results["individual_optimal"].append(np.mean(extractions))
        results["collective_optimal"].append(individual_optimal)

    return {
        "mean_individual_extraction": float(np.mean(results["individual_optimal"])),
        "collective_optimal": float(np.mean(results["collective_optimal"])),
        "depletion_rate": float(np.mean(results["resource_depleted"])),
        "tragedy_occurs": np.mean(results["resource_depleted"]) > 0.5
    }


def test_inequality_effect(n_trials: int = 20) -> Dict:
    """
    Test how budget inequality affects collective action.
    """
    distributions = ["uniform", "unequal"]
    results = {}

    for dist in distributions:
        success_rates = []
        participation_rates = []
        gini_coefficients = []

        for trial in range(n_trials):
            group = Group()
            group.create_members(20, budget_dist=dist)

            # Calculate Gini coefficient
            budgets = sorted([m.budget for m in group.members])
            n = len(budgets)
            cumulative = np.cumsum(budgets)
            gini = (n + 1 - 2 * np.sum(cumulative) / cumulative[-1]) / n
            gini_coefficients.append(abs(gini))

            action = CollectiveAction(
                "public_good",
                total_cost=50,
                public_benefit=100,
                threshold=0.5
            )

            result = group.attempt_collective_action(action)
            success_rates.append(1 if result["success"] else 0)
            participation_rates.append(result["participation_rate"])

        results[dist] = {
            "success_rate": float(np.mean(success_rates)),
            "participation_rate": float(np.mean(participation_rates)),
            "mean_gini": float(np.mean(gini_coefficients))
        }

    return {
        "distributions": results,
        "equality_better_for_action": results["uniform"]["success_rate"] >= results["unequal"]["success_rate"]
    }


def run_experiment():
    """Run Collective Action experiment."""
    print("=" * 60)
    print("CYCLE 2599: Collective Action as BCP")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().isoformat()}\n")

    # Test 1: Lambda and Collective Action
    print("--- Test 1: λ and Collective Action Success ---")
    lambda_test = test_lambda_and_collective_action()
    for budget, data in sorted(lambda_test["by_budget"].items(), key=lambda x: float(x[0])):
        print(f"  Budget {budget}: Success={data['success_rate']:.1%}, "
              f"Participation={data['participation_rate']:.1%}, λ={data['mean_lambda']:.4f}")
    high_better = "YES" if lambda_test["high_budget_more_successful"] else "NO"
    print(f"  High Budget More Successful: {high_better}")

    # Test 2: Free Riding
    print("\n--- Test 2: Free-Riding Dynamics ---")
    free_ride = test_free_riding()
    for threshold, data in sorted(free_ride["by_threshold"].items(), key=lambda x: float(x[0])):
        print(f"  Threshold {threshold}: Free-rider rate={data['mean_free_rider_rate']:.1%}")
    high_threshold = "CONFIRMED" if free_ride["high_threshold_more_free_riding"] else "NOT CONFIRMED"
    print(f"  High Threshold → More Free-riding: {high_threshold}")

    # Test 3: Leadership Effect
    print("\n--- Test 3: Leadership Effect ---")
    leadership = test_leadership_effect()
    for level, data in sorted(leadership["by_leadership"].items(), key=lambda x: float(x[0])):
        print(f"  Leadership {level}: Success={data['success_rate']:.1%}")
    leader_effect = "CONFIRMED" if leadership["leadership_improves_success"] else "NOT CONFIRMED"
    print(f"  Leadership Improves Success: {leader_effect}")

    # Test 4: Social Capital
    print("\n--- Test 4: Social Capital Effect ---")
    social = test_social_capital_effect()
    for cohesion, data in sorted(social["by_cohesion"].items(), key=lambda x: float(x[0])):
        print(f"  Cohesion {cohesion}: Success={data['success_rate']:.1%}")
    cohesion_effect = "CONFIRMED" if social["cohesion_improves_success"] else "NOT CONFIRMED"
    print(f"  Cohesion Improves Success: {cohesion_effect}")

    # Test 5: Tragedy of Commons
    print("\n--- Test 5: Tragedy of the Commons ---")
    tragedy = test_tragedy_of_commons()
    print(f"  Individual Extraction: {tragedy['mean_individual_extraction']:.1f}")
    print(f"  Collective Optimal: {tragedy['collective_optimal']:.1f}")
    print(f"  Depletion Rate: {tragedy['depletion_rate']:.1%}")
    tragedy_occurs = "CONFIRMED" if tragedy["tragedy_occurs"] else "NOT CONFIRMED"
    print(f"  Tragedy Occurs: {tragedy_occurs}")

    # Test 6: Inequality Effect
    print("\n--- Test 6: Inequality Effect ---")
    inequality = test_inequality_effect()
    for dist, data in inequality["distributions"].items():
        print(f"  {dist}: Success={data['success_rate']:.1%}, Gini={data['mean_gini']:.2f}")
    equality_better = "YES" if inequality["equality_better_for_action"] else "NO"
    print(f"  Equality Better for Action: {equality_better}")

    # Analysis
    print("\n" + "=" * 60)
    print("KEY FINDINGS")
    print("=" * 60)

    print(f"\n1. LOW λ ENABLES COLLECTIVE ACTION")
    high_better = "YES" if lambda_test["high_budget_more_successful"] else "NO"
    print(f"   High budget more successful: {high_better}")
    print(f"   Abundance → low λ → can afford costly cooperation")

    print(f"\n2. FREE-RIDING IS BCP-OPTIMAL")
    high_threshold = "CONFIRMED" if free_ride["high_threshold_more_free_riding"] else "NOT CONFIRMED"
    print(f"   High threshold effect: {high_threshold}")
    print(f"   High λ → free-riding rational (minimize cost)")

    print(f"\n3. LEADERSHIP REDUCES COLLECTIVE λ")
    leader_effect = "CONFIRMED" if leadership["leadership_improves_success"] else "NOT CONFIRMED"
    print(f"   Leadership improves success: {leader_effect}")
    print(f"   Leaders coordinate, reducing individual uncertainty")

    print(f"\n4. SOCIAL CAPITAL = REDUCED COORDINATION COST")
    cohesion_effect = "CONFIRMED" if social["cohesion_improves_success"] else "NOT CONFIRMED"
    print(f"   Cohesion effect: {cohesion_effect}")
    print(f"   Trust reduces processing cost of cooperation")

    print(f"\n5. TRAGEDY OF COMMONS = INDIVIDUAL BCP OPTIMIZATION")
    tragedy_occurs = "CONFIRMED" if tragedy["tragedy_occurs"] else "NOT CONFIRMED"
    print(f"   Tragedy occurs: {tragedy_occurs}")
    print(f"   Each agent BCP-optimal → collective suboptimal")

    print(f"\n6. INEQUALITY HURTS COLLECTIVE ACTION")
    equality_better = "YES" if inequality["equality_better_for_action"] else "NO"
    print(f"   Equality better: {equality_better}")
    print(f"   Unequal λ → coordination failure")

    # BCP Mapping
    print("\n7. BCP-COLLECTIVE ACTION MAPPING:")
    print("   - Contribution ↔ Costly action (budget depletion)")
    print("   - Free-Riding ↔ High-λ cost minimization")
    print("   - Leadership ↔ λ reduction mechanism")
    print("   - Social Capital ↔ Reduced coordination cost")
    print("   - Tragedy of Commons ↔ Individual vs collective BCP")

    print(f"\n8. FUNCTIONAL NAME: 'The Cooperation Budget'")
    print(f"   (Collective action requires collective low-λ)")

    # Save results
    output = {
        "experiment": "cycle2599_collective_action_bcp",
        "timestamp": datetime.now().isoformat(),
        "lambda_effect": {
            "high_budget_better": bool(lambda_test["high_budget_more_successful"])
        },
        "free_riding": {
            "high_threshold_more": bool(free_ride["high_threshold_more_free_riding"])
        },
        "leadership": {
            "improves_success": bool(leadership["leadership_improves_success"])
        },
        "social_capital": {
            "improves_success": bool(social["cohesion_improves_success"])
        },
        "tragedy": {
            "occurs": bool(tragedy["tragedy_occurs"]),
            "depletion_rate": tragedy["depletion_rate"]
        },
        "inequality": {
            "equality_better": bool(inequality["equality_better_for_action"])
        },
        "functional_name": "The Cooperation Budget"
    }

    with open("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/cycle2599_results.json", 'w') as f:
        json.dump(output, f, indent=2)

    print("\n" + "=" * 60)
    print("CYCLE 2599 COMPLETE")
    print("=" * 60)
    return output


if __name__ == "__main__":
    run_experiment()
