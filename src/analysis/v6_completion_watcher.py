#!/usr/bin/env python3
"""
V6 Completion Watcher and Automated Analysis Trigger

Purpose: Monitor V6 experiment completion and automatically execute analysis
         pipeline to achieve zero-delay between completion and results.

Workflow:
1. Monitor for V6 results file appearance
2. Validate completion (all 40 experiments present)
3. Execute analysis script
4. Generate figures @ 300 DPI
5. Document results
6. Update Paper 4 with V6 findings

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Authored-By: Claude <noreply@anthropic.com>
Date: 2025-11-09 (Cycle 1343)
License: GPL-3.0
"""

import json
import subprocess
import time
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

# Paths
V6_RESULTS_FILE = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c186_v6_ultra_low_frequency_test.json")
ANALYSIS_SCRIPT = Path("/Volumes/dual/DUALITY-ZERO-V2/code/analysis/analyze_c186_v6_results.py")
FIGURE_SCRIPT = Path("/Volumes/dual/DUALITY-ZERO-V2/code/analysis/generate_c186_v6_ultra_low_frequency_figure.py")
COMPLETION_LOG = Path("/Volumes/dual/DUALITY-ZERO-V2/archive/v6_completion_log.txt")

# Expected experiments
EXPECTED_FREQUENCIES = 4
EXPECTED_SEEDS_PER_FREQ = 10
EXPECTED_TOTAL_EXPERIMENTS = EXPECTED_FREQUENCIES * EXPECTED_SEEDS_PER_FREQ  # 40


def check_v6_completion() -> Optional[Dict[str, Any]]:
    """
    Check if V6 has completed.

    Returns:
        None if not complete
        Results dict if complete
    """
    if not V6_RESULTS_FILE.exists():
        return None

    try:
        with open(V6_RESULTS_FILE, 'r') as f:
            results = json.load(f)

        # Validate structure
        if "experiments" not in results:
            return None

        # Check all experiments present
        n_experiments = len(results["experiments"])

        # Each experiment should have SEEDS_PER_FREQ individual runs
        total_runs = sum(
            len(exp.get("individual_runs", []))
            for exp in results["experiments"]
        )

        if total_runs == EXPECTED_TOTAL_EXPERIMENTS:
            return results

        return None

    except (json.JSONDecodeError, KeyError):
        return None


def validate_results_quality(results: Dict[str, Any]) -> bool:
    """
    Validate V6 results quality.

    Checks:
    - All frequencies tested
    - All seeds completed
    - Statistics computed
    - No corruption
    """
    try:
        experiments = results["experiments"]

        # Check frequency coverage
        frequencies = sorted([exp["f_intra_pct"] for exp in experiments])
        expected_freqs = sorted([0.75, 0.50, 0.25, 0.10])

        if frequencies != expected_freqs:
            print(f"  ❌ Frequency mismatch: {frequencies} != {expected_freqs}")
            return False

        # Check each frequency has all seeds
        for exp in experiments:
            n_runs = len(exp.get("individual_runs", []))
            if n_runs != EXPECTED_SEEDS_PER_FREQ:
                f_pct = exp["f_intra_pct"]
                print(f"  ❌ Frequency {f_pct}% incomplete: {n_runs}/{EXPECTED_SEEDS_PER_FREQ} seeds")
                return False

            # Check aggregate statistics exist
            if "aggregate_statistics" not in exp:
                print(f"  ❌ Missing aggregate statistics for f={exp['f_intra_pct']}%")
                return False

        print(f"  ✅ All {len(experiments)} frequencies complete")
        print(f"  ✅ All {EXPECTED_TOTAL_EXPERIMENTS} experiments valid")
        return True

    except (KeyError, TypeError) as e:
        print(f"  ❌ Validation error: {e}")
        return False


def run_analysis_pipeline() -> bool:
    """
    Execute V6 analysis pipeline.

    Steps:
    1. Run statistical analysis
    2. Generate publication figures
    3. Save analysis results

    Returns:
        True if successful, False otherwise
    """
    print("\n" + "=" * 80)
    print("EXECUTING V6 ANALYSIS PIPELINE")
    print("=" * 80)

    # Step 1: Statistical analysis
    print("\n[1/2] Running statistical analysis...")
    try:
        result = subprocess.run(
            ["python3", str(ANALYSIS_SCRIPT)],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )

        if result.returncode != 0:
            print(f"  ❌ Analysis failed:")
            print(result.stderr)
            return False

        print("  ✅ Statistical analysis complete")

    except subprocess.TimeoutExpired:
        print("  ❌ Analysis timeout (>5 minutes)")
        return False
    except Exception as e:
        print(f"  ❌ Analysis error: {e}")
        return False

    # Step 2: Figure generation
    print("\n[2/2] Generating publication figures @ 300 DPI...")
    try:
        result = subprocess.run(
            ["python3", str(FIGURE_SCRIPT)],
            capture_output=True,
            text=True,
            timeout=120  # 2 minute timeout
        )

        if result.returncode != 0:
            print(f"  ❌ Figure generation failed:")
            print(result.stderr)
            return False

        print("  ✅ Figures generated")

    except subprocess.TimeoutExpired:
        print("  ❌ Figure generation timeout (>2 minutes)")
        return False
    except Exception as e:
        print(f"  ❌ Figure generation error: {e}")
        return False

    print("\n" + "=" * 80)
    print("V6 ANALYSIS PIPELINE COMPLETE")
    print("=" * 80)

    return True


def log_completion(results: Dict[str, Any]):
    """Log V6 completion for audit trail."""
    COMPLETION_LOG.parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Extract summary statistics
    summary_lines = [
        f"\nV6 Completion: {timestamp}",
        "=" * 80,
        f"Total experiments: {EXPECTED_TOTAL_EXPERIMENTS}",
        f"Frequencies tested: {EXPECTED_FREQUENCIES}",
        f"Seeds per frequency: {EXPECTED_SEEDS_PER_FREQ}",
        "\nResults by frequency:",
    ]

    for exp in results["experiments"]:
        f_pct = exp["f_intra_pct"]
        stats = exp["aggregate_statistics"]
        basin_a_pct = stats["basin_a_pct"]
        mean_pop = stats["mean_population_avg"]

        summary_lines.append(
            f"  f={f_pct:5.2f}%: Basin A {basin_a_pct:5.1f}%, "
            f"Mean pop {mean_pop:6.2f}"
        )

    summary_lines.append("=" * 80)
    summary_lines.append("")

    with open(COMPLETION_LOG, 'a') as f:
        f.write("\n".join(summary_lines))

    print(f"\n✅ Completion logged to: {COMPLETION_LOG}")


def watch_v6_completion(
    check_interval: int = 300,
    max_checks: Optional[int] = None,
    run_once: bool = False
) -> bool:
    """
    Monitor V6 experiment for completion.

    Args:
        check_interval: Seconds between checks (default: 300 = 5 minutes)
        max_checks: Maximum number of checks (None = unlimited)
        run_once: If True, check once and exit (for manual testing)

    Returns:
        True if V6 completed and analysis succeeded
        False otherwise
    """
    print("=" * 80)
    print("V6 COMPLETION WATCHER - ZERO-DELAY ANALYSIS")
    print("=" * 80)
    print(f"\nMonitoring: {V6_RESULTS_FILE}")
    print(f"Check interval: {check_interval}s ({check_interval/60:.1f} minutes)")

    if max_checks:
        print(f"Max checks: {max_checks}")

    if run_once:
        print("Mode: Single check (manual testing)")
    else:
        print("Mode: Continuous monitoring")

    print()

    check_count = 0

    while True:
        check_count += 1
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        print(f"[{timestamp}] Check #{check_count}: ", end="")

        # Check if V6 completed
        results = check_v6_completion()

        if results is None:
            if V6_RESULTS_FILE.exists():
                print("Incomplete (file exists but not all experiments done)")
            else:
                print("Not started (no results file)")
        else:
            print("COMPLETE! Validating...")

            # Validate results quality
            if not validate_results_quality(results):
                print("\n❌ V6 results validation FAILED")
                return False

            # Log completion
            log_completion(results)

            # Execute analysis pipeline
            analysis_success = run_analysis_pipeline()

            if analysis_success:
                print("\n" + "=" * 80)
                print("✅ V6 COMPLETE - ZERO-DELAY ANALYSIS SUCCESSFUL")
                print("=" * 80)
                print("\nNext steps:")
                print("1. Review analysis results")
                print("2. Integrate V6 findings into Paper 4")
                print("3. Update Paper 4 completion percentage")
                print("4. Sync to GitHub")
                return True
            else:
                print("\n❌ V6 analysis pipeline FAILED")
                return False

        # Exit conditions
        if run_once:
            print("\nSingle check complete (run_once=True)")
            return False

        if max_checks and check_count >= max_checks:
            print(f"\nMax checks ({max_checks}) reached")
            return False

        # Wait before next check
        time.sleep(check_interval)


def main():
    """Main entry point."""
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == "--check-once":
            # Single check for manual testing
            watch_v6_completion(run_once=True)
        elif sys.argv[1] == "--help":
            print(__doc__)
        else:
            print(f"Unknown argument: {sys.argv[1]}")
            print("Usage:")
            print("  python3 v6_completion_watcher.py            # Continuous monitoring")
            print("  python3 v6_completion_watcher.py --check-once  # Single check")
            print("  python3 v6_completion_watcher.py --help        # Show help")
    else:
        # Default: continuous monitoring with 5-minute checks
        watch_v6_completion(check_interval=300)


if __name__ == "__main__":
    main()
