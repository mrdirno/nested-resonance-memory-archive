#!/usr/bin/env python3
"""
COMPOSITE VALIDATION ANALYSIS: C186-C189 Integration

Purpose: Generate integrated validation scorecard for Extension validation campaign

Framework: 20-point composite scorecard
- Extension 1 (Network): C187 validation (0-4 points)
- Extension 2 (Hierarchical): C186 validation (0-12 points)
- Extension 4a (Memory): C188 validation (0-5 points)
- Extension 4b (Burst): C189 validation (0-3 points)

Interpretation:
  17-20 points: Framework STRONGLY VALIDATED → Paper 4 submission
  13-16 points: Framework PARTIALLY VALIDATED → refinement experiments
  9-12 points: Framework WEAKLY SUPPORTED → major revision
  0-8 points: Framework REJECTED → alternative theories needed

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Date: 2025-11-04
Cycle: 998
"""

import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict

# Validation report paths
C186_REPORT_PATH = Path(__file__).parent / "results" / "cycle186_validation_report.json"
C187_REPORT_PATH = Path(__file__).parent / "results" / "cycle187_validation_report.json"
C188_REPORT_PATH = Path(__file__).parent / "results" / "cycle188_validation_report.json"
C189_REPORT_PATH = Path(__file__).parent / "results" / "cycle189_validation_report.json"


def load_validation_report(path: Path) -> Dict:
    """
    Load validation report from JSON file.

    Args:
        path: Path to validation report JSON

    Returns:
        dict with validation results, or None if not found
    """
    if not path.exists():
        return None

    with open(path, 'r') as f:
        return json.load(f)


def generate_composite_scorecard() -> Dict:
    """
    Generate composite validation scorecard from all experiments.

    Returns:
        dict with composite analysis
    """
    print("=" * 80)
    print("COMPOSITE VALIDATION ANALYSIS: C186-C189")
    print("=" * 80)
    print()

    # Load individual validation reports
    reports = {
        'c186': load_validation_report(C186_REPORT_PATH),
        'c187': load_validation_report(C187_REPORT_PATH),
        'c188': load_validation_report(C188_REPORT_PATH),
        'c189': load_validation_report(C189_REPORT_PATH),
    }

    # Check which experiments have completed
    completed_experiments = [key for key, report in reports.items() if report is not None]

    print(f"Experiments with validation reports: {len(completed_experiments)}/4")
    for key in ['c186', 'c187', 'c188', 'c189']:
        status = "✅" if reports[key] is not None else "⏳"
        print(f"  {status} {key.upper()}")
    print()

    if len(completed_experiments) == 0:
        print("ERROR: No validation reports found. Run experiments first.")
        return {'error': 'no_reports'}

    # Extract scores from each experiment
    scores = {}
    max_scores = {
        'c186': 12.0,  # Hierarchical resonance (6 validations × 2 points)
        'c187': 4.0,   # Network structure (3 validations, weighted)
        'c188': 5.0,   # Memory effects (3 validations, weighted)
        'c189': 3.0,   # Burst clustering (3 validations × 1 point)
    }

    # C186: Hierarchical Resonance (Extension 2)
    if reports['c186'] is not None:
        scores['c186'] = reports['c186']['composite_score']
        print("EXTENSION 2: Hierarchical Resonance (C186)")
        print("-" * 80)
        print(f"Score: {scores['c186']:.1f} / {max_scores['c186']:.1f}")
        print(f"Interpretation: {reports['c186']['interpretation']}")
        print(f"Confidence: {reports['c186']['confidence']}")
        print()
    else:
        scores['c186'] = 0.0
        print("EXTENSION 2: Hierarchical Resonance (C186) - NOT AVAILABLE")
        print()

    # C187: Network Structure Effects (Extension 1)
    if reports['c187'] is not None:
        scores['c187'] = reports['c187']['composite_score']
        print("EXTENSION 1: Network Structure Effects (C187)")
        print("-" * 80)
        print(f"Score: {scores['c187']:.1f} / {max_scores['c187']:.1f}")
        print(f"Interpretation: {reports['c187']['interpretation']}")
        print(f"Confidence: {reports['c187']['confidence']}")
        print()
    else:
        scores['c187'] = 0.0
        print("EXTENSION 1: Network Structure Effects (C187) - NOT AVAILABLE")
        print()

    # C188: Memory Effects (Extension 4, Part B)
    if reports['c188'] is not None:
        scores['c188'] = reports['c188']['composite_score']
        print("EXTENSION 4 (PART B): Memory Effects (C188)")
        print("-" * 80)
        print(f"Score: {scores['c188']:.1f} / {max_scores['c188']:.1f}")
        print(f"Interpretation: {reports['c188']['interpretation']}")
        print(f"Confidence: {reports['c188']['confidence']}")
        print()
    else:
        scores['c188'] = 0.0
        print("EXTENSION 4 (PART B): Memory Effects (C188) - NOT AVAILABLE")
        print()

    # C189: Burst Clustering (Extension 4, Part C)
    if reports['c189'] is not None:
        scores['c189'] = reports['c189']['composite_score']
        print("EXTENSION 4 (PART C): Burst Clustering (C189)")
        print("-" * 80)
        print(f"Score: {scores['c189']:.1f} / {max_scores['c189']:.1f}")
        print(f"Interpretation: {reports['c189']['interpretation']}")
        print(f"Confidence: {reports['c189']['confidence']}")
        print()
    else:
        scores['c189'] = 0.0
        print("EXTENSION 4 (PART C): Burst Clustering (C189) - NOT AVAILABLE")
        print()

    # Calculate composite score
    total_score = sum(scores.values())
    total_possible = sum(max_scores[key] for key in completed_experiments)
    max_total = sum(max_scores.values())

    print("=" * 80)
    print("COMPOSITE SCORECARD")
    print("=" * 80)
    print()
    print(f"Extension 1 (Network):      {scores['c187']:.1f} / {max_scores['c187']:.1f}")
    print(f"Extension 2 (Hierarchical): {scores['c186']:.1f} / {max_scores['c186']:.1f}")
    print(f"Extension 4a (Memory):      {scores['c188']:.1f} / {max_scores['c188']:.1f}")
    print(f"Extension 4b (Burst):       {scores['c189']:.1f} / {max_scores['c189']:.1f}")
    print()
    print(f"TOTAL SCORE: {total_score:.1f} / {max_total:.1f}")
    print()

    # Interpretation
    if total_score >= 17.0:
        interpretation = "STRONGLY VALIDATED"
        confidence = "High"
        recommendation = "Proceed with Paper 4 submission"
    elif total_score >= 13.0:
        interpretation = "PARTIALLY VALIDATED"
        confidence = "Medium"
        recommendation = "Consider refinement experiments before publication"
    elif total_score >= 9.0:
        interpretation = "WEAKLY SUPPORTED"
        confidence = "Low"
        recommendation = "Major revision of theoretical framework needed"
    else:
        interpretation = "FRAMEWORK REJECTED"
        confidence = "Very Low"
        recommendation = "Alternative theoretical approaches required"

    print(f"Interpretation: {interpretation}")
    print(f"Confidence: {confidence}")
    print(f"Recommendation: {recommendation}")
    print()

    # Completion status
    if len(completed_experiments) == 4:
        completion_status = "COMPLETE"
        print("✅ All validation experiments complete")
    else:
        completion_status = "INCOMPLETE"
        remaining = [key.upper() for key in ['c186', 'c187', 'c188', 'c189']
                    if reports[key] is None]
        print(f"⏳ Awaiting: {', '.join(remaining)}")

    print()

    return {
        'scores': scores,
        'max_scores': max_scores,
        'total_score': float(total_score),
        'total_possible': float(total_possible),
        'max_total': float(max_total),
        'interpretation': interpretation,
        'confidence': confidence,
        'recommendation': recommendation,
        'completion_status': completion_status,
        'completed_experiments': completed_experiments,
        'individual_reports': {
            key: reports[key] for key in completed_experiments
        }
    }


def create_composite_figure(composite_data: Dict):
    """
    Create 2×2 figure showing composite validation results.

    Panels:
      1. Scores by extension (bar chart)
      2. Score breakdown (stacked bar)
      3. Validation status matrix (grid)
      4. Composite interpretation (text)
    """
    if 'error' in composite_data:
        print(f"Cannot create figure: {composite_data['error']}")
        return

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Composite Validation Analysis: C186-C189', fontsize=16, fontweight='bold')

    # Panel 1: Scores by extension (bar chart)
    ax = axes[0, 0]
    extensions = ['Extension 1\n(Network)', 'Extension 2\n(Hierarchical)',
                 'Extension 4a\n(Memory)', 'Extension 4b\n(Burst)']
    experiments = ['c187', 'c186', 'c188', 'c189']

    scores_list = [composite_data['scores'][exp] for exp in experiments]
    max_scores_list = [composite_data['max_scores'][exp] for exp in experiments]

    colors = ['green' if s / m >= 0.75 else 'yellow' if s / m >= 0.5 else 'red'
             for s, m in zip(scores_list, max_scores_list)]

    ax.bar(range(4), scores_list, alpha=0.7, color=colors, edgecolor='black')
    ax.set_xticks(range(4))
    ax.set_xticklabels(extensions, fontsize=10)
    ax.set_ylabel('Score')
    ax.set_title('Scores by Extension')
    ax.grid(axis='y', alpha=0.3)

    # Add max score lines
    for i, (score, max_score) in enumerate(zip(scores_list, max_scores_list)):
        ax.plot([i-0.4, i+0.4], [max_score, max_score], 'k--', linewidth=2)
        ax.text(i, max_score + 0.3, f'Max: {max_score:.1f}', ha='center', fontsize=8)

    # Panel 2: Score breakdown (stacked bar)
    ax = axes[0, 1]

    # Create stacked bar showing achieved vs remaining
    achieved = scores_list
    remaining = [max_scores_list[i] - scores_list[i] for i in range(4)]

    ax.bar(range(4), achieved, label='Achieved', color='steelblue', alpha=0.8)
    ax.bar(range(4), remaining, bottom=achieved, label='Remaining', color='lightgray', alpha=0.5)
    ax.set_xticks(range(4))
    ax.set_xticklabels(extensions, fontsize=10)
    ax.set_ylabel('Score')
    ax.set_title('Score Breakdown (Achieved vs Possible)')
    ax.legend()
    ax.grid(axis='y', alpha=0.3)

    # Panel 3: Validation status matrix
    ax = axes[1, 0]

    # Create matrix showing status of each validation
    status_data = []
    status_labels = []

    for exp_key in experiments:
        if exp_key in composite_data['completed_experiments']:
            report = composite_data['individual_reports'][exp_key]
            for val_name, val_data in report['validations'].items():
                status = val_data['status']
                status_val = 2 if status == 'VALIDATED' else 1 if status == 'PARTIAL' else 0
                status_data.append(status_val)
                status_labels.append(f"{exp_key.upper()}: {val_name[:15]}")

    if status_data:
        colors_map = {2: 'green', 1: 'yellow', 0: 'red'}
        bar_colors = [colors_map[val] for val in status_data]

        y_pos = range(len(status_data))
        ax.barh(y_pos, status_data, color=bar_colors, alpha=0.7, edgecolor='black')
        ax.set_yticks(y_pos)
        ax.set_yticklabels(status_labels, fontsize=8)
        ax.set_xlabel('Status (0=Rejected, 1=Partial, 2=Validated)')
        ax.set_xlim(0, 2)
        ax.set_title('Individual Validation Status')
        ax.grid(axis='x', alpha=0.3)
    else:
        ax.text(0.5, 0.5, 'No validation data available',
               ha='center', va='center', transform=ax.transAxes)

    # Panel 4: Composite interpretation (text)
    ax = axes[1, 1]
    ax.axis('off')

    text_content = f"""
    COMPOSITE VALIDATION RESULTS

    Total Score: {composite_data['total_score']:.1f} / {composite_data['max_total']:.1f}

    Interpretation:
    {composite_data['interpretation']}

    Confidence Level:
    {composite_data['confidence']}

    Recommendation:
    {composite_data['recommendation']}

    Completion Status:
    {composite_data['completion_status']}
    ({len(composite_data['completed_experiments'])}/4 experiments)
    """

    ax.text(0.1, 0.9, text_content, fontsize=11, verticalalignment='top',
           family='monospace', transform=ax.transAxes)

    plt.tight_layout()

    # Save figure
    output_path = Path(__file__).parent.parent / "data" / "figures" / "composite_validation.png"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Figure saved: {output_path}")
    print()


def main():
    """Execute composite validation analysis."""
    # Generate scorecard
    composite_data = generate_composite_scorecard()

    # Create figure
    create_composite_figure(composite_data)

    # Save JSON report
    output_path = Path(__file__).parent / "results" / "composite_validation_report.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(composite_data, f, indent=2)

    print(f"Composite report saved: {output_path}")
    print()
    print("=" * 80)
    print("COMPOSITE ANALYSIS COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
