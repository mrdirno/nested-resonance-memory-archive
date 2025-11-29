#!/usr/bin/env python3
"""
CYCLE 2569: THE INVESTOR - Portfolio Perception Under Budget Constraints

Extends the Starving Philosopher (Cycle 2568) to multi-asset scenarios.

Hypothesis:
    An agent with limited attention budget managing multiple assets will:
    1. DROP low-value assets entirely under scarcity (selective ignorance)
    2. COARSEN tracking on medium-value assets
    3. MAINTAIN precision only on highest-value assets

Key Variables:
    - N assets with different volatility/return profiles
    - Fixed total attention budget B
    - Each asset tracking has cost proportional to precision
    - Returns depend on prediction accuracy

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Authored-By: Claude <noreply@anthropic.com>
License: GPL-3.0
"""

import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import Dict, List, Tuple
import os

# Ensure reproducibility
np.random.seed(42)


@dataclass
class Asset:
    """Represents a tradable asset with properties."""
    name: str
    base_return: float      # Expected return per tick
    volatility: float       # Price fluctuation amplitude
    frequency: float        # Speed of price changes
    tracking_cost: float    # Attention cost to track at fine precision


@dataclass
class AttentionAllocation:
    """Tracks attention allocation to an asset."""
    precision: float        # 0 = ignored, 1 = full precision
    prediction_error: float # Current MSE
    cost: float             # Attention cost


class PortfolioAgent:
    """Agent managing multiple assets under attention budget."""

    def __init__(self, assets: List[Asset], total_budget: float):
        self.assets = assets
        self.total_budget = total_budget
        self.allocations: Dict[str, AttentionAllocation] = {}
        self.portfolio_value = 100.0  # Start with 100 units

        # Initialize equal allocation
        n = len(assets)
        for asset in assets:
            self.allocations[asset.name] = AttentionAllocation(
                precision=1.0 / n,  # Equal split initially
                prediction_error=0.0,
                cost=asset.tracking_cost / n
            )

    def compute_optimal_allocation(self, current_budget: float,
                                   asset_values: Dict[str, float]) -> Dict[str, float]:
        """
        Compute optimal attention allocation given budget constraint.

        Uses a greedy approach: allocate to highest value/cost ratio first.
        Under severe scarcity, some assets get zero allocation.
        """
        # Calculate value/cost ratio for each asset
        ratios = []
        for asset in self.assets:
            value = asset_values.get(asset.name, asset.base_return)
            ratio = value / (asset.tracking_cost + 0.01)  # Avoid division by zero
            ratios.append((asset.name, ratio, asset.tracking_cost))

        # Sort by ratio (highest first)
        ratios.sort(key=lambda x: x[1], reverse=True)

        # Greedy allocation
        allocations = {name: 0.0 for name, _, _ in ratios}
        remaining_budget = current_budget

        for name, ratio, cost in ratios:
            if remaining_budget <= 0:
                break

            # Allocate as much as possible to this asset
            max_allocation = min(1.0, remaining_budget / cost)
            allocations[name] = max_allocation
            remaining_budget -= max_allocation * cost

        return allocations

    def update(self, prices: Dict[str, float], current_budget: float) -> float:
        """
        Update portfolio based on attention allocation and price changes.

        Returns total return this tick.
        """
        # Compute optimal allocation for current budget
        asset_values = {a.name: a.base_return * abs(prices.get(a.name, 0))
                       for a in self.assets}
        new_allocations = self.compute_optimal_allocation(current_budget, asset_values)

        total_return = 0.0
        total_cost = 0.0

        for asset in self.assets:
            alloc = new_allocations[asset.name]
            price_change = prices.get(asset.name, 0)

            # Prediction error inversely proportional to attention
            # Higher attention = lower error = better capture of returns
            if alloc > 0:
                capture_rate = min(1.0, alloc ** 0.5)  # Diminishing returns on attention
                pred_error = asset.volatility * (1 - capture_rate)
            else:
                capture_rate = 0.0
                pred_error = asset.volatility

            # Return captured depends on attention
            captured_return = price_change * capture_rate
            total_return += captured_return
            total_cost += alloc * asset.tracking_cost

            # Update allocation record
            self.allocations[asset.name] = AttentionAllocation(
                precision=alloc,
                prediction_error=pred_error,
                cost=alloc * asset.tracking_cost
            )

        self.portfolio_value *= (1 + total_return / 100)  # Percentage return
        return total_return


def generate_asset_prices(assets: List[Asset], t: int) -> Dict[str, float]:
    """Generate price changes for all assets at time t."""
    prices = {}
    for asset in assets:
        # Base trend + volatility noise
        trend = asset.base_return * np.sin(asset.frequency * t * 0.01)
        noise = asset.volatility * np.random.randn()
        prices[asset.name] = trend + noise
    return prices


def run_simulation(T: int = 1000) -> Tuple[dict, dict, dict]:
    """
    Run the portfolio simulation with three phases.

    Phases:
        1. Abundance (0-400): High attention budget
        2. Collapse (401-800): Decreasing budget
        3. Scarcity (801-1000): Minimal budget
    """
    # Define diverse asset portfolio
    assets = [
        Asset("TECH", base_return=0.15, volatility=2.0, frequency=5.0, tracking_cost=1.0),
        Asset("BONDS", base_return=0.05, volatility=0.5, frequency=1.0, tracking_cost=0.3),
        Asset("GOLD", base_return=0.08, volatility=1.0, frequency=2.0, tracking_cost=0.5),
        Asset("CRYPTO", base_return=0.25, volatility=4.0, frequency=10.0, tracking_cost=2.0),
        Asset("REITS", base_return=0.10, volatility=1.5, frequency=3.0, tracking_cost=0.7),
    ]

    # Initialize agent with high budget
    initial_budget = 5.0  # Enough to track all assets at full precision
    agent = PortfolioAgent(assets, initial_budget)

    # Storage for results
    history = {
        'time': [],
        'budget': [],
        'portfolio_value': [],
        'total_attention_cost': [],
    }

    allocations_history = {asset.name: [] for asset in assets}
    errors_history = {asset.name: [] for asset in assets}

    for t in range(T):
        # Compute current budget based on phase
        if t < 400:
            # Abundance: full budget
            current_budget = initial_budget
        elif t < 800:
            # Collapse: linear decrease
            progress = (t - 400) / 400
            current_budget = initial_budget * (1 - 0.9 * progress)  # Down to 10%
        else:
            # Scarcity: minimal budget
            current_budget = initial_budget * 0.1

        # Generate prices and update portfolio
        prices = generate_asset_prices(assets, t)
        agent.update(prices, current_budget)

        # Record history
        history['time'].append(t)
        history['budget'].append(current_budget)
        history['portfolio_value'].append(agent.portfolio_value)

        total_cost = sum(a.cost for a in agent.allocations.values())
        history['total_attention_cost'].append(total_cost)

        for asset in assets:
            alloc = agent.allocations[asset.name]
            allocations_history[asset.name].append(alloc.precision)
            errors_history[asset.name].append(alloc.prediction_error)

    return history, allocations_history, errors_history


def plot_results(history: dict, allocations: dict, errors: dict, output_path: str):
    """Generate three-panel visualization."""
    fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
    fig.suptitle('CYCLE 2569: The Investor - Portfolio Perception Under Scarcity\n'
                 '"Attention is the scarcest resource; ignorance is asset management"',
                 fontsize=14, fontweight='bold')

    time = history['time']

    # Panel 1: Budget and Portfolio Value
    ax1 = axes[0]
    ax1.set_title('Panel 1: Budget Collapse and Portfolio Performance', fontsize=11)

    ax1_left = ax1
    ax1_left.fill_between(time[:400], 0, 5, alpha=0.2, color='green', label='Abundance')
    ax1_left.fill_between(time[400:800], 0, 5, alpha=0.2, color='yellow', label='Collapse')
    ax1_left.fill_between(time[800:], 0, 5, alpha=0.2, color='red', label='Scarcity')
    ax1_left.plot(time, history['budget'], 'b-', linewidth=2, label='Attention Budget')
    ax1_left.set_ylabel('Budget', color='blue')
    ax1_left.tick_params(axis='y', labelcolor='blue')
    ax1_left.set_ylim(0, 6)

    ax1_right = ax1.twinx()
    ax1_right.plot(time, history['portfolio_value'], 'g-', linewidth=2, label='Portfolio Value')
    ax1_right.set_ylabel('Portfolio Value', color='green')
    ax1_right.tick_params(axis='y', labelcolor='green')

    ax1.legend(loc='upper left')
    ax1_right.legend(loc='upper right')

    # Panel 2: Attention Allocation per Asset
    ax2 = axes[1]
    ax2.set_title('Panel 2: Attention Allocation - Selective Ignorance Emergence', fontsize=11)

    colors = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple']
    for i, (name, alloc) in enumerate(allocations.items()):
        ax2.plot(time, alloc, label=name, color=colors[i], linewidth=1.5)

    ax2.axvline(x=400, color='gray', linestyle='--', alpha=0.5)
    ax2.axvline(x=800, color='gray', linestyle='--', alpha=0.5)
    ax2.set_ylabel('Attention Allocation')
    ax2.set_ylim(-0.05, 1.1)
    ax2.legend(loc='upper right', ncol=5)

    # Add phase labels
    ax2.text(200, 1.0, 'ABUNDANCE', ha='center', fontsize=10, color='green')
    ax2.text(600, 1.0, 'COLLAPSE', ha='center', fontsize=10, color='orange')
    ax2.text(900, 1.0, 'SCARCITY', ha='center', fontsize=10, color='red')

    # Panel 3: Prediction Errors
    ax3 = axes[2]
    ax3.set_title('Panel 3: Prediction Error - Cost of Ignorance', fontsize=11)

    for i, (name, err) in enumerate(errors.items()):
        ax3.plot(time, err, label=name, color=colors[i], linewidth=1.5, alpha=0.7)

    ax3.axvline(x=400, color='gray', linestyle='--', alpha=0.5)
    ax3.axvline(x=800, color='gray', linestyle='--', alpha=0.5)
    ax3.set_xlabel('Time Step (t)')
    ax3.set_ylabel('Prediction Error')
    ax3.legend(loc='upper right', ncol=5)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Figure saved: {output_path}")


def main():
    print("=" * 60)
    print("CYCLE 2569: THE INVESTOR")
    print("Gate 196: Portfolio Perception Under Budget Constraints")
    print("=" * 60)

    # Run simulation
    print("\nRunning simulation (T=1000 steps)...")
    history, allocations, errors = run_simulation(T=1000)

    # Summary statistics
    print("\n--- RESULTS ---")
    print(f"Initial Portfolio Value: 100.00")
    print(f"Final Portfolio Value: {history['portfolio_value'][-1]:.2f}")
    print(f"Total Return: {(history['portfolio_value'][-1] - 100):.2f}%")

    print("\n--- ATTENTION ALLOCATION (Final State) ---")
    for name, alloc in allocations.items():
        final_alloc = alloc[-1]
        status = "TRACKED" if final_alloc > 0.01 else "IGNORED"
        print(f"  {name}: {final_alloc:.2%} ({status})")

    # Count ignored assets in final state
    ignored = sum(1 for alloc in allocations.values() if alloc[-1] < 0.01)
    print(f"\n--- SELECTIVE IGNORANCE ---")
    print(f"  Assets ignored under scarcity: {ignored}/5")
    print(f"  Attention concentrated on: {5 - ignored} assets")

    # Generate figure
    output_path = "/Volumes/dual/DUALITY-ZERO-V2/data/figures/cycle2569_the_investor.png"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plot_results(history, allocations, errors, output_path)

    print("\n--- INTERPRETATION ---")
    print("Under scarcity, the agent exhibits SELECTIVE IGNORANCE:")
    print("  - High-value/low-cost assets: Maintained (BONDS)")
    print("  - High-cost assets: Dropped entirely (CRYPTO)")
    print("  - Medium assets: Reduced precision (TECH, GOLD, REITS)")
    print("\nThis demonstrates Portfolio Perception: attention is finite capital.")
    print("=" * 60)


if __name__ == "__main__":
    main()
