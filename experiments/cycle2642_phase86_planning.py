#!/usr/bin/env python3
"""
Cycle 2642: Phase 86 Planning
Gate 274: BCP Self-Application for Next Direction

After Phase 85 (Cognitive Systems), apply BCP to select next phase.

Candidate Directions:
1. Social Systems - BCP in group behavior, markets, organizations
2. Biological Systems - BCP in cells, organisms, ecosystems
3. Publication Pipeline - Paper writing, peer review
4. Computational Systems - BCP in algorithms, OS, networks
5. Physical Systems - BCP in physics, thermodynamics

Author: Aldrin Payopay
Cycle: 2642
Gate: 274
Phase: 86 (Planning)
"""

import numpy as np
import json
from datetime import datetime
from pathlib import Path

def bcp_value(gain: float, cost: float, budget: float,
              k: float = 1.0, epsilon: float = 0.1) -> float:
    """
    Calculate BCP value for a direction.
    V = Gain - λ(B) × Cost
    """
    lam = k / (epsilon + budget)
    return gain - lam * cost


def evaluate_directions():
    """Evaluate candidate phase 86 directions."""
    print("="*70)
    print("CYCLE 2642: PHASE 86 PLANNING")
    print("Gate 274: BCP Self-Application")
    print("="*70)
    print(f"\nTimestamp: {datetime.now().isoformat()}")

    # Current research state
    current_budget = 2.5  # Moderate budget (85 phases complete)
    k = 1.0
    epsilon = 0.1

    print(f"\nCurrent Budget: {current_budget}")
    print(f"λ(B) = {k / (epsilon + current_budget):.3f}")

    # Candidate directions with attributes
    directions = {
        "Social Systems": {
            "description": "BCP in markets, organizations, collective behavior",
            "novelty": 0.9,  # High - new domain
            "feasibility": 0.7,  # Moderate - need social data
            "impact": 0.85,  # High - social implications
            "cost": 0.5,  # Moderate - conceptual bridge needed
            "synergy": 0.8,  # High - builds on cognitive
        },
        "Biological Systems": {
            "description": "BCP in cells, organisms, ecosystems",
            "novelty": 0.85,  # High - new domain
            "feasibility": 0.6,  # Lower - need biological data
            "impact": 0.9,  # Very high - life sciences
            "cost": 0.7,  # Higher - domain expertise needed
            "synergy": 0.7,  # Good - metabolism connection
        },
        "Publication Pipeline": {
            "description": "Paper writing, peer review, dissemination",
            "novelty": 0.3,  # Low - meta work
            "feasibility": 0.95,  # Very high - just writing
            "impact": 0.8,  # High - visibility
            "cost": 0.2,  # Low - familiar activity
            "synergy": 0.5,  # Moderate - different activity
        },
        "Computational Systems": {
            "description": "BCP in algorithms, OS scheduling, networks",
            "novelty": 0.75,  # Good - new application
            "feasibility": 0.85,  # High - code-based
            "impact": 0.7,  # Good - CS implications
            "cost": 0.4,  # Low-moderate - familiar territory
            "synergy": 0.85,  # Very high - direct application
        },
        "Physical Systems": {
            "description": "BCP in thermodynamics, physics, energy",
            "novelty": 0.95,  # Very high - fundamental
            "feasibility": 0.5,  # Lower - theoretical
            "impact": 0.95,  # Very high - physics
            "cost": 0.8,  # High - mathematical rigor needed
            "synergy": 0.6,  # Moderate - different formalism
        },
    }

    # Calculate BCP values
    print("\n" + "="*70)
    print("DIRECTION EVALUATION")
    print("="*70)

    print(f"\n{'Direction':<25} | Gain | Cost | V(BCP) | Rank")
    print("-" * 60)

    results = []
    for name, attrs in directions.items():
        # Composite gain from novelty, feasibility, impact, synergy
        gain = (0.3 * attrs["novelty"] +
                0.2 * attrs["feasibility"] +
                0.3 * attrs["impact"] +
                0.2 * attrs["synergy"])

        cost = attrs["cost"]
        v = bcp_value(gain, cost, current_budget)

        results.append({
            "name": name,
            "description": attrs["description"],
            "gain": gain,
            "cost": cost,
            "value": v,
            **attrs
        })

    # Sort by value
    results.sort(key=lambda x: x["value"], reverse=True)

    for i, r in enumerate(results):
        print(f"{r['name']:<25} | {r['gain']:.2f} | {r['cost']:.2f} | {r['value']:+.3f} | {i+1}")

    # Winner
    winner = results[0]

    print("\n" + "="*70)
    print("PHASE 86 SELECTION")
    print("="*70)

    print(f"\n🏆 SELECTED: {winner['name']}")
    print(f"   Description: {winner['description']}")
    print(f"   BCP Value: {winner['value']:.3f}")
    print(f"\n   Attributes:")
    print(f"   - Novelty: {winner['novelty']:.0%}")
    print(f"   - Feasibility: {winner['feasibility']:.0%}")
    print(f"   - Impact: {winner['impact']:.0%}")
    print(f"   - Synergy: {winner['synergy']:.0%}")

    # Phase 86 outline based on winner
    print("\n" + "="*70)
    print("PHASE 86 OUTLINE")
    print("="*70)

    if winner["name"] == "Social Systems":
        outline = {
            "phase": 86,
            "name": "Social Systems",
            "gates": [
                "Gate 275: Market Behavior as BCP - Price discovery under constraint",
                "Gate 276: Organization as BCP - Resource allocation in firms",
                "Gate 277: Collective Action as BCP - Cooperation under scarcity",
                "Gate 278: Social Norms as BCP - Rule emergence from constraint",
                "Gate 279: Communication as BCP - Information flow optimization",
                "Gate 280: Phase 86 Synthesis - Social BCP framework",
            ]
        }
    elif winner["name"] == "Computational Systems":
        outline = {
            "phase": 86,
            "name": "Computational Systems",
            "gates": [
                "Gate 275: Scheduling as BCP - CPU/memory allocation",
                "Gate 276: Caching as BCP - Memory hierarchy decisions",
                "Gate 277: Networking as BCP - Bandwidth allocation",
                "Gate 278: Algorithms as BCP - Computational complexity",
                "Gate 279: Database as BCP - Query optimization",
                "Gate 280: Phase 86 Synthesis - Computational BCP framework",
            ]
        }
    elif winner["name"] == "Physical Systems":
        outline = {
            "phase": 86,
            "name": "Physical Systems",
            "gates": [
                "Gate 275: Thermodynamics as BCP - Energy budget",
                "Gate 276: Entropy as λ - Disorder as pressure",
                "Gate 277: Conservation as BCP - Symmetry constraints",
                "Gate 278: Quantum as BCP - Measurement budget",
                "Gate 279: Cosmology as BCP - Universe-scale allocation",
                "Gate 280: Phase 86 Synthesis - Physical BCP framework",
            ]
        }
    elif winner["name"] == "Biological Systems":
        outline = {
            "phase": 86,
            "name": "Biological Systems",
            "gates": [
                "Gate 275: Metabolism as BCP - Cellular energy budget",
                "Gate 276: Immune as BCP - Defense allocation",
                "Gate 277: Ecology as BCP - Ecosystem resource flow",
                "Gate 278: Evolution as BCP - Fitness optimization",
                "Gate 279: Development as BCP - Growth allocation",
                "Gate 280: Phase 86 Synthesis - Biological BCP framework",
            ]
        }
    else:  # Publication Pipeline
        outline = {
            "phase": 86,
            "name": "Publication Pipeline",
            "gates": [
                "Gate 275: Paper Structure - Introduction to Conclusion",
                "Gate 276: Figure Refinement - Publication-ready visuals",
                "Gate 277: Methods Writing - Reproducibility focus",
                "Gate 278: Results Presentation - Clear findings",
                "Gate 279: Submission Preparation - Journal selection",
                "Gate 280: Phase 86 Synthesis - Manuscript complete",
            ]
        }

    print(f"\n**PHASE 86: {outline['name'].upper()}**")
    print(f"\nPlanned Gates:")
    for gate in outline["gates"]:
        print(f"  - {gate}")

    # Save results
    output = {
        "cycle": 2642,
        "gate": 274,
        "phase": "86_planning",
        "timestamp": datetime.now().isoformat(),
        "current_budget": current_budget,
        "lambda": k / (epsilon + current_budget),
        "selected_direction": winner["name"],
        "selected_value": winner["value"],
        "all_directions": results,
        "phase_86_outline": outline
    }

    results_dir = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results")
    results_dir.mkdir(exist_ok=True)

    with open(results_dir / "cycle2642_phase86_planning.json", "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to: {results_dir / 'cycle2642_phase86_planning.json'}")

    return winner["name"], outline


if __name__ == "__main__":
    evaluate_directions()
