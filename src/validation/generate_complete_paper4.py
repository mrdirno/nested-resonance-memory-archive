#!/usr/bin/env python3
"""
Paper 4 Master Compilation Orchestrator

Purpose: Coordinate generation of all Paper 4 components
Integrates: figures, tables, Results section, Discussion section, abstract
Produces: Complete publication-ready manuscript

Target: "Hierarchical Energy Dynamics in Nested Resonance Memory Systems"
Journal: Physical Review E
Format: LaTeX

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Date: 2025-11-05
Cycle: 1026
License: GPL-3.0

Co-Authored-By: Claude <noreply@anthropic.com>
"""

import sys
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Import component generators
sys.path.insert(0, str(Path(__file__).parent))


def check_data_availability() -> Dict[str, bool]:
    """
    Check which experimental datasets are available.

    Returns:
        Dictionary mapping data types to availability
    """
    results_dir = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/")

    availability = {
        'C186': (results_dir / "cycle186_metapopulation_hierarchical_validation_results.json").exists(),
        'C187': (results_dir / "cycle187_network_structure_effects_results.json").exists(),
        'C188': (results_dir / "cycle188_memory_effects_results.json").exists(),
        'C189': (results_dir / "cycle189_burst_clustering_results.json").exists(),
        'composite': (results_dir / "composite_validation_results.json").exists(),
        'baseline': (results_dir / "cycle171_baseline_results.json").exists()
    }

    return availability


def generate_all_figures() -> bool:
    """
    Generate all Paper 4 figures using master orchestrator.

    Returns:
        True if successful
    """
    print("\n[1/4] Generating figures...")

    try:
        # Use existing figure generation orchestrator
        from generate_all_paper4_figures import generate_all_figures

        results = generate_all_figures(skip_missing=True)

        success_count = sum(1 for v in results.values() if v)
        print(f"  ✓ Generated {success_count}/6 figures")

        return success_count > 0

    except Exception as e:
        print(f"  Error generating figures: {e}")
        return False


def generate_results_section() -> bool:
    """
    Generate Results section using results generator.

    Returns:
        True if successful
    """
    print("\n[2/4] Generating Results section...")

    try:
        from generate_paper4_results_section import generate_results_section

        c186_path = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/cycle186_metapopulation_hierarchical_validation_results.json")
        c187_path = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/cycle187_network_structure_effects_results.json")
        c188_path = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/cycle188_memory_effects_results.json")
        c189_path = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/cycle189_burst_clustering_results.json")
        scorecard_path = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/composite_validation_results.json")
        output_path = Path("/Volumes/dual/DUALITY-ZERO-V2/papers/paper4_results_section.tex")

        success = generate_results_section(
            c186_path, c187_path, c188_path, c189_path, scorecard_path, output_path
        )

        if success:
            print("  ✓ Results section generated")
        else:
            print("  ⏳ Results section pending (data incomplete)")

        return success

    except Exception as e:
        print(f"  Error generating Results section: {e}")
        return False


def generate_discussion_section() -> bool:
    """
    Generate Discussion section using discussion generator.

    Returns:
        True if successful
    """
    print("\n[3/4] Generating Discussion section...")

    try:
        from generate_paper4_discussion_section import generate_discussion_section

        scorecard_path = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/composite_validation_results.json")
        output_path = Path("/Volumes/dual/DUALITY-ZERO-V2/papers/paper4_discussion_section.tex")

        from generate_paper4_discussion_section import load_composite_scorecard
        scorecard_data = load_composite_scorecard(scorecard_path)

        success = generate_discussion_section(scorecard_data, output_path)

        if success:
            print("  ✓ Discussion section generated")
        else:
            print("  ⏳ Discussion section pending")

        return success

    except Exception as e:
        print(f"  Error generating Discussion section: {e}")
        return False


def generate_composite_scorecard() -> bool:
    """
    Generate composite validation scorecard.

    Returns:
        True if successful
    """
    print("\n[4/4] Generating composite validation scorecard...")

    try:
        from generate_composite_validation_scorecard import generate_composite_scorecard

        c186_path = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/cycle186_metapopulation_hierarchical_validation_results.json")
        c187_path = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/cycle187_network_structure_effects_results.json")
        c188_path = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/cycle188_memory_effects_results.json")
        c189_path = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/cycle189_burst_clustering_results.json")
        output_path = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/composite_validation_results.json")

        scorecard = generate_composite_scorecard(
            c186_path, c187_path, c188_path, c189_path, output_path
        )

        if scorecard:
            print("  ✓ Composite scorecard generated")
            return True
        else:
            print("  ⏳ Composite scorecard pending (data incomplete)")
            return False

    except Exception as e:
        print(f"  Error generating composite scorecard: {e}")
        return False


def generate_complete_paper4():
    """
    Generate complete Paper 4 manuscript.

    Orchestrates:
    1. Composite validation scorecard
    2. All figures (Fig 1-6)
    3. Results section
    4. Discussion section
    5. (Optional) LaTeX compilation
    """
    print("=" * 80)
    print("PAPER 4 MASTER COMPILATION")
    print("=" * 80)
    print()
    print("Target: Hierarchical Energy Dynamics in Nested Resonance Memory Systems")
    print("Format: Physical Review E")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Check data availability
    print("Checking data availability...")
    availability = check_data_availability()

    for data_type, available in availability.items():
        status = "✓" if available else "⏳"
        print(f"  {status} {data_type}: {'Available' if available else 'Pending'}")

    print()

    # Generate components
    results = {
        'scorecard': False,
        'figures': False,
        'results': False,
        'discussion': False
    }

    results['scorecard'] = generate_composite_scorecard()
    results['figures'] = generate_all_figures()
    results['results'] = generate_results_section()
    results['discussion'] = generate_discussion_section()

    # Summary
    print()
    print("=" * 80)
    print("COMPILATION SUMMARY")
    print("=" * 80)
    print()

    complete_count = sum(1 for v in results.values() if v)
    total_count = len(results)

    for component, success in results.items():
        status = "✓ Generated" if success else "⏳ Pending"
        print(f"  {status}: {component.title()}")

    print()
    print(f"Components Complete: {complete_count}/{total_count}")
    print()

    if complete_count == total_count:
        print("🎉 ALL COMPONENTS GENERATED")
        print()
        print("Paper 4 manuscript ready for final LaTeX compilation and submission.")
    elif complete_count > 0:
        print("⏳ PARTIAL GENERATION COMPLETE")
        print()
        print("Waiting for remaining experimental data (C187-C189).")
    else:
        print("⏳ NO COMPONENTS GENERATED")
        print()
        print("Experimental data pending. Re-run after validation campaign completes.")

    print()
    print("=" * 80)

    # Output file locations
    print()
    print("Generated files:")
    print("  - Figures: /Volumes/dual/DUALITY-ZERO-V2/data/figures/")
    print("  - Results: /Volumes/dual/DUALITY-ZERO-V2/papers/paper4_results_section.tex")
    print("  - Discussion: /Volumes/dual/DUALITY-ZERO-V2/papers/paper4_discussion_section.tex")
    print("  - Scorecard: /Volumes/dual/DUALITY-ZERO-V2/experiments/results/composite_validation_results.json")
    print()


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate complete Paper 4 manuscript from validation campaign results"
    )

    parser.add_argument(
        '--component',
        choices=['scorecard', 'figures', 'results', 'discussion', 'all'],
        default='all',
        help='Generate specific component or all'
    )

    args = parser.parse_args()

    if args.component == 'scorecard':
        generate_composite_scorecard()
    elif args.component == 'figures':
        generate_all_figures()
    elif args.component == 'results':
        generate_results_section()
    elif args.component == 'discussion':
        generate_discussion_section()
    else:
        generate_complete_paper4()


if __name__ == "__main__":
    main()
