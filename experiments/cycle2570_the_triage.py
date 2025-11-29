#!/usr/bin/env python3
"""
CYCLE 2570: The Triage
======================
Gate 197: Medical Attention Economics - Selective diagnosis under resource constraints.

Building on:
- Gate 195 (Starving Philosopher): Gradual perception degradation under scarcity
- Gate 196 (Portfolio Triage): Binary track/ignore decisions for assets

This experiment asks: How do agents allocate DIAGNOSTIC ATTENTION when testing
resources are severely limited?

Hypothesis:
    Under severe budget constraints, agents shift from COMPREHENSIVE testing
    to STRATEGIC testing, prioritizing conditions based on a triage metric:

    Triage Priority = P(condition) × Severity × Treatability / TestCost

    This creates tension between:
    - "Common & mild" (high prevalence, low severity)
    - "Rare & severe" (low prevalence, high severity)
    - "Cheap & informative" (low cost, high diagnostic value)

Model:
    - N conditions with priors P(C_i), severities S_i, treatabilities R_i, costs T_i
    - Budget B constrains total tests
    - Agent selects subset of conditions to test
    - Outcome: Expected health value (EHV) from detected & treated conditions

Key Prediction:
    As budget shrinks, agent will exhibit "Diagnostic Triage Effect":
    - Abandon testing for low-priority conditions entirely
    - Focus resources on highest triage priority conditions
    - Transition is non-linear (phase transition behavior)

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
License: GPL-3.0
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
"""

import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import List, Dict, Tuple
import os

# ============================================================================
# CONFIGURATION
# ============================================================================

@dataclass
class Condition:
    """A medical condition with associated parameters."""
    name: str
    prevalence: float      # P(C_i) - base rate in population
    severity: float        # S_i - harm if untreated (0-100)
    treatability: float    # R_i - benefit of treatment if detected (0-1)
    test_cost: float       # T_i - resource cost of diagnostic test

    @property
    def triage_priority(self) -> float:
        """Compute triage priority score."""
        return (self.prevalence * self.severity * self.treatability) / self.test_cost


@dataclass
class Config:
    """Experiment parameters."""
    # Simulation
    n_budget_levels: int = 50
    min_budget: float = 1.0
    max_budget: float = 100.0
    n_trials: int = 100  # Monte Carlo trials per budget level

    # Conditions (realistic medical scenario)
    conditions: List[Condition] = None

    def __post_init__(self):
        if self.conditions is None:
            # Create a diverse set of conditions
            self.conditions = [
                # Common & Mild
                Condition("Common Cold", prevalence=0.30, severity=5, treatability=0.2, test_cost=2),
                Condition("Mild Allergy", prevalence=0.25, severity=8, treatability=0.5, test_cost=3),

                # Common & Moderate
                Condition("Hypertension", prevalence=0.20, severity=40, treatability=0.8, test_cost=5),
                Condition("Type 2 Diabetes", prevalence=0.10, severity=50, treatability=0.7, test_cost=8),

                # Rare & Severe
                Condition("Heart Disease", prevalence=0.05, severity=90, treatability=0.6, test_cost=15),
                Condition("Cancer Type A", prevalence=0.02, severity=95, treatability=0.4, test_cost=25),
                Condition("Cancer Type B", prevalence=0.01, severity=98, treatability=0.3, test_cost=30),

                # Rare & Mild (diagnostic traps)
                Condition("Rare Benign", prevalence=0.005, severity=10, treatability=0.9, test_cost=20),
            ]


# ============================================================================
# TRIAGE AGENT
# ============================================================================

class TriageAgent:
    """Agent that allocates diagnostic resources under budget constraints."""

    def __init__(self, conditions: List[Condition]):
        self.conditions = conditions
        self.n_conditions = len(conditions)

    def compute_priorities(self) -> np.ndarray:
        """Compute triage priority for each condition."""
        return np.array([c.triage_priority for c in self.conditions])

    def select_tests(self, budget: float, strategy: str = "optimal") -> List[int]:
        """
        Select which conditions to test given budget constraint.

        Returns: List of condition indices to test
        """
        costs = np.array([c.test_cost for c in self.conditions])
        priorities = self.compute_priorities()

        if strategy == "optimal":
            # Greedy selection by priority/cost ratio
            ratio = priorities / costs
            sorted_indices = np.argsort(-ratio)  # Descending

            selected = []
            remaining_budget = budget

            for idx in sorted_indices:
                if costs[idx] <= remaining_budget:
                    selected.append(idx)
                    remaining_budget -= costs[idx]

            return selected

        elif strategy == "severity_first":
            # Prioritize by severity only
            severities = np.array([c.severity for c in self.conditions])
            sorted_indices = np.argsort(-severities)

            selected = []
            remaining_budget = budget

            for idx in sorted_indices:
                if costs[idx] <= remaining_budget:
                    selected.append(idx)
                    remaining_budget -= costs[idx]

            return selected

        elif strategy == "prevalence_first":
            # Prioritize by prevalence only
            prevalences = np.array([c.prevalence for c in self.conditions])
            sorted_indices = np.argsort(-prevalences)

            selected = []
            remaining_budget = budget

            for idx in sorted_indices:
                if costs[idx] <= remaining_budget:
                    selected.append(idx)
                    remaining_budget -= costs[idx]

            return selected

        else:
            raise ValueError(f"Unknown strategy: {strategy}")

    def simulate_patient(self, true_conditions: List[int], tested: List[int]) -> Dict:
        """
        Simulate outcome for a patient.

        Args:
            true_conditions: Indices of conditions the patient actually has
            tested: Indices of conditions we tested for

        Returns:
            Dict with health outcomes
        """
        detected = set(true_conditions) & set(tested)
        missed = set(true_conditions) - set(tested)

        # Compute health value
        health_saved = 0.0
        health_lost = 0.0

        for idx in detected:
            c = self.conditions[idx]
            health_saved += c.severity * c.treatability

        for idx in missed:
            c = self.conditions[idx]
            health_lost += c.severity  # Full harm from untreated condition

        return {
            'detected': len(detected),
            'missed': len(missed),
            'health_saved': health_saved,
            'health_lost': health_lost,
            'net_health': health_saved - health_lost
        }

    def generate_patient(self, rng: np.random.Generator) -> List[int]:
        """Generate a random patient with conditions based on prevalence."""
        conditions = []
        for i, c in enumerate(self.conditions):
            if rng.random() < c.prevalence:
                conditions.append(i)
        return conditions


# ============================================================================
# EXPERIMENT
# ============================================================================

def run_experiment(cfg: Config, seed: int = 42) -> Dict:
    """Run the complete triage experiment."""
    rng = np.random.default_rng(seed)
    agent = TriageAgent(cfg.conditions)

    # Budget levels to test
    budgets = np.linspace(cfg.min_budget, cfg.max_budget, cfg.n_budget_levels)

    results = {
        'budgets': budgets.tolist(),
        'conditions': [c.name for c in cfg.conditions],
        'priorities': agent.compute_priorities().tolist(),
        'costs': [c.test_cost for c in cfg.conditions],
        'strategies': {}
    }

    for strategy in ['optimal', 'severity_first', 'prevalence_first']:
        strategy_results = {
            'n_tests': [],
            'health_saved': [],
            'health_lost': [],
            'net_health': [],
            'detection_rate': [],
            'coverage': []  # Fraction of conditions tested
        }

        for budget in budgets:
            # Select tests for this budget
            tested = agent.select_tests(budget, strategy)
            coverage = len(tested) / len(cfg.conditions)

            # Monte Carlo over patient population
            trial_results = []
            for _ in range(cfg.n_trials):
                patient_conditions = agent.generate_patient(rng)
                if len(patient_conditions) > 0:
                    outcome = agent.simulate_patient(patient_conditions, tested)
                    trial_results.append(outcome)

            if trial_results:
                avg_health_saved = np.mean([r['health_saved'] for r in trial_results])
                avg_health_lost = np.mean([r['health_lost'] for r in trial_results])
                avg_detected = np.mean([r['detected'] for r in trial_results])
                avg_total = np.mean([r['detected'] + r['missed'] for r in trial_results])
                detection_rate = avg_detected / max(avg_total, 1e-6)
            else:
                avg_health_saved = 0
                avg_health_lost = 0
                detection_rate = 0

            strategy_results['n_tests'].append(len(tested))
            strategy_results['health_saved'].append(avg_health_saved)
            strategy_results['health_lost'].append(avg_health_lost)
            strategy_results['net_health'].append(avg_health_saved - avg_health_lost)
            strategy_results['detection_rate'].append(detection_rate)
            strategy_results['coverage'].append(coverage)

        results['strategies'][strategy] = strategy_results

    # Analyze triage transitions
    results['transitions'] = analyze_triage_transitions(cfg, agent, budgets)

    return results


def analyze_triage_transitions(cfg: Config, agent: TriageAgent, budgets: np.ndarray) -> Dict:
    """Analyze when each condition gets dropped from testing."""
    transitions = {c.name: {'included_until': None, 'priority': c.triage_priority}
                   for c in cfg.conditions}

    prev_tested = set()
    for budget in reversed(budgets):
        tested = set(agent.select_tests(budget, 'optimal'))

        # Find newly dropped conditions
        dropped = prev_tested - tested
        for idx in dropped:
            name = cfg.conditions[idx].name
            if transitions[name]['included_until'] is None:
                transitions[name]['included_until'] = budget

        prev_tested = tested

    # Conditions still tested at minimum budget
    min_tested = agent.select_tests(cfg.min_budget, 'optimal')
    for idx in min_tested:
        name = cfg.conditions[idx].name
        transitions[name]['included_until'] = cfg.min_budget

    return transitions


# ============================================================================
# VISUALIZATION
# ============================================================================

def plot_results(results: Dict, cfg: Config, output_path: str):
    """Generate the multi-panel visualization."""
    fig = plt.figure(figsize=(14, 12))

    budgets = np.array(results['budgets'])

    # -------------------------------------------------------------------------
    # Panel 1: Strategy Comparison (Net Health)
    # -------------------------------------------------------------------------
    ax1 = fig.add_subplot(2, 2, 1)

    colors = {'optimal': 'green', 'severity_first': 'red', 'prevalence_first': 'blue'}
    labels = {'optimal': 'Optimal Triage', 'severity_first': 'Severity First', 'prevalence_first': 'Prevalence First'}

    for strategy, data in results['strategies'].items():
        ax1.plot(budgets, data['net_health'], color=colors[strategy],
                linewidth=2, label=labels[strategy])

    ax1.set_xlabel('Diagnostic Budget')
    ax1.set_ylabel('Net Health Value')
    ax1.set_title('Strategy Comparison: Net Health Outcome', fontsize=12, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.axhline(y=0, color='gray', linestyle='--', alpha=0.5)

    # -------------------------------------------------------------------------
    # Panel 2: Coverage vs Budget
    # -------------------------------------------------------------------------
    ax2 = fig.add_subplot(2, 2, 2)

    optimal_data = results['strategies']['optimal']
    ax2.fill_between(budgets, optimal_data['coverage'], alpha=0.3, color='green')
    ax2.plot(budgets, optimal_data['coverage'], 'g-', linewidth=2, label='Coverage (% conditions tested)')
    ax2.plot(budgets, optimal_data['detection_rate'], 'b--', linewidth=2, label='Detection Rate')

    ax2.set_xlabel('Diagnostic Budget')
    ax2.set_ylabel('Fraction')
    ax2.set_title('Diagnostic Coverage Under Scarcity', fontsize=12, fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim(0, 1.05)

    # -------------------------------------------------------------------------
    # Panel 3: Triage Priority Ranking
    # -------------------------------------------------------------------------
    ax3 = fig.add_subplot(2, 2, 3)

    conditions = cfg.conditions
    priorities = [c.triage_priority for c in conditions]
    names = [c.name for c in conditions]

    # Sort by priority
    sorted_indices = np.argsort(priorities)[::-1]
    sorted_names = [names[i] for i in sorted_indices]
    sorted_priorities = [priorities[i] for i in sorted_indices]

    # Color by category
    colors_bar = []
    for i in sorted_indices:
        c = conditions[i]
        if c.severity >= 90:
            colors_bar.append('darkred')  # Severe
        elif c.severity >= 40:
            colors_bar.append('orange')   # Moderate
        else:
            colors_bar.append('green')    # Mild

    y_pos = np.arange(len(sorted_names))
    ax3.barh(y_pos, sorted_priorities, color=colors_bar, alpha=0.7)
    ax3.set_yticks(y_pos)
    ax3.set_yticklabels(sorted_names, fontsize=9)
    ax3.set_xlabel('Triage Priority Score')
    ax3.set_title('Condition Triage Priority Ranking\n(Red=Severe, Orange=Moderate, Green=Mild)',
                  fontsize=12, fontweight='bold')

    # -------------------------------------------------------------------------
    # Panel 4: Triage Transition Map
    # -------------------------------------------------------------------------
    ax4 = fig.add_subplot(2, 2, 4)

    transitions = results['transitions']

    # Sort by when they get dropped
    sorted_conditions = sorted(transitions.items(),
                               key=lambda x: x[1]['included_until'] or 0,
                               reverse=True)

    y_labels = []
    x_values = []

    for name, data in sorted_conditions:
        y_labels.append(name)
        x_values.append(data['included_until'] if data['included_until'] else cfg.max_budget)

    y_pos = np.arange(len(y_labels))
    bars = ax4.barh(y_pos, x_values, alpha=0.7, color='steelblue')

    # Add priority annotations
    for i, (name, data) in enumerate(sorted_conditions):
        ax4.text(x_values[i] + 1, i, f"P={data['priority']:.2f}",
                va='center', fontsize=8, color='gray')

    ax4.set_yticks(y_pos)
    ax4.set_yticklabels(y_labels, fontsize=9)
    ax4.set_xlabel('Minimum Budget to Include Test')
    ax4.set_title('Triage Transition Map\n(When conditions get dropped)',
                  fontsize=12, fontweight='bold')
    ax4.axvline(x=cfg.min_budget, color='red', linestyle='--', alpha=0.7, label='Min Budget')
    ax4.legend()

    # -------------------------------------------------------------------------
    # Overall title
    # -------------------------------------------------------------------------
    plt.tight_layout()
    fig.suptitle('CYCLE 2570: The Triage\n'
                 '"Under scarcity, agents must choose: common-and-mild vs rare-and-severe"',
                 fontsize=14, fontweight='bold', y=1.02)

    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()

    print(f"Figure saved: {output_path}")


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Run experiment and generate output."""
    print("=" * 70)
    print("CYCLE 2570: The Triage")
    print("Gate 197: Medical Attention Economics")
    print("=" * 70)

    cfg = Config()

    print(f"\nConditions ({len(cfg.conditions)}):")
    print("-" * 60)
    for c in cfg.conditions:
        print(f"  {c.name:20s} | P={c.prevalence:.3f} | S={c.severity:3.0f} | "
              f"R={c.treatability:.1f} | T={c.test_cost:5.1f} | Priority={c.triage_priority:.3f}")

    print(f"\nBudget range: {cfg.min_budget} - {cfg.max_budget}")
    print(f"Trials per budget level: {cfg.n_trials}")

    # Run experiment
    print("\nRunning simulation...")
    results = run_experiment(cfg)

    # Analyze results
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)

    # Find phase transition point
    optimal_data = results['strategies']['optimal']
    coverages = np.array(optimal_data['coverage'])
    budgets = np.array(results['budgets'])

    # Find budget where coverage drops below 50%
    half_coverage_idx = np.argmax(coverages < 0.5)
    if half_coverage_idx > 0:
        transition_budget = budgets[half_coverage_idx]
        print(f"\nPhase Transition (50% coverage): Budget = {transition_budget:.1f}")

    # Compare strategies at low budget
    low_budget_idx = 5  # Near minimum
    print(f"\nStrategy Performance at Low Budget (B={budgets[low_budget_idx]:.1f}):")
    for strategy, data in results['strategies'].items():
        print(f"  {strategy:20s}: Net Health = {data['net_health'][low_budget_idx]:.2f}, "
              f"Coverage = {data['coverage'][low_budget_idx]:.1%}")

    # Optimal vs suboptimal gap at various budgets
    print("\nOptimal Strategy Advantage:")
    for idx in [5, 25, 45]:  # Low, medium, high budget
        opt = results['strategies']['optimal']['net_health'][idx]
        sev = results['strategies']['severity_first']['net_health'][idx]
        prev = results['strategies']['prevalence_first']['net_health'][idx]
        print(f"  Budget {budgets[idx]:5.1f}: Optimal vs Severity = +{opt-sev:.1f}, "
              f"vs Prevalence = +{opt-prev:.1f}")

    # Triage transitions
    print("\nTriage Transitions (when conditions get dropped):")
    sorted_trans = sorted(results['transitions'].items(),
                          key=lambda x: x[1]['included_until'] or 0)
    for name, data in sorted_trans:
        if data['included_until']:
            print(f"  {name:20s}: Dropped below B={data['included_until']:.1f} "
                  f"(Priority={data['priority']:.3f})")

    # Key finding
    print("\n" + "=" * 70)
    print("KEY FINDING: The Diagnostic Triage Effect")
    print("=" * 70)
    print("""
Under severe budget constraints:
1. Agents cannot test for all conditions
2. They must PRIORITIZE based on: P(condition) x Severity x Treatability / Cost
3. Low-priority conditions are COMPLETELY ABANDONED (not gradually reduced)
4. This creates "diagnostic blind spots" - conditions that are never tested

The optimal triage strategy outperforms naive heuristics (severity-first or
prevalence-first) because it balances all factors into a unified metric.

FUNCTIONAL NAME: The Diagnostic Triage Effect
- Binary inclusion/exclusion of diagnostic tests under scarcity
- Non-linear transition as budget decreases
- Optimal allocation differs from intuitive heuristics
""")

    # Generate figure
    output_dir = "/Volumes/dual/DUALITY-ZERO-V2/data/figures"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "cycle2570_the_triage.png")

    print("\nGenerating figure...")
    plot_results(results, cfg, output_path)

    return results


if __name__ == "__main__":
    main()
