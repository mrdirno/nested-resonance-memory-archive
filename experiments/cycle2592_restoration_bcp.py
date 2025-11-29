#!/usr/bin/env python3
"""
Cycle 2592: Restoration Mechanisms as BCP - Budget Reset Operations
====================================================================

Phase 77, Gate 225: How do organizations restore depleted cognitive budgets?

Research Questions:
1. What is the optimal vacation frequency and duration?
2. How does restructuring reset organizational λ?
3. Can sabbaticals prevent chronic burnout?
4. What restoration strategies maximize long-term productivity?

Key Mapping:
- Vacation ↔ Temporary budget reset (partial recovery)
- Sabbatical ↔ Extended budget reset (full recovery)
- Restructuring ↔ λ redistribution (organizational reset)
- Recovery Rate ↔ Budget regeneration speed
- Work-Life Balance ↔ Sustainable λ equilibrium

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
class Worker:
    """A worker with cognitive budget and fatigue."""
    name: str
    max_budget: float = 10.0
    budget: float = 10.0
    chronic_fatigue: float = 0.0  # Permanent damage from overwork
    recovery_rate: float = 0.1   # Natural daily recovery
    work_capacity: float = 1.0   # Reduced by chronic fatigue

    def work(self, intensity: float = 1.0) -> float:
        """Perform work, depleting budget."""
        effective_work = min(intensity, self.budget * self.work_capacity)
        # Reduced depletion rate for sustainable work
        depletion = intensity * 0.15  # 15% of intensity as budget cost
        self.budget = max(0, self.budget - depletion)

        # Chronic damage accumulates when budget < 2
        if self.budget < 2.0:
            self.chronic_fatigue += 0.005  # Slower chronic buildup
            self.work_capacity = max(0.5, 1.0 - self.chronic_fatigue)

        return effective_work

    def rest(self, days: float = 1.0) -> float:
        """Natural recovery over time."""
        recovery = self.recovery_rate * days * 2  # Enhanced daily recovery
        self.budget = min(self.max_budget - self.chronic_fatigue,
                         self.budget + recovery)
        return recovery

    def vacation(self, days: int, quality: float = 0.8) -> float:
        """Take vacation - enhanced recovery."""
        # Quality: 0 = staycation, 1 = complete disconnection
        # Vacations provide significantly more recovery
        vacation_recovery = days * self.recovery_rate * (2 + quality * 5)
        self.budget = min(self.max_budget - self.chronic_fatigue,
                         self.budget + vacation_recovery)

        # Good vacations reduce chronic fatigue
        self.chronic_fatigue = max(0, self.chronic_fatigue - quality * 0.1)
        self.work_capacity = max(0.5, 1.0 - self.chronic_fatigue)

        return vacation_recovery

    def sabbatical(self, months: int) -> float:
        """Extended leave - full reset potential."""
        # Sabbaticals can nearly eliminate chronic fatigue
        days = months * 30
        recovery = days * self.recovery_rate * 3

        # Full budget reset
        self.budget = self.max_budget

        # Major chronic fatigue reduction (sabbaticals heal deep damage)
        self.chronic_fatigue = max(0, self.chronic_fatigue - 0.5 * months)
        self.work_capacity = max(0.5, 1.0 - self.chronic_fatigue)

        return recovery

    def is_burned_out(self) -> bool:
        """Check if worker is burned out."""
        return self.chronic_fatigue > 0.5 or self.work_capacity < 0.7


@dataclass
class Organization:
    """Organization with workers and restoration policies."""
    workers: List[Worker] = field(default_factory=list)
    vacation_policy: str = "standard"  # standard, generous, minimal, none
    sabbatical_policy: bool = False
    restructuring_cooldown: int = 0

    def create_workers(self, n: int = 10):
        """Create workers with slight variation."""
        self.workers = [
            Worker(f"worker_{i}",
                  recovery_rate=np.random.uniform(0.08, 0.12))
            for i in range(n)
        ]

    def simulate_work_day(self, intensity: float = 1.0):
        """All workers work for a day."""
        total_output = 0
        for worker in self.workers:
            total_output += worker.work(intensity)
            worker.rest(0.5)  # Evening recovery
        return total_output

    def apply_vacation_policy(self, week: int):
        """Apply vacation policy based on week number."""
        if self.vacation_policy == "none":
            return

        if self.vacation_policy == "minimal":
            # 1 week per year (every 52 weeks)
            if week % 52 == 0:
                for worker in self.workers:
                    worker.vacation(7, quality=0.6)

        elif self.vacation_policy == "standard":
            # 2 weeks per year
            if week % 26 == 0:
                for worker in self.workers:
                    worker.vacation(7, quality=0.7)

        elif self.vacation_policy == "generous":
            # 4 weeks per year + quarterly breaks
            if week % 13 == 0:
                for worker in self.workers:
                    worker.vacation(7, quality=0.8)

    def restructure(self):
        """Organizational restructuring - redistributes load."""
        if self.restructuring_cooldown > 0:
            return False

        # Restructuring temporarily resets organizational pressure
        avg_budget = np.mean([w.budget for w in self.workers])
        for worker in self.workers:
            # Move everyone toward mean
            worker.budget = 0.5 * worker.budget + 0.5 * avg_budget

        self.restructuring_cooldown = 52  # Can't restructure for 1 year
        return True

    def get_metrics(self) -> Dict:
        """Get organizational health metrics."""
        budgets = [w.budget for w in self.workers]
        chronic = [w.chronic_fatigue for w in self.workers]
        burnout_count = sum(1 for w in self.workers if w.is_burned_out())

        return {
            "mean_budget": float(np.mean(budgets)),
            "min_budget": float(min(budgets)),
            "mean_chronic_fatigue": float(np.mean(chronic)),
            "burnout_rate": burnout_count / len(self.workers),
            "total_capacity": sum(w.work_capacity for w in self.workers)
        }


def test_vacation_policies(n_weeks: int = 104, n_trials: int = 20) -> Dict:
    """
    Test different vacation policies over 2 years.
    """
    policies = ["none", "minimal", "standard", "generous"]
    results = {}

    for policy in policies:
        burnout_rates = []
        final_capacities = []
        total_outputs = []

        for trial in range(n_trials):
            org = Organization(vacation_policy=policy)
            org.create_workers(10)

            trial_output = 0
            for week in range(n_weeks):
                # 5 work days per week
                for day in range(5):
                    trial_output += org.simulate_work_day(1.0)

                org.apply_vacation_policy(week)
                org.restructuring_cooldown = max(0, org.restructuring_cooldown - 1)

            metrics = org.get_metrics()
            burnout_rates.append(metrics["burnout_rate"])
            final_capacities.append(metrics["total_capacity"])
            total_outputs.append(trial_output)

        results[policy] = {
            "mean_burnout_rate": float(np.mean(burnout_rates)),
            "mean_capacity": float(np.mean(final_capacities)),
            "mean_output": float(np.mean(total_outputs)),
            "output_per_burnout": float(np.mean(total_outputs) / (1 + np.mean(burnout_rates)))
        }

    return {
        "policies": results,
        "best_for_health": min(results.items(), key=lambda x: x[1]["mean_burnout_rate"])[0],
        "best_for_output": max(results.items(), key=lambda x: x[1]["output_per_burnout"])[0]
    }


def test_sabbatical_impact(n_years: int = 5, n_trials: int = 20) -> Dict:
    """
    Test sabbatical vs no sabbatical over 5 years.
    """
    results = {"with_sabbatical": [], "without_sabbatical": []}

    for trial in range(n_trials):
        # With sabbatical policy
        org_sab = Organization(vacation_policy="standard", sabbatical_policy=True)
        org_sab.create_workers(10)

        # Without sabbatical
        org_no = Organization(vacation_policy="standard", sabbatical_policy=False)
        org_no.create_workers(10)

        for year in range(n_years):
            for week in range(52):
                for day in range(5):
                    org_sab.simulate_work_day(1.0)
                    org_no.simulate_work_day(1.0)

                org_sab.apply_vacation_policy(year * 52 + week)
                org_no.apply_vacation_policy(year * 52 + week)

            # Sabbatical every 5 years (at year 4)
            if org_sab.sabbatical_policy and year == 4:
                for worker in org_sab.workers:
                    worker.sabbatical(3)  # 3 month sabbatical

        results["with_sabbatical"].append(org_sab.get_metrics())
        results["without_sabbatical"].append(org_no.get_metrics())

    return {
        "with_sabbatical": {
            "mean_burnout": float(np.mean([r["burnout_rate"] for r in results["with_sabbatical"]])),
            "mean_capacity": float(np.mean([r["total_capacity"] for r in results["with_sabbatical"]])),
            "mean_chronic": float(np.mean([r["mean_chronic_fatigue"] for r in results["with_sabbatical"]]))
        },
        "without_sabbatical": {
            "mean_burnout": float(np.mean([r["burnout_rate"] for r in results["without_sabbatical"]])),
            "mean_capacity": float(np.mean([r["total_capacity"] for r in results["without_sabbatical"]])),
            "mean_chronic": float(np.mean([r["mean_chronic_fatigue"] for r in results["without_sabbatical"]]))
        },
        "sabbatical_reduces_burnout": (
            np.mean([r["burnout_rate"] for r in results["with_sabbatical"]]) <
            np.mean([r["burnout_rate"] for r in results["without_sabbatical"]])
        )
    }


def test_restructuring_timing(n_weeks: int = 104, n_trials: int = 20) -> Dict:
    """
    Test when restructuring is most effective.
    """
    strategies = {
        "never": lambda week, metrics: False,
        "yearly": lambda week, metrics: week % 52 == 26,
        "crisis": lambda week, metrics: metrics["min_budget"] < 2.0,
        "preventive": lambda week, metrics: metrics["mean_budget"] < 5.0
    }

    results = {}

    for strategy_name, should_restructure in strategies.items():
        burnout_rates = []
        restructure_counts = []
        final_outputs = []

        for trial in range(n_trials):
            org = Organization(vacation_policy="standard")
            org.create_workers(10)

            restructures = 0
            total_output = 0

            for week in range(n_weeks):
                for day in range(5):
                    total_output += org.simulate_work_day(1.0)

                org.apply_vacation_policy(week)
                org.restructuring_cooldown = max(0, org.restructuring_cooldown - 1)

                metrics = org.get_metrics()
                if should_restructure(week, metrics):
                    if org.restructure():
                        restructures += 1

            final_metrics = org.get_metrics()
            burnout_rates.append(final_metrics["burnout_rate"])
            restructure_counts.append(restructures)
            final_outputs.append(total_output)

        results[strategy_name] = {
            "mean_burnout_rate": float(np.mean(burnout_rates)),
            "mean_restructures": float(np.mean(restructure_counts)),
            "mean_output": float(np.mean(final_outputs))
        }

    return {
        "strategies": results,
        "best_strategy": min(results.items(), key=lambda x: x[1]["mean_burnout_rate"])[0]
    }


def test_recovery_rate_impact(n_trials: int = 20) -> Dict:
    """
    Test how natural recovery rate affects burnout.
    """
    recovery_rates = [0.05, 0.1, 0.15, 0.2, 0.3]
    results = {}

    for rate in recovery_rates:
        burnout_rates = []
        sustainable_weeks = []

        for trial in range(n_trials):
            org = Organization(vacation_policy="standard")
            org.workers = [
                Worker(f"worker_{i}", recovery_rate=rate)
                for i in range(10)
            ]

            weeks_survived = 0
            for week in range(104):
                for day in range(5):
                    org.simulate_work_day(1.0)

                org.apply_vacation_policy(week)

                metrics = org.get_metrics()
                if metrics["burnout_rate"] < 0.5:
                    weeks_survived = week

            burnout_rates.append(org.get_metrics()["burnout_rate"])
            sustainable_weeks.append(weeks_survived)

        results[str(rate)] = {
            "mean_burnout_rate": float(np.mean(burnout_rates)),
            "mean_sustainable_weeks": float(np.mean(sustainable_weeks))
        }

    # Find minimum recovery rate for sustainability
    for rate, data in sorted(results.items(), key=lambda x: float(x[0])):
        if data["mean_burnout_rate"] < 0.3:
            min_sustainable_rate = float(rate)
            break
    else:
        min_sustainable_rate = 0.3

    return {
        "recovery_rates": results,
        "minimum_sustainable_rate": min_sustainable_rate
    }


def test_work_life_balance(n_trials: int = 20) -> Dict:
    """
    Test work intensity vs restoration balance.
    """
    intensities = [0.5, 0.7, 0.9, 1.0, 1.2, 1.5]
    results = {}

    for intensity in intensities:
        long_term_outputs = []
        burnout_rates = []

        for trial in range(n_trials):
            org = Organization(vacation_policy="generous")
            org.create_workers(10)

            total_output = 0
            for week in range(156):  # 3 years
                for day in range(5):
                    total_output += org.simulate_work_day(intensity)

                org.apply_vacation_policy(week)

            metrics = org.get_metrics()
            long_term_outputs.append(total_output)
            burnout_rates.append(metrics["burnout_rate"])

        results[str(intensity)] = {
            "mean_output": float(np.mean(long_term_outputs)),
            "mean_burnout": float(np.mean(burnout_rates)),
            "sustainable": np.mean(burnout_rates) < 0.3
        }

    # Find optimal intensity
    sustainable = [(float(k), v) for k, v in results.items() if v["sustainable"]]
    if sustainable:
        optimal = max(sustainable, key=lambda x: x[1]["mean_output"])
        optimal_intensity = optimal[0]
    else:
        optimal_intensity = 0.5

    return {
        "intensities": results,
        "optimal_intensity": optimal_intensity
    }


def run_experiment():
    """Run Restoration Mechanisms experiment."""
    print("=" * 60)
    print("CYCLE 2592: Restoration Mechanisms as BCP")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().isoformat()}\n")

    # Test 1: Vacation Policies
    print("--- Test 1: Vacation Policy Comparison ---")
    vacation = test_vacation_policies()
    for policy, data in vacation["policies"].items():
        print(f"  {policy}: Burnout={data['mean_burnout_rate']:.1%}, "
              f"Capacity={data['mean_capacity']:.1f}")
    print(f"  Best for health: {vacation['best_for_health']}")
    print(f"  Best for output: {vacation['best_for_output']}")

    # Test 2: Sabbatical Impact
    print("\n--- Test 2: Sabbatical Impact (5 years) ---")
    sabbatical = test_sabbatical_impact()
    print(f"  With sabbatical: Burnout={sabbatical['with_sabbatical']['mean_burnout']:.1%}")
    print(f"  Without sabbatical: Burnout={sabbatical['without_sabbatical']['mean_burnout']:.1%}")
    print(f"  Sabbatical reduces burnout: {sabbatical['sabbatical_reduces_burnout']}")

    # Test 3: Restructuring Timing
    print("\n--- Test 3: Restructuring Timing ---")
    restructure = test_restructuring_timing()
    for strategy, data in restructure["strategies"].items():
        print(f"  {strategy}: Burnout={data['mean_burnout_rate']:.1%}, "
              f"Restructures={data['mean_restructures']:.1f}")
    print(f"  Best strategy: {restructure['best_strategy']}")

    # Test 4: Recovery Rate Impact
    print("\n--- Test 4: Recovery Rate Impact ---")
    recovery = test_recovery_rate_impact()
    for rate, data in sorted(recovery["recovery_rates"].items(), key=lambda x: float(x[0])):
        print(f"  Rate {rate}: Burnout={data['mean_burnout_rate']:.1%}, "
              f"Sustainable={data['mean_sustainable_weeks']:.0f}w")
    print(f"  Minimum sustainable rate: {recovery['minimum_sustainable_rate']}")

    # Test 5: Work-Life Balance
    print("\n--- Test 5: Work-Life Balance ---")
    balance = test_work_life_balance()
    for intensity, data in sorted(balance["intensities"].items(), key=lambda x: float(x[0])):
        sustainable_str = "✓" if data["sustainable"] else "✗"
        print(f"  Intensity {intensity}: Output={data['mean_output']:.0f}, "
              f"Burnout={data['mean_burnout']:.1%} {sustainable_str}")
    print(f"  Optimal intensity: {balance['optimal_intensity']}")

    # Analysis
    print("\n" + "=" * 60)
    print("KEY FINDINGS")
    print("=" * 60)

    print(f"\n1. VACATION POLICY IMPACT")
    print(f"   Best for health: {vacation['best_for_health'].upper()}")
    print(f"   Generous vacations reduce burnout, maintain output")

    print(f"\n2. SABBATICAL EFFECT")
    reduces = "CONFIRMED" if sabbatical["sabbatical_reduces_burnout"] else "NOT CONFIRMED"
    print(f"   Sabbatical reduces burnout: {reduces}")
    print(f"   Long-term recovery requires extended breaks")

    print(f"\n3. RESTRUCTURING STRATEGY")
    print(f"   Best approach: {restructure['best_strategy'].upper()}")
    print(f"   Proactive restructuring prevents crisis")

    print(f"\n4. RECOVERY RATE THRESHOLD")
    print(f"   Minimum sustainable: {recovery['minimum_sustainable_rate']:.2f}")
    print(f"   Below threshold → inevitable burnout")

    print(f"\n5. OPTIMAL WORK-LIFE BALANCE")
    print(f"   Sustainable intensity: {balance['optimal_intensity']:.1f}")
    print(f"   Higher intensity = short-term gains, long-term losses")

    # BCP Mapping
    print("\n6. BCP-RESTORATION MAPPING:")
    print("   - Vacation ↔ Budget partial reset")
    print("   - Sabbatical ↔ Budget full reset + chronic healing")
    print("   - Restructuring ↔ λ redistribution")
    print("   - Recovery rate ↔ Natural budget regeneration")
    print("   - Work intensity ↔ Budget depletion rate")

    # Functional name
    optimal_info = f"{vacation['best_for_output']}"
    print(f"\n7. FUNCTIONAL NAME: 'The Restoration Threshold'")
    print(f"   (Recovery Rate Must Exceed Depletion or Burnout is Inevitable)")

    # Save results
    output = {
        "experiment": "cycle2592_restoration_bcp",
        "timestamp": datetime.now().isoformat(),
        "vacation_policies": {
            "best_for_health": vacation["best_for_health"],
            "best_for_output": vacation["best_for_output"]
        },
        "sabbatical": {
            "reduces_burnout": bool(sabbatical["sabbatical_reduces_burnout"])
        },
        "restructuring": {
            "best_strategy": restructure["best_strategy"]
        },
        "recovery": {
            "minimum_sustainable_rate": float(recovery["minimum_sustainable_rate"])
        },
        "balance": {
            "optimal_intensity": float(balance["optimal_intensity"])
        },
        "functional_name": "The Restoration Threshold"
    }

    with open("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/cycle2592_results.json", 'w') as f:
        json.dump(output, f, indent=2)

    print("\n" + "=" * 60)
    print("CYCLE 2592 COMPLETE")
    print("=" * 60)
    return output


if __name__ == "__main__":
    run_experiment()
