#!/usr/bin/env python3
"""
PUBLICATION-READY DATA EXPORTER
Export experimental data in publication formats

Purpose:
  Generate publication-ready data exports for manuscript submission:
    - CSV files for supplementary materials
    - Excel workbooks with multiple sheets
    - LaTeX formatted tables for direct manuscript inclusion
    - Summary statistics tables
    - Formatted for journal submission standards

Output Formats:
  - CSV: Raw experimental data with descriptive headers
  - Excel: Multi-sheet workbook (experiments, analysis, metadata)
  - LaTeX: Publication-ready tables with booktabs formatting
  - JSON: Structured data for reproducibility

Framework Validation:
  - Temporal Stewardship: Data formatted for maximum reproducibility
  - Self-Giving: System documents own research trajectory
  - NRM: Hierarchical data organization (cycles → experiments → metrics)

Date: 2025-10-25
Status: Production data export utility
Researcher: Claude (DUALITY-ZERO-V2)
"""

import json
import csv
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


# =============================================================================
# DATA LOADING
# =============================================================================

def load_all_experimental_data() -> List[Dict]:
    """Load all experiments from all cycles."""
    results_dir = Path(__file__).parent / 'results'

    all_experiments = []

    for file_path in sorted(results_dir.glob('cycle*.json')):
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)

            # Handle different formats
            if isinstance(data, list):
                experiments = data
            elif 'experiments' in data:
                experiments = data['experiments']
            elif 'results' in data:
                experiments = data['results']
            else:
                continue

            # Add cycle number and metadata
            cycle_num = int(file_path.stem.split('_')[0].replace('cycle', ''))

            for exp in experiments:
                exp['cycle'] = cycle_num
                exp['source_file'] = file_path.name

            all_experiments.extend(experiments)

        except (json.JSONDecodeError, ValueError, KeyError):
            continue

    return all_experiments


# =============================================================================
# CSV EXPORT
# =============================================================================

def export_to_csv(experiments: List[Dict], output_path: Path):
    """Export experiments to CSV format with descriptive headers."""

    # Define field mapping with descriptive names
    field_mapping = {
        'cycle': 'Experimental_Cycle',
        'frequency': 'Composition_Frequency_Pct',
        'seed': 'Random_Seed',
        'threshold': 'Composition_Threshold',
        'agent_cap': 'Maximum_Agent_Count',
        'n_agents': 'Initial_Agent_Count',
        'avg_composition_events': 'Mean_Composition_Events',
        'composition_events': 'Composition_Events',
        'basin': 'Bistable_Basin_Classification',
        'spawn_accuracy_pct': 'Spawn_Accuracy_Percent',
        'runtime_seconds': 'Execution_Time_Seconds',
    }

    # Collect all unique fields
    all_fields = set()
    for exp in experiments:
        all_fields.update(exp.keys())

    # Order fields logically
    ordered_fields = ['cycle', 'frequency', 'seed', 'threshold', 'agent_cap', 'n_agents']

    # Add outcome fields
    outcome_fields = ['avg_composition_events', 'composition_events', 'basin', 'spawn_accuracy_pct', 'runtime_seconds']
    ordered_fields.extend([f for f in outcome_fields if f in all_fields])

    # Add any remaining fields
    ordered_fields.extend([f for f in sorted(all_fields) if f not in ordered_fields and f not in ['source_file']])

    # Map to descriptive names
    csv_headers = [field_mapping.get(f, f) for f in ordered_fields]

    # Write CSV
    with open(output_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=csv_headers)
        writer.writeheader()

        for exp in experiments:
            # Map experiment data to descriptive field names
            row = {}
            for orig_field, csv_field in zip(ordered_fields, csv_headers):
                row[csv_field] = exp.get(orig_field, '')

            writer.writerow(row)


# =============================================================================
# EXCEL EXPORT
# =============================================================================

def export_to_excel(experiments: List[Dict], output_path: Path):
    """Export to Excel workbook with multiple sheets."""

    try:
        import openpyxl
    except ImportError:
        print("⚠️  openpyxl not available - skipping Excel export")
        return

    # Convert to DataFrame
    df = pd.DataFrame(experiments)

    # Create Excel writer
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        # Sheet 1: Raw experimental data
        df.to_excel(writer, sheet_name='Experiments', index=False)

        # Sheet 2: Summary statistics by cycle
        if 'cycle' in df.columns:
            summary = df.groupby('cycle').agg({
                'avg_composition_events': ['mean', 'std', 'count'] if 'avg_composition_events' in df.columns else 'count',
            }).round(3)
            summary.to_excel(writer, sheet_name='Summary_By_Cycle')

        # Sheet 3: Metadata
        metadata = pd.DataFrame({
            'Field': ['Export_Date', 'Total_Experiments', 'Cycles_Included', 'Analysis_Tool'],
            'Value': [
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                len(experiments),
                len(set(exp.get('cycle') for exp in experiments if 'cycle' in exp)),
                'DUALITY-ZERO-V2 Publication Exporter'
            ]
        })
        metadata.to_excel(writer, sheet_name='Metadata', index=False)


# =============================================================================
# LATEX EXPORT
# =============================================================================

def export_summary_table_latex(experiments: List[Dict], output_path: Path):
    """Export summary statistics as LaTeX table."""

    # Group by cycle
    df = pd.DataFrame(experiments)

    if 'cycle' not in df.columns:
        return

    # Calculate summary statistics
    summary = df.groupby('cycle').agg({
        'avg_composition_events': ['mean', 'std', 'count'] if 'avg_composition_events' in df.columns else 'count',
    }).round(3)

    # Generate LaTeX table
    latex = []
    latex.append("\\begin{table}[htbp]")
    latex.append("\\centering")
    latex.append("\\caption{Experimental Results Summary by Cycle}")
    latex.append("\\label{tab:cycle_summary}")
    latex.append("\\begin{tabular}{lccc}")
    latex.append("\\toprule")
    latex.append("Cycle & Mean Composition & Std Dev & N \\\\")
    latex.append("\\midrule")

    for cycle in sorted(summary.index):
        if 'avg_composition_events' in df.columns:
            mean_val = summary.loc[cycle, ('avg_composition_events', 'mean')]
            std_val = summary.loc[cycle, ('avg_composition_events', 'std')]
            count_val = int(summary.loc[cycle, ('avg_composition_events', 'count')])
            latex.append(f"{cycle} & {mean_val:.3f} & {std_val:.3f} & {count_val} \\\\")
        else:
            count_val = summary.loc[cycle]
            latex.append(f"{cycle} & -- & -- & {count_val} \\\\")

    latex.append("\\bottomrule")
    latex.append("\\end{tabular}")
    latex.append("\\end{table}")

    # Write to file
    with open(output_path, 'w') as f:
        f.write('\n'.join(latex))


def export_parameter_effects_latex(output_path: Path):
    """Export parameter sensitivity results as LaTeX table."""

    # Load sensitivity analysis results
    sensitivity_file = Path(__file__).parent / 'results' / 'parameter_sensitivity_analysis.json'

    if not sensitivity_file.exists():
        return

    with open(sensitivity_file, 'r') as f:
        data = json.load(f)

    variance_decomp = data.get('variance_decomposition', {})

    # Generate LaTeX table
    latex = []
    latex.append("\\begin{table}[htbp]")
    latex.append("\\centering")
    latex.append("\\caption{Parameter Influence on System Outcomes}")
    latex.append("\\label{tab:parameter_effects}")
    latex.append("\\begin{tabular}{llr}")
    latex.append("\\toprule")
    latex.append("Outcome & Parameter & Variance Explained (\\%) \\\\")
    latex.append("\\midrule")

    for outcome, decomp in variance_decomp.items():
        params = decomp.get('parameters', {})

        # Sort by variance explained
        sorted_params = sorted(
            params.items(),
            key=lambda x: x[1]['variance_explained_pct'],
            reverse=True
        )

        for i, (param, stats) in enumerate(sorted_params):
            outcome_label = outcome.replace('_', ' ').title() if i == 0 else ''
            latex.append(f"{outcome_label} & {param} & {stats['variance_explained_pct']:.1f} \\\\")

        if sorted_params:
            latex.append("\\midrule")

    # Remove last midrule
    if latex[-1] == "\\midrule":
        latex.pop()

    latex.append("\\bottomrule")
    latex.append("\\end{tabular}")
    latex.append("\\end{table}")

    # Write to file
    with open(output_path, 'w') as f:
        f.write('\n'.join(latex))


# =============================================================================
# MAIN EXPORT PIPELINE
# =============================================================================

def main():
    """Run complete publication data export."""

    print("=" * 80)
    print("PUBLICATION DATA EXPORTER")
    print("=" * 80)
    print()

    # Load data
    print("Loading experimental data...")
    experiments = load_all_experimental_data()
    print(f"✅ Loaded {len(experiments)} experiments")
    print()

    # Create export directory
    export_dir = Path(__file__).parent / 'publication_exports'
    export_dir.mkdir(exist_ok=True)

    # CSV Export
    print("1. CSV EXPORT")
    print("=" * 80)
    csv_path = export_dir / 'experimental_data.csv'
    export_to_csv(experiments, csv_path)
    print(f"  ✅ CSV: {csv_path.name} ({csv_path.stat().st_size / 1024:.1f} KB)")
    print()

    # Excel Export
    print("2. EXCEL EXPORT")
    print("=" * 80)
    excel_path = export_dir / 'experimental_data.xlsx'
    export_to_excel(experiments, excel_path)

    if excel_path.exists():
        print(f"  ✅ Excel: {excel_path.name} ({excel_path.stat().st_size / 1024:.1f} KB)")
    else:
        print("  ⚠️  Excel export skipped (openpyxl not available)")
    print()

    # LaTeX Exports
    print("3. LATEX TABLE EXPORTS")
    print("=" * 80)

    # Summary table
    summary_latex = export_dir / 'table_cycle_summary.tex'
    export_summary_table_latex(experiments, summary_latex)
    print(f"  ✅ Summary table: {summary_latex.name}")

    # Parameter effects table
    effects_latex = export_dir / 'table_parameter_effects.tex'
    export_parameter_effects_latex(effects_latex)

    if effects_latex.exists():
        print(f"  ✅ Parameter effects: {effects_latex.name}")

    print()

    # Export metadata
    print("4. METADATA")
    print("=" * 80)

    metadata = {
        'export_date': datetime.now().isoformat(),
        'total_experiments': len(experiments),
        'unique_cycles': len(set(exp.get('cycle') for exp in experiments if 'cycle' in exp)),
        'date_range': {
            'earliest_cycle': min((exp.get('cycle') for exp in experiments if 'cycle' in exp), default=None),
            'latest_cycle': max((exp.get('cycle') for exp in experiments if 'cycle' in exp), default=None),
        },
        'data_fields': list(set(key for exp in experiments for key in exp.keys())),
        'framework': 'DUALITY-ZERO-V2: Nested Resonance Memory Research',
    }

    metadata_path = export_dir / 'export_metadata.json'
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)

    print(f"  ✅ Metadata: {metadata_path.name}")
    print()

    print("=" * 80)
    print("PUBLICATION DATA EXPORT COMPLETE")
    print("=" * 80)
    print()
    print(f"Export directory: {export_dir}")
    print()
    print("Framework Validation:")
    print("  ✅ Temporal Stewardship: Data formatted for maximum reproducibility")
    print("  ✅ Self-Giving: System documented own research trajectory")
    print("  ✅ NRM: Hierarchical data organization preserved")
    print()


if __name__ == '__main__':
    main()
