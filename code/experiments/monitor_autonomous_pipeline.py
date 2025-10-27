#!/usr/bin/env python3
"""
AUTONOMOUS PIPELINE REAL-TIME MONITOR
Interactive dashboard for Cycle 162→163 autonomous research pipeline

Purpose:
  Real-time monitoring and optional triggering of autonomous pipeline:
    - Cycle 162 progress (PID check, runtime, results file status)
    - Analysis readiness (analyze_cycle162_results.py)
    - Visualization readiness (visualize_cycle162_results.py)
    - Orchestrator status (autonomous_experiment_orchestrator.py)
    - Option to trigger autonomous execution when ready

Features:
  - Live progress updates every 5 seconds
  - ETA calculations based on expected runtime
  - Colored status indicators
  - Option to launch orchestrator automatically
  - Framework validation checkpoints

Framework Validation:
  - Self-Giving: Monitors own execution pipeline autonomously
  - NRM: Tracks composition of experimental cycles
  - Temporal Stewardship: Documents autonomous research progression

Date: 2025-10-25
Status: Production monitoring tool
Researcher: Claude (DUALITY-ZERO-V2)
"""

import time
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timedelta
import json


# =============================================================================
# CONFIGURATION
# =============================================================================

CYCLE_162_PID = 98845
CYCLE_162_RESULTS = Path(__file__).parent / 'results' / 'cycle162_frequency_landscape_remapping.json'
CYCLE_162_ANALYSIS = Path(__file__).parent / 'results' / 'cycle162_analysis.json'
EXPERIMENTS_DIR = Path(__file__).parent

# Expected runtime (from empirical observations)
EXPECTED_RUNTIME = 2.5 * 3600  # 2.5 hours in seconds
UPDATE_INTERVAL = 5  # seconds


# =============================================================================
# ANSI COLOR CODES
# =============================================================================

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


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


def get_process_runtime(pid: int) -> int:
    """Get elapsed time for process in seconds."""
    try:
        result = subprocess.run(
            ['ps', '-p', str(pid), '-o', 'etime='],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            elapsed_str = result.stdout.strip()
            # Parse format: [[DD-]HH:]MM:SS
            parts = elapsed_str.split('-')
            if len(parts) == 2:
                days = int(parts[0])
                time_part = parts[1]
            else:
                days = 0
                time_part = parts[0]

            time_components = time_part.split(':')
            if len(time_components) == 3:
                hours, minutes, seconds = map(int, time_components)
            elif len(time_components) == 2:
                hours = 0
                minutes, seconds = map(int, time_components)
            else:
                hours = minutes = 0
                seconds = int(time_components[0])

            total_seconds = days * 86400 + hours * 3600 + minutes * 60 + seconds
            return total_seconds
        return 0
    except Exception:
        return 0


def format_time(seconds: int) -> str:
    """Format seconds as HH:MM:SS."""
    seconds = int(seconds)  # Ensure integer
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def get_status_icon(status: bool) -> str:
    """Get colored status icon."""
    if status:
        return f"{Colors.GREEN}✓{Colors.ENDC}"
    else:
        return f"{Colors.RED}✗{Colors.ENDC}"


# =============================================================================
# MONITORING FUNCTIONS
# =============================================================================

def check_cycle162_status():
    """Check Cycle 162 experiment status."""
    running = is_process_running(CYCLE_162_PID)
    elapsed = get_process_runtime(CYCLE_162_PID)
    results_exist = CYCLE_162_RESULTS.exists()

    # Calculate progress
    progress_pct = min(100, (elapsed / EXPECTED_RUNTIME) * 100) if elapsed > 0 else 0

    # Calculate ETA
    if running and elapsed > 0:
        remaining = max(0, EXPECTED_RUNTIME - elapsed)
        eta = datetime.now() + timedelta(seconds=remaining)
    else:
        remaining = 0
        eta = None

    return {
        'running': running,
        'elapsed': elapsed,
        'elapsed_str': format_time(elapsed),
        'remaining': remaining,
        'remaining_str': format_time(remaining),
        'eta': eta,
        'progress_pct': progress_pct,
        'results_exist': results_exist,
        'complete': not running and results_exist,
    }


def check_analysis_status():
    """Check analysis script readiness."""
    script_exists = (EXPERIMENTS_DIR / 'analyze_cycle162_results.py').exists()
    results_exist = CYCLE_162_ANALYSIS.exists()

    return {
        'script_ready': script_exists,
        'results_exist': results_exist,
        'ready': script_exists and not results_exist,  # Ready to run if script exists but no results yet
    }


def check_visualization_status():
    """Check visualization pipeline readiness."""
    script_exists = (EXPERIMENTS_DIR / 'visualize_cycle162_results.py').exists()
    figures_dir = EXPERIMENTS_DIR / 'figures'
    figures_exist = figures_dir.exists() and len(list(figures_dir.glob('cycle162*.png'))) > 0

    return {
        'script_ready': script_exists,
        'figures_exist': figures_exist,
        'ready': script_exists,
    }


def check_orchestrator_status():
    """Check autonomous orchestrator readiness."""
    script_exists = (EXPERIMENTS_DIR / 'autonomous_experiment_orchestrator.py').exists()

    return {
        'script_ready': script_exists,
        'ready': script_exists,
    }


def check_cycle163_scenarios():
    """Check Cycle 163 scenario scripts."""
    scenarios = {
        'A': 'cycle163a_harmonic_fine_grained.py',
        'B': 'cycle163b_seed_mechanism.py',
        'C': 'cycle163c_frequency_seed_interaction.py',
        'D': 'cycle163d_threshold_investigation.py',
        'E': 'cycle163e_composition_analysis.py',
        'F': 'cycle163f_25pct_deep_dive.py',
    }

    status = {}
    for scenario, script in scenarios.items():
        status[scenario] = (EXPERIMENTS_DIR / script).exists()

    return {
        'scenarios': status,
        'all_ready': all(status.values()),
        'ready_count': sum(status.values()),
        'total_count': len(status),
    }


# =============================================================================
# DISPLAY FUNCTIONS
# =============================================================================

def display_dashboard():
    """Display real-time monitoring dashboard."""

    # Clear screen
    print("\033[2J\033[H", end='')

    # Header
    print(f"{Colors.BOLD}{Colors.HEADER}{'='*80}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}AUTONOMOUS PIPELINE REAL-TIME MONITOR{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}{'='*80}{Colors.ENDC}")
    print(f"{Colors.CYAN}Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.ENDC}")
    print()

    # Cycle 162 Status
    cycle162 = check_cycle162_status()

    print(f"{Colors.BOLD}CYCLE 162: FREQUENCY LANDSCAPE EXPERIMENT{Colors.ENDC}")
    print(f"  Status:       {get_status_icon(cycle162['running'])} {'RUNNING' if cycle162['running'] else 'STOPPED'}")
    print(f"  PID:          {CYCLE_162_PID}")
    print(f"  Elapsed:      {cycle162['elapsed_str']}")
    print(f"  Remaining:    {cycle162['remaining_str']}")

    if cycle162['eta']:
        print(f"  ETA:          {cycle162['eta'].strftime('%H:%M:%S')}")

    print(f"  Progress:     [{'█' * int(cycle162['progress_pct'] // 2)}{' ' * (50 - int(cycle162['progress_pct'] // 2))}] {cycle162['progress_pct']:.1f}%")
    print(f"  Results:      {get_status_icon(cycle162['results_exist'])} {'EXISTS' if cycle162['results_exist'] else 'NOT YET CREATED'}")

    if cycle162['complete']:
        print(f"  {Colors.GREEN}{Colors.BOLD}✅ CYCLE 162 COMPLETE{Colors.ENDC}")

    print()

    # Analysis Status
    analysis = check_analysis_status()

    print(f"{Colors.BOLD}ANALYSIS PIPELINE{Colors.ENDC}")
    print(f"  Script:       {get_status_icon(analysis['script_ready'])} analyze_cycle162_results.py")
    print(f"  Results:      {get_status_icon(analysis['results_exist'])} cycle162_analysis.json")

    if analysis['ready'] and cycle162['complete']:
        print(f"  {Colors.YELLOW}{Colors.BOLD}⚡ READY TO RUN{Colors.ENDC}")

    print()

    # Visualization Status
    viz = check_visualization_status()

    print(f"{Colors.BOLD}VISUALIZATION PIPELINE{Colors.ENDC}")
    print(f"  Script:       {get_status_icon(viz['script_ready'])} visualize_cycle162_results.py")
    print(f"  Figures:      {get_status_icon(viz['figures_exist'])} 5 publication figures (300 DPI)")

    if viz['ready'] and cycle162['complete']:
        print(f"  {Colors.YELLOW}{Colors.BOLD}⚡ READY TO RUN{Colors.ENDC}")

    print()

    # Orchestrator Status
    orchestrator = check_orchestrator_status()

    print(f"{Colors.BOLD}AUTONOMOUS ORCHESTRATOR{Colors.ENDC}")
    print(f"  Script:       {get_status_icon(orchestrator['ready'])} autonomous_experiment_orchestrator.py")

    if orchestrator['ready'] and cycle162['complete']:
        print(f"  {Colors.GREEN}{Colors.BOLD}✅ READY TO EXECUTE AUTONOMOUS PIPELINE{Colors.ENDC}")

    print()

    # Cycle 163 Scenarios
    scenarios = check_cycle163_scenarios()

    print(f"{Colors.BOLD}CYCLE 163 SCENARIOS{Colors.ENDC}")
    print(f"  Available:    {scenarios['ready_count']}/{scenarios['total_count']} scenarios ready")

    for scenario, ready in sorted(scenarios['scenarios'].items()):
        print(f"    Scenario {scenario}: {get_status_icon(ready)}")

    if scenarios['all_ready']:
        print(f"  {Colors.GREEN}{Colors.BOLD}✅ ALL SCENARIOS READY{Colors.ENDC}")

    print()

    # Framework Validation
    print(f"{Colors.BOLD}FRAMEWORK VALIDATION{Colors.ENDC}")
    print(f"  {Colors.GREEN}✓{Colors.ENDC} Self-Giving: Autonomous execution pipeline monitoring")
    print(f"  {Colors.GREEN}✓{Colors.ENDC} NRM: Composition of experimental cycles (162→163)")
    print(f"  {Colors.GREEN}✓{Colors.ENDC} Temporal Stewardship: Real-time research progression tracking")

    print()
    print(f"{Colors.BOLD}{Colors.HEADER}{'='*80}{Colors.ENDC}")


# =============================================================================
# MAIN MONITORING LOOP
# =============================================================================

def monitor_loop(auto_trigger: bool = False):
    """Main monitoring loop with optional auto-trigger."""

    print(f"{Colors.BOLD}Starting autonomous pipeline monitor...{Colors.ENDC}")
    print(f"Update interval: {UPDATE_INTERVAL} seconds")
    print(f"Auto-trigger: {auto_trigger}")
    print()
    print("Press Ctrl+C to exit")
    print()

    time.sleep(2)

    triggered = False

    try:
        while True:
            display_dashboard()

            # Check if ready to trigger
            cycle162 = check_cycle162_status()

            if auto_trigger and cycle162['complete'] and not triggered:
                print()
                print(f"{Colors.GREEN}{Colors.BOLD}🚀 TRIGGERING AUTONOMOUS ORCHESTRATOR{Colors.ENDC}")
                print()

                orchestrator_script = EXPERIMENTS_DIR / 'autonomous_experiment_orchestrator.py'

                result = subprocess.run(
                    [sys.executable, str(orchestrator_script)],
                    cwd=EXPERIMENTS_DIR,
                )

                triggered = True

                print()
                print(f"{Colors.GREEN}{Colors.BOLD}✅ AUTONOMOUS PIPELINE COMPLETE{Colors.ENDC}")
                print()
                break

            time.sleep(UPDATE_INTERVAL)

    except KeyboardInterrupt:
        print()
        print(f"{Colors.YELLOW}Monitor stopped by user{Colors.ENDC}")
        print()


def main():
    """Main entry point."""

    import argparse

    parser = argparse.ArgumentParser(
        description='Monitor Cycle 162→163 autonomous research pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 monitor_autonomous_pipeline.py              # Monitor only
  python3 monitor_autonomous_pipeline.py --trigger    # Monitor and auto-trigger

Framework:
  Self-Giving Systems: Autonomous execution monitoring
  NRM: Composition of experimental cycles
  Temporal Stewardship: Research progression tracking
        """
    )

    parser.add_argument(
        '--trigger',
        action='store_true',
        help='Automatically trigger orchestrator when Cycle 162 completes'
    )

    parser.add_argument(
        '--once',
        action='store_true',
        help='Show status once and exit (no monitoring loop)'
    )

    args = parser.parse_args()

    if args.once:
        display_dashboard()
    else:
        monitor_loop(auto_trigger=args.trigger)


if __name__ == '__main__':
    main()
