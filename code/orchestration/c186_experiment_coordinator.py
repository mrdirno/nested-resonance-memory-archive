#!/usr/bin/env python3
"""
C186 Experiment Coordinator
Autonomous pipeline for V6 → Analysis → V7 → V8 execution

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Date: 2025-11-05 (Cycle 1079)
License: GPL-3.0
"""

import json
import subprocess
import time
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime

@dataclass
class ExperimentStatus:
    """Track status of individual experiment"""
    name: str
    script_path: Path
    results_path: Path
    analysis_script: Optional[Path]
    status: str  # 'pending', 'running', 'completed', 'failed'
    pid: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    runtime_seconds: Optional[float] = None


class C186ExperimentCoordinator:
    """
    Coordinates C186 experiment pipeline:
    V6 (running) → V6 Analysis → V7 → V8

    Features:
    - Monitors running experiments
    - Detects completion
    - Triggers analysis automatically
    - Queues next experiments
    - Provides comprehensive status reporting
    """

    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root
        self.experiments_dir = workspace_root / 'experiments'
        self.analysis_dir = workspace_root / 'analysis'
        self.results_dir = workspace_root / 'experiments' / 'results'

        # Define experiment pipeline
        self.pipeline = [
            ExperimentStatus(
                name='V6: Ultra-Low Frequency',
                script_path=self.experiments_dir / 'c186_v6_ultra_low_frequency_test.py',
                results_path=self.results_dir / 'c186_v6_ultra_low_frequency_results.json',
                analysis_script=self.analysis_dir / 'analyze_c186_v6_results.py',
                status='running'  # Already executing
            ),
            ExperimentStatus(
                name='V7: Migration Rate Variation',
                script_path=self.experiments_dir / 'c186_v7_migration_rate_variation.py',
                results_path=self.results_dir / 'c186_v7_migration_rate_variation_results.json',
                analysis_script=None,  # Will use comprehensive viz
                status='pending'
            ),
            ExperimentStatus(
                name='V8: Population Count Variation',
                script_path=self.experiments_dir / 'c186_v8_population_count_variation.py',
                results_path=self.results_dir / 'c186_v8_population_count_variation_results.json',
                analysis_script=None,  # Will use comprehensive viz
                status='pending'
            )
        ]

    def check_experiment_status(self, experiment: ExperimentStatus) -> str:
        """Check current status of an experiment"""
        if experiment.results_path.exists():
            return 'completed'

        if experiment.pid is not None:
            # Check if process is still running
            try:
                result = subprocess.run(
                    ['ps', '-p', str(experiment.pid)],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    return 'running'
                else:
                    return 'failed'  # Process died without results
            except Exception:
                return 'unknown'

        return experiment.status

    def get_running_pid(self, experiment_name: str) -> Optional[int]:
        """Get PID of running experiment by name"""
        try:
            result = subprocess.run(
                ['pgrep', '-f', str(self.pipeline[0 if 'V6' in experiment_name else 1 if 'V7' in experiment_name else 2].script_path.name)],
                capture_output=True,
                text=True
            )
            if result.returncode == 0 and result.stdout.strip():
                return int(result.stdout.strip().split('\n')[0])
        except Exception:
            pass
        return None

    def execute_analysis(self, experiment: ExperimentStatus) -> bool:
        """Execute analysis script for completed experiment"""
        if experiment.analysis_script is None:
            print(f"  No dedicated analysis script for {experiment.name}, using comprehensive viz")
            return True

        if not experiment.analysis_script.exists():
            print(f"  ⚠️  Analysis script not found: {experiment.analysis_script}")
            return False

        print(f"  Executing analysis: {experiment.analysis_script.name}")
        try:
            result = subprocess.run(
                ['python', str(experiment.analysis_script)],
                cwd=self.analysis_dir,
                capture_output=True,
                text=True,
                timeout=300  # 5 min timeout
            )

            if result.returncode == 0:
                print(f"  ✅ Analysis complete")
                return True
            else:
                print(f"  ❌ Analysis failed:")
                print(result.stderr[:500])
                return False
        except subprocess.TimeoutExpired:
            print(f"  ⏱️  Analysis timeout (5 min)")
            return False
        except Exception as e:
            print(f"  ❌ Analysis error: {e}")
            return False

    def launch_experiment(self, experiment: ExperimentStatus) -> bool:
        """Launch next experiment in pipeline"""
        if not experiment.script_path.exists():
            print(f"  ❌ Script not found: {experiment.script_path}")
            return False

        print(f"  Launching: {experiment.name}")
        print(f"  Script: {experiment.script_path.name}")

        try:
            # Launch in background
            log_file = self.experiments_dir / f"{experiment.script_path.stem}_output.log"
            with open(log_file, 'w') as log:
                process = subprocess.Popen(
                    ['python', '-u', str(experiment.script_path)],
                    cwd=self.experiments_dir,
                    stdout=log,
                    stderr=subprocess.STDOUT
                )

            experiment.pid = process.pid
            experiment.start_time = datetime.now()
            experiment.status = 'running'

            print(f"  ✅ Launched (PID: {experiment.pid})")
            print(f"  Log: {log_file}")
            return True

        except Exception as e:
            print(f"  ❌ Launch error: {e}")
            return False

    def update_pipeline_status(self):
        """Update status of all experiments in pipeline"""
        for experiment in self.pipeline:
            if experiment.status == 'running':
                # Try to get PID if not already set
                if experiment.pid is None:
                    experiment.pid = self.get_running_pid(experiment.name)

                # Check status
                new_status = self.check_experiment_status(experiment)
                if new_status != experiment.status:
                    if new_status == 'completed':
                        experiment.end_time = datetime.now()
                        if experiment.start_time:
                            experiment.runtime_seconds = (experiment.end_time - experiment.start_time).total_seconds()
                    experiment.status = new_status

    def process_pipeline(self, dry_run: bool = False) -> dict:
        """
        Process experiment pipeline:
        1. Check status of all experiments
        2. Run analysis on newly completed experiments
        3. Launch next pending experiments

        Args:
            dry_run: If True, report status but don't execute anything

        Returns:
            dict with pipeline status summary
        """
        print("="*70)
        print("C186 EXPERIMENT PIPELINE COORDINATOR")
        print("="*70)
        print()

        # Update all statuses
        self.update_pipeline_status()

        # Report current status
        print("CURRENT STATUS:")
        for i, exp in enumerate(self.pipeline, 1):
            status_icon = {
                'pending': '⏳',
                'running': '🔄',
                'completed': '✅',
                'failed': '❌',
                'unknown': '❓'
            }.get(exp.status, '?')

            print(f"{i}. {status_icon} {exp.name}: {exp.status.upper()}")
            if exp.pid:
                print(f"   PID: {exp.pid}")
            if exp.runtime_seconds:
                hours = exp.runtime_seconds / 3600
                print(f"   Runtime: {hours:.2f} hours")
        print()

        if dry_run:
            print("DRY RUN MODE: No actions taken")
            print("="*70)
            return self.get_status_summary()

        # Process completions
        actions_taken = []
        for i, exp in enumerate(self.pipeline):
            if exp.status == 'completed' and exp.analysis_script:
                # Check if analysis already run
                analysis_done = False  # Could check for analysis outputs
                if not analysis_done:
                    print(f"PROCESSING COMPLETION: {exp.name}")
                    success = self.execute_analysis(exp)
                    if success:
                        actions_taken.append(f"Analyzed {exp.name}")
                    print()

            if exp.status == 'completed' and i < len(self.pipeline) - 1:
                # Launch next experiment if pending
                next_exp = self.pipeline[i + 1]
                if next_exp.status == 'pending':
                    print(f"LAUNCHING NEXT: {next_exp.name}")
                    success = self.launch_experiment(next_exp)
                    if success:
                        actions_taken.append(f"Launched {next_exp.name}")
                    print()

        # Summary
        summary = self.get_status_summary()
        summary['actions_taken'] = actions_taken

        print("="*70)
        print("PIPELINE SUMMARY:")
        print(f"  Pending: {summary['pending_count']}")
        print(f"  Running: {summary['running_count']}")
        print(f"  Completed: {summary['completed_count']}")
        print(f"  Failed: {summary['failed_count']}")
        if actions_taken:
            print(f"  Actions: {len(actions_taken)}")
            for action in actions_taken:
                print(f"    - {action}")
        print("="*70)

        return summary

    def get_status_summary(self) -> dict:
        """Get summary of pipeline status"""
        status_counts = {
            'pending': 0,
            'running': 0,
            'completed': 0,
            'failed': 0
        }

        for exp in self.pipeline:
            status_counts[exp.status] = status_counts.get(exp.status, 0) + 1

        return {
            'pending_count': status_counts['pending'],
            'running_count': status_counts['running'],
            'completed_count': status_counts['completed'],
            'failed_count': status_counts['failed'],
            'total_count': len(self.pipeline),
            'experiments': [
                {
                    'name': exp.name,
                    'status': exp.status,
                    'pid': exp.pid,
                    'runtime_seconds': exp.runtime_seconds
                }
                for exp in self.pipeline
            ]
        }

    def save_status(self, output_path: Path):
        """Save current pipeline status to JSON"""
        summary = self.get_status_summary()
        summary['timestamp'] = datetime.now().isoformat()

        with open(output_path, 'w') as f:
            json.dump(summary, f, indent=2)

        print(f"Status saved: {output_path}")


def main():
    """Execute pipeline coordinator"""
    workspace_root = Path('/Volumes/dual/DUALITY-ZERO-V2')

    coordinator = C186ExperimentCoordinator(workspace_root)

    # Process pipeline
    summary = coordinator.process_pipeline(dry_run=False)

    # Save status
    status_file = workspace_root / 'c186_pipeline_status.json'
    coordinator.save_status(status_file)

    print()
    print("NEXT STEPS:")
    if summary['running_count'] > 0:
        print("  - Experiments running, check back later")
        print("  - Run coordinator again after completion")
    if summary['pending_count'] > 0:
        print(f"  - {summary['pending_count']} experiments pending")
        print("  - Will auto-launch when predecessors complete")
    if summary['completed_count'] == summary['total_count']:
        print("  ✅ ALL EXPERIMENTS COMPLETE")
        print("  - Ready for manuscript integration")
        print("  - Run comprehensive visualization")

    print()
    print("Coordinator execution complete")


if __name__ == '__main__':
    main()
