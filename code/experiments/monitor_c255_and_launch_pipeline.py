#!/usr/bin/env python3
"""
C255 Completion Monitor and Paper 3 Pipeline Auto-Launcher

Purpose: Automatically detect C255 experiment completion and optionally
         launch the Paper 3 pipeline (C256-C260 → aggregation → visualization).

Design Philosophy:
- Proactive automation to eliminate latency upon C255 completion
- Embodiment of "when blocked, prepare downstream infrastructure"
- Perpetual research mandate - continuous autonomous operation
- Reality-grounded monitoring (file system, process checks)

Usage:
    # Monitor only (check every 60 seconds, no auto-launch)
    python monitor_c255_and_launch_pipeline.py --monitor-only

    # Auto-launch pipeline when C255 completes
    python monitor_c255_and_launch_pipeline.py --auto-launch

    # One-time check (no loop)
    python monitor_c255_and_launch_pipeline.py --check-once

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Author: Claude (DUALITY-ZERO-V2)
Date: 2025-10-27 (Cycle 421)
License: GPL-3.0
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
"""

import sys
import time
import json
import subprocess
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List


class C255Monitor:
    """Monitor C255 experiment completion and manage Paper 3 pipeline."""

    def __init__(self, workspace_dir: Path, check_interval: int = 60):
        """
        Initialize monitor.

        Args:
            workspace_dir: Root workspace directory
            check_interval: Seconds between checks (default 60)
        """
        self.workspace = workspace_dir
        self.check_interval = check_interval
        self.results_dir = workspace_dir / "experiments" / "results"
        self.experiments_dir = workspace_dir / "experiments"

        # Expected output file from C255
        self.c255_output = self.results_dir / "cycle255_h1h2_mechanism_validation_results.json"

        # Paper 3 pipeline scripts (in execution order)
        self.pipeline_scripts = [
            self.experiments_dir / "cycle256_h1h4_mechanism_validation.py",
            self.experiments_dir / "cycle257_h1h5_mechanism_validation.py",
            self.experiments_dir / "cycle258_h2h4_mechanism_validation.py",
            self.experiments_dir / "cycle259_h2h5_mechanism_validation.py",
            self.experiments_dir / "cycle260_h4h5_mechanism_validation.py"
        ]

        # Analysis scripts
        self.aggregate_script = self.experiments_dir / "aggregate_paper3_results.py"
        self.visualize_script = self.experiments_dir / "visualize_factorial_synergy.py"

        # Audit log
        self.log_file = workspace_dir / "paper3_pipeline_execution.log"

    def log(self, message: str):
        """Write timestamped log entry."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        print(log_entry)

        # Append to log file
        with open(self.log_file, 'a') as f:
            f.write(log_entry + "\n")

    def check_c255_completion(self) -> bool:
        """
        Check if C255 has completed by verifying output file exists and is valid.

        Returns:
            True if C255 completed successfully, False otherwise
        """
        # Check if output file exists
        if not self.c255_output.exists():
            return False

        # Verify file is valid JSON and non-empty
        try:
            with open(self.c255_output, 'r') as f:
                data = json.load(f)

            # Basic validation - check for expected keys
            required_keys = ['experiment_name', 'conditions', 'metadata']
            if not all(key in data for key in required_keys):
                self.log(f"WARNING: C255 output file exists but missing required keys")
                return False

            # Check if file was recently modified (within last hour)
            file_age = time.time() - self.c255_output.stat().st_mtime
            if file_age > 3600:  # More than 1 hour old
                self.log(f"WARNING: C255 output file is {file_age/3600:.1f}h old, may be stale")

            self.log(f"✅ C255 completion verified: {self.c255_output.name}")
            return True

        except json.JSONDecodeError as e:
            self.log(f"ERROR: C255 output file is not valid JSON: {e}")
            return False
        except Exception as e:
            self.log(f"ERROR checking C255 completion: {e}")
            return False

    def check_process_running(self) -> bool:
        """Check if C255 process is still running."""
        try:
            result = subprocess.run(
                ['ps', 'aux'],
                capture_output=True,
                text=True,
                timeout=5
            )

            # Search for cycle255 in process list
            for line in result.stdout.split('\n'):
                if 'cycle255' in line and 'python' in line.lower():
                    return True

            return False

        except Exception as e:
            self.log(f"ERROR checking process status: {e}")
            return None  # Unknown state

    def verify_pipeline_scripts(self) -> bool:
        """Verify all pipeline scripts exist and are executable."""
        missing = []

        # Check C256-C260
        for script in self.pipeline_scripts:
            if not script.exists():
                missing.append(script.name)

        # Check analysis scripts
        if not self.aggregate_script.exists():
            missing.append(self.aggregate_script.name)
        if not self.visualize_script.exists():
            missing.append(self.visualize_script.name)

        if missing:
            self.log(f"ERROR: Missing pipeline scripts: {', '.join(missing)}")
            return False

        self.log(f"✅ All pipeline scripts verified present")
        return True

    def execute_experiment(self, script_path: Path) -> bool:
        """
        Execute a single experiment script.

        Args:
            script_path: Path to experiment script

        Returns:
            True if execution succeeded, False otherwise
        """
        self.log(f"Executing: {script_path.name}")

        try:
            # Execute script
            result = subprocess.run(
                ['python3', str(script_path)],
                capture_output=True,
                text=True,
                cwd=str(self.experiments_dir),
                timeout=1200  # 20 minute timeout per experiment
            )

            if result.returncode == 0:
                self.log(f"✅ {script_path.name} completed successfully")
                return True
            else:
                self.log(f"ERROR: {script_path.name} failed with code {result.returncode}")
                self.log(f"STDERR: {result.stderr[:500]}")  # First 500 chars
                return False

        except subprocess.TimeoutExpired:
            self.log(f"ERROR: {script_path.name} timed out (>20 minutes)")
            return False
        except Exception as e:
            self.log(f"ERROR executing {script_path.name}: {e}")
            return False

    def execute_analysis(self, script_path: Path, args: List[str] = None) -> bool:
        """
        Execute an analysis script.

        Args:
            script_path: Path to analysis script
            args: Optional command-line arguments

        Returns:
            True if execution succeeded, False otherwise
        """
        self.log(f"Executing analysis: {script_path.name}")

        cmd = ['python3', str(script_path)]
        if args:
            cmd.extend(args)

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(self.experiments_dir),
                timeout=300  # 5 minute timeout for analysis
            )

            if result.returncode == 0:
                self.log(f"✅ {script_path.name} completed successfully")
                return True
            else:
                self.log(f"ERROR: {script_path.name} failed with code {result.returncode}")
                self.log(f"STDERR: {result.stderr[:500]}")
                return False

        except subprocess.TimeoutExpired:
            self.log(f"ERROR: {script_path.name} timed out (>5 minutes)")
            return False
        except Exception as e:
            self.log(f"ERROR executing {script_path.name}: {e}")
            return False

    def execute_pipeline(self) -> bool:
        """
        Execute complete Paper 3 pipeline:
        1. C256-C260 experiments (5 experiments, ~67 minutes)
        2. Aggregate results (~5 minutes)
        3. Visualize results (~5 minutes)

        Returns:
            True if entire pipeline succeeded, False if any step failed
        """
        self.log("=" * 60)
        self.log("PAPER 3 PIPELINE EXECUTION STARTING")
        self.log("=" * 60)

        start_time = time.time()

        # Step 1: Execute C256-C260 experiments
        self.log("STEP 1: Executing C256-C260 factorial experiments")
        for script in self.pipeline_scripts:
            if not self.execute_experiment(script):
                self.log(f"❌ Pipeline FAILED at {script.name}")
                return False

        # Step 2: Aggregate results
        self.log("STEP 2: Aggregating factorial results")
        aggregate_args = [
            '--input', str(self.results_dir),
            '--output', str(self.results_dir / 'paper3_aggregated_results.json')
        ]
        if not self.execute_analysis(self.aggregate_script, aggregate_args):
            self.log("❌ Pipeline FAILED at aggregation")
            return False

        # Step 3: Generate visualizations
        self.log("STEP 3: Generating visualizations")
        viz_args = [
            '--input', str(self.results_dir / 'paper3_aggregated_results.json'),
            '--output-dir', str(self.workspace / 'papers' / 'figures')
        ]
        if not self.execute_analysis(self.visualize_script, viz_args):
            self.log("❌ Pipeline FAILED at visualization")
            return False

        # Pipeline completed successfully
        elapsed = time.time() - start_time
        self.log("=" * 60)
        self.log(f"✅ PAPER 3 PIPELINE COMPLETED SUCCESSFULLY")
        self.log(f"Total execution time: {elapsed/60:.1f} minutes")
        self.log("=" * 60)

        return True

    def monitor_loop(self, auto_launch: bool = False):
        """
        Continuously monitor C255 completion.

        Args:
            auto_launch: If True, automatically launch pipeline when C255 completes
        """
        self.log(f"Starting C255 monitoring (check interval: {self.check_interval}s)")
        self.log(f"Auto-launch: {'ENABLED' if auto_launch else 'DISABLED'}")

        # Verify pipeline scripts before starting
        if not self.verify_pipeline_scripts():
            self.log("❌ Pipeline verification failed, cannot continue")
            sys.exit(1)

        iteration = 0
        while True:
            iteration += 1

            # Check if C255 completed
            if self.check_c255_completion():
                self.log(f"🎉 C255 COMPLETION DETECTED (iteration {iteration})")

                if auto_launch:
                    self.log("Auto-launch enabled, starting Paper 3 pipeline...")

                    if self.execute_pipeline():
                        self.log("✅ Pipeline execution completed successfully")
                        self.log("Exiting monitor (mission accomplished)")
                        sys.exit(0)
                    else:
                        self.log("❌ Pipeline execution failed")
                        self.log("Exiting monitor (manual intervention required)")
                        sys.exit(1)
                else:
                    self.log("Auto-launch disabled, exiting monitor")
                    self.log("Ready for manual pipeline execution")
                    sys.exit(0)

            # Check if process is still running
            process_running = self.check_process_running()
            if process_running is False:
                self.log("WARNING: C255 process not found, but output file not detected")
                self.log("Process may have failed or output path may be incorrect")

            # Log periodic status
            if iteration % 10 == 0:
                self.log(f"Status check #{iteration}: C255 still running, output not detected")

            # Wait before next check
            time.sleep(self.check_interval)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Monitor C255 completion and optionally launch Paper 3 pipeline"
    )

    parser.add_argument(
        '--workspace',
        type=Path,
        default=Path('/Volumes/dual/DUALITY-ZERO-V2'),
        help='Workspace directory (default: /Volumes/dual/DUALITY-ZERO-V2)'
    )

    parser.add_argument(
        '--check-interval',
        type=int,
        default=60,
        help='Seconds between checks (default: 60)'
    )

    parser.add_argument(
        '--monitor-only',
        action='store_true',
        help='Monitor only, do not auto-launch pipeline'
    )

    parser.add_argument(
        '--auto-launch',
        action='store_true',
        help='Automatically launch pipeline when C255 completes'
    )

    parser.add_argument(
        '--check-once',
        action='store_true',
        help='Check once and exit (no monitoring loop)'
    )

    args = parser.parse_args()

    # Validate workspace
    if not args.workspace.exists():
        print(f"ERROR: Workspace directory not found: {args.workspace}")
        sys.exit(1)

    # Create monitor
    monitor = C255Monitor(args.workspace, args.check_interval)

    # Execute based on mode
    if args.check_once:
        # One-time check
        if monitor.check_c255_completion():
            print("✅ C255 has completed")
            sys.exit(0)
        else:
            print("⏳ C255 still running")
            sys.exit(1)

    elif args.auto_launch:
        # Monitor and auto-launch
        monitor.monitor_loop(auto_launch=True)

    else:
        # Monitor only (default)
        monitor.monitor_loop(auto_launch=False)


if __name__ == '__main__':
    main()
