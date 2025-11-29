#!/usr/bin/env python3
"""
DUALITY-ZERO: Cycle 2789 - Phase 108 Planning
Gate 428 - Domain Selection for 23rd Scientific Domain

PURPOSE: Select optimal domain for BCP validation using value function
V(domain) = Weighted_Gain - lambda(B) x Cost

Previously Validated Domains (22):
  Phase 86: Social Systems
  Phase 87: Cognitive Systems
  Phase 88: Computational Systems
  Phase 89: Biological Systems
  Phase 90: Economic Systems
  Phase 91: Physical Systems
  Phase 92: Quantum Systems
  Phase 93: Information Theory
  Phase 94: Computational II
  Phase 95: Game Theory
  Phase 96: Network Science
  Phase 97: Medical Systems
  Phase 98: Control Theory
  Phase 99: Linguistic Systems
  Phase 100: Decision Theory
  Phase 101: Complex Systems
  Phase 102: Robotics & Control
  Phase 103: Developmental Biology
  Phase 104: Immunology
  Phase 105: Metabolic Systems
  Phase 106: Cellular Biology
  Phase 107: Neuroscience

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
    print("CYCLE 2789: PHASE 108 DOMAIN SELECTION")
    print("Gate 428 - BCP Domain Planning")
    print("="*70)
    print(f"\nTimestamp: {datetime.now().isoformat()}")

    # Candidate domains for 23rd validation
    candidates = {
        'Ecological Systems': {
            'novelty': 0.90,        # Population dynamics, ecosystems
            'testability': 0.92,    # Well-defined models
            'impact': 0.88,         # Environmental applications
            'universality': 0.90,   # Fundamental to life
            'overlap': 0.15,        # Low overlap with validated
            'complexity': 0.35      # Moderate complexity
        },
        'Thermodynamics': {
            'novelty': 0.85,
            'testability': 0.95,    # Very well-defined laws
            'impact': 0.90,
            'universality': 0.95,   # Universal physical laws
            'overlap': 0.25,        # Some overlap with physics
            'complexity': 0.30
        },
        'Signal Processing': {
            'novelty': 0.82,
            'testability': 0.93,
            'impact': 0.85,
            'universality': 0.80,
            'overlap': 0.30,        # Overlap with information theory
            'complexity': 0.25
        },
        'Pharmacology': {
            'novelty': 0.88,
            'testability': 0.85,
            'impact': 0.92,         # Medical applications
            'universality': 0.78,
            'overlap': 0.20,
            'complexity': 0.40
        },
        'Materials Science': {
            'novelty': 0.84,
            'testability': 0.88,
            'impact': 0.86,
            'universality': 0.82,
            'overlap': 0.22,
            'complexity': 0.38
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

    # Define tests for Ecological Systems
    print("\n  Planned Gates (429-434):")
    tests = [
        ("Gate 429", "Population Dynamics", "Logistic, Lotka-Volterra, Age-Structure, Metapopulation, Stochastic"),
        ("Gate 430", "Community Ecology", "Competition, Predation, Mutualism, Trophic, Niche"),
        ("Gate 431", "Ecosystem Dynamics", "Energy Flow, Nutrient Cycling, Productivity, Decomposition, Succession"),
        ("Gate 432", "Biogeochemistry", "Carbon, Nitrogen, Phosphorus, Water, Feedback"),
        ("Gate 433", "Conservation Ecology", "Fragmentation, Corridors, Reserves, Restoration, Monitoring")
    ]

    for gate, name, tests_str in tests:
        print(f"    {gate}: {name}")
        print(f"            Tests: {tests_str}")

    print("\n  Gate 434: Phase 108 Synthesis")

    # BCP formulation for ecology
    print("\n" + "="*70)
    print("BCP FORMULATION: ECOLOGICAL SYSTEMS")
    print("="*70)
    print("  Master Equation:")
    print("    V(ecological) = Fitness_Outcome - λ(B_resources) × Metabolic_Cost")
    print("  Where:")
    print("    λ(B) = k / (ε + B)")
    print("    B = available resources (energy, nutrients, space)")
    print("\n  Key Predictions:")
    print("    1. Low resources → conservative strategies dominate")
    print("    2. High resources → growth/competition strategies emerge")
    print("    3. Transition points follow BCP pressure curve")
    print("    4. Optimal allocation shifts with resource availability")

    # Save selection
    selection = {
        "experiment": "Phase 108 Domain Selection",
        "gate": 428,
        "cycle": 2789,
        "phase": 108,
        "timestamp": datetime.now().isoformat(),
        "selected_domain": selected[0],
        "selection_score": round(selected[1], 4),
        "candidates_evaluated": len(candidates),
        "planned_gates": "429-434",
        "predictions": 20
    }

    with open("results/cycle2789_phase108_planning.json", "w") as f:
        json.dump(selection, f, indent=2)
    print(f"\n  Selection saved to results/cycle2789_phase108_planning.json")

    print("\n" + "="*70)
    print("GATE 428 COMPLETE: DOMAIN SELECTED")
    print(f"Phase 108 Domain: {selected[0]}")
    print("="*70)

    return selected[0]

if __name__ == "__main__":
    main()
    print("\nEXECUTION COMPLETE")
