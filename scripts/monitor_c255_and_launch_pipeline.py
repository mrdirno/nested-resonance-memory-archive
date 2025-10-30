#!/usr/bin/env python3
"""
Monitor C255 completion and auto-launch C256-C260 pipeline.

This script:
1. Monitors C255 completion (checks for output file + process termination)
2. Auto-launches C256-C260 optimized factorial experiments in sequence
3. Logs progress with timestamps
4. Can run autonomously or be monitored

Usage:
    python scripts/monitor_c255_and_launch_pipeline.py
    python scripts/monitor_c255_and_launch_pipeline.py --check-only  # Just check status
"""

import subprocess
import time
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple


# Configuration
DUALITY_WORKSPACE = Path("/Volumes/dual/DUALITY-ZERO-V2")
EXPERIMENTS_DIR = DUALITY_WORKSPACE / "experiments"
RESULTS_DIR = EXPERIMENTS_DIR / "results"

C255_SCRIPT = "cycle255_h1h2_optimized.py"
C255_EXPECTED_OUTPUT = "cycle255_h1h2_optimized_results.json"

# Pipeline experiments (in order)
PIPELINE = [
    ("cycle256", "cycle256_h1h4_optimized.py", "H1×H4", 10),  # 10 min estimate
    ("cycle257", "cycle257_h1h5_optimized.py", "H1×H5", 11),  # 11 min estimate
    ("cycle258", "cycle258_h2h4_optimized.py", "H2×H4", 12),  # 12 min estimate
    ("cycle259", "cycle259_h2h5_optimized.py", "H2×H5", 13),  # 13 min estimate
    ("cycle260", "cycle260_h4h5_optimized.py", "H4×H5", 11),  # 11 min estimate
]


def log(message: str):
    """Log message with timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")


def check_process_running(script_name: str) -> bool:
    """Check if a Python process is running for given script."""
    try:
        result = subprocess.run(
            ["ps", "aux"],
            capture_output=True,
            text=True,
            check=True
        )
        for line in result.stdout.split("\n"):
            if "python" in line and script_name in line and "grep" not in line:
                return True
        return False
    except Exception as e:
        log(f"Error checking process: {e}")
        return False


def check_output_exists(output_file: str) -> bool:
    """Check if output file exists in results directory."""
    output_path = RESULTS_DIR / output_file
    return output_path.exists()


def check_c255_status() -> Tuple[bool, bool, Optional[float]]:
    """
    Check C255 status.

    Returns:
        (completed, running, file_size_mb)
    """
    running = check_process_running(C255_SCRIPT)
    output_exists = check_output_exists(C255_EXPECTED_OUTPUT)

    file_size = None
    if output_exists:
        output_path = RESULTS_DIR / C255_EXPECTED_OUTPUT
        file_size = output_path.stat().st_size / (1024 * 1024)  # MB

    completed = output_exists and not running

    return completed, running, file_size


def run_experiment(cycle_id: str, script_name: str, description: str, estimate_min: int) -> bool:
    """
    Run a single experiment in the pipeline.

    Returns:
        True if successful, False otherwise
    """
    log(f"Starting {cycle_id}: {description}")
    log(f"Script: {script_name}")
    log(f"Estimate: {estimate_min} minutes")

    script_path = EXPERIMENTS_DIR / script_name

    if not script_path.exists():
        log(f"ERROR: Script not found: {script_path}")
        return False

    try:
        start_time = time.time()

        # Run experiment
        result = subprocess.run(
            ["python", str(script_path)],
            cwd=EXPERIMENTS_DIR,
            capture_output=True,
            text=True,
            timeout=estimate_min * 60 * 2  # 2× safety margin
        )

        elapsed = time.time() - start_time
        elapsed_min = elapsed / 60

        if result.returncode == 0:
            log(f"✓ {cycle_id} completed successfully in {elapsed_min:.1f} minutes")
            return True
        else:
            log(f"✗ {cycle_id} failed with return code {result.returncode}")
            log(f"STDERR: {result.stderr[:500]}")
            return False

    except subprocess.TimeoutExpired:
        elapsed_min = estimate_min * 2
        log(f"✗ {cycle_id} timed out after {elapsed_min} minutes")
        return False
    except Exception as e:
        log(f"✗ {cycle_id} failed with exception: {e}")
        return False


def run_pipeline():
    """Run the full C256-C260 pipeline."""
    log("=" * 80)
    log("STARTING C256-C260 PIPELINE")
    log("=" * 80)

    pipeline_start = time.time()
    results = {}

    for cycle_id, script_name, description, estimate_min in PIPELINE:
        success = run_experiment(cycle_id, script_name, description, estimate_min)
        results[cycle_id] = {
            "success": success,
            "description": description,
            "script": script_name
        }

        if not success:
            log(f"Pipeline halted due to {cycle_id} failure")
            break

    pipeline_elapsed = (time.time() - pipeline_start) / 60

    log("=" * 80)
    log("PIPELINE SUMMARY")
    log("=" * 80)
    log(f"Total time: {pipeline_elapsed:.1f} minutes")

    successes = sum(1 for r in results.values() if r["success"])
    log(f"Completed: {successes}/{len(PIPELINE)} experiments")

    for cycle_id, result in results.items():
        status = "✓" if result["success"] else "✗"
        log(f"  {status} {cycle_id}: {result['description']}")

    return results


def monitor_and_launch(check_interval: int = 60):
    """
    Monitor C255 and auto-launch pipeline when complete.

    Args:
        check_interval: Seconds between status checks
    """
    log("=" * 80)
    log("MONITORING C255 COMPLETION")
    log("=" * 80)
    log(f"Check interval: {check_interval} seconds")
    log(f"Press Ctrl+C to stop monitoring")

    try:
        while True:
            completed, running, file_size = check_c255_status()

            if completed:
                log("=" * 80)
                log("C255 COMPLETED!")
                log("=" * 80)
                log(f"Output file: {C255_EXPECTED_OUTPUT}")
                log(f"File size: {file_size:.2f} MB")
                log("")

                # Launch pipeline
                results = run_pipeline()

                # Exit after pipeline completes
                return results

            elif running:
                if file_size is not None:
                    log(f"C255 still running... (output file: {file_size:.2f} MB)")
                else:
                    log(f"C255 still running... (no output yet)")
            else:
                log(f"C255 not running and no output found. Waiting...")

            # Sleep until next check
            time.sleep(check_interval)

    except KeyboardInterrupt:
        log("")
        log("Monitoring stopped by user")
        return None


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Monitor C255 and launch C256-C260 pipeline")
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Only check status, don't monitor or launch"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=60,
        help="Check interval in seconds (default: 60)"
    )
    parser.add_argument(
        "--launch-now",
        action="store_true",
        help="Skip monitoring and launch pipeline immediately"
    )

    args = parser.parse_args()

    if args.check_only:
        # Just check status
        completed, running, file_size = check_c255_status()
        log("=" * 80)
        log("C255 STATUS CHECK")
        log("=" * 80)
        log(f"Completed: {completed}")
        log(f"Running: {running}")
        if file_size is not None:
            log(f"Output file size: {file_size:.2f} MB")
        else:
            log(f"Output file: Not found")
        return

    if args.launch_now:
        # Launch pipeline immediately
        log("Launching pipeline immediately (skipping C255 monitoring)")
        results = run_pipeline()
        return

    # Monitor and auto-launch
    results = monitor_and_launch(check_interval=args.interval)

    if results:
        log("")
        log("All pipeline experiments completed!")


if __name__ == "__main__":
    main()
