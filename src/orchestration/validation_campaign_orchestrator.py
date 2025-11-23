#!/usr/bin/env python3
"""
Validation Campaign Orchestrator

Purpose: Automated sequential execution of C186-C189 validation experiments

This orchestrator ensures zero-delay handoff between validation experiments:
1. C186: Hierarchical Energy Dynamics (10 exp, ~6h)
2. C187: Network Structure Effects (30 exp, ~5h)
3. C188: Memory Effects (40 exp, ~6.7h)
4. C189: Burst Clustering (100 exp, ~16.7h)

Total: 180 experiments, ~28 hours (estimated)

The orchestrator:
- Monitors experiment completion via log parsing
- Launches next experiment immediately upon completion
- Generates intermediate validation reports
- Executes post-validation pipeline after C189
- Handles errors gracefully with notifications

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Date: 2025-11-05
Cycle: 1021
License: GPL-3.0

Co-Authored-By: Claude <noreply@anthropic.com>
"""

import subprocess
import time
import json
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass


@dataclass
class ExperimentConfig:
    """Configuration for validation experiment."""
    cycle_id: str
    script_name: str
    log_path: Path
    results_path: Path
    total_experiments: int
    estimated_hours: float
    description: str


# Validation campaign configuration
EXPERIMENTS = [
    ExperimentConfig(
        cycle_id="C186",
        script_name="cycle186_metapopulation_hierarchical_validation.py",
        log_path=Path("/tmp/c186_output.log"),
        results_path=Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/cycle186_metapopulation_hierarchical_validation_results.json"),
        total_experiments=10,
        estimated_hours=6.0,
        description="Hierarchical Energy Dynamics"
    ),
    ExperimentConfig(
        cycle_id="C187",
        script_name="cycle187_network_structure_effects.py",
        log_path=Path("/tmp/c187_output.log"),
        results_path=Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/cycle187_network_structure_effects_results.json"),
        total_experiments=30,
        estimated_hours=5.0,
        description="Network Structure Effects"
    ),
    ExperimentConfig(
        cycle_id="C188",
        script_name="cycle188_memory_effects.py",
        log_path=Path("/tmp/c188_output.log"),
        results_path=Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/cycle188_memory_effects_results.json"),
        total_experiments=40,
        estimated_hours=6.7,
        description="Memory Effects"
    ),
    ExperimentConfig(
        cycle_id="C189",
        script_name="cycle189_burst_clustering.py",
        log_path=Path("/tmp/c189_output.log"),
        results_path=Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/cycle189_burst_clustering_results.json"),
        total_experiments=100,
        estimated_hours=16.7,
        description="Burst Clustering"
    ),
]

EXPERIMENTS_DIR = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments")
POST_VALIDATION_PIPELINE = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/run_post_validation_pipeline.py")


def check_experiment_completion(config: ExperimentConfig) -> bool:
    """
    Check if experiment has completed.

    Args:
        config: Experiment configuration

    Returns:
        True if complete, False otherwise
    """
    # Check for results JSON first (definitive completion)
    if config.results_path.exists():
        try:
            with open(config.results_path, 'r') as f:
                data = json.load(f)
                if data.get('status') == 'complete':
                    return True
        except Exception as e:
            print(f"Error reading results JSON: {e}")

    # Check log file for completion marker
    if config.log_path.exists():
        try:
            with open(config.log_path, 'r') as f:
                log_content = f.read()

            # Count completed experiments
            completed = log_content.count('Basin A:')  # Results marker

            if completed >= config.total_experiments:
                return True

        except Exception as e:
            print(f"Error reading log: {e}")

    return False


def check_experiment_running(config: ExperimentConfig) -> bool:
    """
    Check if experiment is currently running.

    Args:
        config: Experiment configuration

    Returns:
        True if running, False otherwise
    """
    # Check if log file exists and is being written to
    if config.log_path.exists():
        try:
            # Check if file has been modified in last 60 seconds
            mtime = config.log_path.stat().st_mtime
            age = time.time() - mtime

            if age < 60:  # Modified within last minute
                return True

        except Exception as e:
            print(f"Error checking log modification time: {e}")

    return False


def launch_experiment(config: ExperimentConfig) -> Optional[subprocess.Popen]:
    """
    Launch validation experiment.

    Args:
        config: Experiment configuration

    Returns:
        Subprocess handle, or None on error
    """
    script_path = EXPERIMENTS_DIR / config.script_name

    if not script_path.exists():
        print(f"❌ Script not found: {script_path}")
        return None

    print(f"🚀 Launching {config.cycle_id}: {config.description}")
    print(f"   Script: {script_path}")
    print(f"   Expected experiments: {config.total_experiments}")
    print(f"   Estimated duration: {config.estimated_hours:.1f} hours")
    print(f"   Log: {config.log_path}")
    print()

    try:
        # Launch in background with output redirect
        process = subprocess.Popen(
            ['python3', '-u', str(script_path)],
            stdout=open(config.log_path, 'w'),
            stderr=subprocess.STDOUT,
            cwd=EXPERIMENTS_DIR
        )

        print(f"✅ {config.cycle_id} launched successfully (PID: {process.pid})")
        print()

        return process

    except Exception as e:
        print(f"❌ Failed to launch {config.cycle_id}: {e}")
        return None


def generate_intermediate_report(completed_configs: list):
    """
    Generate intermediate validation report for completed experiments.

    Args:
        completed_configs: List of completed experiment configs
    """
    print(f"\n{'='*80}")
    print(f"INTERMEDIATE VALIDATION REPORT")
    print(f"{'='*80}\n")

    for config in completed_configs:
        print(f"✅ {config.cycle_id}: {config.description}")

        if config.results_path.exists():
            try:
                with open(config.results_path, 'r') as f:
                    data = json.load(f)

                print(f"   Experiments: {len(data.get('experiments', []))}/{config.total_experiments}")
                print(f"   Status: {data.get('status', 'unknown')}")

            except Exception as e:
                print(f"   Error reading results: {e}")

        print()

    print(f"{'='*80}\n")


def run_post_validation_pipeline():
    """Execute post-validation pipeline after C189 completion."""

    if not POST_VALIDATION_PIPELINE.exists():
        print(f"⚠️ Post-validation pipeline not found: {POST_VALIDATION_PIPELINE}")
        return False

    print(f"\n{'='*80}")
    print(f"EXECUTING POST-VALIDATION PIPELINE")
    print(f"{'='*80}\n")

    try:
        result = subprocess.run(
            ['python3', str(POST_VALIDATION_PIPELINE)],
            capture_output=True,
            text=True,
            cwd=EXPERIMENTS_DIR
        )

        print(result.stdout)

        if result.returncode != 0:
            print(f"⚠️ Pipeline completed with errors:")
            print(result.stderr)
            return False

        print(f"\n✅ Post-validation pipeline complete")
        return True

    except Exception as e:
        print(f"❌ Pipeline execution failed: {e}")
        return False


def orchestrate_campaign(start_from: str = "C186", monitor_only: bool = False):
    """
    Orchestrate validation campaign execution.

    Args:
        start_from: Which experiment to start from (C186, C187, C188, C189)
        monitor_only: If True, only monitor existing experiments without launching new ones
    """
    print(f"\n{'='*80}")
    print(f"VALIDATION CAMPAIGN ORCHESTRATOR")
    print(f"{'='*80}\n")
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Start from: {start_from}")
    print(f"Mode: {'MONITOR ONLY' if monitor_only else 'ORCHESTRATE'}")
    print()

    # Find starting index
    start_idx = next((i for i, exp in enumerate(EXPERIMENTS) if exp.cycle_id == start_from), 0)

    completed = []
    current_process = None
    current_config = None

    for idx in range(start_idx, len(EXPERIMENTS)):
        config = EXPERIMENTS[idx]

        print(f"[{idx+1}/{len(EXPERIMENTS)}] Checking {config.cycle_id}...")

        # Check if already complete
        if check_experiment_completion(config):
            print(f"   ✅ Already complete")
            completed.append(config)
            continue

        # Check if currently running
        if check_experiment_running(config):
            print(f"   ⏳ Currently running")

            if monitor_only:
                print(f"   Monitoring mode: Skipping to next experiment")
                continue

            # Wait for completion
            print(f"   Waiting for completion...")

            while not check_experiment_completion(config):
                time.sleep(60)  # Check every minute

                # Print progress update
                if config.log_path.exists():
                    try:
                        with open(config.log_path, 'r') as f:
                            log_content = f.read()

                        completed_count = log_content.count('Basin A:')
                        progress = (completed_count / config.total_experiments) * 100

                        print(f"   Progress: {completed_count}/{config.total_experiments} ({progress:.1f}%)")

                    except:
                        pass

            print(f"   ✅ Completed!")
            completed.append(config)

            # Generate intermediate report
            generate_intermediate_report(completed)

            continue

        # Not complete, not running - launch it
        if monitor_only:
            print(f"   ⏸️ Not running (monitor mode, not launching)")
            continue

        print(f"   🚀 Launching...")

        current_process = launch_experiment(config)

        if current_process is None:
            print(f"   ❌ Launch failed, aborting campaign")
            return False

        current_config = config

        # Wait for completion
        print(f"   ⏳ Waiting for completion...")

        while not check_experiment_completion(config):
            time.sleep(60)  # Check every minute

            # Check if process crashed
            if current_process.poll() is not None:
                # Process exited
                if not check_experiment_completion(config):
                    print(f"   ❌ Process exited before completion!")
                    return False

            # Print progress update
            if config.log_path.exists():
                try:
                    with open(config.log_path, 'r') as f:
                        log_content = f.read()

                    completed_count = log_content.count('Basin A:')
                    progress = (completed_count / config.total_experiments) * 100

                    print(f"   Progress: {completed_count}/{config.total_experiments} ({progress:.1f}%)")

                except:
                    pass

        print(f"   ✅ Completed!")
        completed.append(config)

        # Generate intermediate report
        generate_intermediate_report(completed)

    # All experiments complete
    print(f"\n{'='*80}")
    print(f"ALL VALIDATION EXPERIMENTS COMPLETE")
    print(f"{'='*80}\n")

    print(f"Completed experiments:")
    for config in completed:
        print(f"  ✅ {config.cycle_id}: {config.description}")

    print()

    # Run post-validation pipeline
    if not monitor_only:
        success = run_post_validation_pipeline()

        if success:
            print(f"\n🎉 VALIDATION CAMPAIGN COMPLETE!")
        else:
            print(f"\n⚠️ Campaign complete, but post-validation pipeline had issues")

    print(f"\nEnd time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}\n")

    return True


if __name__ == "__main__":
    import sys

    # Parse command line arguments
    start_from = "C186"
    monitor_only = False

    if len(sys.argv) > 1:
        start_from = sys.argv[1]

    if len(sys.argv) > 2 and sys.argv[2] == "--monitor-only":
        monitor_only = True

    # Run orchestration
    orchestrate_campaign(start_from=start_from, monitor_only=monitor_only)
