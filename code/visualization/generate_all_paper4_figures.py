#!/usr/bin/env python3
"""
Paper 4 Master Figure Generation Orchestrator

Purpose: Automated generation of all Paper 4 figures from validation campaign results
Integrates individual figure generators into unified publication pipeline.

Figures Generated:
- Figure 1: Hierarchical Energy Regulation (C186)
- Figure 2: Network Structure Effects (C187)
- Figure 3: Memory Effects (C188)
- Figure 4: Burst Clustering (C189)
- Figure 5: Composite Validation Scorecard (C186-C189)
- Figure 6: Runtime Variance Analysis (C186-C189)

Supplementary Figures:
- S1: Parameter Sensitivity Analysis
- S2: Convergence Testing
- S3: Theoretical Model Comparison
- S4: Control Experiments

Target Journal: Physical Review E
Resolution: 300 DPI (publication quality)

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Date: 2025-11-05
Cycle: 1027 (Updated)
License: GPL-3.0

Co-Authored-By: Claude <noreply@anthropic.com>
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional


# Import individual figure generators
sys.path.insert(0, str(Path(__file__).parent))


def check_data_availability() -> Dict[str, bool]:
    """
    Check which experimental datasets are available.

    Returns:
        Dictionary mapping experiment IDs to availability status
    """
    results_dir = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/")

    availability = {
        'C186': (results_dir / "cycle186_metapopulation_hierarchical_validation_results.json").exists(),
        'C187': (results_dir / "cycle187_network_structure_effects_results.json").exists(),
        'C188': (results_dir / "cycle188_memory_effects_results.json").exists(),
        'C189': (results_dir / "cycle189_burst_clustering_results.json").exists(),
        'baseline': (results_dir / "cycle171_baseline_results.json").exists(),
        'composite': (results_dir / "composite_validation_results.json").exists()
    }

    return availability


def generate_figure1() -> bool:
    """Generate Figure 1: Hierarchical Energy Regulation."""
    try:
        from generate_paper4_fig1_hierarchical_regulation import generate_figure1

        c186_path = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/cycle186_metapopulation_hierarchical_validation_results.json")
        baseline_path = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/cycle171_baseline_results.json")
        output_path = Path("/Volumes/dual/DUALITY-ZERO-V2/data/figures/paper4_fig1_hierarchical_regulation.png")

        print("\n[1/6] Generating Figure 1: Hierarchical Energy Regulation...")
        success = generate_figure1(c186_path, baseline_path, output_path, dpi=300)

        return success

    except Exception as e:
        print(f"Error generating Figure 1: {e}")
        return False


def generate_figure2() -> bool:
    """Generate Figure 2: Network Structure Effects."""
    try:
        from generate_paper4_fig2_network_topology import generate_figure2

        c187_path = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/cycle187_network_structure_effects_results.json")
        output_path = Path("/Volumes/dual/DUALITY-ZERO-V2/data/figures/paper4_fig2_network_topology.png")

        print("\n[2/6] Generating Figure 2: Network Structure Effects...")
        success = generate_figure2(c187_path, output_path, dpi=300)

        return success

    except Exception as e:
        print(f"Error generating Figure 2: {e}")
        return False


def generate_figure3() -> bool:
    """Generate Figure 3: Memory Effects."""
    try:
        from generate_paper4_fig3_memory_effects import generate_figure3

        c188_path = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/cycle188_memory_effects_results.json")
        output_path = Path("/Volumes/dual/DUALITY-ZERO-V2/data/figures/paper4_fig3_memory_effects.png")

        print("\n[3/6] Generating Figure 3: Memory Effects...")
        success = generate_figure3(c188_path, output_path, dpi=300)

        return success

    except Exception as e:
        print(f"Error generating Figure 3: {e}")
        return False


def generate_figure4() -> bool:
    """Generate Figure 4: Burst Clustering."""
    try:
        from generate_paper4_fig4_burst_clustering import generate_figure4

        c189_path = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/cycle189_burst_clustering_results.json")
        output_path = Path("/Volumes/dual/DUALITY-ZERO-V2/data/figures/paper4_fig4_burst_clustering.png")

        print("\n[4/6] Generating Figure 4: Burst Clustering...")
        success = generate_figure4(c189_path, output_path, dpi=300)

        return success

    except Exception as e:
        print(f"Error generating Figure 4: {e}")
        return False


def generate_figure5() -> bool:
    """Generate Figure 5: Composite Validation Scorecard."""
    try:
        from generate_paper4_fig5_composite_scorecard import generate_figure5

        scorecard_path = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/composite_validation_results.json")
        output_path = Path("/Volumes/dual/DUALITY-ZERO-V2/data/figures/paper4_fig5_composite_scorecard.png")

        print("\n[5/6] Generating Figure 5: Composite Validation Scorecard...")
        success = generate_figure5(scorecard_path, output_path, dpi=300)

        return success

    except Exception as e:
        print(f"Error generating Figure 5: {e}")
        return False


def generate_figure6() -> bool:
    """Generate Figure 6: Runtime Variance Analysis."""
    try:
        from generate_paper4_fig6_runtime_variance import generate_figure6

        c186_path = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/cycle186_metapopulation_hierarchical_validation_results.json")
        c187_path = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/cycle187_network_structure_effects_results.json")
        c188_path = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/cycle188_memory_effects_results.json")
        c189_path = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/cycle189_burst_clustering_results.json")
        output_path = Path("/Volumes/dual/DUALITY-ZERO-V2/data/figures/paper4_fig6_runtime_variance.png")

        print("\n[6/6] Generating Figure 6: Runtime Variance Analysis...")
        success = generate_figure6(c186_path, c187_path, c188_path, c189_path,
                                   output_path, dpi=300)

        return success

    except Exception as e:
        print(f"Error generating Figure 6: {e}")
        return False


def generate_all_figures(skip_missing: bool = True) -> Dict[str, bool]:
    """
    Generate all Paper 4 figures.

    Args:
        skip_missing: If True, skip figures with missing data (default)

    Returns:
        Dictionary mapping figure IDs to generation success status
    """
    print("=" * 80)
    print("PAPER 4 FIGURE GENERATION PIPELINE")
    print("=" * 80)
    print()
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Target Resolution: 300 DPI")
    print("Publication Standards: Physical Review E")
    print()

    # Check data availability
    print("Checking data availability...")
    availability = check_data_availability()

    for exp_id, available in availability.items():
        status = "✓" if available else "⏳"
        print(f"  {status} {exp_id}: {'Available' if available else 'Pending'}")

    print()

    # Generate figures
    results = {}

    # Main figures
    results['Figure 1'] = generate_figure1()
    results['Figure 2'] = generate_figure2()
    results['Figure 3'] = generate_figure3()
    results['Figure 4'] = generate_figure4()
    results['Figure 5'] = generate_figure5()
    results['Figure 6'] = generate_figure6()

    # Summary
    print()
    print("=" * 80)
    print("GENERATION SUMMARY")
    print("=" * 80)
    print()

    success_count = sum(1 for v in results.values() if v)
    pending_count = sum(1 for v in results.values() if not v)

    for fig_id, success in results.items():
        status = "✓ Generated" if success else "⏳ Pending"
        print(f"  {status}: {fig_id}")

    print()
    print(f"Generated: {success_count}/6")
    print(f"Pending: {pending_count}/6")

    if success_count == 6:
        print()
        print("🎉 ALL FIGURES GENERATED SUCCESSFULLY")
    elif success_count > 0:
        print()
        print("⏳ Partial generation complete. Waiting for remaining experimental data.")
    else:
        print()
        print("⏳ No figures generated. Experimental data pending.")

    print()
    print("=" * 80)

    return results


def list_available_figures():
    """List available figure generators and their status."""
    print("=" * 80)
    print("PAPER 4 FIGURE GENERATORS")
    print("=" * 80)
    print()

    generators = [
        ("Figure 1", "Hierarchical Energy Regulation", "generate_paper4_fig1_hierarchical_regulation.py", True),
        ("Figure 2", "Network Structure Effects", "generate_paper4_fig2_network_topology.py", True),
        ("Figure 3", "Memory Effects", "generate_paper4_fig3_memory_effects.py", True),
        ("Figure 4", "Burst Clustering", "generate_paper4_fig4_burst_clustering.py", True),
        ("Figure 5", "Composite Validation Scorecard", "generate_paper4_fig5_composite_scorecard.py", True),
        ("Figure 6", "Runtime Variance Analysis", "generate_paper4_fig6_runtime_variance.py", True),
    ]

    for fig_id, title, generator, implemented in generators:
        status = "✓" if implemented else "⏳"
        print(f"{status} {fig_id}: {title}")
        print(f"   Generator: {generator}")
        print()

    print("=" * 80)


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate all Paper 4 figures from validation campaign results"
    )

    parser.add_argument(
        '--list',
        action='store_true',
        help='List available figure generators'
    )

    parser.add_argument(
        '--figures',
        nargs='+',
        type=int,
        choices=range(1, 7),
        help='Generate specific figures (e.g., --figures 1 2 3)'
    )

    parser.add_argument(
        '--skip-missing',
        action='store_true',
        default=True,
        help='Skip figures with missing data (default: True)'
    )

    args = parser.parse_args()

    if args.list:
        list_available_figures()
        return

    if args.figures:
        # Generate specific figures
        print(f"Generating figures: {args.figures}")
        results = {}

        if 1 in args.figures:
            results['Figure 1'] = generate_figure1()
        if 2 in args.figures:
            results['Figure 2'] = generate_figure2()
        if 3 in args.figures:
            results['Figure 3'] = generate_figure3()
        if 4 in args.figures:
            results['Figure 4'] = generate_figure4()
        if 5 in args.figures:
            results['Figure 5'] = generate_figure5()
        if 6 in args.figures:
            results['Figure 6'] = generate_figure6()

        # Summary
        print()
        for fig_id, success in results.items():
            status = "✓" if success else "✗"
            print(f"{status} {fig_id}")

    else:
        # Generate all figures
        generate_all_figures(skip_missing=args.skip_missing)


if __name__ == "__main__":
    main()
