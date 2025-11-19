#!/usr/bin/env python3
"""
EXPERIMENTAL RESULTS AGGREGATOR
Rapid status overview of all experimental cycles and available data

Purpose:
  Quick diagnostic tool to answer:
    - Which cycles have completed?
    - What data is available for analysis?
    - What parameter spaces have been explored?
    - Which experiments are currently running?
    - What's the status of autonomous pipeline?

Framework Validation:
  - Self-Giving: System provides own status overview autonomously
  - Temporal Stewardship: Rapid access to research state for continuity

Date: 2025-10-25
Status: Diagnostic utility
Researcher: Claude (DUALITY-ZERO-V2)
"""

import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


# =============================================================================
# DATA LOADING
# =============================================================================

def scan_available_results() -> Dict:
    """Scan results directory for all available cycle data."""
    results_dir = Path(__file__).parent / 'results'

    if not results_dir.exists():
        return {}

    results = {
        'cycle_results': {},
        'analysis_results': {},
        'other_results': {},
    }

    # Scan for cycle results
    for file_path in sorted(results_dir.glob('cycle*.json')):
        try:
            cycle_num = int(file_path.stem.split('_')[0].replace('cycle', ''))

            # Get file info
            stat = file_path.stat()
            size_kb = stat.st_size / 1024

            # Quick peek at data
            with open(file_path, 'r') as f:
                data = json.load(f)

            # Extract experiment count
            if isinstance(data, list):
                n_exp = len(data)
            elif 'experiments' in data:
                n_exp = len(data['experiments'])
            elif 'results' in data:
                n_exp = len(data['results'])
            else:
                n_exp = 0

            results['cycle_results'][cycle_num] = {
                'filename': file_path.name,
                'size_kb': round(size_kb, 1),
                'n_experiments': n_exp,
                'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M'),
            }

        except (ValueError, json.JSONDecodeError, KeyError) as e:
            # Skip malformed files
            continue

    # Scan for analysis results
    analysis_files = [
        'cycle162_analysis.json',
        'cross_cycle_comparison.json',
        'comprehensive_meta_analysis.json',
        'publication_analysis_corrected.json',
    ]

    for filename in analysis_files:
        file_path = results_dir / filename
        if file_path.exists():
            stat = file_path.stat()
            results['analysis_results'][filename] = {
                'size_kb': round(stat.st_size / 1024, 1),
                'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M'),
            }

    return results


def check_running_processes() -> List[Dict]:
    """Check for currently running cycle experiments."""
    running = []

    try:
        # Get all python processes
        result = subprocess.run(
            ['ps', 'aux'],
            capture_output=True,
            text=True
        )

        # Filter for cycle experiments
        for line in result.stdout.split('\n'):
            if 'cycle' in line.lower() and '.py' in line and 'python' in line:
                # Extract PID and command
                parts = line.split()
                if len(parts) >= 11:
                    pid = parts[1]
                    cmd_start = ' '.join(parts[10:])

                    # Try to extract cycle number
                    for part in parts:
                        if 'cycle' in part and '.py' in part:
                            try:
                                cycle_num = int(part.split('cycle')[1].split('_')[0].split('.')[0])
                                running.append({
                                    'pid': pid,
                                    'cycle': cycle_num,
                                    'command': cmd_start[:80],  # Truncate long commands
                                })
                                break
                            except (ValueError, IndexError):
                                continue

    except Exception:
        pass

    return running


def check_autonomous_infrastructure() -> Dict:
    """Check status of autonomous infrastructure components."""
    experiments_dir = Path(__file__).parent

    infrastructure = {
        'cycle_163_scenarios': {},
        'analysis_pipeline': {},
        'autonomous_orchestrator': False,
        'monitoring_dashboard': False,
        'visualization_pipeline': False,
        'meta_analysis': False,
    }

    # Check Cycle 163 scenarios
    scenarios = {
        'A': 'cycle163a_harmonic_fine_grained.py',
        'B': 'cycle163b_seed_mechanism.py',
        'C': 'cycle163c_frequency_seed_interaction.py',
        'D': 'cycle163d_threshold_investigation.py',
        'E': 'cycle163e_composition_analysis.py',
        'F': 'cycle163f_25pct_deep_dive.py',
    }

    for scenario, filename in scenarios.items():
        infrastructure['cycle_163_scenarios'][scenario] = (experiments_dir / filename).exists()

    # Check pipeline components
    infrastructure['analysis_pipeline'] = (experiments_dir / 'analyze_cycle162_results.py').exists()
    infrastructure['autonomous_orchestrator'] = (experiments_dir / 'autonomous_experiment_orchestrator.py').exists()
    infrastructure['monitoring_dashboard'] = (experiments_dir / 'monitor_autonomous_pipeline.py').exists()
    infrastructure['visualization_pipeline'] = (experiments_dir / 'visualize_cycle162_results.py').exists()
    infrastructure['meta_analysis'] = (experiments_dir / 'comprehensive_meta_analysis.py').exists()

    return infrastructure


# =============================================================================
# DISPLAY FUNCTIONS
# =============================================================================

def display_summary(results: Dict, running: List[Dict], infrastructure: Dict):
    """Display comprehensive status summary."""

    print("=" * 80)
    print("EXPERIMENTAL RESULTS AGGREGATOR")
    print("=" * 80)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Cycle Results Summary
    print("CYCLE RESULTS AVAILABLE")
    print("=" * 80)

    if results['cycle_results']:
        cycles = sorted(results['cycle_results'].keys())
        print(f"  Cycles: {min(cycles)}-{max(cycles)} ({len(cycles)} cycles)")
        print(f"  Total experiments: {sum(c['n_experiments'] for c in results['cycle_results'].values())}")
        print()

        print("  Recent cycles:")
        for cycle_num in sorted(cycles)[-10:]:  # Show last 10
            info = results['cycle_results'][cycle_num]
            print(f"    Cycle {cycle_num}: {info['n_experiments']} experiments, "
                  f"{info['size_kb']} KB, modified {info['modified']}")
    else:
        print("  No cycle results found")

    print()

    # Analysis Results
    print("ANALYSIS RESULTS AVAILABLE")
    print("=" * 80)

    if results['analysis_results']:
        for filename, info in results['analysis_results'].items():
            print(f"  ✅ {filename} ({info['size_kb']} KB, {info['modified']})")
    else:
        print("  No analysis results found")

    print()

    # Running Processes
    print("CURRENTLY RUNNING EXPERIMENTS")
    print("=" * 80)

    if running:
        for proc in running:
            print(f"  • Cycle {proc['cycle']} (PID {proc['pid']})")
            print(f"    {proc['command']}")
    else:
        print("  No experiments currently running")

    print()

    # Infrastructure Status
    print("AUTONOMOUS INFRASTRUCTURE STATUS")
    print("=" * 80)

    print("  Cycle 163 Scenarios:")
    scenarios = infrastructure['cycle_163_scenarios']
    ready_count = sum(scenarios.values())
    print(f"    {ready_count}/6 scenarios ready: ", end='')
    print(' '.join([f"{s}:{'✅' if status else '❌'}" for s, status in sorted(scenarios.items())]))

    print()
    print("  Pipeline Components:")
    components = [
        ('Analysis Pipeline', infrastructure['analysis_pipeline']),
        ('Visualization Pipeline', infrastructure['visualization_pipeline']),
        ('Autonomous Orchestrator', infrastructure['autonomous_orchestrator']),
        ('Monitoring Dashboard', infrastructure['monitoring_dashboard']),
        ('Meta-Analysis Tool', infrastructure['meta_analysis']),
    ]

    for name, status in components:
        print(f"    {'✅' if status else '❌'} {name}")

    print()

    # Summary Statistics
    print("SUMMARY STATISTICS")
    print("=" * 80)

    if results['cycle_results']:
        cycles_list = sorted(results['cycle_results'].keys())
        total_exp = sum(c['n_experiments'] for c in results['cycle_results'].values())
        total_size = sum(c['size_kb'] for c in results['cycle_results'].values())

        print(f"  Total cycles completed: {len(cycles_list)}")
        print(f"  Cycle range: {min(cycles_list)}-{max(cycles_list)}")
        print(f"  Total experiments: {total_exp}")
        print(f"  Total data size: {total_size:.1f} KB ({total_size/1024:.1f} MB)")
        print(f"  Average experiments per cycle: {total_exp/len(cycles_list):.1f}")

    print()
    print("=" * 80)


# =============================================================================
# MAIN
# =============================================================================

def main():
    """Run results aggregator."""

    # Scan for available results
    results = scan_available_results()

    # Check running processes
    running = check_running_processes()

    # Check infrastructure
    infrastructure = check_autonomous_infrastructure()

    # Display summary
    display_summary(results, running, infrastructure)


if __name__ == '__main__':
    main()
