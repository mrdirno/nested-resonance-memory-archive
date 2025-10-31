#!/usr/bin/env python3
"""
Paper Status Tracker - Research Pipeline Visibility Dashboard

Tracks completion status across the 9-paper publication pipeline:
- Experiment execution status (C171-C263)
- Data file existence and validity
- Analysis pipeline status
- Figure generation status
- Documentation completeness
- Blocker identification

Provides comprehensive visibility into research progress and identifies
next actions for each paper.

Author: Aldrin Payopay (aldrin.gdf@gmail.com)
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
License: GPL-3.0
"""

import argparse
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import sys


# Paper definitions with expected cycles, analysis, and figures
PAPER_DEFINITIONS = {
    'paper1': {
        'title': 'Resonance Validation (C171)',
        'cycles': ['cycle171'],
        'experiments': 1,
        'analysis_scripts': [],
        'expected_figures': 4,
        'status': 'PUBLISHED'
    },
    'paper2': {
        'title': 'Harmonic Mechanism (C175)',
        'cycles': ['cycle175'],
        'experiments': 1,
        'analysis_scripts': [],
        'expected_figures': 4,
        'status': 'MANUSCRIPT (~90%)'
    },
    'paper3': {
        'title': 'Pairwise Factorial Validation (C255-C260)',
        'cycles': [
            'cycle255',  # H1×H2 (completed)
            'cycle256',  # H1×H4 (RUNNING)
            'cycle257',  # H1×H5 (pending)
            'cycle258',  # H2×H4 (pending)
            'cycle259',  # H2×H5 (pending)
            'cycle260'   # H4×H5 (pending)
        ],
        'experiments': 24,  # 6 pairs × 4 conditions each
        'analysis_scripts': [
            'paper3_phase1_synergy_classification.py',
            'paper3_phase2_cross_pair_comparison.py',
            'paper3_visualize_synergy_results.py'
        ],
        'expected_figures': 4,
        'status': 'DATA COLLECTION (2/6 experiments complete)'
    },
    'paper4': {
        'title': 'Higher-Order Interactions (C262-C263)',
        'cycles': [
            'cycle262',  # 3-way factorials (4 combos × 8 = 32 conditions)
            'cycle263'   # 4-way factorial (1 combo × 16 = 16 conditions)
        ],
        'experiments': 48,  # 32 + 16 conditions
        'analysis_scripts': [
            'paper4_phase1_higher_order_synergy.py',
            'paper4_phase2_generalization_test.py',
            'paper4_visualize_higher_order_results.py'
        ],
        'expected_figures': 5,
        'status': 'PENDING (awaits Paper 3 completion)'
    },
    'paper5d': {
        'title': 'NRM Framework Exposition',
        'cycles': [],  # Primarily theoretical
        'experiments': 0,
        'analysis_scripts': [],
        'expected_figures': 0,
        'status': 'DRAFT'
    },
    'paper6': {
        'title': 'Configuration Space Exploration',
        'cycles': [],  # Various early cycles
        'experiments': 0,
        'analysis_scripts': [],
        'expected_figures': 0,
        'status': 'PLANNING'
    },
    'paper6b': {
        'title': 'Extended Configuration Analysis',
        'cycles': [],
        'experiments': 0,
        'analysis_scripts': [],
        'expected_figures': 0,
        'status': 'PLANNING'
    },
    'paper7': {
        'title': 'Theoretical Models',
        'cycles': ['cycle143'],  # Theoretical harmonic model
        'experiments': 1,
        'analysis_scripts': [
            'paper7_theoretical_framework.py',
            'paper7_v2_constrained_model.py',
            'paper7_v2_rotating_frame.py',
            'paper7_v3_corrected_phi.py',
            'paper7_v4_energy_threshold.py',
            'paper7_v5a_allee_effect.py',
            'paper7_v5b_energy_reservoir.py',
            'paper7_verify_v4_equilibrium.py',
            'paper7_phase2_sindy.py',
            'paper7_phase3_bifurcation_analysis.py',
            'paper7_phase3_regime_classification.py',
            'paper7_phase4_empirical_cv_validation.py',
            'paper7_phase5_eigenvalue_analysis.py',
            'paper7_phase6_chemical_langevin_v4.py'
        ],
        'expected_figures': 8,
        'status': 'ACTIVE DEVELOPMENT'
    },
    'paper8': {
        'title': 'Optimization Comparison (C256)',
        'cycles': ['cycle256'],
        'experiments': 1,
        'analysis_scripts': [
            'paper8_phase1a_hypothesis_testing.py',
            'paper8_phase1b_optimization_comparison.py',
            'paper8_visualize_phase1a_results.py',
            'paper8_visualize_phase1b_results.py'
        ],
        'expected_figures': 6,
        'status': 'DATA COLLECTION (C256 running ~18+ hours)'
    }
}


class PaperStatusTracker:
    """
    Track and report status of all papers in the publication pipeline.

    Checks:
    - Experiment data files (data/results/)
    - Analysis scripts (code/analysis/)
    - Figures (data/figures/)
    - Documentation (papers/compiled/)
    - Identifies blockers and next actions
    """

    def __init__(self, repo_root: Path):
        """
        Initialize status tracker.

        Args:
            repo_root: Root directory of repository
        """
        self.repo_root = Path(repo_root)
        self.results_dir = self.repo_root / 'data' / 'results'
        self.analysis_dir = self.repo_root / 'code' / 'analysis'
        self.figures_dir = self.repo_root / 'data' / 'figures'
        self.papers_dir = self.repo_root / 'papers' / 'compiled'

        self.status = {}

    def check_paper_status(self, paper_id: str, definition: Dict) -> Dict:
        """
        Check comprehensive status for a single paper.

        Args:
            paper_id: Paper identifier (e.g., 'paper1')
            definition: Paper definition dict

        Returns:
            Status dict with completion metrics
        """
        status = {
            'paper_id': paper_id,
            'title': definition['title'],
            'current_status': definition['status'],
            'experiments': {},
            'analysis': {},
            'figures': {},
            'documentation': {},
            'blockers': [],
            'next_actions': [],
            'completion_percent': 0
        }

        # Check experiment data
        expected_cycles = definition['cycles']
        experiments_complete = 0
        experiments_total = len(expected_cycles)

        for cycle in expected_cycles:
            data_files = list(self.results_dir.glob(f"{cycle}*.json"))

            if data_files:
                experiments_complete += 1
                status['experiments'][cycle] = {
                    'status': 'COMPLETE',
                    'files': [f.name for f in data_files]
                }
            else:
                status['experiments'][cycle] = {
                    'status': 'MISSING',
                    'files': []
                }
                status['blockers'].append(f"Missing data: {cycle}")

        # Check analysis scripts
        analysis_scripts = definition.get('analysis_scripts', [])
        analysis_complete = 0
        analysis_total = len(analysis_scripts)

        for script in analysis_scripts:
            script_path = self.analysis_dir / script

            if script_path.exists():
                analysis_complete += 1
                status['analysis'][script] = 'EXISTS'
            else:
                status['analysis'][script] = 'MISSING'
                status['blockers'].append(f"Missing analysis: {script}")

        # Check figures
        paper_figures = list(self.figures_dir.glob(f"{paper_id}_*.png"))
        figures_count = len(paper_figures)
        expected_figures = definition.get('expected_figures', 0)

        status['figures'] = {
            'count': figures_count,
            'expected': expected_figures,
            'files': [f.name for f in paper_figures]
        }

        if expected_figures > 0 and figures_count < expected_figures:
            status['blockers'].append(f"Missing figures: {figures_count}/{expected_figures}")

        # Check documentation
        readme_path = self.papers_dir / paper_id / 'README.md'

        if readme_path.exists():
            readme_size = readme_path.stat().st_size
            status['documentation'] = {
                'readme': 'EXISTS',
                'size_bytes': readme_size
            }
        else:
            status['documentation'] = {
                'readme': 'MISSING',
                'size_bytes': 0
            }
            status['blockers'].append(f"Missing README: {paper_id}")

        # Calculate completion percentage
        completion_factors = []

        if experiments_total > 0:
            completion_factors.append(experiments_complete / experiments_total)

        if analysis_total > 0:
            completion_factors.append(analysis_complete / analysis_total)

        if expected_figures > 0:
            completion_factors.append(min(figures_count / expected_figures, 1.0))

        if readme_path.exists():
            completion_factors.append(1.0)
        else:
            completion_factors.append(0.0)

        if completion_factors:
            status['completion_percent'] = sum(completion_factors) / len(completion_factors) * 100
        else:
            status['completion_percent'] = 0

        # Identify next actions
        if status['current_status'] == 'PUBLISHED':
            status['next_actions'].append('✓ Published - Continue to next paper')
        elif experiments_complete < experiments_total:
            missing_cycles = [c for c in expected_cycles if not status['experiments'][c]['status'] == 'COMPLETE']
            status['next_actions'].append(f"Run experiments: {', '.join(missing_cycles)}")
        elif analysis_complete < analysis_total:
            missing_analysis = [s for s in analysis_scripts if status['analysis'][s] == 'MISSING']
            if missing_analysis:
                status['next_actions'].append(f"Create analysis: {missing_analysis[0]}")
            else:
                status['next_actions'].append(f"Run analysis pipelines")
        elif figures_count < expected_figures:
            status['next_actions'].append(f"Generate figures ({figures_count}/{expected_figures})")
        else:
            status['next_actions'].append('Finalize manuscript and submit')

        return status

    def check_all_papers(self) -> Dict[str, Dict]:
        """
        Check status for all papers.

        Returns:
            Dict mapping paper_id to status dict
        """
        all_status = {}

        for paper_id, definition in PAPER_DEFINITIONS.items():
            all_status[paper_id] = self.check_paper_status(paper_id, definition)

        return all_status

    def generate_report(self, status_data: Dict[str, Dict]) -> str:
        """
        Generate human-readable status report.

        Args:
            status_data: Status data from check_all_papers()

        Returns:
            Formatted status report
        """
        lines = []
        lines.append("=" * 100)
        lines.append("NESTED RESONANCE MEMORY ARCHIVE - PUBLICATION PIPELINE STATUS")
        lines.append("=" * 100)
        lines.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"Repository: {self.repo_root}")
        lines.append("")

        # Overall summary
        total_papers = len(status_data)
        published = sum(1 for s in status_data.values() if s['current_status'] == 'PUBLISHED')
        avg_completion = sum(s['completion_percent'] for s in status_data.values()) / total_papers

        lines.append("OVERALL SUMMARY")
        lines.append("-" * 100)
        lines.append(f"Total Papers: {total_papers}")
        lines.append(f"Published: {published}")
        lines.append(f"In Progress: {total_papers - published}")
        lines.append(f"Average Completion: {avg_completion:.1f}%")
        lines.append("")

        # Per-paper status
        for paper_id in sorted(status_data.keys()):
            status = status_data[paper_id]

            lines.append("=" * 100)
            lines.append(f"{paper_id.upper()}: {status['title']}")
            lines.append("=" * 100)
            lines.append(f"Status: {status['current_status']}")
            lines.append(f"Completion: {status['completion_percent']:.1f}%")
            lines.append("")

            # Experiments
            if status['experiments']:
                lines.append("EXPERIMENTS:")
                for cycle, exp_status in status['experiments'].items():
                    symbol = "✓" if exp_status['status'] == 'COMPLETE' else "✗"
                    lines.append(f"  {symbol} {cycle}: {exp_status['status']}")
                    if exp_status['files']:
                        for f in exp_status['files']:
                            lines.append(f"      - {f}")
                lines.append("")

            # Analysis
            if status['analysis']:
                lines.append("ANALYSIS:")
                for script, script_status in status['analysis'].items():
                    symbol = "✓" if script_status == 'EXISTS' else "✗"
                    lines.append(f"  {symbol} {script}: {script_status}")
                lines.append("")

            # Figures
            lines.append("FIGURES:")
            lines.append(f"  Count: {status['figures']['count']}/{status['figures']['expected']}")
            if status['figures']['files']:
                for f in status['figures']['files']:
                    lines.append(f"    - {f}")
            lines.append("")

            # Documentation
            lines.append("DOCUMENTATION:")
            doc = status['documentation']
            symbol = "✓" if doc['readme'] == 'EXISTS' else "✗"
            lines.append(f"  {symbol} README.md: {doc['readme']}")
            if doc['size_bytes'] > 0:
                lines.append(f"      Size: {doc['size_bytes']:,} bytes")
            lines.append("")

            # Blockers
            if status['blockers']:
                lines.append("⚠️  BLOCKERS:")
                for blocker in status['blockers']:
                    lines.append(f"  - {blocker}")
                lines.append("")

            # Next actions
            if status['next_actions']:
                lines.append("📋 NEXT ACTIONS:")
                for action in status['next_actions']:
                    lines.append(f"  → {action}")
                lines.append("")

        lines.append("=" * 100)
        lines.append("END OF REPORT")
        lines.append("=" * 100)

        return "\n".join(lines)

    def export_json(self, status_data: Dict[str, Dict], output_path: Path):
        """
        Export status data as JSON.

        Args:
            status_data: Status data from check_all_papers()
            output_path: Path to write JSON file
        """
        export_data = {
            'generated': datetime.now().isoformat(),
            'repository': str(self.repo_root),
            'papers': status_data
        }

        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description='Track publication pipeline status across all papers',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate status report for all papers
  python paper_status_tracker.py

  # Export status as JSON
  python paper_status_tracker.py --json status_report.json

  # Check specific paper
  python paper_status_tracker.py --paper paper3

  # Verbose output with detailed checks
  python paper_status_tracker.py --verbose
        """
    )

    parser.add_argument('--repo', type=Path, default=Path.cwd(),
                       help='Repository root (default: current directory)')
    parser.add_argument('--paper', type=str, default=None,
                       help='Check specific paper only (e.g., paper3)')
    parser.add_argument('--json', type=Path, default=None,
                       help='Export status as JSON to specified file')
    parser.add_argument('--verbose', action='store_true',
                       help='Verbose output with detailed checks')

    args = parser.parse_args()

    # Create tracker
    tracker = PaperStatusTracker(args.repo)

    # Check status
    if args.paper:
        if args.paper not in PAPER_DEFINITIONS:
            print(f"ERROR: Unknown paper '{args.paper}'", file=sys.stderr)
            print(f"Available papers: {', '.join(sorted(PAPER_DEFINITIONS.keys()))}", file=sys.stderr)
            sys.exit(1)

        definition = PAPER_DEFINITIONS[args.paper]
        status_data = {args.paper: tracker.check_paper_status(args.paper, definition)}
    else:
        status_data = tracker.check_all_papers()

    # Generate report
    report = tracker.generate_report(status_data)
    print(report)

    # Export JSON if requested
    if args.json:
        tracker.export_json(status_data, args.json)
        print(f"\nJSON exported to: {args.json}")


if __name__ == '__main__':
    main()
