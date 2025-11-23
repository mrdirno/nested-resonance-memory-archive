#!/usr/bin/env python3
"""
Paper 4 Figure 5 Generator: Composite Validation Scorecard

Purpose: Automated generation of Figure 5 from composite validation results
Visualizes 24-point Extension 2 validation framework across C186-C189

Figure Layout (Single panel with annotations):
- Main: 4×6 heatmap grid (4 experiments × 6 predictions each)
- Color: Validation confidence (0.0-1.0)
- Annotations: Status symbols (✓, ~, ✗, ?)
- Summary: Overall validation rate and confidence

Target: Physical Review E standards (300 DPI, publication-ready)
Format: Single comprehensive validation heatmap

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Date: 2025-11-05
Cycle: 1027
License: GPL-3.0

Co-Authored-By: Claude <noreply@anthropic.com>
"""

import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class ValidationPoint:
    """Single validation point."""
    experiment_id: str
    criterion_id: str
    prediction_name: str
    status: str  # VALIDATED, PARTIAL, REJECTED, INSUFFICIENT
    confidence: float  # 0.0 - 1.0


def load_composite_scorecard(scorecard_path: Path) -> Optional[Dict]:
    """
    Load composite validation scorecard.

    Args:
        scorecard_path: Path to composite scorecard JSON

    Returns:
        Scorecard dictionary or None
    """
    if not scorecard_path.exists():
        print(f"⏳ Composite scorecard not available: {scorecard_path}")
        return None

    try:
        with open(scorecard_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading composite scorecard: {e}")
        return None


def extract_validation_matrix(scorecard_data: Dict) -> np.ndarray:
    """
    Extract validation confidence matrix from scorecard.

    Args:
        scorecard_data: Composite scorecard data

    Returns:
        4×6 numpy array of confidence values
    """
    # Initialize matrix (4 experiments × 6 predictions each)
    matrix = np.zeros((4, 6))

    validation_points = scorecard_data.get('validation_points', [])

    # Map experiment IDs to rows
    exp_map = {
        'C186': 0,
        'C187': 1,
        'C188': 2,
        'C189': 3
    }

    for point_data in validation_points:
        exp_id = point_data.get('experiment_id', '')
        criterion_id = point_data.get('criterion_id', '')
        confidence = point_data.get('confidence', 0.0)

        # Extract experiment and criterion indices
        if exp_id in exp_map:
            exp_idx = exp_map[exp_id]

            # Extract criterion number (e.g., "C186.1" → 0)
            try:
                crit_num = int(criterion_id.split('.')[-1]) - 1
                if 0 <= crit_num < 6:
                    matrix[exp_idx, crit_num] = confidence
            except (ValueError, IndexError):
                continue

    return matrix


def extract_status_matrix(scorecard_data: Dict) -> List[List[str]]:
    """
    Extract validation status matrix from scorecard.

    Args:
        scorecard_data: Composite scorecard data

    Returns:
        4×6 list of status strings
    """
    # Initialize matrix
    status_matrix = [['INSUFFICIENT' for _ in range(6)] for _ in range(4)]

    validation_points = scorecard_data.get('validation_points', [])

    # Map experiment IDs to rows
    exp_map = {
        'C186': 0,
        'C187': 1,
        'C188': 2,
        'C189': 3
    }

    for point_data in validation_points:
        exp_id = point_data.get('experiment_id', '')
        criterion_id = point_data.get('criterion_id', '')
        status = point_data.get('status', 'INSUFFICIENT')

        if exp_id in exp_map:
            exp_idx = exp_map[exp_id]

            try:
                crit_num = int(criterion_id.split('.')[-1]) - 1
                if 0 <= crit_num < 6:
                    status_matrix[exp_idx][crit_num] = status
            except (ValueError, IndexError):
                continue

    return status_matrix


def get_status_symbol(status: str) -> str:
    """
    Get symbol for validation status.

    Args:
        status: Validation status

    Returns:
        Symbol character
    """
    symbol_map = {
        'VALIDATED': '✓',
        'PARTIAL': '~',
        'REJECTED': '✗',
        'INSUFFICIENT': '?'
    }
    return symbol_map.get(status, '?')


def generate_figure5(
    scorecard_path: Path,
    output_path: Path,
    dpi: int = 300
) -> bool:
    """
    Generate Paper 4 Figure 5: Composite Validation Scorecard.

    Args:
        scorecard_path: Path to composite scorecard JSON
        output_path: Path to save figure
        dpi: Resolution (default 300 for publication)

    Returns:
        True if successful
    """
    print("=" * 80)
    print("GENERATING PAPER 4 FIGURE 5: COMPOSITE VALIDATION SCORECARD")
    print("=" * 80)
    print()

    # Load data
    scorecard_data = load_composite_scorecard(scorecard_path)

    if not scorecard_data:
        print("⏳ Composite scorecard not available. Skipping Figure 5 generation.")
        return False

    print(f"✓ Loaded composite scorecard")
    print()

    # Extract matrices
    confidence_matrix = extract_validation_matrix(scorecard_data)
    status_matrix = extract_status_matrix(scorecard_data)

    # Summary statistics
    scorecard = scorecard_data.get('scorecard', {})
    validation_rate = scorecard.get('validation_rate', 0.0)
    mean_confidence = scorecard.get('mean_confidence', 0.0)
    validated_count = scorecard.get('validated_count', 0)
    total_points = scorecard.get('total_points', 24)

    print(f"Validation Summary:")
    print(f"  Validated: {validated_count}/{total_points} ({validation_rate*100:.1f}%)")
    print(f"  Mean Confidence: {mean_confidence*100:.1f}%")
    print()

    # Create figure
    fig, ax = plt.subplots(figsize=(12, 8))
    fig.suptitle('Figure 5: Extension 2 Composite Validation Scorecard',
                 fontsize=14, fontweight='bold', y=0.96)

    # Plot heatmap
    im = ax.imshow(confidence_matrix, aspect='auto', cmap='RdYlGn',
                   vmin=0.0, vmax=1.0, interpolation='nearest')

    # Experiment labels (rows)
    exp_labels = [
        'C186: Hierarchical\nRegulation',
        'C187: Network\nTopology',
        'C188: Memory\nEffects',
        'C189: Burst\nClustering'
    ]
    ax.set_yticks(range(4))
    ax.set_yticklabels(exp_labels, fontsize=10, fontweight='bold')

    # Prediction labels (columns)
    pred_labels = [
        'Pred 1:\nBasin A',
        'Pred 2:\nMigrations',
        'Pred 3:\nVariance',
        'Pred 4:\nHomeostasis',
        'Pred 5:\nMemory',
        'Pred 6:\nClustering'
    ]
    ax.set_xticks(range(6))
    ax.set_xticklabels(pred_labels, fontsize=9, rotation=0, ha='center')

    # Annotate cells with status symbols
    for i in range(4):
        for j in range(6):
            status = status_matrix[i][j]
            symbol = get_status_symbol(status)
            confidence = confidence_matrix[i, j]

            # Text color based on confidence
            text_color = 'white' if confidence < 0.5 else 'black'

            ax.text(j, i, symbol, ha='center', va='center',
                    fontsize=20, fontweight='bold', color=text_color)

    # Colorbar
    cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label('Validation Confidence', fontsize=10, fontweight='bold')

    # Grid
    ax.set_xticks(np.arange(6) - 0.5, minor=True)
    ax.set_yticks(np.arange(4) - 0.5, minor=True)
    ax.grid(which='minor', color='gray', linestyle='-', linewidth=2)

    # Summary box
    summary_text = (
        f"Overall Validation: {validated_count}/{total_points} "
        f"({validation_rate*100:.1f}%)\n"
        f"Mean Confidence: {mean_confidence*100:.1f}%\n\n"
        f"Legend: ✓ Validated | ~ Partial | ✗ Rejected | ? Insufficient"
    )

    # Add text box below heatmap
    ax.text(0.5, -0.25, summary_text,
            transform=ax.transAxes,
            fontsize=10, ha='center', va='top',
            bbox=dict(boxstyle='round,pad=0.8', facecolor='lightgray',
                      edgecolor='black', linewidth=1.5, alpha=0.9))

    # Title annotation
    ax.text(0.5, 1.05, 'Extension 2: Hierarchical Energy Dynamics Validation',
            transform=ax.transAxes,
            fontsize=11, ha='center', va='bottom', style='italic')

    # Layout
    plt.tight_layout(rect=[0, 0.05, 1, 0.94])

    # Save
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        plt.savefig(output_path, dpi=dpi, bbox_inches='tight', facecolor='white')
        plt.close()

        print(f"✓ Figure 5 saved: {output_path}")
        print(f"  Resolution: {dpi} DPI")
        print(f"  Format: PNG")
        print()

        return True

    except Exception as e:
        print(f"Error saving Figure 5: {e}")
        plt.close()
        return False


def main():
    """Generate Figure 5 standalone."""

    scorecard_path = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/composite_validation_results.json")
    output_path = Path("/Volumes/dual/DUALITY-ZERO-V2/data/figures/paper4_fig5_composite_scorecard.png")

    success = generate_figure5(scorecard_path, output_path, dpi=300)

    if success:
        print("=" * 80)
        print("FIGURE 5 GENERATION COMPLETE")
        print("=" * 80)
    else:
        print("=" * 80)
        print("FIGURE 5 GENERATION SKIPPED (DATA PENDING)")
        print("=" * 80)


if __name__ == "__main__":
    main()
