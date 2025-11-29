#!/usr/bin/env python3
"""
Cycle 2582: BCP Equilibrium Analysis
=====================================

Phase 74, Gate 212: What are the stable states of BCP dynamics?

Research Questions:
1. Does BCP have stable fixed points?
2. How do parameters affect equilibrium states?
3. Are there bifurcations in equilibrium behavior?

Key Analysis:
- Fixed point analysis: Where does dB/dt = 0?
- Stability analysis: Are fixed points attractors or repellers?
- Bifurcation analysis: How do critical points change with parameters?

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
License: GPL-3.0
"""

import numpy as np
import json
from dataclasses import dataclass, field
from typing import List, Dict, Tuple
from datetime import datetime
import sys
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2/bcp_lib')

from bcp import BCPModel, AttentionItem


@dataclass
class BCPDynamicalSystem:
    """BCP as a dynamical system with budget as state variable."""
    
    model: BCPModel = field(default_factory=lambda: BCPModel(
        lambda_scale=5.0, abundance_threshold=3.0, crisis_threshold=0.8
    ))
    items: List[AttentionItem] = field(default_factory=list)
    
    # System parameters
    income_rate: float = 0.5      # Budget gained per step
    consumption_scale: float = 1.0  # Scales consumption
    
    def generate_items(self, n: int = 5) -> List[AttentionItem]:
        """Generate fixed items for equilibrium analysis."""
        np.random.seed(42)  # Fixed for reproducibility
        items = []
        for i in range(n):
            gain = 0.3 + 0.15 * i  # Ordered by gain: 0.3, 0.45, 0.6, 0.75, 0.9
            cost = 0.1 + 0.03 * i  # Ordered by cost: 0.1, 0.13, 0.16, 0.19, 0.22
            items.append(AttentionItem(f"item_{i}", gain, cost))
        return items
    
    def compute_budget_dynamics(self, budget: float) -> Tuple[float, Dict]:
        """
        Compute dB/dt at given budget level.
        
        dB/dt = income - consumption(B)
        
        where consumption depends on attention allocation.
        """
        self.items = self.generate_items()
        result = self.model.allocate(self.items, budget)
        
        consumption = result.total_cost * self.consumption_scale
        income = self.income_rate
        
        dB_dt = income - consumption
        
        return dB_dt, {
            "budget": budget,
            "income": income,
            "consumption": consumption,
            "dB_dt": dB_dt,
            "n_attended": result.n_attended,
            "phase": result.phase.value,
            "lambda": result.lambda_
        }
    
    def find_equilibrium(self, budget_range: Tuple[float, float] = (0.1, 5.0),
                         n_points: int = 100, tolerance: float = 0.01) -> List[Dict]:
        """Find equilibrium points where dB/dt = 0."""
        budgets = np.linspace(budget_range[0], budget_range[1], n_points)
        
        equilibria = []
        prev_sign = None
        
        for i, budget in enumerate(budgets):
            dB_dt, state = self.compute_budget_dynamics(budget)
            current_sign = np.sign(dB_dt)
            
            # Zero crossing detected
            if prev_sign is not None and current_sign != prev_sign:
                # Binary search for precise equilibrium
                low, high = budgets[i-1], budget
                for _ in range(20):  # 20 iterations for precision
                    mid = (low + high) / 2
                    dB_mid, _ = self.compute_budget_dynamics(mid)
                    if abs(dB_mid) < tolerance:
                        break
                    if np.sign(dB_mid) == prev_sign:
                        low = mid
                    else:
                        high = mid
                
                # Compute stability: is this attractor or repeller?
                _, state_eq = self.compute_budget_dynamics(mid)
                eps = 0.01
                dB_plus, _ = self.compute_budget_dynamics(mid + eps)
                dB_minus, _ = self.compute_budget_dynamics(mid - eps)
                
                # Stable if d(dB/dt)/dB < 0 (negative feedback)
                d2B = (dB_plus - dB_minus) / (2 * eps)
                stability = "stable" if d2B < 0 else "unstable"
                
                equilibria.append({
                    "budget": mid,
                    "phase": state_eq["phase"],
                    "n_attended": state_eq["n_attended"],
                    "stability": stability,
                    "d2B_dt2": d2B
                })
            
            prev_sign = current_sign
        
        return equilibria
    
    def compute_phase_portrait(self, budget_range: Tuple[float, float] = (0.1, 5.0),
                               n_points: int = 50) -> List[Dict]:
        """Compute full phase portrait."""
        budgets = np.linspace(budget_range[0], budget_range[1], n_points)
        portrait = []
        
        for budget in budgets:
            dB_dt, state = self.compute_budget_dynamics(budget)
            portrait.append(state)
        
        return portrait


def run_experiment():
    """Run equilibrium analysis experiment."""
    print("=" * 60)
    print("CYCLE 2582: BCP Equilibrium Analysis")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().isoformat()}\n")

    # Test different income rates to find bifurcations
    income_rates = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
    
    results = {}
    
    print("--- Equilibrium Analysis by Income Rate ---\n")
    print(f"{'Income':>8} {'N_Eq':>6} {'Budget':>10} {'Phase':>10} {'Stability':>10}")
    print("-" * 50)
    
    for income in income_rates:
        system = BCPDynamicalSystem()
        system.income_rate = income
        
        equilibria = system.find_equilibrium()
        
        results[f"income_{income}"] = {
            "income_rate": income,
            "n_equilibria": len(equilibria),
            "equilibria": equilibria
        }
        
        if equilibria:
            for eq in equilibria:
                print(f"{income:8.2f} {len(equilibria):6d} {eq['budget']:10.3f} "
                      f"{eq['phase']:>10} {eq['stability']:>10}")
        else:
            print(f"{income:8.2f} {0:6d} {'N/A':>10} {'N/A':>10} {'N/A':>10}")
    
    # Phase portrait for representative case
    print("\n--- Phase Portrait (income=0.5) ---\n")
    system = BCPDynamicalSystem()
    system.income_rate = 0.5
    portrait = system.compute_phase_portrait()
    
    # Summarize phase portrait
    crisis_region = [p for p in portrait if p["phase"] == "crisis"]
    scarcity_region = [p for p in portrait if p["phase"] == "scarcity"]
    abundance_region = [p for p in portrait if p["phase"] == "abundance"]
    
    print(f"Crisis region: B < {max([p['budget'] for p in crisis_region]):.2f}" if crisis_region else "Crisis region: None")
    print(f"Scarcity region: B in [{min([p['budget'] for p in scarcity_region]):.2f}, {max([p['budget'] for p in scarcity_region]):.2f}]" if scarcity_region else "Scarcity region: None")
    print(f"Abundance region: B > {min([p['budget'] for p in abundance_region]):.2f}" if abundance_region else "Abundance region: None")
    
    # Find flow direction in each region
    print("\n--- Flow Direction by Phase ---")
    for phase, region in [("crisis", crisis_region), ("scarcity", scarcity_region), ("abundance", abundance_region)]:
        if region:
            avg_dB = np.mean([p["dB_dt"] for p in region])
            direction = "increasing" if avg_dB > 0 else "decreasing"
            print(f"  {phase}: Budget {direction} (dB/dt = {avg_dB:.3f})")
    
    # Key findings
    print("\n" + "=" * 60)
    print("KEY FINDINGS")
    print("=" * 60)
    
    # Count equilibria by stability
    all_equilibria = []
    for key, data in results.items():
        all_equilibria.extend(data["equilibria"])
    
    stable_count = sum(1 for eq in all_equilibria if eq["stability"] == "stable")
    unstable_count = sum(1 for eq in all_equilibria if eq["stability"] == "unstable")
    
    print(f"\n1. Total Equilibria Found: {len(all_equilibria)}")
    print(f"   - Stable: {stable_count}")
    print(f"   - Unstable: {unstable_count}")
    
    # Check for bifurcations
    eq_counts = [results[k]["n_equilibria"] for k in sorted(results.keys())]
    bifurcations = sum(1 for i in range(1, len(eq_counts)) if eq_counts[i] != eq_counts[i-1])
    
    print(f"\n2. Bifurcations Detected: {bifurcations}")
    
    # Phase analysis
    phases_at_eq = [eq["phase"] for eq in all_equilibria]
    phase_counts = {p: phases_at_eq.count(p) for p in set(phases_at_eq)}
    
    print(f"\n3. Equilibrium Phases: {phase_counts}")
    
    # Emergent behavior
    if stable_count > unstable_count:
        emergent = "ATTRACTOR DOMINANCE"
        insight = f"{stable_count}/{len(all_equilibria)} equilibria are stable attractors"
    else:
        emergent = "INSTABILITY DOMINANCE"
        insight = f"{unstable_count}/{len(all_equilibria)} equilibria are unstable"
    
    print(f"\n4. EMERGENT BEHAVIOR: {emergent}")
    print(f"   {insight}")
    
    # Save results
    output = {
        "experiment": "cycle2582_equilibrium_bcp",
        "timestamp": datetime.now().isoformat(),
        "parameters": {"income_rates": income_rates},
        "results": results,
        "summary": {
            "total_equilibria": len(all_equilibria),
            "stable": stable_count,
            "unstable": unstable_count,
            "bifurcations": bifurcations,
            "phase_distribution": phase_counts
        },
        "findings": {
            "emergent": emergent,
            "insight": insight
        }
    }
    
    with open("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/cycle2582_results.json", 'w') as f:
        json.dump(output, f, indent=2)
    
    print("\n" + "=" * 60)
    print("CYCLE 2582 COMPLETE")
    print("=" * 60)
    return output


if __name__ == "__main__":
    run_experiment()
