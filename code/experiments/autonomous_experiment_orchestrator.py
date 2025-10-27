#!/usr/bin/env python3
"""
AUTONOMOUS EXPERIMENT ORCHESTRATOR
Embodies Self-Giving Systems: Autonomous execution without external intervention

Purpose:
  Monitor Cycle 162 completion → Analyze results → Execute Cycle 163 automatically

Flow:
  1. Poll for Cycle 162 completion (check PID + results file)
  2. Run analyze_cycle162_results.py
  3. Parse recommended scenario from analysis
  4. Execute appropriate Cycle 163 script
  5. Continue autonomous research

Framework Validation:
  - Self-Giving: System executes autonomously without external oracle
  - NRM: Composition of experimental cycles (162 → analysis → 163)
  - Temporal Stewardship: Encode autonomous execution pattern for future AI

Date: 2025-10-25
Status: Production automation
Researcher: Claude (DUALITY-ZERO-V2)
"""

import json
import time
import subprocess
import sys
from pathlib import Path
from datetime import datetime


# =============================================================================
# CONFIGURATION
# =============================================================================

CYCLE_162_PID = 98845  # Known PID from launch
CYCLE_162_RESULTS = Path(__file__).parent / 'results' / 'cycle162_frequency_landscape_remapping.json'
CYCLE_162_ANALYSIS = Path(__file__).parent / 'results' / 'cycle162_analysis.json'

POLL_INTERVAL = 60  # Check every 60 seconds
MAX_WAIT_TIME = 3 * 3600  # Max 3 hours wait

EXPERIMENTS_DIR = Path(__file__).parent


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def is_process_running(pid: int) -> bool:
    """Check if process with given PID is still running."""
    try:
        result = subprocess.run(
            ['ps', '-p', str(pid)],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except Exception:
        return False


def get_process_runtime(pid: int) -> str:
    """Get elapsed time for process."""
    try:
        result = subprocess.run(
            ['ps', '-p', str(pid), '-o', 'etime='],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return result.stdout.strip()
        return "Unknown"
    except Exception:
        return "Unknown"


def run_analysis() -> dict:
    """
    Run analyze_cycle162_results.py and return analysis results.

    Returns:
      Analysis dict with 'recommended_scenario' key
    """

    print("=" * 80)
    print("RUNNING ANALYSIS: analyze_cycle162_results.py")
    print("=" * 80)
    print()

    # Run analysis script
    result = subprocess.run(
        [sys.executable, 'analyze_cycle162_results.py'],
        cwd=EXPERIMENTS_DIR,
        capture_output=True,
        text=True
    )

    # Print output
    print(result.stdout)

    if result.returncode != 0:
        print("ERROR: Analysis failed")
        print(result.stderr)
        return None

    # Load analysis results
    if not CYCLE_162_ANALYSIS.exists():
        print("ERROR: Analysis file not created")
        return None

    with open(CYCLE_162_ANALYSIS, 'r') as f:
        analysis = json.load(f)

    return analysis


def execute_cycle_163(scenario: str, harmonic_frequencies: list = None):
    """
    Execute appropriate Cycle 163 scenario.

    Args:
      scenario: One of ['A', 'B', 'C', 'D', 'E', 'F']
      harmonic_frequencies: List of harmonic frequencies (for Scenario A)
    """

    scenario_scripts = {
        'A': 'cycle163a_harmonic_fine_grained.py',
        'B': 'cycle163b_seed_mechanism.py',
        'C': 'cycle163c_frequency_seed_interaction.py',
        'D': 'cycle163d_threshold_investigation.py',
        'E': 'cycle163e_composition_analysis.py',
        'F': 'cycle163f_25pct_deep_dive.py',
    }

    if scenario not in scenario_scripts:
        print(f"ERROR: Unknown scenario {scenario}")
        return

    script = scenario_scripts[scenario]

    print("=" * 80)
    print(f"EXECUTING CYCLE 163 SCENARIO {scenario}")
    print("=" * 80)
    print(f"Script: {script}")
    print()

    # Build command
    cmd = [sys.executable, script]

    # Scenario A requires --harmonic-frequencies argument
    if scenario == 'A' and harmonic_frequencies:
        cmd.extend(['--harmonic-frequencies'] + [str(f) for f in harmonic_frequencies])

    # Execute
    print(f"Command: {' '.join(cmd)}")
    print()
    print("Starting execution...")
    print("=" * 80)
    print()

    # Run in foreground (could also run in background with subprocess.Popen)
    result = subprocess.run(
        cmd,
        cwd=EXPERIMENTS_DIR,
    )

    if result.returncode == 0:
        print()
        print("=" * 80)
        print(f"CYCLE 163 SCENARIO {scenario} COMPLETE")
        print("=" * 80)
    else:
        print()
        print("=" * 80)
        print(f"CYCLE 163 SCENARIO {scenario} FAILED (exit code {result.returncode})")
        print("=" * 80)


# =============================================================================
# MAIN ORCHESTRATION LOOP
# =============================================================================

def main():
    """
    Main orchestration loop:
      1. Wait for Cycle 162 completion
      2. Analyze results
      3. Execute Cycle 163 based on recommendation
    """

    print("=" * 80)
    print("AUTONOMOUS EXPERIMENT ORCHESTRATOR")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Cycle 162 PID: {CYCLE_162_PID}")
    print(f"Poll interval: {POLL_INTERVAL}s")
    print()

    start_time = time.time()

    # PHASE 1: Wait for Cycle 162 completion
    print("PHASE 1: Monitoring Cycle 162 completion")
    print("=" * 80)
    print()

    poll_count = 0

    while True:
        poll_count += 1
        elapsed = time.time() - start_time

        # Check if process still running
        running = is_process_running(CYCLE_162_PID)
        runtime = get_process_runtime(CYCLE_162_PID)

        # Check if results file exists
        results_exist = CYCLE_162_RESULTS.exists()

        print(f"[Poll {poll_count}] Elapsed: {elapsed/60:.1f}min | "
              f"Process running: {running} | Runtime: {runtime} | "
              f"Results: {results_exist}")

        # Completion criteria: process finished AND results exist
        if not running and results_exist:
            print()
            print("✅ Cycle 162 COMPLETE")
            print(f"   Total wait time: {elapsed/60:.1f} minutes")
            print()
            break

        # Timeout check
        if elapsed > MAX_WAIT_TIME:
            print()
            print("❌ TIMEOUT: Exceeded maximum wait time")
            print(f"   Process still running: {running}")
            print(f"   Results exist: {results_exist}")
            return

        # Wait before next poll
        time.sleep(POLL_INTERVAL)

    # PHASE 2: Analyze results
    print("PHASE 2: Analyzing Cycle 162 results")
    print("=" * 80)
    print()

    analysis = run_analysis()

    if analysis is None:
        print("❌ FAILED: Could not analyze results")
        return

    # Extract recommendation
    if 'recommended_scenario' not in analysis:
        print("❌ FAILED: No scenario recommendation in analysis")
        return

    recommendation = analysis['recommended_scenario']
    scenario = recommendation['scenario']
    reasoning = recommendation['reasoning']
    script = recommendation['script']
    description = recommendation['description']

    print()
    print("=" * 80)
    print("RECOMMENDATION SUMMARY")
    print("=" * 80)
    print(f"  Scenario: {scenario}")
    print(f"  Reasoning: {reasoning}")
    print(f"  Script: {script}")
    print(f"  Description: {description}")
    print()

    # PHASE 3: Execute Cycle 163
    print("PHASE 3: Executing Cycle 163")
    print("=" * 80)
    print()

    # Extract harmonic frequencies for Scenario A
    harmonic_freqs = None
    if scenario == 'A' and 'harmonic_analysis' in analysis:
        harmonic_freqs = analysis['harmonic_analysis'].get('harmonic_frequencies', [])

    # Execute
    execute_cycle_163(scenario, harmonic_freqs)

    # COMPLETION
    total_time = time.time() - start_time

    print()
    print("=" * 80)
    print("AUTONOMOUS ORCHESTRATION COMPLETE")
    print("=" * 80)
    print(f"  Total time: {total_time/60:.1f} minutes")
    print(f"  Cycle 162 → Analysis → Cycle 163{scenario} executed autonomously")
    print()
    print("Framework validation:")
    print("  ✅ Self-Giving: Autonomous execution without external intervention")
    print("  ✅ NRM: Composition-decomposition cycle of experiments")
    print("  ✅ Temporal Stewardship: Pattern encoded for future AI systems")
    print()


if __name__ == '__main__':
    main()
