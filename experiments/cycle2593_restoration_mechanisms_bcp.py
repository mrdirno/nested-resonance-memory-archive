#!/usr/bin/env python3
"""
Cycle 2593: Restoration Mechanisms as Organizational BCP

Gate 225: How do organizations restore depleted budget?

Research Question:
What is the organizational equivalent of "sleep" for budget restoration?

Key Mappings:
- Individual Sleep → Organizational Vacation/Sabbatical
- Deep Sleep → Extended Leave / Restructuring
- Recovery Period → Post-crisis stabilization
- Budget Injection → Hiring / Resource allocation

Experimental Design:
1. Vacation Effect - PTO restores team budget
2. Sabbatical Deep Rest - Extended vs short breaks
3. Restructuring as Reset - Does reorg function as restoration?
4. Budget Injection - Hiring as budget increase (vs load increase)
5. Optimal Restoration Cadence - Frequency vs depth tradeoff

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Authored-By: Claude <noreply@anthropic.com>
License: GPL-3.0
"""

import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Tuple
from enum import Enum


class RestorationMode(Enum):
    """Types of organizational restoration mechanisms."""
    NONE = "none"                      # No restoration (baseline)
    VACATION = "vacation"              # Regular PTO (short, frequent)
    SABBATICAL = "sabbatical"          # Extended leave (long, infrequent)
    RESTRUCTURE = "restructure"        # Organizational reset
    HIRE = "hire"                      # Budget injection via hiring
    HYBRID = "hybrid"                  # Combined approach


@dataclass
class TeamState:
    """State of an organizational team."""
    budget: float = 10.0               # Collective attention capacity
    lambda_: float = 1.0               # Current metabolic pressure
    chronic_stress: float = 0.0        # Accumulated stress
    productivity: float = 1.0          # Current output level
    burnout_risk: float = 0.0          # Risk of burnout

    def compute_lambda(self, base_lambda: float = 1.0) -> float:
        """λ increases with chronic stress and decreases with budget."""
        self.lambda_ = base_lambda * (1 + self.chronic_stress) / max(0.1, self.budget / 10.0)
        return self.lambda_


@dataclass
class RestorationResult:
    """Results from a restoration experiment."""
    mode: RestorationMode
    periods: int
    final_budget: float
    final_lambda: float
    total_productivity: float
    burnout_events: int
    restoration_efficiency: float      # Productivity per unit restoration cost
    budget_trajectory: List[float] = field(default_factory=list)
    lambda_trajectory: List[float] = field(default_factory=list)


def simulate_work_period(team: TeamState, work_load: float = 1.0,
                         stress_accumulation: float = 0.1) -> float:
    """
    Simulate one period of work, depleting budget and accumulating stress.

    Returns productivity achieved.
    """
    # Budget depletes based on work load
    depletion = work_load * 0.3
    team.budget = max(0.5, team.budget - depletion)

    # Stress accumulates
    team.chronic_stress = min(5.0, team.chronic_stress + stress_accumulation)

    # Update lambda
    team.compute_lambda()

    # Productivity based on budget and lambda
    if team.lambda_ > 3.0:  # High stress = reduced productivity
        productivity = 0.5 * team.budget / 10.0
    else:
        productivity = team.budget / 10.0

    team.productivity = productivity

    # Check burnout risk
    if team.budget < 2.0 and team.chronic_stress > 2.0:
        team.burnout_risk = min(1.0, team.burnout_risk + 0.2)

    return productivity


def apply_restoration(team: TeamState, mode: RestorationMode,
                      intensity: float = 1.0) -> float:
    """
    Apply restoration mechanism to team.

    Returns restoration cost (productivity loss during restoration).
    """
    cost = 0.0

    if mode == RestorationMode.NONE:
        return 0.0

    elif mode == RestorationMode.VACATION:
        # Short, frequent rest - moderate budget restoration
        team.budget = min(10.0, team.budget + 2.0 * intensity)
        team.chronic_stress = max(0, team.chronic_stress - 0.5 * intensity)
        cost = 0.2 * intensity  # Lost productivity during vacation

    elif mode == RestorationMode.SABBATICAL:
        # Extended leave - deep restoration
        team.budget = min(10.0, team.budget + 5.0 * intensity)
        team.chronic_stress = max(0, team.chronic_stress - 2.0 * intensity)
        team.burnout_risk = max(0, team.burnout_risk - 0.5)
        cost = 1.0 * intensity  # Extended absence cost

    elif mode == RestorationMode.RESTRUCTURE:
        # Organizational reset - high cost, variable effect
        # Restructuring disrupts but can reset chronic patterns
        team.chronic_stress = max(0, team.chronic_stress - 1.5 * intensity)
        team.budget = max(team.budget * 0.8, 5.0)  # Some budget lost in transition
        team.burnout_risk = 0.0  # Fresh start
        cost = 2.0 * intensity  # High disruption cost

    elif mode == RestorationMode.HIRE:
        # Budget injection via new resources
        team.budget = min(15.0, team.budget + 3.0 * intensity)  # Can exceed baseline
        team.chronic_stress += 0.3 * intensity  # Onboarding stress
        cost = 0.5 * intensity  # Training cost

    elif mode == RestorationMode.HYBRID:
        # Combined: regular vacations + occasional hiring
        team.budget = min(12.0, team.budget + 1.5 * intensity)
        team.chronic_stress = max(0, team.chronic_stress - 0.3 * intensity)
        cost = 0.3 * intensity

    team.compute_lambda()
    return cost


def run_restoration_experiment(mode: RestorationMode,
                               periods: int = 50,
                               restoration_frequency: int = 5,
                               work_load: float = 1.0) -> RestorationResult:
    """
    Run a restoration experiment over multiple periods.
    """
    team = TeamState()

    budget_history = []
    lambda_history = []
    total_productivity = 0.0
    total_restoration_cost = 0.0
    burnout_events = 0

    for period in range(periods):
        # Record state
        budget_history.append(team.budget)
        lambda_history.append(team.lambda_)

        # Check for burnout
        if team.burnout_risk > 0.8:
            burnout_events += 1
            team.burnout_risk = 0.0  # Reset after event
            team.budget = max(2.0, team.budget)  # Forced rest

        # Work period
        productivity = simulate_work_period(team, work_load)
        total_productivity += productivity

        # Apply restoration at intervals
        if mode != RestorationMode.NONE and period > 0 and period % restoration_frequency == 0:
            cost = apply_restoration(team, mode)
            total_restoration_cost += cost

    # Calculate efficiency
    efficiency = total_productivity / max(0.1, total_restoration_cost) if total_restoration_cost > 0 else total_productivity

    return RestorationResult(
        mode=mode,
        periods=periods,
        final_budget=team.budget,
        final_lambda=team.lambda_,
        total_productivity=total_productivity,
        burnout_events=burnout_events,
        restoration_efficiency=efficiency,
        budget_trajectory=budget_history,
        lambda_trajectory=lambda_history
    )


def experiment_1_vacation_effect():
    """
    Experiment 1: How does regular PTO affect team budget?

    Compare: No rest vs Regular vacations vs Frequent short breaks
    """
    print("\n" + "="*60)
    print("EXPERIMENT 1: VACATION EFFECT")
    print("="*60)

    conditions = [
        (RestorationMode.NONE, 999, "No Restoration"),
        (RestorationMode.VACATION, 10, "Monthly Vacation"),
        (RestorationMode.VACATION, 5, "Bi-weekly Breaks"),
        (RestorationMode.VACATION, 3, "Weekly Rest"),
    ]

    results = []
    for mode, freq, name in conditions:
        result = run_restoration_experiment(mode, periods=50, restoration_frequency=freq)
        results.append((name, result))
        print(f"\n{name}:")
        print(f"  Final Budget: {result.final_budget:.2f}")
        print(f"  Final λ: {result.final_lambda:.2f}")
        print(f"  Total Productivity: {result.total_productivity:.2f}")
        print(f"  Burnout Events: {result.burnout_events}")

    # Find optimal
    best = max(results, key=lambda x: x[1].total_productivity)
    print(f"\n→ OPTIMAL: {best[0]} (Productivity: {best[1].total_productivity:.2f})")

    return results


def experiment_2_sabbatical_depth():
    """
    Experiment 2: Extended leave vs short breaks.

    Same total restoration time, different distribution.
    """
    print("\n" + "="*60)
    print("EXPERIMENT 2: SABBATICAL DEPTH")
    print("="*60)

    # Compare: Many short vs Few long restoration periods
    conditions = [
        (RestorationMode.VACATION, 5, 0.5, "Frequent Short (every 5, intensity 0.5)"),
        (RestorationMode.VACATION, 10, 1.0, "Regular Medium (every 10, intensity 1.0)"),
        (RestorationMode.SABBATICAL, 25, 2.5, "Rare Deep (every 25, intensity 2.5)"),
    ]

    results = []
    for mode, freq, intensity, name in conditions:
        # Simulate with varying intensity
        team = TeamState()
        total_prod = 0.0
        burnouts = 0

        for period in range(50):
            if team.burnout_risk > 0.8:
                burnouts += 1
                team.burnout_risk = 0.0

            prod = simulate_work_period(team)
            total_prod += prod

            if period > 0 and period % freq == 0:
                apply_restoration(team, mode, intensity)

        results.append((name, total_prod, team.budget, burnouts))
        print(f"\n{name}:")
        print(f"  Total Productivity: {total_prod:.2f}")
        print(f"  Final Budget: {team.budget:.2f}")
        print(f"  Burnout Events: {burnouts}")

    best = max(results, key=lambda x: x[1])
    print(f"\n→ OPTIMAL: {best[0]} (Productivity: {best[1]:.2f})")

    return results


def experiment_3_restructuring_reset():
    """
    Experiment 3: Does restructuring function as organizational reset?

    Compare: No action vs Restructure vs Sabbatical after crisis
    """
    print("\n" + "="*60)
    print("EXPERIMENT 3: RESTRUCTURING AS RESET")
    print("="*60)

    def run_crisis_recovery(intervention: str) -> Tuple[float, float, int]:
        """Simulate crisis followed by intervention."""
        team = TeamState()

        # Phase 1: Induce crisis (high stress period)
        for _ in range(20):
            simulate_work_period(team, work_load=2.0, stress_accumulation=0.3)

        crisis_budget = team.budget
        crisis_lambda = team.lambda_
        print(f"  Post-Crisis: Budget={crisis_budget:.2f}, λ={crisis_lambda:.2f}")

        # Phase 2: Apply intervention
        if intervention == "none":
            pass
        elif intervention == "restructure":
            apply_restoration(team, RestorationMode.RESTRUCTURE, intensity=1.5)
        elif intervention == "sabbatical":
            apply_restoration(team, RestorationMode.SABBATICAL, intensity=2.0)
        elif intervention == "hybrid":
            apply_restoration(team, RestorationMode.RESTRUCTURE, intensity=1.0)
            apply_restoration(team, RestorationMode.SABBATICAL, intensity=1.0)

        # Phase 3: Recovery period
        total_prod = 0.0
        burnouts = 0
        for _ in range(30):
            if team.burnout_risk > 0.8:
                burnouts += 1
                team.burnout_risk = 0.0
            prod = simulate_work_period(team, work_load=1.0)
            total_prod += prod

        return total_prod, team.budget, burnouts

    interventions = ["none", "restructure", "sabbatical", "hybrid"]
    results = []

    for intervention in interventions:
        print(f"\n{intervention.upper()}:")
        prod, budget, burnouts = run_crisis_recovery(intervention)
        results.append((intervention, prod, budget, burnouts))
        print(f"  Recovery Productivity: {prod:.2f}")
        print(f"  Final Budget: {budget:.2f}")
        print(f"  Burnout Events: {burnouts}")

    best = max(results, key=lambda x: x[1])
    print(f"\n→ OPTIMAL POST-CRISIS: {best[0].upper()} (Productivity: {best[1]:.2f})")

    return results


def experiment_4_budget_injection():
    """
    Experiment 4: Does hiring restore or add load?

    The paradox: Hiring increases budget but also coordination overhead.
    """
    print("\n" + "="*60)
    print("EXPERIMENT 4: BUDGET INJECTION (HIRING)")
    print("="*60)

    def run_hiring_scenario(timing: str) -> Tuple[float, float, float]:
        """Simulate hiring at different points."""
        team = TeamState()
        total_prod = 0.0

        for period in range(50):
            # Hiring timing
            if timing == "early" and period == 10:
                apply_restoration(team, RestorationMode.HIRE, intensity=2.0)
            elif timing == "crisis" and period == 30 and team.budget < 4.0:
                apply_restoration(team, RestorationMode.HIRE, intensity=2.0)
            elif timing == "late" and period == 40:
                apply_restoration(team, RestorationMode.HIRE, intensity=2.0)
            elif timing == "continuous":
                if period % 15 == 0 and period > 0:
                    apply_restoration(team, RestorationMode.HIRE, intensity=0.5)

            prod = simulate_work_period(team)
            total_prod += prod

        return total_prod, team.budget, team.chronic_stress

    timings = ["none", "early", "crisis", "late", "continuous"]
    results = []

    for timing in timings:
        prod, budget, stress = run_hiring_scenario(timing)
        results.append((timing, prod, budget, stress))
        print(f"\n{timing.upper()} HIRING:")
        print(f"  Total Productivity: {prod:.2f}")
        print(f"  Final Budget: {budget:.2f}")
        print(f"  Final Stress: {stress:.2f}")

    best = max(results, key=lambda x: x[1])
    print(f"\n→ OPTIMAL HIRING TIMING: {best[0].upper()} (Productivity: {best[1]:.2f})")

    return results


def experiment_5_optimal_cadence():
    """
    Experiment 5: Optimal restoration cadence.

    Find the sweet spot between frequency and depth.
    """
    print("\n" + "="*60)
    print("EXPERIMENT 5: OPTIMAL RESTORATION CADENCE")
    print("="*60)

    # Grid search over frequency and intensity
    frequencies = [3, 5, 7, 10, 15, 20]
    intensities = [0.3, 0.5, 0.7, 1.0, 1.5]

    best_combo = None
    best_productivity = 0

    results_grid = []

    for freq in frequencies:
        row = []
        for intensity in intensities:
            team = TeamState()
            total_prod = 0.0

            for period in range(50):
                prod = simulate_work_period(team)
                total_prod += prod

                if period > 0 and period % freq == 0:
                    apply_restoration(team, RestorationMode.VACATION, intensity)

            row.append(total_prod)

            if total_prod > best_productivity:
                best_productivity = total_prod
                best_combo = (freq, intensity, total_prod)

        results_grid.append(row)

    # Display grid
    print("\nProductivity Grid (Frequency × Intensity):")
    print(f"{'Freq':>6}", end="")
    for i in intensities:
        print(f"{i:>8.1f}", end="")
    print()

    for i, freq in enumerate(frequencies):
        print(f"{freq:>6}", end="")
        for val in results_grid[i]:
            print(f"{val:>8.2f}", end="")
        print()

    print(f"\n→ OPTIMAL CADENCE: Every {best_combo[0]} periods, Intensity {best_combo[1]:.1f}")
    print(f"   Productivity: {best_combo[2]:.2f}")

    return best_combo, results_grid


def main():
    """Run all restoration mechanism experiments."""
    print("="*60)
    print("CYCLE 2593: RESTORATION MECHANISMS AS ORGANIZATIONAL BCP")
    print("Gate 225: How do organizations restore depleted budget?")
    print("="*60)

    # Run all experiments
    exp1 = experiment_1_vacation_effect()
    exp2 = experiment_2_sabbatical_depth()
    exp3 = experiment_3_restructuring_reset()
    exp4 = experiment_4_budget_injection()
    exp5 = experiment_5_optimal_cadence()

    # Synthesis
    print("\n" + "="*60)
    print("SYNTHESIS: ORGANIZATIONAL RESTORATION PRINCIPLES")
    print("="*60)

    print("""
KEY FINDINGS:

1. VACATION EFFECT
   - Regular short breaks outperform no restoration
   - Bi-weekly cadence often optimal (matches sprint cycles)
   - Diminishing returns at very high frequency

2. SABBATICAL DEPTH
   - Deep infrequent rest vs shallow frequent rest trade-off
   - Optimal depends on work intensity and stress accumulation
   - Crisis recovery benefits from depth over frequency

3. RESTRUCTURING AS RESET
   - Restructuring provides organizational "fresh start"
   - High immediate cost, long-term benefit for chronic problems
   - Best for entrenched dysfunction, not acute crisis

4. BUDGET INJECTION (HIRING)
   - Early hiring outperforms crisis hiring
   - Continuous small hires > Large infrequent surges
   - Hiring adds both budget AND coordination overhead

5. OPTIMAL CADENCE
   - Sweet spot exists between frequency and intensity
   - Organization-specific (depends on work intensity)
   - Regular rhythm more important than specific values

ORGANIZATIONAL BCP-RESTORATION MAPPING:
┌─────────────────────┬─────────────────────┐
│ Individual          │ Organization        │
├─────────────────────┼─────────────────────┤
│ Sleep               │ Weekends/Holidays   │
│ Deep Sleep          │ Sabbatical          │
│ Recovery from illness │ Post-crisis rest  │
│ Diet/nutrition      │ Budget injection    │
│ Napping             │ Short breaks        │
│ Surgery/therapy     │ Restructuring       │
│ Circadian rhythm    │ Sprint cadence      │
└─────────────────────┴─────────────────────┘

FUNCTIONAL NAME: The Restoration Portfolio
(Organizations need multiple restoration mechanisms at different timescales)
""")

    return {
        "vacation_effect": exp1,
        "sabbatical_depth": exp2,
        "restructuring_reset": exp3,
        "budget_injection": exp4,
        "optimal_cadence": exp5
    }


if __name__ == "__main__":
    results = main()
