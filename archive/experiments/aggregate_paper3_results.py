#!/usr/bin/env python3
"""
Results Aggregation Tool: Paper 3 Factorial Validation Experiments

Purpose: Automatically aggregate results from C255-C260 factorial experiments,
         generate cross-pair comparisons, and populate manuscript template.

Usage: python aggregate_paper3_results.py --input results/ --output paper3_aggregated.json

Outputs:
1. JSON with all 6 experiments aggregated
2. Cross-pair synergy heatmap data
3. Markdown summary for manuscript integration
4. LaTeX tables for publication

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Date: 2025-10-27 (Cycle 350)
License: GPL-3.0
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
"""

import sys
import json
import argparse
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime
from collections import defaultdict


# Experiment metadata
EXPERIMENTS = {
    'cycle255': {
        'pair': 'H1×H2',
        'mechanisms': ('H1_pooling', 'H2_sources'),
        'names': ('Energy Pooling', 'Reality Sources'),
        'file': 'cycle255_h1h2_mechanism_validation_results.json'
    },
    'cycle256': {
        'pair': 'H1×H4',
        'mechanisms': ('H1_pooling', 'H4_throttling'),
        'names': ('Energy Pooling', 'Spawn Throttling'),
        'file': 'cycle256_h1h4_mechanism_validation_results.json'
    },
    'cycle257': {
        'pair': 'H1×H5',
        'mechanisms': ('H1_pooling', 'H5_recovery'),
        'names': ('Energy Pooling', 'Energy Recovery'),
        'file': 'cycle257_h1h5_mechanism_validation_results.json'
    },
    'cycle258': {
        'pair': 'H2×H4',
        'mechanisms': ('H2_sources', 'H4_throttling'),
        'names': ('Reality Sources', 'Spawn Throttling'),
        'file': 'cycle258_h2h4_mechanism_validation_results.json'
    },
    'cycle259': {
        'pair': 'H2×H5',
        'mechanisms': ('H2_sources', 'H5_recovery'),
        'names': ('Reality Sources', 'Energy Recovery'),
        'file': 'cycle259_h2h5_mechanism_validation_results.json'
    },
    'cycle260': {
        'pair': 'H4×H5',
        'mechanisms': ('H4_throttling', 'H5_recovery'),
        'names': ('Spawn Throttling', 'Energy Recovery'),
        'file': 'cycle260_h4h5_mechanism_validation_results.json'
    }
}


def load_experiment_results(input_dir: Path, experiment_id: str) -> Dict:
    """Load results for a single experiment."""
    exp_meta = EXPERIMENTS[experiment_id]
    filepath = input_dir / exp_meta['file']

    if not filepath.exists():
        print(f"⚠️  Warning: {experiment_id} not found at {filepath}")
        return None

    with open(filepath, 'r') as f:
        data = json.load(f)

    # Add metadata
    data['experiment_id'] = experiment_id
    data['pair'] = exp_meta['pair']
    data['mechanism_names'] = exp_meta['names']

    return data


def aggregate_all_experiments(input_dir: Path) -> Dict:
    """Load and aggregate all 6 experiments."""
    aggregated = {
        'metadata': {
            'aggregation_date': datetime.now().isoformat(),
            'experiments_included': [],
            'experiments_missing': []
        },
        'experiments': {},
        'cross_pair_analysis': {}
    }

    for exp_id in EXPERIMENTS.keys():
        result = load_experiment_results(input_dir, exp_id)
        if result:
            aggregated['experiments'][exp_id] = result
            aggregated['metadata']['experiments_included'].append(exp_id)
            print(f"✅ Loaded: {exp_id} ({EXPERIMENTS[exp_id]['pair']})")
        else:
            aggregated['metadata']['experiments_missing'].append(exp_id)
            print(f"❌ Missing: {exp_id} ({EXPERIMENTS[exp_id]['pair']})")

    return aggregated


def generate_synergy_heatmap_data(aggregated: Dict) -> Dict:
    """
    Generate synergy heatmap data for visualization.

    Returns matrix of synergy values for all mechanism pairs.
    """
    mechanisms = ['H1', 'H2', 'H4', 'H5']
    synergy_matrix = np.zeros((len(mechanisms), len(mechanisms)))
    synergy_matrix[:] = np.nan  # Initialize with NaN

    mechanism_indices = {mech: idx for idx, mech in enumerate(mechanisms)}

    # Populate matrix from experiments
    for exp_id, exp_data in aggregated['experiments'].items():
        if 'synergy_analysis' not in exp_data:
            continue

        synergy_val = exp_data['synergy_analysis']['synergy']
        pair = EXPERIMENTS[exp_id]['pair']

        # Extract mechanism IDs from pair (e.g., "H1×H2" → "H1", "H2")
        m1, m2 = pair.split('×')

        if m1 in mechanism_indices and m2 in mechanism_indices:
            i, j = mechanism_indices[m1], mechanism_indices[m2]
            synergy_matrix[i, j] = synergy_val
            synergy_matrix[j, i] = synergy_val  # Symmetric

    return {
        'mechanisms': mechanisms,
        'synergy_matrix': synergy_matrix.tolist(),
        'interpretation': {
            'synergistic': [
                f"{mechanisms[i]}×{mechanisms[j]}"
                for i in range(len(mechanisms))
                for j in range(i+1, len(mechanisms))
                if not np.isnan(synergy_matrix[i, j]) and synergy_matrix[i, j] > 0.1
            ],
            'antagonistic': [
                f"{mechanisms[i]}×{mechanisms[j]}"
                for i in range(len(mechanisms))
                for j in range(i+1, len(mechanisms))
                if not np.isnan(synergy_matrix[i, j]) and synergy_matrix[i, j] < -0.1
            ],
            'additive': [
                f"{mechanisms[i]}×{mechanisms[j]}"
                for i in range(len(mechanisms))
                for j in range(i+1, len(mechanisms))
                if not np.isnan(synergy_matrix[i, j]) and abs(synergy_matrix[i, j]) <= 0.1
            ]
        }
    }


def generate_markdown_summary(aggregated: Dict, heatmap_data: Dict) -> str:
    """Generate markdown summary for manuscript integration."""
    md = []

    md.append("# Paper 3: Factorial Validation Results Summary")
    md.append("")
    md.append(f"**Generated:** {aggregated['metadata']['aggregation_date']}")
    md.append(f"**Experiments Completed:** {len(aggregated['experiments'])}/6")
    md.append("")

    # Results table
    md.append("## Summary Table")
    md.append("")
    md.append("| Experiment | Pair | H1 Effect | H2 Effect | Synergy | Classification |")
    md.append("|------------|------|-----------|-----------|---------|----------------|")

    for exp_id in sorted(aggregated['experiments'].keys()):
        exp_data = aggregated['experiments'][exp_id]
        syn = exp_data.get('synergy_analysis', {})

        pair = exp_data.get('pair', 'Unknown')
        h1_eff = syn.get('h1_effect', 0.0)
        h2_eff = syn.get('h2_effect', 0.0)
        synergy = syn.get('synergy', 0.0)
        classification = syn.get('classification', 'Unknown')

        md.append(f"| {exp_id} | {pair} | {h1_eff:+.2f} | {h2_eff:+.2f} | {synergy:+.2f} | **{classification}** |")

    md.append("")

    # Classification breakdown
    md.append("## Classification Breakdown")
    md.append("")
    interp = heatmap_data['interpretation']
    md.append(f"- **Synergistic pairs ({len(interp['synergistic'])}):** {', '.join(interp['synergistic']) if interp['synergistic'] else 'None'}")
    md.append(f"- **Antagonistic pairs ({len(interp['antagonistic'])}):** {', '.join(interp['antagonistic']) if interp['antagonistic'] else 'None'}")
    md.append(f"- **Additive pairs ({len(interp['additive'])}):** {', '.join(interp['additive']) if interp['additive'] else 'None'}")
    md.append("")

    # Computational expense summary
    md.append("## Computational Expense Summary")
    md.append("")
    total_runtime = 0.0
    for exp_id, exp_data in aggregated['experiments'].items():
        conditions = exp_data.get('conditions', {})
        exp_runtime = sum(
            cond.get('runtime_seconds', 0) for cond in conditions.values()
        ) / 60.0  # Convert to minutes
        total_runtime += exp_runtime

        md.append(f"- **{exp_id}:** {exp_runtime:.1f} minutes")

    md.append("")
    md.append(f"**Total computational time:** {total_runtime:.1f} minutes ({total_runtime/60:.2f} hours)")
    md.append("")

    return "\n".join(md)


def generate_latex_tables(aggregated: Dict) -> str:
    """Generate LaTeX tables for publication."""
    latex = []

    latex.append("% LaTeX tables for Paper 3")
    latex.append("% Copy into manuscript as needed")
    latex.append("")

    # Main results table
    latex.append("\\begin{table}[h]")
    latex.append("\\centering")
    latex.append("\\caption{Factorial Validation Results: Mechanism Synergy Analysis}")
    latex.append("\\label{tab:factorial_results}")
    latex.append("\\begin{tabular}{lccccc}")
    latex.append("\\hline")
    latex.append("Pair & H1 Effect & H2 Effect & Synergy & Fold-Change & Classification \\\\")
    latex.append("\\hline")

    for exp_id in sorted(aggregated['experiments'].keys()):
        exp_data = aggregated['experiments'][exp_id]
        syn = exp_data.get('synergy_analysis', {})

        pair = exp_data.get('pair', 'Unknown').replace('×', '$\\times$')
        h1_eff = syn.get('h1_effect', 0.0)
        h2_eff = syn.get('h2_effect', 0.0)
        synergy = syn.get('synergy', 0.0)
        fold = syn.get('fold_change', 1.0)
        classification = syn.get('classification', 'Unknown')

        latex.append(f"{pair} & {h1_eff:+.2f} & {h2_eff:+.2f} & {synergy:+.2f} & {fold:.2f} & \\textbf{{{classification}}} \\\\")

    latex.append("\\hline")
    latex.append("\\end{tabular}")
    latex.append("\\end{table}")
    latex.append("")

    return "\n".join(latex)


def populate_manuscript_template(aggregated: Dict, template_path: Path, output_path: Path):
    """
    Populate manuscript template with actual experimental results.

    Replaces placeholders like **[VALUE]** with actual data.
    """
    if not template_path.exists():
        print(f"⚠️  Template not found: {template_path}")
        return False

    with open(template_path, 'r') as f:
        template = f.read()

    # Extract key values for replacement
    replacements = {}

    for exp_id, exp_data in aggregated['experiments'].items():
        syn = exp_data.get('synergy_analysis', {})

        # Create replacement keys
        prefix = exp_id.replace('cycle', 'C')
        replacements[f"{prefix}_OFF_OFF"] = f"{syn.get('off_off', 0.0):.2f}"
        replacements[f"{prefix}_ON_OFF"] = f"{syn.get('on_off', 0.0):.2f}"
        replacements[f"{prefix}_OFF_ON"] = f"{syn.get('off_on', 0.0):.2f}"
        replacements[f"{prefix}_ON_ON"] = f"{syn.get('on_on', 0.0):.2f}"
        replacements[f"{prefix}_H1_EFFECT"] = f"{syn.get('h1_effect', 0.0):+.2f}"
        replacements[f"{prefix}_H2_EFFECT"] = f"{syn.get('h2_effect', 0.0):+.2f}"
        replacements[f"{prefix}_SYNERGY"] = f"{syn.get('synergy', 0.0):+.2f}"
        replacements[f"{prefix}_CLASS"] = syn.get('classification', 'Unknown')

    # Perform replacements
    populated = template
    for key, value in replacements.items():
        populated = populated.replace(f"**[{key}]**", value)

    # Write populated manuscript
    with open(output_path, 'w') as f:
        f.write(populated)

    print(f"✅ Populated manuscript saved: {output_path}")
    return True


def main():
    """Main aggregation pipeline."""
    parser = argparse.ArgumentParser(
        description='Aggregate Paper 3 factorial validation results'
    )
    parser.add_argument(
        '--input',
        type=Path,
        default=Path('results'),
        help='Input directory containing experiment JSON files'
    )
    parser.add_argument(
        '--output',
        type=Path,
        default=Path('paper3_aggregated.json'),
        help='Output JSON file for aggregated results'
    )
    parser.add_argument(
        '--markdown',
        type=Path,
        default=Path('paper3_summary.md'),
        help='Output markdown summary file'
    )
    parser.add_argument(
        '--latex',
        type=Path,
        default=Path('paper3_tables.tex'),
        help='Output LaTeX tables file'
    )
    parser.add_argument(
        '--template',
        type=Path,
        default=Path('../papers/paper3_full_manuscript_template.md'),
        help='Manuscript template to populate'
    )
    parser.add_argument(
        '--manuscript',
        type=Path,
        default=Path('../papers/paper3_full_manuscript_FINAL.md'),
        help='Output populated manuscript'
    )

    args = parser.parse_args()

    print("=" * 70)
    print("PAPER 3 RESULTS AGGREGATION")
    print("=" * 70)
    print(f"Input directory: {args.input}")
    print(f"Output files:")
    print(f"  - JSON: {args.output}")
    print(f"  - Markdown: {args.markdown}")
    print(f"  - LaTeX: {args.latex}")
    print(f"  - Manuscript: {args.manuscript}")
    print()

    # Step 1: Load all experiments
    print("📂 Loading experiments...")
    aggregated = aggregate_all_experiments(args.input)
    print()

    if not aggregated['experiments']:
        print("❌ No experiments found. Exiting.")
        return 1

    # Step 2: Generate synergy heatmap data
    print("🔥 Generating synergy heatmap data...")
    heatmap_data = generate_synergy_heatmap_data(aggregated)
    aggregated['cross_pair_analysis']['synergy_heatmap'] = heatmap_data
    print(f"  - Synergistic pairs: {len(heatmap_data['interpretation']['synergistic'])}")
    print(f"  - Antagonistic pairs: {len(heatmap_data['interpretation']['antagonistic'])}")
    print(f"  - Additive pairs: {len(heatmap_data['interpretation']['additive'])}")
    print()

    # Step 3: Save aggregated JSON
    print("💾 Saving aggregated JSON...")
    with open(args.output, 'w') as f:
        json.dump(aggregated, f, indent=2)
    print(f"✅ Saved: {args.output}")
    print()

    # Step 4: Generate markdown summary
    print("📝 Generating markdown summary...")
    markdown_summary = generate_markdown_summary(aggregated, heatmap_data)
    with open(args.markdown, 'w') as f:
        f.write(markdown_summary)
    print(f"✅ Saved: {args.markdown}")
    print()

    # Step 5: Generate LaTeX tables
    print("📐 Generating LaTeX tables...")
    latex_tables = generate_latex_tables(aggregated)
    with open(args.latex, 'w') as f:
        f.write(latex_tables)
    print(f"✅ Saved: {args.latex}")
    print()

    # Step 6: Populate manuscript template
    if args.template.exists():
        print("📄 Populating manuscript template...")
        success = populate_manuscript_template(aggregated, args.template, args.manuscript)
        if success:
            print("✅ Manuscript ready for review and submission!")
        print()
    else:
        print(f"⚠️  Template not found: {args.template}")
        print("   Skipping manuscript population.")
        print()

    # Summary
    print("=" * 70)
    print("✅ AGGREGATION COMPLETE")
    print("=" * 70)
    print(f"Experiments processed: {len(aggregated['experiments'])}/6")
    print(f"Missing experiments: {len(aggregated['metadata']['experiments_missing'])}")
    print()
    print("Next steps:")
    print("  1. Review aggregated results in JSON and markdown")
    print("  2. Verify synergy classifications match expectations")
    print("  3. Check populated manuscript for accuracy")
    print("  4. Generate figures: python visualize_factorial_synergy.py <results_json>")
    print("  5. Finalize Discussion section based on synergy patterns")
    print("  6. Submit for peer review")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())
