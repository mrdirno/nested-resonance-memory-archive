#!/usr/bin/env python3
"""
Paper 4 Complete Analysis Pipeline

Master script that runs all Paper 4 experimental analyses in sequence:
- C186: Hierarchical energy dynamics (if new results available)
- C187: Network structure effects
- C188: Temporal regulation
- C189: Self-organized criticality

Generates comprehensive composite scorecard across all extensions.

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Date: 2025-11-08 (Cycle 1287+)
Repository: https://github.com/mrdirno/nested-resonance-memory-archive

Usage:
    python analyze_paper4_complete.py [results_dir] [output_dir]

Zero-Delay Infrastructure: Master pipeline coordinates instant analysis
when experiments complete, generating full Paper 4 validation.

Co-Authored-By: Claude <noreply@anthropic.com>
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Import individual analyzers
sys.path.append(str(Path(__file__).parent))

from analyze_c186_validation_campaign import C186ValidationAnalyzer
from analyze_c187_network_structure import C187NetworkAnalyzer
from analyze_c188_temporal_regulation import C188TemporalAnalyzer
from analyze_c189_criticality import C189CriticalityAnalyzer


class Paper4MasterAnalyzer:
    """
    Master coordinator for complete Paper 4 analysis.
    Runs all experimental analyses and generates unified scorecard.
    """

    def __init__(self, results_dir: str, output_dir: str):
        """Initialize master analyzer."""
        self.results_dir = Path(results_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.results = {}
        self.scorecard = {}

    def run_c186_analysis(self) -> bool:
        """
        Run C186 hierarchical dynamics analysis.

        Returns:
            True if analysis completed successfully
        """
        print("\n" + "="*80)
        print("EXTENSION 1: HIERARCHICAL ENERGY DYNAMICS (C186)")
        print("="*80 + "\n")

        try:
            c186_output = self.output_dir / "c186"
            analyzer = C186ValidationAnalyzer(str(self.results_dir), str(c186_output))
            analyzer.run_full_analysis()

            # Load results
            results_file = c186_output / "c186_composite_scorecard.json"
            if results_file.exists():
                with open(results_file, 'r') as f:
                    self.results['C186'] = json.load(f)

            return True

        except Exception as e:
            print(f"  ERROR: C186 analysis failed: {e}")
            return False

    def run_c187_analysis(self) -> bool:
        """
        Run C187 network structure analysis.

        Returns:
            True if analysis completed successfully
        """
        print("\n" + "="*80)
        print("EXTENSION 2: NETWORK STRUCTURE EFFECTS (C187)")
        print("="*80 + "\n")

        try:
            c187_output = self.output_dir / "c187"
            analyzer = C187NetworkAnalyzer(str(self.results_dir), str(c187_output))
            analyzer.run_full_analysis()

            # Load results
            results_file = c187_output / "c187_analysis_results.json"
            if results_file.exists():
                with open(results_file, 'r') as f:
                    self.results['C187'] = json.load(f)

            return True

        except Exception as e:
            print(f"  ERROR: C187 analysis failed: {e}")
            return False

    def run_c188_analysis(self) -> bool:
        """
        Run C188 temporal regulation analysis.

        Returns:
            True if analysis completed successfully
        """
        print("\n" + "="*80)
        print("EXTENSION 4: TEMPORAL REGULATION (C188)")
        print("="*80 + "\n")

        try:
            c188_output = self.output_dir / "c188"
            analyzer = C188TemporalAnalyzer(str(self.results_dir), str(c188_output))
            analyzer.run_full_analysis()

            # Load results
            results_file = c188_output / "c188_analysis_results.json"
            if results_file.exists():
                with open(results_file, 'r') as f:
                    self.results['C188'] = json.load(f)

            return True

        except Exception as e:
            print(f"  ERROR: C188 analysis failed: {e}")
            return False

    def run_c189_analysis(self) -> bool:
        """
        Run C189 self-organized criticality analysis.

        Returns:
            True if analysis completed successfully
        """
        print("\n" + "="*80)
        print("EXTENSION 5: SELF-ORGANIZED CRITICALITY (C189)")
        print("="*80 + "\n")

        try:
            c189_output = self.output_dir / "c189"
            analyzer = C189CriticalityAnalyzer(str(self.results_dir), str(c189_output))
            analyzer.run_full_analysis()

            # Load results
            results_file = c189_output / "c189_analysis_results.json"
            if results_file.exists():
                with open(results_file, 'r') as f:
                    self.results['C189'] = json.load(f)

            return True

        except Exception as e:
            print(f"  ERROR: C189 analysis failed: {e}")
            return False

    def calculate_master_scorecard(self) -> None:
        """
        Calculate master composite scorecard across all extensions.

        Scorecard Structure:
        - Extension 1 (C186): 6 hypotheses × 2 points = 12 points max
        - Extension 2 (C187): 3 hypotheses × 2 points = 6 points max
        - Extension 4 (C188): 3 hypotheses × 2 points = 6 points max
        - Extension 5 (C189): 3 hypotheses × 2 points = 6 points max
        - TOTAL: 15 hypotheses × 2 points = 30 points max

        Note: Original design had 20 points (10 hypotheses), but C186 has 6 hypotheses
        contributing 12 points, bringing total to 30 points.

        Interpretation:
        - 25-30 points: Strong support for framework
        - 19-24 points: Partial support (refinement needed)
        - 13-18 points: Weak support (major revision)
        - 0-12 points: Framework rejected
        """
        print("\n" + "="*80)
        print("PAPER 4 MASTER COMPOSITE SCORECARD")
        print("="*80 + "\n")

        total_points = 0
        max_points = 0

        # Extension 1: Hierarchical (C186)
        if 'C186' in self.results and 'composite_scorecard' in self.results['C186']:
            c186_score = self.results['C186']['composite_scorecard']
            ext1_points = c186_score.get('total_points', 0)
            ext1_max = c186_score.get('max_points', 12)

            total_points += ext1_points
            max_points += ext1_max

            print(f"Extension 1 (Hierarchical - C186): {ext1_points}/{ext1_max} points")

        # Extension 2: Network (C187)
        if 'C187' in self.results and 'composite_scorecard' in self.results['C187']:
            c187_score = self.results['C187']['composite_scorecard']
            ext2_points = c187_score.get('total_points', 0)
            ext2_max = c187_score.get('max_points', 6)

            total_points += ext2_points
            max_points += ext2_max

            print(f"Extension 2 (Network - C187): {ext2_points}/{ext2_max} points")

        # Extension 4: Temporal (C188)
        if 'C188' in self.results and 'composite_scorecard' in self.results['C188']:
            c188_score = self.results['C188']['composite_scorecard']
            ext4_points = c188_score.get('total_points', 0)
            ext4_max = c188_score.get('max_points', 6)

            total_points += ext4_points
            max_points += ext4_max

            print(f"Extension 4 (Temporal - C188): {ext4_points}/{ext4_max} points")

        # Extension 5: Criticality (C189)
        if 'C189' in self.results and 'composite_scorecard' in self.results['C189']:
            c189_score = self.results['C189']['composite_scorecard']
            ext5_points = c189_score.get('total_points', 0)
            ext5_max = c189_score.get('max_points', 6)

            total_points += ext5_points
            max_points += ext5_max

            print(f"Extension 5 (Criticality - C189): {ext5_points}/{ext5_max} points")

        # Calculate percentage
        percentage = (100 * total_points / max_points) if max_points > 0 else 0

        print("\n" + "-"*80)
        print(f"TOTAL SCORE: {total_points}/{max_points} points ({percentage:.1f}%)")
        print("-"*80 + "\n")

        # Interpretation
        if percentage >= 83.3:  # 25/30
            interpretation = "STRONG SUPPORT - Framework strongly validated"
        elif percentage >= 63.3:  # 19/30
            interpretation = "PARTIAL SUPPORT - Framework shows promise, refinement needed"
        elif percentage >= 43.3:  # 13/30
            interpretation = "WEAK SUPPORT - Major revisions required"
        else:
            interpretation = "FRAMEWORK REJECTED - Fundamental rethinking needed"

        print(f"INTERPRETATION: {interpretation}\n")

        self.scorecard = {
            'total_points': total_points,
            'max_points': max_points,
            'percentage': percentage,
            'interpretation': interpretation,
            'extensions': {
                'C186': self.results.get('C186', {}).get('composite_scorecard', {}),
                'C187': self.results.get('C187', {}).get('composite_scorecard', {}),
                'C188': self.results.get('C188', {}).get('composite_scorecard', {}),
                'C189': self.results.get('C189', {}).get('composite_scorecard', {})
            }
        }

    def save_master_results(self) -> None:
        """Save master analysis results and scorecard."""
        output_file = self.output_dir / "paper4_master_scorecard.json"

        master_results = {
            'paper': 'Paper 4: Multi-Scale Energy Regulation in Nested Resonance Memory',
            'date_analyzed': datetime.now().strftime('%Y-%m-%d'),
            'master_scorecard': self.scorecard,
            'individual_results': self.results
        }

        with open(output_file, 'w') as f:
            json.dump(master_results, f, indent=2)

        print(f"Master results saved to: {output_file}\n")

    def run_complete_analysis(self) -> None:
        """Execute complete Paper 4 analysis pipeline."""
        print("="*80)
        print("PAPER 4: MULTI-SCALE ENERGY REGULATION - COMPLETE ANALYSIS")
        print("="*80)
        print(f"\nAnalysis started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Results directory: {self.results_dir}")
        print(f"Output directory: {self.output_dir}\n")

        # Run all analyses
        c186_success = self.run_c186_analysis()
        c187_success = self.run_c187_analysis()
        c188_success = self.run_c188_analysis()
        c189_success = self.run_c189_analysis()

        # Generate master scorecard
        self.calculate_master_scorecard()
        self.save_master_results()

        # Summary
        print("="*80)
        print("ANALYSIS SUMMARY")
        print("="*80 + "\n")

        print("Extension Status:")
        print(f"  C186 (Hierarchical):    {'✓ COMPLETE' if c186_success else '✗ FAILED'}")
        print(f"  C187 (Network):         {'✓ COMPLETE' if c187_success else '✗ FAILED'}")
        print(f"  C188 (Temporal):        {'✓ COMPLETE' if c188_success else '✗ FAILED'}")
        print(f"  C189 (Criticality):     {'✓ COMPLETE' if c189_success else '✗ FAILED'}")

        print(f"\nMaster Scorecard: {self.scorecard.get('total_points', 0)}/{self.scorecard.get('max_points', 30)} points")
        print(f"Framework Status: {self.scorecard.get('interpretation', 'Unknown')}")

        print("\n" + "="*80)
        print("PAPER 4 COMPLETE ANALYSIS FINISHED")
        print("="*80)


def main():
    """Main entry point for Paper 4 master analysis."""
    # Default paths
    results_dir = "/Volumes/dual/DUALITY-ZERO-V2/experiments/results"
    output_dir = "/Volumes/dual/DUALITY-ZERO-V2/data/figures/paper4"

    # Allow command-line overrides
    if len(sys.argv) > 1:
        results_dir = sys.argv[1]
    if len(sys.argv) > 2:
        output_dir = sys.argv[2]

    # Run master analysis
    analyzer = Paper4MasterAnalyzer(results_dir, output_dir)
    analyzer.run_complete_analysis()


if __name__ == "__main__":
    main()
