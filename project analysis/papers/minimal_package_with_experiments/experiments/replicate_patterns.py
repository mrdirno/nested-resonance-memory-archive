#!/usr/bin/env python3
"""
Replicability demonstration for pattern detection.

This script simulates detection of temporal or retention patterns across
multiple runs.  Each run yields a similarity score between 0 and 1.  A
run is counted as a positive detection when its similarity exceeds a
user-specified threshold.  A set of runs (healthy or degraded) is
declared replicable when at least 80% of runs exceed the threshold.

Two modes are provided:

    healthy  -- similarity scores are drawn from a Gaussian distribution
                centred near 0.995, representing stable systems.
    degraded -- similarity scores are drawn from a Gaussian distribution
                centred near 0.96, representing systems with degraded
                memory or temporal stability.

Usage
-----
    python replicate_patterns.py --runs 20 --threshold 0.99 --mode healthy

Parameters
----------
    --runs : int, optional
        Number of runs to simulate (default: 20).
    --threshold : float, optional
        Similarity threshold for counting a run as a positive detection (default: 0.99).
    --mode : str, optional
        "healthy" or "degraded" (default: "healthy").  In degraded mode the
        mean similarity is lower.

Outputs
-------
    Prints the pass rate (fraction of runs exceeding the threshold) and
    whether the replicability criterion (≥80% runs) is satisfied.
"""

import argparse
import random


def simulate_run(threshold: float, mode: str) -> bool:
    """Simulate a single run and return True if it exceeds the threshold."""
    if mode == "healthy":
        mean = 0.995
    else:
        mean = 0.96
    similarity = random.gauss(mean, 0.01)
    return similarity >= threshold


def run_simulation(runs: int, threshold: float, mode: str) -> float:
    passes = 0
    for _ in range(runs):
        if simulate_run(threshold, mode):
            passes += 1
    return passes / runs


def main():
    parser = argparse.ArgumentParser(description="Replicability demonstration for pattern detection")
    parser.add_argument("--runs", type=int, default=20, help="Number of runs to simulate (default: 20)")
    parser.add_argument("--threshold", type=float, default=0.99, help="Similarity threshold (default: 0.99)")
    parser.add_argument("--mode", type=str, default="healthy", choices=["healthy", "degraded"], help="Mode: healthy or degraded")
    args = parser.parse_args()
    pass_rate = run_simulation(args.runs, args.threshold, args.mode)
    criterion_met = pass_rate >= 0.8
    print(f"Mode: {args.mode}")
    print(f"Runs: {args.runs}")
    print(f"Threshold: {args.threshold:.3f}")
    print(f"Pass rate = {pass_rate:.3f}")
    print(f"Replicability criterion met (≥80%)? {'YES' if criterion_met else 'NO'}")


if __name__ == "__main__":
    main()