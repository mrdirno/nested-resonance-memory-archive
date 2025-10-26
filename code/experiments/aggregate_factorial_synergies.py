#!/usr/bin/env python3
"""
Aggregate Factorial Synergy Results - Paper 3 Analysis

Purpose: Automatically collect and analyze synergy results from all 6 factorial
         experiments (Cycles 255-260), generate summary tables, and prepare
         Paper 3 Results section content.

Usage: Run after all 6 factorial experiments complete
       python3 aggregate_factorial_synergies.py

Output:
  - results/paper3_factorial_synergy_summary.json
  - results/paper3_synergy_matrix.txt (human-readable table)
  - results/paper3_results_draft.md (manuscript section)

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Date: 2025-10-26
Cycle: 259 (Paper 3 mechanism validation phase)
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

# Experimental metadata
EXPERIMENTS = [
    {
        'cycle': 255,
        'name': 'H1×H2',
        'mechanisms': ('H1: Energy Pooling', 'H2: Reality Sources'),
        'file': 'cycle255_h1h2_mechanism_validation_results.json',
        'hypothesis': 'SYNERGISTIC (pooling amplifies source benefits)'
    },
    {
        'cycle': 256,
        'name': 'H1×H4',
        'mechanisms': ('H1: Energy Pooling', 'H4: Spawn Throttling'),
        'file': 'cycle256_h1h4_mechanism_validation_results.json',
        'hypothesis': 'ANTAGONISTIC (throttling reduces pooling benefits)'
    },
    {
        'cycle': 257,
        'name': 'H1×H5',
        'mechanisms': ('H1: Energy Pooling', 'H5: Energy Recovery'),
        'file': 'cycle257_h1h5_mechanism_validation_results.json',
        'hypothesis': 'SYNERGISTIC (recovery extends pooled agent lifespan)'
    },
    {
        'cycle': 258,
        'name': 'H2×H4',
        'mechanisms': ('H2: Reality Sources', 'H4: Spawn Throttling'),
        'file': 'cycle258_h2h4_mechanism_validation_results.json',
        'hypothesis': 'ADDITIVE (independent mechanisms)'
    },
    {
        'cycle': 259,
        'name': 'H2×H5',
        'mechanisms': ('H2: Reality Sources', 'H5: Energy Recovery'),
        'file': 'cycle259_h2h5_mechanism_validation_results.json',
        'hypothesis': 'SYNERGISTIC (sources provide energy, recovery sustains)'
    },
    {
        'cycle': 260,
        'name': 'H4×H5',
        'mechanisms': ('H4: Spawn Throttling', 'H5: Energy Recovery'),
        'file': 'cycle260_h4h5_mechanism_validation_results.json',
        'hypothesis': 'ANTAGONISTIC/ADDITIVE (throttling limits, recovery helps survive)'
    }
]

RESULTS_DIR = Path(__file__).parent / "results"


def load_experiment_results() -> Dict:
    """Load all 6 factorial experiment results."""
    results = {}
    missing = []

    for exp in EXPERIMENTS:
        file_path = RESULTS_DIR / exp['file']
        if not file_path.exists():
            missing.append(exp['name'])
            continue

        with open(file_path, 'r') as f:
            data = json.load(f)

        results[exp['name']] = {
            'cycle': exp['cycle'],
            'mechanisms': exp['mechanisms'],
            'hypothesis': exp['hypothesis'],
            'synergy_analysis': data['synergy_analysis'],
            'conditions': data['conditions'],
            'metadata': data['metadata']
        }

    if missing:
        print(f"⚠️  Warning: {len(missing)} experiments incomplete: {', '.join(missing)}")

    return results


def create_synergy_matrix(results: Dict) -> str:
    """Generate formatted synergy matrix table."""

    # Header
    table = "=" * 80 + "\n"
    table += "PAPER 3: FACTORIAL SYNERGY MATRIX\n"
    table += "=" * 80 + "\n\n"

    # Column headers
    table += f"{'Experiment':<12} {'Mechanisms':<35} {'Synergy':<10} {'Class':<15} {'Match?':<8}\n"
    table += "-" * 80 + "\n"

    # Data rows
    for exp_name, data in sorted(results.items()):
        mech_str = f"{data['mechanisms'][0][:8]} × {data['mechanisms'][1][:8]}"
        synergy = data['synergy_analysis']['synergy']
        classification = data['synergy_analysis']['classification']
        hypothesis = data['hypothesis'].split('(')[0].strip()

        # Check if result matches hypothesis
        match = "✅" if classification == hypothesis else "❌"

        table += f"{exp_name:<12} {mech_str:<35} {synergy:>9.4f} {classification:<15} {match:<8}\n"

    table += "-" * 80 + "\n"

    # Summary statistics
    synergies = [d['synergy_analysis']['synergy'] for d in results.values()]
    classifications = [d['synergy_analysis']['classification'] for d in results.values()]

    n_synergistic = classifications.count('SYNERGISTIC')
    n_antagonistic = classifications.count('ANTAGONISTIC')
    n_additive = classifications.count('ADDITIVE')

    table += f"\nSummary (n={len(results)}):\n"
    table += f"  Synergistic:  {n_synergistic} ({n_synergistic/len(results)*100:.1f}%)\n"
    table += f"  Antagonistic: {n_antagonistic} ({n_antagonistic/len(results)*100:.1f}%)\n"
    table += f"  Additive:     {n_additive} ({n_additive/len(results)*100:.1f}%)\n"
    table += f"\n  Mean synergy: {sum(synergies)/len(synergies):.4f}\n"
    table += f"  Range:        [{min(synergies):.4f}, {max(synergies):.4f}]\n"

    return table


def draft_results_section(results: Dict) -> str:
    """Generate Paper 3 Results section draft."""

    md = "# Results: Factorial Mechanism Interactions\n\n"
    md += "## Overview\n\n"
    md += f"We tested {len(results)} pairwise mechanism interactions using the "
    md += "mechanism validation paradigm (n=1 deterministic runs per condition). "
    md += "Each factorial experiment measured synergy as the deviation from additive "
    md += "prediction: `synergy = ON-ON - (OFF-OFF + effect1 + effect2)`.\n\n"

    md += "## Individual Factorial Results\n\n"

    for exp_name, data in sorted(results.items()):
        md += f"### {exp_name}: {data['mechanisms'][0]} × {data['mechanisms'][1]}\n\n"

        sa = data['synergy_analysis']

        md += f"- **Hypothesis**: {data['hypothesis']}\n"
        md += f"- **Observed Classification**: {sa['classification']}\n"
        md += f"- **Synergy**: {sa['synergy']:.4f}\n"
        md += f"- **Fold-change**: {sa['fold_change']:.2f}×\n\n"

        md += "**Condition Outcomes**:\n"
        md += f"- OFF-OFF (baseline): {sa['off_off']:.4f}\n"
        md += f"- ON-OFF (mechanism 1 only): {sa['on_off']:.4f}\n"
        md += f"- OFF-ON (mechanism 2 only): {sa['off_on']:.4f}\n"
        md += f"- ON-ON (both mechanisms): {sa['on_on']:.4f}\n\n"

        md += f"**Interpretation**: {sa['interpretation']}\n\n"

    md += "## Synthesis\n\n"
    md += "TODO: Interpret patterns across all factorial combinations. "
    md += "Which mechanisms exhibit strong synergies? Which interfere? "
    md += "Implications for system design and NRM framework validation.\n\n"

    return md


def main():
    """Aggregate and analyze all factorial experiment results."""
    print("=" * 70)
    print("PAPER 3: FACTORIAL SYNERGY AGGREGATION")
    print("=" * 70)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()

    # Load results
    print("Loading experiment results...")
    results = load_experiment_results()

    if not results:
        print("❌ No results found. Ensure all factorial experiments have completed.")
        return 1

    print(f"✅ Loaded {len(results)}/{len(EXPERIMENTS)} factorial experiments")
    print()

    # Generate synergy matrix
    print("Generating synergy matrix...")
    synergy_matrix = create_synergy_matrix(results)
    print(synergy_matrix)

    # Save matrix to file
    matrix_file = RESULTS_DIR / "paper3_synergy_matrix.txt"
    with open(matrix_file, 'w') as f:
        f.write(synergy_matrix)
    print(f"✅ Synergy matrix saved: {matrix_file}")
    print()

    # Draft Results section
    print("Drafting Paper 3 Results section...")
    results_draft = draft_results_section(results)

    draft_file = RESULTS_DIR / "paper3_results_draft.md"
    with open(draft_file, 'w') as f:
        f.write(results_draft)
    print(f"✅ Results draft saved: {draft_file}")
    print()

    # Save aggregated JSON
    summary = {
        'metadata': {
            'timestamp': datetime.now().isoformat(),
            'n_experiments': len(results),
            'paradigm': 'mechanism_validation',
            'author': 'Aldrin Payopay <aldrin.gdf@gmail.com>'
        },
        'experiments': results,
        'summary': {
            'classifications': [r['synergy_analysis']['classification'] for r in results.values()],
            'synergies': [r['synergy_analysis']['synergy'] for r in results.values()],
            'fold_changes': [r['synergy_analysis']['fold_change'] for r in results.values()]
        }
    }

    summary_file = RESULTS_DIR / "paper3_factorial_synergy_summary.json"
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"✅ Summary JSON saved: {summary_file}")
    print()

    print("=" * 70)
    print("AGGREGATION COMPLETE")
    print("=" * 70)
    print()
    print("Next steps:")
    print("  1. Review synergy matrix for consistency with hypotheses")
    print("  2. Draft interpretation section in Paper 3")
    print("  3. Generate figures/visualizations from summary JSON")
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
