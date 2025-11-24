#!/usr/bin/env python3
"""
Monitor C176 V3 Completion and Auto-Analyze Results

Purpose: Watch for C176 V3 completion, immediately analyze results,
         and determine Paper 2 revision scenario

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Date: 2025-10-26 (Cycle 215)
"""

import time
import json
import sys
from pathlib import Path
from datetime import datetime
import subprocess

# Paths
RESULTS_FILE = Path("results/cycle176_ablation_study_v3.json")
PID = 72073  # C176 V3 process ID

def check_process_running(pid):
    """Check if process is still running."""
    try:
        result = subprocess.run(
            ['ps', '-p', str(pid)],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except:
        return False

def analyze_baseline_results(data):
    """Analyze BASELINE condition results and determine scenario."""

    # Extract BASELINE experiments
    baseline_results = [
        r for r in data.get('experiments', [])
        if r.get('condition') == 'BASELINE'
    ]

    if not baseline_results:
        print("ERROR: No BASELINE results found!")
        return None

    n = len(baseline_results)

    # Calculate key metrics
    mean_pop = sum(r['mean_population'] for r in baseline_results) / n
    cv_pop = sum(r['cv_population'] for r in baseline_results) / n
    basin_a_count = sum(1 for r in baseline_results if r['basin'] == 'A')
    basin_a_pct = (basin_a_count / n) * 100
    comp_events = sum(r['total_composition_events'] for r in baseline_results) / n
    spawn_count = sum(r['spawn_count'] for r in baseline_results) / n

    # Determine scenario
    if mean_pop >= 5:
        scenario = "A - SUCCESS"
        revision = "Minimal (2-3 hours)"
        interpretation = "Energy recharge enables sustained populations"
    elif mean_pop >= 2:
        scenario = "B - PARTIAL SUCCESS"
        revision = "Moderate (3-4 hours)"
        interpretation = "Sustained but variable populations"
    else:
        scenario = "C - FAILURE"
        revision = "Major (1-2 weeks, highest impact)"
        interpretation = "Energy constraints fundamental limitation"

    # Display results
    print("=" * 80)
    print("C176 V3 BASELINE RESULTS ANALYSIS")
    print("=" * 80)
    print()
    print(f"Experiments Analyzed: {n}")
    print()
    print("KEY METRICS:")
    print("-" * 80)
    print(f"  Mean Population:       {mean_pop:6.2f}  (target: ≥5 for success)")
    print(f"  CV Population:         {cv_pop:6.1f}% (target: <50% for stability)")
    print(f"  Basin A Occupation:    {basin_a_pct:6.0f}% (target: ≥80% for dominance)")
    print(f"  Composition Events:    {comp_events:6.0f}  (target: >1000 for activity)")
    print(f"  Spawn Count:           {spawn_count:6.1f}")
    print()
    print("SCENARIO DETERMINATION:")
    print("-" * 80)
    print(f"  Scenario:   {scenario}")
    print(f"  Revision:   {revision}")
    print(f"  Interpretation: {interpretation}")
    print()

    # Detailed per-experiment breakdown
    print("PER-EXPERIMENT BREAKDOWN:")
    print("-" * 80)
    print(f"{'Seed':>6} | {'Mean Pop':>8} | {'CV%':>6} | {'Basin':>5} | {'Comp':>5} | {'Spawn':>5}")
    print("-" * 80)
    for r in sorted(baseline_results, key=lambda x: x['seed']):
        print(f"{r['seed']:6d} | {r['mean_population']:8.2f} | {r['cv_population']:6.1f} | "
              f"{r['basin']:>5} | {r['total_composition_events']:5d} | {r['spawn_count']:5d}")
    print()

    # Statistical summary
    populations = [r['mean_population'] for r in baseline_results]
    min_pop = min(populations)
    max_pop = max(populations)

    print("POPULATION STATISTICS:")
    print("-" * 80)
    print(f"  Minimum:  {min_pop:.2f}")
    print(f"  Maximum:  {max_pop:.2f}")
    print(f"  Mean:     {mean_pop:.2f}")
    print(f"  Range:    {max_pop - min_pop:.2f}")
    print()

    # Comparison with C171 and C176 V2
    print("HISTORICAL COMPARISON:")
    print("-" * 80)
    print(f"{'Experiment':>15} | {'Population':>12} | {'Composition':>12} | {'Status':>15}")
    print("-" * 80)
    print(f"{'C171 (no death)':>15} | {'~17 (final)':>12} | {'~3000':>12} | {'Accumulation':>15}")
    print(f"{'C176 V2 (death)':>15} | {'0.49 (mean)':>12} | {'38':>12} | {'Collapse':>15}")
    print(f"{'C176 V3 (+ rech)':>15} | {f'{mean_pop:.2f} (mean)':>12} | {f'{comp_events:.0f}':>12} | {scenario.split('-')[1].strip():>15}")
    print()

    # Next actions
    print("RECOMMENDED NEXT ACTIONS:")
    print("-" * 80)

    if mean_pop >= 5:
        print("  1. Execute Scenario A revision (minimal, 2-3 hours)")
        print("  2. Replace C171 with C176 V3 throughout Paper 2")
        print("  3. Add energy recharge subsection to Methods")
        print("  4. Update Results and Conclusions with V3 data")
        print("  5. Launch C177 boundary mapping immediately")
        print("  6. Commit updated Paper 2 to repository")

    elif mean_pop >= 2:
        print("  1. Execute Scenario B revision (moderate, 3-4 hours)")
        print("  2. Frame as 'sustained variability' regime")
        print("  3. Document oscillatory dynamics")
        print("  4. Consider launching C177 with monitoring")
        print("  5. Analyze time-series for patterns")

    else:
        print("  1. Execute Scenario C revision (major, 1-2 weeks)")
        print("  2. Reframe as three-regime classification paper")
        print("  3. Create detailed revision plan with timeline")
        print("  4. HOLD C177 pending energy model redesign")
        print("  5. Consider alternative publication venues (PRE)")
        print("  6. Document energy constraints as fundamental finding")

    print()
    print("=" * 80)
    print(f"Analysis completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()

    return {
        'scenario': scenario,
        'mean_population': mean_pop,
        'cv_population': cv_pop,
        'basin_a_pct': basin_a_pct,
        'composition_events': comp_events,
        'n_experiments': n
    }

def main():
    """Monitor C176 V3 and auto-analyze when complete."""

    print("=" * 80)
    print("C176 V3 MONITORING SCRIPT")
    print("=" * 80)
    print()
    print(f"Monitoring PID: {PID}")
    print(f"Results file: {RESULTS_FILE}")
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    print("Waiting for C176 V3 to complete...")
    print()

    check_interval = 30  # seconds
    last_check = None

    while True:
        # Check if process is still running
        running = check_process_running(PID)

        # Check if results file exists
        results_exist = RESULTS_FILE.exists()

        current_time = datetime.now().strftime('%H:%M:%S')

        if last_check != current_time:
            if running:
                status = f"[{current_time}] C176 V3 still running (PID {PID})..."
            else:
                status = f"[{current_time}] C176 V3 process ended"

            if results_exist:
                status += " | Results file exists"

            print(status)
            last_check = current_time

        # If process ended AND results exist, analyze
        if not running and results_exist:
            print()
            print("=" * 80)
            print("C176 V3 COMPLETED - Beginning Analysis")
            print("=" * 80)
            print()

            time.sleep(2)  # Brief pause to ensure file fully written

            try:
                with open(RESULTS_FILE) as f:
                    data = json.load(f)

                results = analyze_baseline_results(data)

                # Save analysis summary
                summary_path = RESULTS_FILE.parent / "cycle176_v3_analysis_summary.json"
                with open(summary_path, 'w') as f:
                    json.dump(results, f, indent=2)

                print(f"Analysis summary saved: {summary_path}")
                print()

                return 0

            except Exception as e:
                print(f"ERROR during analysis: {e}")
                import traceback
                traceback.print_exc()
                return 1

        # If process ended but no results, error
        if not running and not results_exist:
            print()
            print("ERROR: C176 V3 process ended but no results file found!")
            print(f"Expected: {RESULTS_FILE.absolute()}")
            print()
            return 1

        # Otherwise, keep waiting
        time.sleep(check_interval)

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nMonitoring interrupted by user")
        sys.exit(0)
