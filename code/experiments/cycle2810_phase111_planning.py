#!/usr/bin/env python3
"""
DUALITY-ZERO: Cycle 2810 - Phase 111 Planning
Gate 449 - Domain Selection for 26th Scientific Domain

PURPOSE: Select optimal domain for BCP validation using value function
V(domain) = Weighted_Gain - lambda(B) x Cost

Previously Validated Domains (25):
  Phase 86-110: Social, Cognitive, Computational, Biological, Economic,
                Physical, Quantum, Information Theory, Comp II, Game Theory,
                Network Science, Medical, Control Theory, Linguistic, Decision,
                Complex Systems, Robotics, Dev Biology, Immunology, Metabolic,
                Cellular Biology, Neuroscience, Ecological, Thermodynamics,
                Fluid Dynamics

Author: Aldrin Payopay (aldrin.gdf@gmail.com)
License: GPL-3.0
"""
import json
from datetime import datetime

def selection_lambda(b, k=1.0, e=0.1):
    return k / (e + max(0.01, b))

def selection_value(gain, cost, budget):
    return gain - selection_lambda(budget) * cost

def main():
    print("="*70)
    print("CYCLE 2810: PHASE 111 DOMAIN SELECTION")
    print("Gate 449 - BCP Domain Planning")
    print("="*70)
    print(f"\nTimestamp: {datetime.now().isoformat()}")

    # Candidate domains for 26th validation
    candidates = {
        'Signal Processing': {
            'novelty': 0.85,
            'testability': 0.93,
            'impact': 0.88,
            'universality': 0.86,
            'overlap': 0.25,
            'complexity': 0.25
        },
        'Pharmacology': {
            'novelty': 0.86,
            'testability': 0.85,
            'impact': 0.92,
            'universality': 0.78,
            'overlap': 0.25,
            'complexity': 0.38
        },
        'Evolutionary Biology': {
            'novelty': 0.88,
            'testability': 0.88,
            'impact': 0.92,
            'universality': 0.90,
            'overlap': 0.22,
            'complexity': 0.32
        },
        'Structural Mechanics': {
            'novelty': 0.84,
            'testability': 0.92,
            'impact': 0.88,
            'universality': 0.85,
            'overlap': 0.20,
            'complexity': 0.30
        },
        'Optics & Photonics': {
            'novelty': 0.86,
            'testability': 0.90,
            'impact': 0.88,
            'universality': 0.88,
            'overlap': 0.22,
            'complexity': 0.28
        }
    }

    print("\n" + "="*70)
    print("CANDIDATE DOMAIN ANALYSIS")
    print("="*70)

    results = {}
    for budget in [0.1, 0.3, 0.5, 1.0, 2.0]:
        print(f"\n  Budget Level: {budget}")
        print("-"*60)
        for domain, params in candidates.items():
            gain = (0.3 * params['novelty'] +
                   0.3 * params['testability'] +
                   0.2 * params['impact'] +
                   0.2 * params['universality'])
            cost = 0.6 * params['overlap'] + 0.4 * params['complexity']
            value = selection_value(gain, cost, budget)
            results[(domain, budget)] = value
            print(f"    {domain:22} | Gain={gain:.3f} Cost={cost:.3f} V={value:+.3f}")

    # Select optimal domain
    print("\n" + "="*70)
    print("DOMAIN SELECTION RESULTS")
    print("="*70)

    # Aggregate across budgets
    domain_scores = {}
    for domain in candidates:
        scores = [results[(domain, b)] for b in [0.1, 0.3, 0.5, 1.0, 2.0]]
        domain_scores[domain] = sum(scores) / len(scores)
        print(f"  {domain:22} | Mean Value: {domain_scores[domain]:+.3f}")

    selected = max(domain_scores.items(), key=lambda x: x[1])

    print("\n" + "="*70)
    print(f"SELECTED DOMAIN: {selected[0].upper()}")
    print(f"Mean Value Score: {selected[1]:+.3f}")
    print("="*70)

    # Define tests for Evolutionary Biology
    print("\n  Planned Gates (450-454):")
    tests = [
        ("Gate 450", "Natural Selection", "Fitness, Adaptation, Selection Pressure, Drift, Directional"),
        ("Gate 451", "Genetic Variation", "Mutation, Recombination, Gene Flow, Polymorphism, Heritability"),
        ("Gate 452", "Speciation", "Allopatric, Sympatric, Parapatric, Reproductive Isolation, Divergence"),
        ("Gate 453", "Phylogenetics", "Cladistics, Molecular, Morphological, Coalescent, Ancestral"),
        ("Gate 454", "Coevolution", "Arms Race, Mutualistic, Parasitic, Diffuse, Reciprocal")
    ]

    for gate, name, tests_str in tests:
        print(f"    {gate}: {name}")
        print(f"            Tests: {tests_str}")

    print("\n  Gate 455: Phase 111 Synthesis")

    # BCP formulation for evolutionary biology
    print("\n" + "="*70)
    print("BCP FORMULATION: EVOLUTIONARY BIOLOGY")
    print("="*70)
    print("  Master Equation:")
    print("    V(evolution) = Fitness_Gain - λ(B_resources) × Adaptation_Cost")
    print("  Where:")
    print("    λ(B) = k / (ε + B)")
    print("    B = available resources (energy, food, mates)")
    print("\n  Key Predictions:")
    print("    1. Low resources → conservative strategies dominate")
    print("    2. High resources → diversification and specialization")
    print("    3. Selection intensity follows resource gradients")
    print("    4. Optimal fitness at ecological equilibrium")

    # Save selection
    selection = {
        "experiment": "Phase 111 Domain Selection",
        "gate": 449,
        "cycle": 2810,
        "phase": 111,
        "timestamp": datetime.now().isoformat(),
        "selected_domain": selected[0],
        "selection_score": round(selected[1], 4),
        "candidates_evaluated": len(candidates),
        "planned_gates": "450-455",
        "predictions": 20
    }

    with open("results/cycle2810_phase111_planning.json", "w") as f:
        json.dump(selection, f, indent=2)
    print(f"\n  Selection saved to results/cycle2810_phase111_planning.json")

    print("\n" + "="*70)
    print("GATE 449 COMPLETE: DOMAIN SELECTED")
    print(f"Phase 111 Domain: {selected[0]}")
    print("="*70)

    return selected[0]

if __name__ == "__main__":
    main()
    print("\nEXECUTION COMPLETE")
