#!/usr/bin/env python3
"""
C186 Runtime Variance Analysis

Purpose: Track and analyze seed-dependent runtime variance in metapopulation experiments

This tool monitors C186 execution and correlates runtime with dynamical metrics:
- Compositions (depth calculations)
- Migrations (cross-population interactions)
- Memory patterns (pattern retention)
- Synchronization (population coupling)

The goal is to test whether computational expense correlates with dynamical complexity,
providing indirect evidence for hierarchical NRM predictions.

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Date: 2025-11-05
Cycle: 1020
"""

import json
import time
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import statistics

# Experiment configuration
C186_LOG = Path("/tmp/c186_output.log")
C186_RESULTS = Path(__file__).parent / "results" / "cycle186_metapopulation_hierarchical_validation_results.json"
C186_PID_FILE = Path("/tmp/c186_pid.txt")

# Expected parameters
TOTAL_EXPERIMENTS = 10
SEEDS = [42, 123, 456, 789, 101112, 131415, 161718, 192021, 222324, 252627]


def get_process_info(pid: int) -> Optional[Dict]:
    """
    Get process information from ps command.

    Args:
        pid: Process ID

    Returns:
        dict with elapsed time, CPU, memory, or None if process not found
    """
    try:
        result = subprocess.run(
            ['ps', '-p', str(pid), '-o', 'etime,pcpu,pmem'],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode != 0:
            return None

        lines = result.stdout.strip().split('\n')
        if len(lines) < 2:
            return None

        # Parse elapsed time (format: [[DD-]HH:]MM:SS)
        data = lines[1].split()
        if len(data) < 3:
            return None

        elapsed_str = data[0].strip()
        cpu = float(data[1].strip())
        mem = float(data[2].strip())

        # Convert elapsed time to seconds
        elapsed_seconds = parse_elapsed_time(elapsed_str)

        return {
            'elapsed_str': elapsed_str,
            'elapsed_seconds': elapsed_seconds,
            'cpu_percent': cpu,
            'memory_percent': mem
        }

    except Exception as e:
        print(f"Error getting process info: {e}")
        return None


def parse_elapsed_time(elapsed_str: str) -> int:
    """
    Parse ps elapsed time format to seconds.

    Format: [[DD-]HH:]MM:SS

    Args:
        elapsed_str: Elapsed time string from ps

    Returns:
        Total elapsed seconds
    """
    try:
        parts = elapsed_str.split('-')
        if len(parts) == 2:
            # Has days
            days = int(parts[0])
            time_part = parts[1]
        else:
            days = 0
            time_part = parts[0]

        time_parts = time_part.split(':')

        if len(time_parts) == 3:
            # HH:MM:SS
            hours, minutes, seconds = map(int, time_parts)
        elif len(time_parts) == 2:
            # MM:SS
            hours = 0
            minutes, seconds = map(int, time_parts)
        else:
            # SS
            hours = 0
            minutes = 0
            seconds = int(time_parts[0])

        total_seconds = days * 86400 + hours * 3600 + minutes * 60 + seconds
        return total_seconds

    except Exception as e:
        print(f"Error parsing elapsed time '{elapsed_str}': {e}")
        return 0


def parse_c186_log() -> Dict:
    """
    Parse C186 output log to extract experiment progress and results.

    Returns:
        dict with experiment status, completed seeds, and results
    """
    if not C186_LOG.exists():
        return {'status': 'not_started', 'completed': [], 'results': []}

    try:
        with open(C186_LOG, 'r') as f:
            log_content = f.read()

        lines = log_content.strip().split('\n')

        completed = []
        results = []
        current_experiment = None

        for line in lines:
            # Detect experiment start
            if line.startswith('[') and '/10]' in line and 'Running seed' in line:
                # Extract experiment number and seed
                parts = line.split(']')
                exp_num = int(parts[0].strip('[').split('/')[0])
                seed = int(line.split('seed ')[-1].replace('...', '').strip())
                current_experiment = {
                    'experiment': exp_num,
                    'seed': seed,
                    'status': 'running'
                }

            # Detect experiment results
            elif line.strip().startswith('Basin A:'):
                if current_experiment:
                    # Parse results: "Basin A: 0% | Mean Population: 4.9 | CV: 53.3% | Migrations: 14"
                    parts = line.split('|')

                    basin_a = float(parts[0].split(':')[1].strip().replace('%', ''))
                    mean_pop = float(parts[1].split(':')[1].strip())
                    cv = float(parts[2].split(':')[1].strip().replace('%', ''))
                    migrations = int(parts[3].split(':')[1].strip())

                    current_experiment.update({
                        'basin_a_percent': basin_a,
                        'mean_population': mean_pop,
                        'cv_percent': cv,
                        'migrations': migrations,
                        'status': 'completed'
                    })

                    results.append(current_experiment)
                    completed.append(current_experiment['seed'])
                    current_experiment = None

        # Count progress
        num_completed = len(completed)
        if current_experiment:
            status = f"running_seed_{current_experiment['seed']}"
        elif num_completed == TOTAL_EXPERIMENTS:
            status = 'complete'
        elif num_completed > 0:
            status = f"progress_{num_completed}/{TOTAL_EXPERIMENTS}"
        else:
            status = 'started'

        return {
            'status': status,
            'completed': completed,
            'results': results,
            'num_completed': num_completed
        }

    except Exception as e:
        print(f"Error parsing log: {e}")
        return {'status': 'error', 'completed': [], 'results': [], 'error': str(e)}


def estimate_runtimes(completed_results: List[Dict], process_elapsed: int) -> Dict:
    """
    Estimate per-seed runtimes and project total completion time.

    Args:
        completed_results: List of completed experiment results
        process_elapsed: Total process elapsed seconds

    Returns:
        dict with runtime estimates
    """
    num_completed = len(completed_results)

    if num_completed == 0:
        return {
            'seeds_completed': 0,
            'average_runtime_seconds': 0,
            'estimated_total_seconds': 0,
            'estimated_remaining_seconds': 0
        }

    # Estimate per-seed runtimes (rough approximation)
    # Assume seeds complete sequentially, divide total elapsed by completed
    avg_runtime = process_elapsed / num_completed

    # Project total time
    estimated_total = avg_runtime * TOTAL_EXPERIMENTS
    estimated_remaining = estimated_total - process_elapsed

    return {
        'seeds_completed': num_completed,
        'average_runtime_seconds': avg_runtime,
        'average_runtime_minutes': avg_runtime / 60,
        'estimated_total_seconds': estimated_total,
        'estimated_total_hours': estimated_total / 3600,
        'estimated_remaining_seconds': estimated_remaining,
        'estimated_remaining_hours': estimated_remaining / 3600
    }


def analyze_variance(completed_results: List[Dict]) -> Dict:
    """
    Analyze variance in dynamical metrics across completed seeds.

    Args:
        completed_results: List of completed experiment results

    Returns:
        dict with variance statistics
    """
    if len(completed_results) < 2:
        return {'n': len(completed_results), 'note': 'Insufficient data for variance analysis'}

    # Extract metrics
    migrations = [r['migrations'] for r in completed_results]
    mean_pops = [r['mean_population'] for r in completed_results]
    cvs = [r['cv_percent'] for r in completed_results]

    return {
        'n': len(completed_results),
        'migrations': {
            'mean': statistics.mean(migrations),
            'stdev': statistics.stdev(migrations) if len(migrations) > 1 else 0,
            'min': min(migrations),
            'max': max(migrations),
            'range': max(migrations) - min(migrations)
        },
        'mean_population': {
            'mean': statistics.mean(mean_pops),
            'stdev': statistics.stdev(mean_pops) if len(mean_pops) > 1 else 0,
            'min': min(mean_pops),
            'max': max(mean_pops),
            'range': max(mean_pops) - min(mean_pops)
        },
        'cv_percent': {
            'mean': statistics.mean(cvs),
            'stdev': statistics.stdev(cvs) if len(cvs) > 1 else 0,
            'min': min(cvs),
            'max': max(cvs),
            'range': max(cvs) - min(cvs)
        }
    }


def generate_runtime_report(pid: int = 33600):
    """
    Generate comprehensive runtime variance report for C186.

    Args:
        pid: Process ID of C186 experiment
    """
    print("=" * 80)
    print("C186 RUNTIME VARIANCE ANALYSIS")
    print("=" * 80)
    print()
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Process PID: {pid}")
    print()

    # Get process info
    process_info = get_process_info(pid)
    if process_info is None:
        print("❌ Process not found or not running")
        return

    print("PROCESS STATUS")
    print("-" * 80)
    print(f"Elapsed: {process_info['elapsed_str']} ({process_info['elapsed_seconds']} seconds)")
    print(f"CPU: {process_info['cpu_percent']:.1f}%")
    print(f"Memory: {process_info['memory_percent']:.1f}%")
    print()

    # Parse log
    log_data = parse_c186_log()

    print("EXPERIMENT PROGRESS")
    print("-" * 80)
    print(f"Status: {log_data['status']}")
    print(f"Completed: {log_data['num_completed']}/{TOTAL_EXPERIMENTS} experiments")
    print(f"Seeds completed: {log_data['completed']}")
    print()

    if log_data['results']:
        print("COMPLETED EXPERIMENTS")
        print("-" * 80)
        for result in log_data['results']:
            print(f"[{result['experiment']}/10] Seed {result['seed']}:")
            print(f"  Basin A: {result['basin_a_percent']:.1f}% | "
                  f"Mean Pop: {result['mean_population']:.1f} | "
                  f"CV: {result['cv_percent']:.1f}% | "
                  f"Migrations: {result['migrations']}")
        print()

    # Runtime estimates
    estimates = estimate_runtimes(log_data['results'], process_info['elapsed_seconds'])

    print("RUNTIME ESTIMATES")
    print("-" * 80)
    print(f"Seeds completed: {estimates['seeds_completed']}")
    if estimates['seeds_completed'] > 0:
        print(f"Average runtime: {estimates['average_runtime_minutes']:.1f} min/experiment")
        print(f"Estimated total: {estimates['estimated_total_hours']:.1f} hours")
        print(f"Estimated remaining: {estimates['estimated_remaining_hours']:.1f} hours")
    else:
        print("Insufficient data for estimates")
    print()

    # Variance analysis
    if len(log_data['results']) >= 2:
        variance = analyze_variance(log_data['results'])

        print("DYNAMICAL METRICS VARIANCE")
        print("-" * 80)
        print(f"Sample size: {variance['n']} experiments")
        print()

        print("Migrations:")
        print(f"  Mean: {variance['migrations']['mean']:.1f}")
        print(f"  Stdev: {variance['migrations']['stdev']:.1f}")
        print(f"  Range: {variance['migrations']['min']}-{variance['migrations']['max']}")
        print()

        print("Mean Population:")
        print(f"  Mean: {variance['mean_population']['mean']:.2f}")
        print(f"  Stdev: {variance['mean_population']['stdev']:.2f}")
        print(f"  Range: {variance['mean_population']['min']:.1f}-{variance['mean_population']['max']:.1f}")
        print()

        print("CV (%):")
        print(f"  Mean: {variance['cv_percent']['mean']:.1f}%")
        print(f"  Stdev: {variance['cv_percent']['stdev']:.1f}%")
        print(f"  Range: {variance['cv_percent']['min']:.1f}%-{variance['cv_percent']['max']:.1f}%")
        print()

    print("=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    generate_runtime_report()
