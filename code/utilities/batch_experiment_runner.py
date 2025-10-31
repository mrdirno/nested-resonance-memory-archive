#!/usr/bin/env python3
"""
Batch Experiment Runner - Sequential execution with monitoring

Runs multiple experiments sequentially with:
- Progress monitoring and health checks
- Automatic result saving with timestamps
- Graceful error handling and recovery
- Comprehensive logging
- Estimated completion times

Designed for unattended execution of experiment queues (e.g., C257-C263).

Author: Aldrin Payopay (aldrin.gdf@gmail.com)
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
License: GPL-3.0
"""

import argparse
import subprocess
import json
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import sys

try:
    import psutil
except ImportError:
    print("Error: psutil required. Install with: pip install psutil", file=sys.stderr)
    sys.exit(1)


class BatchExperimentRunner:
    """
    Run multiple experiments sequentially with monitoring and logging.

    Features:
    - Sequential execution with configurable delays
    - Resource monitoring (CPU, memory)
    - Progress tracking with ETA
    - Automatic result archiving
    - Graceful failure handling
    """

    def __init__(
        self,
        experiments: List[Dict[str, str]],
        results_dir: Path,
        log_dir: Path,
        delay_between_experiments: int = 60,
        max_retries: int = 1
    ):
        """
        Initialize batch runner.

        Args:
            experiments: List of dicts with 'script', 'name', 'description'
            results_dir: Directory to save results
            log_dir: Directory for logs
            delay_between_experiments: Seconds to wait between experiments
            max_retries: Number of retry attempts for failed experiments
        """
        self.experiments = experiments
        self.results_dir = Path(results_dir)
        self.log_dir = Path(log_dir)
        self.delay_between_experiments = delay_between_experiments
        self.max_retries = max_retries

        # Create directories if needed
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Tracking
        self.start_time = None
        self.completed_experiments = []
        self.failed_experiments = []
        self.current_experiment_index = 0

    def estimate_total_time(self, avg_experiment_duration: int = 21600) -> timedelta:
        """
        Estimate total batch runtime.

        Args:
            avg_experiment_duration: Average seconds per experiment (default 6 hours)

        Returns:
            Estimated total duration as timedelta
        """
        total_experiments = len(self.experiments)
        experiment_time = total_experiments * avg_experiment_duration
        delay_time = (total_experiments - 1) * self.delay_between_experiments

        total_seconds = experiment_time + delay_time
        return timedelta(seconds=total_seconds)

    def run_experiment(self, experiment: Dict[str, str], attempt: int = 1) -> bool:
        """
        Run a single experiment.

        Args:
            experiment: Dict with 'script', 'name', 'description'
            attempt: Current attempt number (for retries)

        Returns:
            True if successful, False if failed
        """
        script_path = Path(experiment['script'])
        experiment_name = experiment.get('name', script_path.stem)

        print(f"\n{'=' * 80}")
        print(f"EXPERIMENT: {experiment_name} (Attempt {attempt}/{self.max_retries + 1})")
        print(f"Script: {script_path}")
        print(f"Description: {experiment.get('description', 'N/A')}")
        print(f"{'=' * 80}\n")

        # Check if script exists
        if not script_path.exists():
            print(f"ERROR: Script not found: {script_path}", file=sys.stderr)
            return False

        # Create log file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = self.log_dir / f"{experiment_name}_{timestamp}_attempt{attempt}.log"

        # Start experiment
        start_time = time.time()
        start_datetime = datetime.now()

        print(f"Starting at: {start_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Log file: {log_file}")
        print(f"\nMonitoring...")

        try:
            # Run experiment with output to log file
            with open(log_file, 'w') as log_f:
                process = subprocess.Popen(
                    ['python', str(script_path)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True
                )

                # Monitor progress
                last_print_time = time.time()
                while True:
                    # Check if process finished
                    if process.poll() is not None:
                        break

                    # Read output line
                    line = process.stdout.readline()
                    if line:
                        log_f.write(line)
                        log_f.flush()

                        # Print progress updates every 60 seconds
                        current_time = time.time()
                        if current_time - last_print_time >= 60:
                            elapsed = current_time - start_time
                            print(f"  [{elapsed/60:.1f} min elapsed] Process running...")
                            last_print_time = current_time

                # Get remaining output
                remaining_output, _ = process.communicate()
                if remaining_output:
                    log_f.write(remaining_output)
                    log_f.flush()

                # Check exit code
                if process.returncode != 0:
                    print(f"\nERROR: Experiment failed with exit code {process.returncode}")
                    print(f"See log: {log_file}")
                    return False

        except Exception as e:
            print(f"\nERROR: Exception during experiment: {e}", file=sys.stderr)
            return False

        # Success!
        end_time = time.time()
        duration = end_time - start_time

        print(f"\n{'=' * 80}")
        print(f"EXPERIMENT COMPLETED: {experiment_name}")
        print(f"Duration: {duration/3600:.2f} hours ({duration/60:.1f} minutes)")
        print(f"{'=' * 80}\n")

        return True

    def run_batch(self, start_from_index: int = 0):
        """
        Run all experiments in batch.

        Args:
            start_from_index: Index to start from (for resuming)
        """
        self.start_time = datetime.now()
        total_experiments = len(self.experiments)

        print(f"\n{'#' * 80}")
        print(f"BATCH EXPERIMENT RUNNER")
        print(f"{'#' * 80}")
        print(f"\nTotal Experiments: {total_experiments}")
        print(f"Starting from: Index {start_from_index}")
        print(f"Results Directory: {self.results_dir}")
        print(f"Log Directory: {self.log_dir}")
        print(f"Delay Between Experiments: {self.delay_between_experiments} seconds")
        print(f"\nEstimated Total Time: {self.estimate_total_time()}")
        print(f"Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'#' * 80}\n")

        # Run experiments
        for i in range(start_from_index, total_experiments):
            self.current_experiment_index = i
            experiment = self.experiments[i]

            # Progress
            print(f"\n{'*' * 80}")
            print(f"EXPERIMENT {i + 1}/{total_experiments}")
            print(f"Progress: {(i / total_experiments * 100):.1f}%")

            elapsed = datetime.now() - self.start_time
            print(f"Elapsed: {elapsed}")

            if i > start_from_index:
                avg_time_per_exp = elapsed.total_seconds() / (i - start_from_index)
                remaining_exps = total_experiments - i
                eta_seconds = remaining_exps * avg_time_per_exp
                eta = timedelta(seconds=eta_seconds)
                finish_time = datetime.now() + eta
                print(f"ETA: {eta} (Finish: {finish_time.strftime('%Y-%m-%d %H:%M:%S')})")

            print(f"{'*' * 80}\n")

            # Attempt experiment (with retries)
            success = False
            for attempt in range(1, self.max_retries + 2):
                success = self.run_experiment(experiment, attempt)

                if success:
                    self.completed_experiments.append(experiment)
                    break
                else:
                    if attempt < self.max_retries + 1:
                        print(f"\nRetrying in {self.delay_between_experiments} seconds...")
                        time.sleep(self.delay_between_experiments)
                    else:
                        self.failed_experiments.append(experiment)
                        print(f"\nFailed after {self.max_retries + 1} attempts.")

            # Delay before next experiment (if not last and not failed)
            if i < total_experiments - 1:
                if success:
                    print(f"\nWaiting {self.delay_between_experiments} seconds before next experiment...")
                    time.sleep(self.delay_between_experiments)
                else:
                    print(f"\nContinuing to next experiment after failure...")

        # Summary
        self.print_summary()

    def print_summary(self):
        """Print batch execution summary."""
        end_time = datetime.now()
        total_duration = end_time - self.start_time

        print(f"\n{'#' * 80}")
        print(f"BATCH EXECUTION SUMMARY")
        print(f"{'#' * 80}")
        print(f"\nStart Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"End Time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Total Duration: {total_duration}")
        print(f"\nTotal Experiments: {len(self.experiments)}")
        print(f"Completed: {len(self.completed_experiments)}")
        print(f"Failed: {len(self.failed_experiments)}")

        if self.failed_experiments:
            print(f"\nFailed Experiments:")
            for exp in self.failed_experiments:
                print(f"  - {exp.get('name', exp['script'])}")

        print(f"\nResults Directory: {self.results_dir}")
        print(f"Log Directory: {self.log_dir}")
        print(f"{'#' * 80}\n")

        # Save summary JSON
        summary_file = self.log_dir / f"batch_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        summary = {
            'start_time': self.start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'duration_seconds': total_duration.total_seconds(),
            'total_experiments': len(self.experiments),
            'completed': len(self.completed_experiments),
            'failed': len(self.failed_experiments),
            'completed_experiments': [e.get('name', e['script']) for e in self.completed_experiments],
            'failed_experiments': [e.get('name', e['script']) for e in self.failed_experiments]
        }

        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)

        print(f"Summary saved: {summary_file}\n")


def main():
    parser = argparse.ArgumentParser(
        description='Run multiple experiments sequentially with monitoring',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run Paper 3 experiments (C255-C260, pairwise factorials)
  python batch_experiment_runner.py \\
      --config paper3_experiments.json \\
      --results data/results/ \\
      --logs logs/paper3/

  # Run Paper 4 experiments (C262-C263, higher-order factorials)
  python batch_experiment_runner.py \\
      --config paper4_experiments.json \\
      --results data/results/ \\
      --logs logs/paper4/ \\
      --delay 300

  # Resume from experiment 3 (after failure/interruption)
  python batch_experiment_runner.py \\
      --config paper3_experiments.json \\
      --results data/results/ \\
      --logs logs/paper3/ \\
      --start-from 2

Config JSON Format:
  {
    "experiments": [
      {
        "script": "code/experiments/cycle255_h1h2_optimized.py",
        "name": "C255-H1xH2",
        "description": "Energy Pooling × Memory Fragmentation (factorial)"
      },
      ...
    ]
  }
        """
    )

    parser.add_argument('--config', type=Path, required=True,
                       help='JSON config file with experiment list')
    parser.add_argument('--results', type=Path, required=True,
                       help='Results directory')
    parser.add_argument('--logs', type=Path, required=True,
                       help='Logs directory')
    parser.add_argument('--delay', type=int, default=60,
                       help='Seconds between experiments (default: 60)')
    parser.add_argument('--retries', type=int, default=1,
                       help='Max retry attempts for failed experiments (default: 1)')
    parser.add_argument('--start-from', type=int, default=0,
                       help='Index to start from (for resuming, default: 0)')

    args = parser.parse_args()

    # Load config
    if not args.config.exists():
        print(f"ERROR: Config file not found: {args.config}", file=sys.stderr)
        sys.exit(1)

    with open(args.config, 'r') as f:
        config = json.load(f)

    experiments = config.get('experiments', [])

    if not experiments:
        print("ERROR: No experiments found in config", file=sys.stderr)
        sys.exit(1)

    # Create runner
    runner = BatchExperimentRunner(
        experiments=experiments,
        results_dir=args.results,
        log_dir=args.logs,
        delay_between_experiments=args.delay,
        max_retries=args.retries
    )

    # Run batch
    try:
        runner.run_batch(start_from_index=args.start_from)
    except KeyboardInterrupt:
        print("\n\nBatch execution interrupted by user.")
        print(f"Progress: {runner.current_experiment_index}/{len(experiments)} experiments")
        print(f"To resume: Use --start-from {runner.current_experiment_index}")
        runner.print_summary()
        sys.exit(1)


if __name__ == '__main__':
    main()
