#!/usr/bin/env python3
"""
PAPERS 5A-5F BATCH LAUNCH ORCHESTRATOR

Purpose: Automatically launch Papers 5A-5F experiments in sequence when C255 completes.

Workflow:
1. Check if C255 (PID 6309) has completed
2. If completed, launch Papers 5A-5F in sequence:
   - Paper 5A: Parameter sensitivity (~4.7 hours)
   - Paper 5B: Extended timescale (~8 hours)
   - Paper 5C: Scaling behavior (~1-2 hours)
   - Paper 5E: Network topology (~2-3 hours)
   - Paper 5F: Environmental perturbations (~2-3 hours)
3. Monitor progress and save results
4. Generate summary report

Total Estimated Runtime: ~17-18 hours (sequential execution)

Design:
- Sequential execution (avoid resource conflicts)
- Progress monitoring with real-time updates
- Error handling and graceful recovery
- Automatic summary generation

Date: 2025-10-27
Author: Aldrin Payopay <aldrin.gdf@gmail.com>
License: GPL-3.0
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
"""

import os
import sys
import time
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional


class Papers5BatchOrchestrator:
    """Orchestrate sequential execution of Papers 5A-5F experiments."""

    def __init__(self, experiments_dir: Path, results_dir: Path):
        """
        Initialize orchestrator.

        Args:
            experiments_dir: Directory containing experiment scripts
            results_dir: Directory for saving results
        """
        self.experiments_dir = experiments_dir
        self.results_dir = results_dir
        self.results_dir.mkdir(parents=True, exist_ok=True)

        # Define experiments in execution order
        self.experiments = [
            {
                'name': 'Paper 5A: Parameter Sensitivity',
                'script': 'paper5a_parameter_sensitivity.py',
                'estimated_hours': 4.7,
                'description': '5 parameters × multiple values × 10 seeds'
            },
            {
                'name': 'Paper 5B: Extended Timescale',
                'script': 'paper5b_extended_timescale.py',
                'estimated_hours': 8.0,
                'description': '5 timescales (5K-100K cycles) × 5 seeds'
            },
            {
                'name': 'Paper 5C: Scaling Behavior',
                'script': 'paper5c_scaling_behavior.py',
                'estimated_hours': 1.5,
                'description': '5 population sizes (50-800 agents) × 10 seeds'
            },
            {
                'name': 'Paper 5E: Network Topology',
                'script': 'paper5e_network_topology.py',
                'estimated_hours': 2.5,
                'description': 'Resonance network analysis'
            },
            {
                'name': 'Paper 5F: Environmental Perturbations',
                'script': 'paper5f_environmental_perturbations.py',
                'estimated_hours': 2.5,
                'description': 'Reality input perturbation testing'
            }
        ]

        self.execution_log = []

    def check_c255_completion(self, pid: int = 6309) -> bool:
        """
        Check if C255 experiment has completed.

        Args:
            pid: Process ID of C255 experiment

        Returns:
            True if C255 has completed, False if still running
        """
        try:
            # Check if process is still running
            result = subprocess.run(
                ['ps', '-p', str(pid)],
                capture_output=True,
                text=True
            )
            return result.returncode != 0  # returncode != 0 means process not found (completed)
        except Exception as e:
            print(f"Error checking C255 status: {e}")
            return False

    def run_experiment(self, experiment: Dict) -> Dict:
        """
        Run a single experiment script.

        Args:
            experiment: Dictionary with name, script, estimated_hours, description

        Returns:
            Execution results dictionary
        """
        script_path = self.experiments_dir / experiment['script']

        if not script_path.exists():
            return {
                'name': experiment['name'],
                'script': experiment['script'],
                'status': 'FAILED',
                'error': f"Script not found: {script_path}",
                'start_time': None,
                'end_time': None,
                'runtime_hours': 0
            }

        print(f"\n{'=' * 70}")
        print(f"LAUNCHING: {experiment['name']}")
        print(f"Script: {experiment['script']}")
        print(f"Estimated runtime: {experiment['estimated_hours']:.1f} hours")
        print(f"Description: {experiment['description']}")
        print(f"{'=' * 70}\n")

        start_time = datetime.now()

        try:
            # Run experiment script
            result = subprocess.run(
                ['python3', str(script_path)],
                capture_output=True,
                text=True,
                cwd=self.experiments_dir
            )

            end_time = datetime.now()
            runtime_hours = (end_time - start_time).total_seconds() / 3600

            if result.returncode == 0:
                status = 'SUCCESS'
                error = None
                print(f"\n✅ {experiment['name']} COMPLETED")
                print(f"Runtime: {runtime_hours:.2f} hours")
            else:
                status = 'FAILED'
                error = result.stderr
                print(f"\n❌ {experiment['name']} FAILED")
                print(f"Error: {error}")

            return {
                'name': experiment['name'],
                'script': experiment['script'],
                'status': status,
                'error': error,
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'runtime_hours': runtime_hours,
                'stdout': result.stdout[-1000:] if len(result.stdout) > 1000 else result.stdout,  # Last 1000 chars
                'stderr': result.stderr[-1000:] if len(result.stderr) > 1000 else result.stderr
            }

        except Exception as e:
            end_time = datetime.now()
            runtime_hours = (end_time - start_time).total_seconds() / 3600

            print(f"\n❌ {experiment['name']} FAILED")
            print(f"Exception: {e}")

            return {
                'name': experiment['name'],
                'script': experiment['script'],
                'status': 'FAILED',
                'error': str(e),
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'runtime_hours': runtime_hours
            }

    def run_batch(self) -> Dict:
        """
        Run all Papers 5A-5F experiments in sequence.

        Returns:
            Batch execution summary
        """
        print("\n" + "=" * 70)
        print("PAPERS 5A-5F BATCH EXECUTION")
        print("=" * 70)
        print(f"Start time: {datetime.now().isoformat()}")
        print(f"Total experiments: {len(self.experiments)}")
        print(f"Estimated total runtime: {sum(e['estimated_hours'] for e in self.experiments):.1f} hours")
        print("=" * 70)

        batch_start = datetime.now()

        for i, experiment in enumerate(self.experiments, 1):
            print(f"\n[{i}/{len(self.experiments)}] Starting: {experiment['name']}")

            result = self.run_experiment(experiment)
            self.execution_log.append(result)

            # Brief pause between experiments
            time.sleep(2)

        batch_end = datetime.now()
        total_runtime = (batch_end - batch_start).total_seconds() / 3600

        # Generate summary
        successful = [r for r in self.execution_log if r['status'] == 'SUCCESS']
        failed = [r for r in self.execution_log if r['status'] == 'FAILED']

        summary = {
            'batch_start': batch_start.isoformat(),
            'batch_end': batch_end.isoformat(),
            'total_runtime_hours': total_runtime,
            'total_experiments': len(self.experiments),
            'successful': len(successful),
            'failed': len(failed),
            'experiments': self.execution_log
        }

        # Save summary
        summary_file = self.results_dir / "papers5_batch_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)

        print("\n" + "=" * 70)
        print("BATCH EXECUTION COMPLETE")
        print("=" * 70)
        print(f"Total runtime: {total_runtime:.2f} hours")
        print(f"Successful: {len(successful)}/{len(self.experiments)}")
        print(f"Failed: {len(failed)}/{len(self.experiments)}")
        print(f"Summary saved: {summary_file}")
        print("=" * 70)

        return summary

    def wait_for_c255(self, check_interval: int = 300, timeout_hours: Optional[int] = 24):
        """
        Wait for C255 to complete before launching batch.

        Args:
            check_interval: Seconds between checks (default: 5 minutes)
            timeout_hours: Maximum hours to wait (default: 24, None = infinite)
        """
        print("\n" + "=" * 70)
        print("WAITING FOR C255 COMPLETION")
        print("=" * 70)
        print(f"Check interval: {check_interval} seconds ({check_interval/60:.1f} minutes)")
        print(f"Timeout: {timeout_hours} hours" if timeout_hours else "Timeout: None (infinite)")
        print("=" * 70)

        start_wait = datetime.now()

        while True:
            if self.check_c255_completion():
                elapsed_hours = (datetime.now() - start_wait).total_seconds() / 3600
                print(f"\n✅ C255 COMPLETED (waited {elapsed_hours:.2f} hours)")
                return True

            elapsed_hours = (datetime.now() - start_wait).total_seconds() / 3600

            if timeout_hours and elapsed_hours >= timeout_hours:
                print(f"\n⏰ TIMEOUT after {elapsed_hours:.2f} hours")
                return False

            print(f"[{datetime.now().strftime('%H:%M:%S')}] C255 still running... (waited {elapsed_hours:.2f}h)")
            time.sleep(check_interval)


def main():
    """Execute Papers 5A-5F batch orchestration."""

    # Set up paths
    base_dir = Path(__file__).parent.parent.parent
    experiments_dir = base_dir / "code" / "experiments"
    results_dir = base_dir / "data" / "results"

    # Create orchestrator
    orchestrator = Papers5BatchOrchestrator(experiments_dir, results_dir)

    # Check C255 status
    if not orchestrator.check_c255_completion():
        print("\n⚠️  C255 (PID 6309) is still running.")
        print("Options:")
        print("  1. Wait for C255 to complete (automatic)")
        print("  2. Launch batch immediately (override)")
        print("  3. Exit")

        choice = input("\nEnter choice (1/2/3): ").strip()

        if choice == '1':
            # Wait for C255
            if not orchestrator.wait_for_c255(check_interval=300, timeout_hours=24):
                print("Timeout exceeded. Exiting.")
                return
        elif choice == '2':
            print("Launching batch immediately (C255 still running)...")
        else:
            print("Exiting.")
            return
    else:
        print("\n✅ C255 has completed. Ready to launch batch.")

    # Run batch
    summary = orchestrator.run_batch()

    # Report status
    if summary['failed'] == 0:
        print("\n🎉 ALL EXPERIMENTS COMPLETED SUCCESSFULLY")
    else:
        print(f"\n⚠️  {summary['failed']} EXPERIMENT(S) FAILED")
        print("Check logs for details.")


if __name__ == "__main__":
    main()
