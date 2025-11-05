#!/usr/bin/env python3
"""
VALIDATION CAMPAIGN STATUS DASHBOARD

Purpose: Real-time monitoring of C186→C187→C188→C189 campaign progress

Features:
  - Process status (running/complete/failed)
  - Experiment progress tracking
  - Timeline estimation
  - Results file verification
  - Monitor health checks
  - Next action recommendations

Usage:
  python3 campaign_status_dashboard.py         # Full dashboard
  python3 campaign_status_dashboard.py --json  # JSON output
  python3 campaign_status_dashboard.py --brief # One-line summary

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Date: 2025-11-05
Cycle: 1035
License: GPL-3.0

Co-Authored-By: Claude <noreply@anthropic.com>
"""

import json
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Campaign configuration
EXPERIMENTS = {
    'C186': {
        'name': 'Hierarchical Energy Dynamics',
        'script': 'cycle186_metapopulation_hierarchical_validation.py',
        'results': 'cycle186_metapopulation_hierarchical_validation_results.json',
        'count': 10,
        'est_hours': 6.0,
        'monitor_pid_file': None,
    },
    'C187': {
        'name': 'Network Structure Effects',
        'script': 'cycle187_network_structure_effects.py',
        'results': 'cycle187_network_structure_effects_results.json',
        'count': 30,
        'est_hours': 5.0,
        'monitor_pid_file': None,
    },
    'C188': {
        'name': 'Memory Effects',
        'script': 'cycle188_memory_effects.py',
        'results': 'cycle188_memory_effects_results.json',
        'count': 40,
        'est_hours': 6.7,
        'monitor_pid_file': None,
    },
    'C189': {
        'name': 'Burst Clustering',
        'script': 'cycle189_burst_clustering.py',
        'results': 'cycle189_burst_clustering_results.json',
        'count': 100,
        'est_hours': 16.7,
        'monitor_pid_file': None,
    },
}

# Paths
EXPERIMENTS_DIR = Path(__file__).parent
RESULTS_DIR = EXPERIMENTS_DIR / "results"
LOG_DIR = Path("/tmp")


def get_process_status(script_name: str) -> Optional[Dict]:
    """Check if a process is running by script name."""
    try:
        # Use ps to find process
        result = subprocess.run(
            ['ps', 'aux'],
            capture_output=True,
            text=True,
            timeout=5
        )

        for line in result.stdout.split('\n'):
            if script_name in line and 'python' in line.lower():
                parts = line.split()
                return {
                    'pid': int(parts[1]),
                    'cpu': float(parts[2]),
                    'mem': float(parts[3]),
                    'elapsed': parts[9],  # May be TIME or START depending on ps format
                    'running': True,
                }

        return None

    except Exception as e:
        print(f"Warning: Could not check process status: {e}", file=sys.stderr)
        return None


def check_results_file(experiment_id: str) -> Optional[Dict]:
    """Check if results file exists and count experiments."""
    results_path = RESULTS_DIR / EXPERIMENTS[experiment_id]['results']

    if not results_path.exists():
        return None

    try:
        with open(results_path, 'r') as f:
            data = json.load(f)

        exp_count = len(data.get('experiments', []))
        expected_count = EXPERIMENTS[experiment_id]['count']

        return {
            'exists': True,
            'experiments': exp_count,
            'expected': expected_count,
            'complete': exp_count == expected_count,
            'size_kb': results_path.stat().st_size / 1024,
            'modified': datetime.fromtimestamp(results_path.stat().st_mtime),
        }

    except Exception as e:
        return {
            'exists': True,
            'error': str(e),
            'size_kb': results_path.stat().st_size / 1024,
        }


def check_monitor_status(experiment_id: str) -> Optional[Dict]:
    """Check if handoff monitor is running."""
    monitor_script = f"monitor_and_launch_{experiment_id.lower()}.sh"

    try:
        result = subprocess.run(
            ['ps', 'aux'],
            capture_output=True,
            text=True,
            timeout=5
        )

        for line in result.stdout.split('\n'):
            if monitor_script in line:
                parts = line.split()
                return {
                    'pid': int(parts[1]),
                    'running': True,
                    'script': monitor_script,
                }

        return None

    except Exception as e:
        return None


def get_experiment_status(experiment_id: str) -> Dict:
    """Get comprehensive status for an experiment."""
    config = EXPERIMENTS[experiment_id]

    # Check process
    process = get_process_status(config['script'])

    # Check results
    results = check_results_file(experiment_id)

    # Check monitor (for next experiment)
    next_exp = {
        'C186': 'C187',
        'C187': 'C188',
        'C188': 'C189',
        'C189': None,
    }.get(experiment_id)

    monitor = check_monitor_status(next_exp) if next_exp else None

    # Determine overall status
    if results and results.get('complete'):
        status = 'COMPLETE'
    elif process and process.get('running'):
        status = 'RUNNING'
    elif results and results.get('experiments', 0) > 0:
        status = 'PARTIAL'
    else:
        status = 'PENDING'

    return {
        'id': experiment_id,
        'name': config['name'],
        'status': status,
        'process': process,
        'results': results,
        'monitor': monitor,
        'config': {
            'experiments': config['count'],
            'est_hours': config['est_hours'],
        },
    }


def estimate_campaign_timeline(statuses: Dict[str, Dict]) -> Dict:
    """Estimate campaign completion timeline."""
    now = datetime.now()
    current_time = now
    timeline = {}

    for exp_id in ['C186', 'C187', 'C188', 'C189']:
        status = statuses[exp_id]
        config = EXPERIMENTS[exp_id]

        if status['status'] == 'COMPLETE':
            timeline[exp_id] = {
                'status': 'COMPLETE',
                'completed': status['results']['modified'] if status['results'] else None,
            }
        elif status['status'] == 'RUNNING':
            # Estimate remaining time
            est_remaining = timedelta(hours=config['est_hours'] * 0.5)  # Assume halfway
            timeline[exp_id] = {
                'status': 'RUNNING',
                'est_completion': current_time + est_remaining,
            }
            current_time += est_remaining
        else:
            # Pending - use full estimate
            timeline[exp_id] = {
                'status': 'PENDING',
                'est_start': current_time,
                'est_completion': current_time + timedelta(hours=config['est_hours']),
            }
            current_time += timedelta(hours=config['est_hours'])

    return {
        'generated_at': now,
        'timeline': timeline,
        'est_campaign_completion': current_time,
        'remaining_hours': (current_time - now).total_seconds() / 3600,
    }


def generate_dashboard(brief: bool = False, json_output: bool = False) -> None:
    """Generate status dashboard."""
    statuses = {
        exp_id: get_experiment_status(exp_id)
        for exp_id in ['C186', 'C187', 'C188', 'C189']
    }

    timeline = estimate_campaign_timeline(statuses)

    if json_output:
        output = {
            'timestamp': datetime.now().isoformat(),
            'experiments': statuses,
            'timeline': {
                'generated_at': timeline['generated_at'].isoformat(),
                'timeline': {
                    k: {
                        **v,
                        'est_start': v['est_start'].isoformat() if 'est_start' in v else None,
                        'est_completion': v['est_completion'].isoformat() if 'est_completion' in v else None,
                        'completed': v['completed'].isoformat() if 'completed' in v and v['completed'] else None,
                    }
                    for k, v in timeline['timeline'].items()
                },
                'est_campaign_completion': timeline['est_campaign_completion'].isoformat(),
                'remaining_hours': timeline['remaining_hours'],
            },
        }
        print(json.dumps(output, indent=2))
        return

    if brief:
        # One-line summary
        statuses_str = ' | '.join([
            f"{exp_id}: {status['status']}"
            for exp_id, status in statuses.items()
        ])
        remaining = f"{timeline['remaining_hours']:.1f}h"
        print(f"{statuses_str} | Remaining: {remaining}")
        return

    # Full dashboard
    print("=" * 80)
    print("VALIDATION CAMPAIGN STATUS DASHBOARD")
    print("=" * 80)
    print()
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Experiment statuses
    for exp_id in ['C186', 'C187', 'C188', 'C189']:
        status = statuses[exp_id]
        print(f"{exp_id}: {status['name']}")
        print(f"  Status: {status['status']}")

        if status['process']:
            proc = status['process']
            print(f"  Process: PID {proc['pid']} ({proc['cpu']}% CPU, {proc['mem']}% MEM)")

        if status['results']:
            res = status['results']
            if res.get('complete'):
                print(f"  Results: ✅ {res['experiments']}/{res['expected']} experiments ({res['size_kb']:.1f} KB)")
            elif res.get('experiments', 0) > 0:
                print(f"  Results: ⏳ {res['experiments']}/{res['expected']} experiments ({res['size_kb']:.1f} KB)")
            elif res.get('error'):
                print(f"  Results: ❌ Error: {res['error']}")
        else:
            print(f"  Results: - (not yet created)")

        if status['monitor']:
            mon = status['monitor']
            print(f"  Monitor: ✅ {mon['script']} (PID {mon['pid']})")

        print()

    # Timeline
    print("-" * 80)
    print("CAMPAIGN TIMELINE")
    print("-" * 80)
    print()

    for exp_id in ['C186', 'C187', 'C188', 'C189']:
        tl = timeline['timeline'][exp_id]

        if tl['status'] == 'COMPLETE':
            completed = tl['completed'].strftime('%Y-%m-%d %H:%M') if tl['completed'] else 'Unknown'
            print(f"{exp_id}: ✅ COMPLETE ({completed})")
        elif tl['status'] == 'RUNNING':
            est_comp = tl['est_completion'].strftime('%Y-%m-%d %H:%M')
            print(f"{exp_id}: ⏳ RUNNING (est. completion: {est_comp})")
        else:
            est_start = tl['est_start'].strftime('%Y-%m-%d %H:%M')
            est_comp = tl['est_completion'].strftime('%Y-%m-%d %H:%M')
            print(f"{exp_id}: - PENDING (est. {est_start} → {est_comp})")

    print()
    print(f"Estimated Campaign Completion: {timeline['est_campaign_completion'].strftime('%Y-%m-%d %H:%M')}")
    print(f"Remaining Time: {timeline['remaining_hours']:.1f} hours")
    print()

    # Next actions
    print("-" * 80)
    print("RECOMMENDED ACTIONS")
    print("-" * 80)
    print()

    # Determine next action
    all_complete = all(s['status'] == 'COMPLETE' for s in statuses.values())
    any_running = any(s['status'] == 'RUNNING' for s in statuses.values())

    if all_complete:
        print("✅ All experiments complete!")
        print("   → Run Paper 4 analysis: python3 ../code/validation/generate_complete_paper4.py")
        print("   → Follow integration guide: papers/paper4/INTEGRATION_GUIDE.md")
    elif any_running:
        running_exp = [exp_id for exp_id, s in statuses.items() if s['status'] == 'RUNNING'][0]
        print(f"⏳ {running_exp} currently running")
        print(f"   → Monitor progress: tail -f /tmp/{running_exp.lower()}_output.log")
        print("   → Automation active, no manual intervention required")
    else:
        next_exp = next((exp_id for exp_id in ['C186', 'C187', 'C188', 'C189'] if statuses[exp_id]['status'] == 'PENDING'), None)
        if next_exp:
            print(f"- Next: {next_exp} pending")
            print(f"   → Check handoff monitor: ps aux | grep monitor_and_launch")
            print(f"   → Manual launch if needed: ./launch_validation_campaign.sh {next_exp}")

    print()
    print("=" * 80)


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Validation Campaign Status Dashboard')
    parser.add_argument('--brief', action='store_true', help='One-line summary')
    parser.add_argument('--json', action='store_true', help='JSON output')

    args = parser.parse_args()

    generate_dashboard(brief=args.brief, json_output=args.json)


if __name__ == '__main__':
    main()
