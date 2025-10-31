#!/usr/bin/env python3
"""
Experiment Monitoring Utility

Monitors long-running experiments (like C256) by tracking:
- Process health (CPU, memory usage)
- Runtime progress estimation
- Log file growth
- Database write activity

Author: Aldrin Payopay (aldrin.gdf@gmail.com)
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
License: GPL-3.0
"""

import argparse
import time
import psutil
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
import json

def find_experiment_process(pattern: str):
    """Find running experiment process by name pattern."""
    for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
        try:
            cmdline = ' '.join(proc.info['cmdline'] or [])
            if pattern in cmdline:
                return proc
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return None

def format_duration(seconds: float) -> str:
    """Format duration in human-readable form."""
    td = timedelta(seconds=int(seconds))
    hours = td.seconds // 3600
    minutes = (td.seconds % 3600) // 60
    secs = td.seconds % 60

    if td.days > 0:
        return f"{td.days}d {hours}h {minutes}m"
    elif hours > 0:
        return f"{hours}h {minutes}m {secs}s"
    elif minutes > 0:
        return f"{minutes}m {secs}s"
    else:
        return f"{secs}s"

def estimate_progress(log_path: Path, expected_cycles: int = 12000):
    """Estimate experiment progress from log file."""
    if not log_path.exists():
        return None

    try:
        # Count cycle completions in log
        with open(log_path, 'r') as f:
            lines = f.readlines()

        # Look for cycle completion patterns
        completed_cycles = 0
        for line in lines[-1000:]:  # Check last 1000 lines for efficiency
            if 'Cycle' in line and 'complete' in line.lower():
                completed_cycles += 1

        if completed_cycles > 0:
            progress_pct = (completed_cycles / expected_cycles) * 100
            return {
                'completed_cycles': completed_cycles,
                'expected_cycles': expected_cycles,
                'progress_pct': progress_pct
            }
    except Exception as e:
        print(f"Warning: Could not estimate progress from log: {e}", file=sys.stderr)

    return None

def monitor_experiment(pattern: str, log_path: Path = None, interval: int = 60, duration: int = None):
    """
    Monitor experiment process in real-time.

    Args:
        pattern: Process name pattern to search for
        log_path: Path to experiment log file (optional)
        interval: Update interval in seconds
        duration: Total monitoring duration in seconds (None = indefinite)
    """
    start_time = time.time()

    print(f"Monitoring experiment: {pattern}")
    print(f"Update interval: {interval}s")
    if duration:
        print(f"Duration: {format_duration(duration)}")
    print("-" * 80)

    iterations = 0
    while True:
        proc = find_experiment_process(pattern)

        if proc is None:
            print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Process not found: {pattern}")
            print("Experiment may have completed or crashed.")
            break

        try:
            # Get process metrics
            with proc.oneshot():
                cpu_percent = proc.cpu_percent(interval=0.1)
                mem_info = proc.memory_info()
                mem_mb = mem_info.rss / (1024 * 1024)
                create_time = proc.create_time()
                runtime = time.time() - create_time

            # Display status
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"\n[{timestamp}]")
            print(f"  PID: {proc.pid}")
            print(f"  Runtime: {format_duration(runtime)}")
            print(f"  CPU: {cpu_percent:.1f}%")
            print(f"  Memory: {mem_mb:.1f} MB")

            # Progress estimation
            if log_path and log_path.exists():
                progress = estimate_progress(log_path)
                if progress:
                    print(f"  Progress: {progress['completed_cycles']}/{progress['expected_cycles']} cycles ({progress['progress_pct']:.1f}%)")

                    # ETA estimation
                    if progress['progress_pct'] > 0:
                        estimated_total = runtime / (progress['progress_pct'] / 100)
                        remaining = estimated_total - runtime
                        print(f"  ETA: {format_duration(remaining)} remaining")

                # Log file size
                log_size_mb = log_path.stat().st_size / (1024 * 1024)
                print(f"  Log size: {log_size_mb:.1f} MB")

            # Health check
            status = "✓ HEALTHY" if cpu_percent > 0.5 and mem_mb < 1000 else "⚠ CHECK"
            print(f"  Status: {status}")

            iterations += 1

            # Check duration limit
            if duration and (time.time() - start_time) >= duration:
                print(f"\nMonitoring duration reached: {format_duration(duration)}")
                break

            # Wait for next iteration
            time.sleep(interval)

        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            print(f"\nError accessing process: {e}")
            break
        except KeyboardInterrupt:
            print(f"\n\nMonitoring stopped by user (Ctrl+C)")
            print(f"Total monitoring time: {format_duration(time.time() - start_time)}")
            print(f"Iterations: {iterations}")
            break

def get_experiment_snapshot(pattern: str, log_path: Path = None):
    """Get single snapshot of experiment status."""
    proc = find_experiment_process(pattern)

    if proc is None:
        return {
            'status': 'NOT_FOUND',
            'pattern': pattern,
            'timestamp': datetime.now().isoformat()
        }

    try:
        with proc.oneshot():
            cpu_percent = proc.cpu_percent(interval=0.1)
            mem_info = proc.memory_info()
            mem_mb = mem_info.rss / (1024 * 1024)
            create_time = proc.create_time()
            runtime = time.time() - create_time

        snapshot = {
            'status': 'RUNNING',
            'pattern': pattern,
            'pid': proc.pid,
            'runtime_seconds': runtime,
            'runtime_formatted': format_duration(runtime),
            'cpu_percent': cpu_percent,
            'memory_mb': mem_mb,
            'timestamp': datetime.now().isoformat()
        }

        # Add progress if log available
        if log_path and log_path.exists():
            progress = estimate_progress(log_path)
            if progress:
                snapshot['progress'] = progress

                # ETA
                if progress['progress_pct'] > 0:
                    estimated_total = runtime / (progress['progress_pct'] / 100)
                    remaining = estimated_total - runtime
                    snapshot['eta_seconds'] = remaining
                    snapshot['eta_formatted'] = format_duration(remaining)

            snapshot['log_size_mb'] = log_path.stat().st_size / (1024 * 1024)

        return snapshot

    except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
        return {
            'status': 'ERROR',
            'pattern': pattern,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }

def main():
    parser = argparse.ArgumentParser(
        description='Monitor long-running experiment processes',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Monitor C256 experiment with default settings
  python monitor_experiment.py --pattern cycle256

  # Monitor with custom interval and log file
  python monitor_experiment.py --pattern cycle256 --log /path/to/experiment.log --interval 30

  # Get single snapshot (non-interactive)
  python monitor_experiment.py --pattern cycle256 --snapshot

  # Monitor for specific duration
  python monitor_experiment.py --pattern cycle256 --duration 3600  # 1 hour
        """
    )

    parser.add_argument('--pattern', type=str, required=True,
                       help='Process name pattern to search for (e.g., "cycle256")')
    parser.add_argument('--log', type=Path, default=None,
                       help='Path to experiment log file for progress estimation')
    parser.add_argument('--interval', type=int, default=60,
                       help='Update interval in seconds (default: 60)')
    parser.add_argument('--duration', type=int, default=None,
                       help='Total monitoring duration in seconds (default: indefinite)')
    parser.add_argument('--snapshot', action='store_true',
                       help='Get single snapshot instead of continuous monitoring')
    parser.add_argument('--json', action='store_true',
                       help='Output snapshot as JSON (requires --snapshot)')

    args = parser.parse_args()

    if args.snapshot:
        snapshot = get_experiment_snapshot(args.pattern, args.log)
        if args.json:
            print(json.dumps(snapshot, indent=2))
        else:
            print(f"Experiment Status: {snapshot['status']}")
            if snapshot['status'] == 'RUNNING':
                print(f"  PID: {snapshot['pid']}")
                print(f"  Runtime: {snapshot['runtime_formatted']}")
                print(f"  CPU: {snapshot['cpu_percent']:.1f}%")
                print(f"  Memory: {snapshot['memory_mb']:.1f} MB")
                if 'progress' in snapshot:
                    print(f"  Progress: {snapshot['progress']['progress_pct']:.1f}%")
                if 'eta_formatted' in snapshot:
                    print(f"  ETA: {snapshot['eta_formatted']}")
    else:
        monitor_experiment(args.pattern, args.log, args.interval, args.duration)

if __name__ == '__main__':
    main()
