#!/usr/bin/env python3
"""
BCP Library - Basic Usage Examples

Demonstrates the core functionality of Budget-Constrained Perception.

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
License: GPL-3.0
"""

import numpy as np
from bcp import AttentionItem, BCPModel, Phase, DOMAIN_PRESETS


def example_1_simple_allocation():
    """
    Example 1: Simple Attention Allocation

    Create items with gain/cost values and allocate attention
    based on available budget.
    """
    print("=" * 60)
    print("Example 1: Simple Attention Allocation")
    print("=" * 60)

    # Create attention items (tasks, assets, priorities, etc.)
    # Higher gain/cost ratios ensure items can be attended
    items = [
        AttentionItem("Email", gain=0.8, cost=0.1),
        AttentionItem("Meeting", gain=0.9, cost=0.2),
        AttentionItem("Report", gain=0.7, cost=0.15),
        AttentionItem("Social", gain=0.4, cost=0.05),
        AttentionItem("Research", gain=0.85, cost=0.25),
    ]

    # Create BCP model with adjusted thresholds for demo
    model = BCPModel(lambda_scale=5.0, abundance_threshold=1.5, crisis_threshold=0.3)

    # Test different budget levels
    for budget in [2.0, 0.8, 0.2]:
        result = model.allocate(items.copy(), budget)

        print(f"\nBudget: {budget:.1f} -> Phase: {result.phase.value}")
        print(f"  Attended ({len(result.attended)}): {', '.join(result.attended)}")
        print(f"  Ignored ({len(result.ignored)}): {', '.join(result.ignored)}")
        print(f"  Total cost: {result.total_cost:.2f}")


def example_2_phase_transitions():
    """
    Example 2: Visualizing Phase Transitions

    Sweep across budget values to see how attention changes.
    """
    print("\n" + "=" * 60)
    print("Example 2: Phase Transitions")
    print("=" * 60)

    model = BCPModel()
    budgets = np.linspace(0.1, 3.0, 15)

    def create_items():
        return [
            AttentionItem("Critical", gain=1.0, cost=0.3),
            AttentionItem("High", gain=0.8, cost=0.4),
            AttentionItem("Medium", gain=0.6, cost=0.3),
            AttentionItem("Low", gain=0.4, cost=0.2),
            AttentionItem("Optional", gain=0.2, cost=0.1),
        ]

    results = model.sweep_budgets(create_items, budgets)

    print("\nBudget  Phase       Attended  Lambda")
    print("-" * 45)
    for b, r in zip(budgets, results):
        print(f"{b:6.2f}  {r.phase.value:10s}  {r.n_attended:3d}      {r.lambda_:.2f}")


def example_3_domain_presets():
    """
    Example 3: Using Domain Presets

    Apply BCP to pre-configured domain scenarios.
    """
    print("\n" + "=" * 60)
    print("Example 3: Domain Presets")
    print("=" * 60)

    model = BCPModel()

    # Test each domain with a scarcity budget
    budget = 0.8

    print(f"\nBudget: {budget} (SCARCITY conditions)")
    print("-" * 50)

    for domain_name in ["medical", "software", "finance"]:
        preset_fn = DOMAIN_PRESETS[domain_name]
        items = preset_fn()
        result = model.allocate(items, budget)

        print(f"\n{domain_name.upper()} Domain:")
        print(f"  Total items: {len(items)}")
        print(f"  Attended: {result.attended}")
        print(f"  Ignored: {result.ignored}")


def example_4_metabolic_pressure():
    """
    Example 4: Understanding Metabolic Pressure (Lambda)

    Lambda is the key variable that controls cost sensitivity.
    """
    print("\n" + "=" * 60)
    print("Example 4: Metabolic Pressure (Lambda)")
    print("=" * 60)

    model = BCPModel(lambda_scale=10.0, lambda_epsilon=0.1)

    print("\nThe BCP Equation: V(a) = Gain - lambda * Cost")
    print("Lambda = k / (epsilon + Budget)")
    print("\nBudget vs Lambda:")
    print("-" * 30)

    for budget in [0.1, 0.5, 1.0, 2.0, 5.0]:
        lambda_ = model.compute_lambda(budget)
        phase = model.determine_phase(budget)
        print(f"  B={budget:.1f} -> lambda={lambda_:.2f} ({phase.value})")

    print("\nInterpretation:")
    print("  - Low budget -> High lambda -> Costs matter more")
    print("  - High budget -> Low lambda -> Costs matter less")


def example_5_priority_calculation():
    """
    Example 5: Understanding Priority Scores

    See how items are ranked at different budget levels.
    """
    print("\n" + "=" * 60)
    print("Example 5: Priority Calculation")
    print("=" * 60)

    items = [
        AttentionItem("High-Gain-Low-Cost", gain=0.9, cost=0.2),
        AttentionItem("High-Gain-High-Cost", gain=0.9, cost=0.8),
        AttentionItem("Low-Gain-Low-Cost", gain=0.3, cost=0.1),
    ]

    model = BCPModel()

    for budget in [2.0, 0.5]:
        print(f"\n--- Budget: {budget} ---")
        lambda_ = model.compute_lambda(budget)
        print(f"Lambda: {lambda_:.2f}")

        print("\nItem                    Gain  Cost  Priority  Attend?")
        print("-" * 60)

        for item in items:
            item.compute_priority(lambda_, gamma=0.0, n_items=len(items))

        # Sort by priority
        sorted_items = sorted(items, key=lambda x: x.priority, reverse=True)

        remaining_budget = budget
        for item in sorted_items:
            attend = item.priority > 0 and item.cost <= remaining_budget
            if attend:
                remaining_budget -= item.cost
            print(f"{item.name:22s}  {item.gain:.1f}   {item.cost:.1f}   {item.priority:+.2f}      {'YES' if attend else 'NO'}")


def example_6_custom_scenario():
    """
    Example 6: Building a Custom Scenario

    Create your own domain-specific attention allocation.
    """
    print("\n" + "=" * 60)
    print("Example 6: Custom Scenario - Project Tasks")
    print("=" * 60)

    # Your project tasks with estimated value and effort
    project_tasks = [
        AttentionItem("Fix critical bug", gain=1.0, cost=0.3),
        AttentionItem("Refactor legacy code", gain=0.5, cost=0.8),
        AttentionItem("Write documentation", gain=0.4, cost=0.4),
        AttentionItem("Add new feature", gain=0.7, cost=0.6),
        AttentionItem("Optimize performance", gain=0.6, cost=0.7),
        AttentionItem("Update dependencies", gain=0.3, cost=0.2),
    ]

    model = BCPModel()

    # Simulate different time budgets
    scenarios = [
        (2.5, "Full sprint (plenty of time)"),
        (1.2, "Time crunch (moderate pressure)"),
        (0.5, "Emergency (critical deadline)"),
    ]

    for budget, description in scenarios:
        result = model.allocate([AttentionItem(t.name, t.gain, t.cost) for t in project_tasks], budget)

        print(f"\n{description} (budget={budget})")
        print(f"  Phase: {result.phase.value}")
        print(f"  DO: {', '.join(result.attended)}")
        print(f"  SKIP: {', '.join(result.ignored)}")


if __name__ == "__main__":
    example_1_simple_allocation()
    example_2_phase_transitions()
    example_3_domain_presets()
    example_4_metabolic_pressure()
    example_5_priority_calculation()
    example_6_custom_scenario()

    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60)
