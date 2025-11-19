#!/usr/bin/env python3
"""
Results Aggregation Tool: Paper 4 Higher-Order Factorial Experiments

Purpose: Aggregate results from C262-C263 higher-order factorial experiments,
         calculate 3-way and 4-way interaction terms, and populate manuscript.

Usage: python aggregate_paper4_results.py --input results/ --output paper4_aggregated.json

Outputs:
1. JSON with 3-way and 4-way experiments aggregated
2. Hierarchical interaction decomposition
3. Variance explained analysis
4. Markdown summary for manuscript integration
5. LaTeX tables for publication

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Date: 2025-10-27 (Cycle 352)
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
from itertools import combinations


# Experiment metadata
EXPERIMENTS = {
    'cycle262': {
        'order': '3-way',
        'mechanisms': ['H1_pooling', 'H2_sources', 'H5_recovery'],
        'names': ['Energy Pooling', 'Reality Sources', 'Energy Recovery'],
        'file': 'cycle262_h1h2h5_3way_factorial_results.json',
        'num_conditions': 8
    },
    'cycle263': {
        'order': '4-way',
        'mechanisms': ['H1_pooling', 'H2_sources', 'H4_throttling', 'H5_recovery'],
        'names': ['Energy Pooling', 'Reality Sources', 'Spawn Throttling', 'Energy Recovery'],
        'file': 'cycle263_h1h2h4h5_4way_factorial_results.json',
        'num_conditions': 16
    }
}


def load_experiment_results(input_dir: Path, experiment_id: str) -> Dict:
    """Load results for a single higher-order factorial experiment."""
    exp_meta = EXPERIMENTS[experiment_id]
    filepath = input_dir / exp_meta['file']

    if not filepath.exists():
        print(f"⚠️  Warning: {experiment_id} not found at {filepath}")
        return None

    with open(filepath, 'r') as f:
        data = json.load(f)

    # Add metadata
    data['experiment_id'] = experiment_id
    data['factorial_order'] = exp_meta['order']
    data['mechanism_names'] = exp_meta['names']

    return data


def calculate_main_effects(conditions: Dict) -> Dict[str, float]:
    """
    Calculate main effects from single-mechanism conditions.

    Returns dict mapping mechanism -> effect size.
    """
    baseline = conditions.get('000', {}).get('mean_population', 0.0) or \
               conditions.get('0000', {}).get('mean_population', 0.0)

    effects = {}

    # Try 3-way patterns (100, 010, 001)
    for mech_idx, mech_code in enumerate(['100', '010', '001']):
        if mech_code in conditions:
            mech_name = f"M{mech_idx+1}"
            effects[mech_name] = conditions[mech_code]['mean_population'] - baseline

    # Try 4-way patterns (1000, 0100, 0010, 0001)
    for mech_idx, mech_code in enumerate(['1000', '0100', '0010', '0001']):
        if mech_code in conditions:
            mech_name = f"M{mech_idx+1}"
            effects[mech_name] = conditions[mech_code]['mean_population'] - baseline

    return effects


def calculate_pairwise_interactions(conditions: Dict, main_effects: Dict) -> Dict[str, float]:
    """
    Calculate pairwise interaction terms.

    Returns dict mapping pair -> synergy.
    """
    baseline = conditions.get('000', {}).get('mean_population', 0.0) or \
               conditions.get('0000', {}).get('mean_population', 0.0)

    pairwise = {}

    # 3-way patterns
    pairs_3way = [
        ('110', 'M1', 'M2'),
        ('101', 'M1', 'M3'),
        ('011', 'M2', 'M3')
    ]

    for code, m1, m2 in pairs_3way:
        if code in conditions:
            observed = conditions[code]['mean_population']
            additive = baseline + main_effects.get(m1, 0.0) + main_effects.get(m2, 0.0)
            pairwise[f"{m1}×{m2}"] = observed - additive

    # 4-way patterns
    pairs_4way = [
        ('1100', 'M1', 'M2'),
        ('1010', 'M1', 'M3'),
        ('1001', 'M1', 'M4'),
        ('0110', 'M2', 'M3'),
        ('0101', 'M2', 'M4'),
        ('0011', 'M3', 'M4')
    ]

    for code, m1, m2 in pairs_4way:
        if code in conditions:
            observed = conditions[code]['mean_population']
            additive = baseline + main_effects.get(m1, 0.0) + main_effects.get(m2, 0.0)
            pairwise[f"{m1}×{m2}"] = observed - additive

    return pairwise


def calculate_3way_interaction(conditions: Dict, main_effects: Dict, pairwise: Dict) -> Dict:
    """
    Calculate 3-way super-synergy term.

    Returns dict with super-synergy and decomposition.
    """
    code_3way = '111'
    if code_3way not in conditions:
        return None

    baseline = conditions.get('000', {}).get('mean_population', 0.0)
    observed = conditions[code_3way]['mean_population']

    # Additive prediction
    additive_pred = baseline + sum(main_effects.values())

    # Pairwise prediction
    pairwise_pred = additive_pred + sum(pairwise.values())

    # Super-synergy
    super_synergy = observed - pairwise_pred

    return {
        'observed': observed,
        'baseline': baseline,
        'additive_prediction': additive_pred,
        'pairwise_prediction': pairwise_pred,
        'super_synergy': super_synergy,
        'fold_change': observed / baseline if baseline > 0 else 0.0,
        'classification': classify_synergy(super_synergy)
    }


def calculate_4way_interaction(conditions: Dict, main_effects: Dict,
                                pairwise: Dict, threeway: Dict) -> Dict:
    """
    Calculate 4-way super-synergy term.

    Returns dict with super-synergy and decomposition.
    """
    code_4way = '1111'
    if code_4way not in conditions:
        return None

    baseline = conditions.get('0000', {}).get('mean_population', 0.0)
    observed = conditions[code_4way]['mean_population']

    # Additive prediction
    additive_pred = baseline + sum(main_effects.values())

    # Pairwise prediction
    pairwise_pred = additive_pred + sum(pairwise.values())

    # 3-way terms (need to calculate from data)
    # For 4-way factorial: 4 possible 3-way combinations
    # 1110 (M1×M2×M3), 1101 (M1×M2×M4), 1011 (M1×M3×M4), 0111 (M2×M3×M4)
    threeway_terms = calculate_all_3way_terms(conditions, main_effects, pairwise)
    threeway_pred = pairwise_pred + sum(threeway_terms.values())

    # Super-synergy (4-way)
    super_synergy = observed - threeway_pred

    return {
        'observed': observed,
        'baseline': baseline,
        'additive_prediction': additive_pred,
        'pairwise_prediction': pairwise_pred,
        'threeway_prediction': threeway_pred,
        'super_synergy': super_synergy,
        'fold_change': observed / baseline if baseline > 0 else 0.0,
        'classification': classify_synergy(super_synergy),
        'threeway_terms': threeway_terms
    }


def calculate_all_3way_terms(conditions: Dict, main_effects: Dict, pairwise: Dict) -> Dict:
    """
    Calculate all 3-way interaction terms for 4-way factorial.

    Returns dict mapping triple -> synergy.
    """
    baseline = conditions.get('0000', {}).get('mean_population', 0.0)

    triples = [
        ('1110', ['M1', 'M2', 'M3'], ['M1×M2', 'M1×M3', 'M2×M3']),
        ('1101', ['M1', 'M2', 'M4'], ['M1×M2', 'M1×M4', 'M2×M4']),
        ('1011', ['M1', 'M3', 'M4'], ['M1×M3', 'M1×M4', 'M3×M4']),
        ('0111', ['M2', 'M3', 'M4'], ['M2×M3', 'M2×M4', 'M3×M4'])
    ]

    threeway_terms = {}

    for code, mechs, pairs in triples:
        if code not in conditions:
            continue

        observed = conditions[code]['mean_population']

        # Additive: baseline + main effects
        additive = baseline + sum(main_effects.get(m, 0.0) for m in mechs)

        # Pairwise: additive + pairwise interactions
        pairwise_sum = sum(pairwise.get(p, 0.0) for p in pairs)
        pairwise_pred = additive + pairwise_sum

        # 3-way interaction = observed - pairwise prediction
        threeway_synergy = observed - pairwise_pred

        threeway_terms[f"{mechs[0]}×{mechs[1]}×{mechs[2]}"] = threeway_synergy

    return threeway_terms


def classify_synergy(synergy: float, threshold: float = 0.1) -> str:
    """Classify synergy as synergistic, antagonistic, or additive."""
    if synergy > threshold:
        return "SYNERGISTIC"
    elif synergy < -threshold:
        return "ANTAGONISTIC"
    else:
        return "ADDITIVE"


def calculate_variance_explained(exp_data: Dict) -> Dict:
    """
    Calculate variance explained by each order of interaction.

    Returns dict with R² for main effects, pairwise, 3-way, 4-way.
    """
    conditions = exp_data.get('conditions', {})

    # Extract all mean populations
    means = [c['mean_population'] for c in conditions.values()]
    grand_mean = np.mean(means)
    total_variance = np.sum((np.array(means) - grand_mean) ** 2)

    # Main effects variance
    main_effects = calculate_main_effects(conditions)
    main_variance = sum(v**2 for v in main_effects.values())

    # Pairwise variance
    pairwise = calculate_pairwise_interactions(conditions, main_effects)
    pairwise_variance = sum(v**2 for v in pairwise.values())

    # Calculate R²
    r2_main = main_variance / total_variance if total_variance > 0 else 0.0
    r2_pairwise = (main_variance + pairwise_variance) / total_variance if total_variance > 0 else 0.0

    return {
        'total_variance': total_variance,
        'main_effects_variance': main_variance,
        'pairwise_variance': pairwise_variance,
        'r2_main': r2_main,
        'r2_pairwise': r2_pairwise,
        'r2_residual': 1.0 - r2_pairwise
    }


def aggregate_all_experiments(input_dir: Path) -> Dict:
    """Load and aggregate all higher-order factorial experiments."""
    aggregated = {
        'metadata': {
            'aggregation_date': datetime.now().isoformat(),
            'experiments_included': [],
            'experiments_missing': []
        },
        'experiments': {},
        'hierarchical_analysis': {}
    }

    for exp_id in EXPERIMENTS.keys():
        result = load_experiment_results(input_dir, exp_id)
        if result:
            # Calculate interaction terms
            conditions = result.get('conditions', {})
            main_effects = calculate_main_effects(conditions)
            pairwise = calculate_pairwise_interactions(conditions, main_effects)

            # Add to result
            result['main_effects'] = main_effects
            result['pairwise_interactions'] = pairwise

            # Calculate higher-order terms
            if EXPERIMENTS[exp_id]['order'] == '3-way':
                result['threeway_analysis'] = calculate_3way_interaction(conditions, main_effects, pairwise)
            elif EXPERIMENTS[exp_id]['order'] == '4-way':
                threeway_terms = calculate_all_3way_terms(conditions, main_effects, pairwise)
                result['fourway_analysis'] = calculate_4way_interaction(conditions, main_effects, pairwise, threeway_terms)

            # Variance explained
            result['variance_explained'] = calculate_variance_explained(result)

            aggregated['experiments'][exp_id] = result
            aggregated['metadata']['experiments_included'].append(exp_id)
            print(f"✅ Loaded: {exp_id} ({EXPERIMENTS[exp_id]['order']})")
        else:
            aggregated['metadata']['experiments_missing'].append(exp_id)
            print(f"❌ Missing: {exp_id} ({EXPERIMENTS[exp_id]['order']})")

    return aggregated


def generate_markdown_summary(aggregated: Dict) -> str:
    """Generate markdown summary for manuscript integration."""
    md = []

    md.append("# Paper 4: Higher-Order Factorial Results Summary")
    md.append("")
    md.append(f"**Generated:** {aggregated['metadata']['aggregation_date']}")
    md.append(f"**Experiments Completed:** {len(aggregated['experiments'])}/2")
    md.append("")

    # C262: 3-way results
    if 'cycle262' in aggregated['experiments']:
        exp = aggregated['experiments']['cycle262']
        threeway = exp.get('threeway_analysis', {})

        md.append("## Cycle 262: 3-Way Factorial (H1 × H2 × H5)")
        md.append("")
        md.append("### Main Effects")
        md.append("")
        for mech, effect in exp.get('main_effects', {}).items():
            md.append(f"- **{mech}:** {effect:+.4f}")
        md.append("")

        md.append("### Pairwise Interactions")
        md.append("")
        for pair, synergy in exp.get('pairwise_interactions', {}).items():
            classification = classify_synergy(synergy)
            md.append(f"- **{pair}:** {synergy:+.4f} ({classification})")
        md.append("")

        md.append("### 3-Way Super-Synergy")
        md.append("")
        md.append(f"- **Observed (111):** {threeway.get('observed', 0.0):.4f}")
        md.append(f"- **Pairwise Prediction:** {threeway.get('pairwise_prediction', 0.0):.4f}")
        md.append(f"- **Super-Synergy:** {threeway.get('super_synergy', 0.0):+.4f}")
        md.append(f"- **Classification:** **{threeway.get('classification', 'UNKNOWN')}**")
        md.append("")

        md.append("### Variance Explained")
        md.append("")
        var = exp.get('variance_explained', {})
        md.append(f"- **Main effects (R²):** {var.get('r2_main', 0.0):.2%}")
        md.append(f"- **Main + Pairwise (R²):** {var.get('r2_pairwise', 0.0):.2%}")
        md.append(f"- **Residual (higher-order):** {var.get('r2_residual', 0.0):.2%}")
        md.append("")

    # C263: 4-way results
    if 'cycle263' in aggregated['experiments']:
        exp = aggregated['experiments']['cycle263']
        fourway = exp.get('fourway_analysis', {})

        md.append("## Cycle 263: 4-Way Factorial (H1 × H2 × H4 × H5)")
        md.append("")
        md.append("### Main Effects")
        md.append("")
        for mech, effect in exp.get('main_effects', {}).items():
            md.append(f"- **{mech}:** {effect:+.4f}")
        md.append("")

        md.append("### Pairwise Interactions (6 pairs)")
        md.append("")
        for pair, synergy in exp.get('pairwise_interactions', {}).items():
            classification = classify_synergy(synergy)
            md.append(f"- **{pair}:** {synergy:+.4f} ({classification})")
        md.append("")

        md.append("### 3-Way Interactions (4 triples)")
        md.append("")
        for triple, synergy in fourway.get('threeway_terms', {}).items():
            classification = classify_synergy(synergy)
            md.append(f"- **{triple}:** {synergy:+.4f} ({classification})")
        md.append("")

        md.append("### 4-Way Super-Synergy")
        md.append("")
        md.append(f"- **Observed (1111):** {fourway.get('observed', 0.0):.4f}")
        md.append(f"- **3-Way Prediction:** {fourway.get('threeway_prediction', 0.0):.4f}")
        md.append(f"- **Super-Synergy (4-way):** {fourway.get('super_synergy', 0.0):+.4f}")
        md.append(f"- **Classification:** **{fourway.get('classification', 'UNKNOWN')}**")
        md.append("")

    # Computational expense
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

    latex.append("% LaTeX tables for Paper 4")
    latex.append("% Higher-Order Factorial Results")
    latex.append("")

    # 3-way table
    if 'cycle262' in aggregated['experiments']:
        exp = aggregated['experiments']['cycle262']
        threeway = exp.get('threeway_analysis', {})

        latex.append("\\begin{table}[h]")
        latex.append("\\centering")
        latex.append("\\caption{3-Way Factorial Results: H1 × H2 × H5}")
        latex.append("\\label{tab:3way_results}")
        latex.append("\\begin{tabular}{lcc}")
        latex.append("\\hline")
        latex.append("Interaction Term & Synergy & Classification \\\\")
        latex.append("\\hline")

        for pair, synergy in exp.get('pairwise_interactions', {}).items():
            classification = classify_synergy(synergy)
            latex.append(f"{pair.replace('×', '$\\\\times$')} & {synergy:+.4f} & {classification} \\\\")

        latex.append(f"\\textbf{{3-Way (Super)}} & \\textbf{{{threeway.get('super_synergy', 0.0):+.4f}}} & \\textbf{{{threeway.get('classification', 'UNKNOWN')}}} \\\\")

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

    # C262 (3-way)
    if 'cycle262' in aggregated['experiments']:
        exp = aggregated['experiments']['cycle262']
        threeway = exp.get('threeway_analysis', {})
        conditions = exp.get('conditions', {})

        # Condition means
        for code in ['000', '100', '010', '001', '110', '101', '011', '111']:
            if code in conditions:
                replacements[f"C262_{code}_MEAN"] = f"{conditions[code]['mean_population']:.2f}"
                replacements[f"C262_{code}_FINAL"] = f"{conditions[code]['final_population']}"
                replacements[f"C262_{code}_MAX"] = f"{conditions[code]['max_population']}"

        # Main effects
        for i, (mech, effect) in enumerate(exp.get('main_effects', {}).items(), 1):
            replacements[f"C262_H{i}_EFFECT"] = f"{effect:+.2f}"

        # Pairwise
        pairwise_keys = {
            'M1×M2': 'H1H2',
            'M1×M3': 'H1H5',
            'M2×M3': 'H2H5'
        }
        for pair, key in pairwise_keys.items():
            synergy = exp.get('pairwise_interactions', {}).get(pair, 0.0)
            replacements[f"C262_{key}_SYNERGY"] = f"{synergy:+.2f}"

        # Super-synergy
        replacements["C262_SUPER_SYNERGY"] = f"{threeway.get('super_synergy', 0.0):+.2f}"
        replacements["C262_SUPER_CLASS"] = threeway.get('classification', 'UNKNOWN')

    # C263 (4-way)
    if 'cycle263' in aggregated['experiments']:
        exp = aggregated['experiments']['cycle263']
        fourway = exp.get('fourway_analysis', {})

        replacements["C263_SUPER_SYNERGY"] = f"{fourway.get('super_synergy', 0.0):+.2f}"
        replacements["C263_SUPER_CLASS"] = fourway.get('classification', 'UNKNOWN')

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
        description='Aggregate Paper 4 higher-order factorial results'
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
        default=Path('paper4_aggregated.json'),
        help='Output JSON file for aggregated results'
    )
    parser.add_argument(
        '--markdown',
        type=Path,
        default=Path('paper4_summary.md'),
        help='Output markdown summary file'
    )
    parser.add_argument(
        '--latex',
        type=Path,
        default=Path('paper4_tables.tex'),
        help='Output LaTeX tables file'
    )
    parser.add_argument(
        '--template',
        type=Path,
        default=Path('../papers/paper4_higher_order_factorial_template.md'),
        help='Manuscript template to populate'
    )
    parser.add_argument(
        '--manuscript',
        type=Path,
        default=Path('../papers/paper4_higher_order_factorial_FINAL.md'),
        help='Output populated manuscript'
    )

    args = parser.parse_args()

    print("=" * 70)
    print("PAPER 4 RESULTS AGGREGATION")
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

    # Step 2: Save aggregated JSON
    print("💾 Saving aggregated JSON...")
    with open(args.output, 'w') as f:
        json.dump(aggregated, f, indent=2)
    print(f"✅ Saved: {args.output}")
    print()

    # Step 3: Generate markdown summary
    print("📝 Generating markdown summary...")
    markdown_summary = generate_markdown_summary(aggregated)
    with open(args.markdown, 'w') as f:
        f.write(markdown_summary)
    print(f"✅ Saved: {args.markdown}")
    print()

    # Step 4: Generate LaTeX tables
    print("📐 Generating LaTeX tables...")
    latex_tables = generate_latex_tables(aggregated)
    with open(args.latex, 'w') as f:
        f.write(latex_tables)
    print(f"✅ Saved: {args.latex}")
    print()

    # Step 5: Populate manuscript template
    if args.template.exists():
        print("📄 Populating manuscript template...")
        success = populate_manuscript_template(aggregated, args.template, args.manuscript)
        if success:
            print("✅ Manuscript ready for review!")
        print()
    else:
        print(f"⚠️  Template not found: {args.template}")
        print("   Skipping manuscript population.")
        print()

    # Summary
    print("=" * 70)
    print("✅ AGGREGATION COMPLETE")
    print("=" * 70)
    print(f"Experiments processed: {len(aggregated['experiments'])}/2")
    print(f"Missing experiments: {len(aggregated['metadata']['experiments_missing'])}")
    print()
    print("Next steps:")
    print("  1. Review aggregated results")
    print("  2. Verify higher-order interaction terms")
    print("  3. Check populated manuscript")
    print("  4. Generate figures: python visualize_higher_order_interactions.py")
    print("  5. Finalize Discussion section")
    print("  6. Submit for peer review")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())
