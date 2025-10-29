#!/usr/bin/env python3
"""
Demonstration script for the overhead validation rule.

This script synthesises predicted and observed overhead values based on an
instrumented call count, an average per-call latency (in milliseconds),
and a pure-simulation baseline.  It simulates measurement noise and
computes the relative error between the predicted and observed overhead
for a number of trials.  A run is considered "authentic" when the
relative error does not exceed the tolerance (default: 5%).

Usage
-----
    python overhead_check.py --N 1080000 --C_ms 67 --T_sim_min 30 \
        --noise 0.02 --trials 50

Parameters
----------
    --N : int or float
        Instrumented call count.
    --C_ms : float
        Average per-call latency in milliseconds.
    --T_sim_min : float
        Duration of the simulation baseline in minutes.
    --tol : float, optional
        Relative error tolerance (default: 0.05 for ±5%).
    --noise : float, optional
        Standard deviation of Gaussian noise applied multiplicatively to
        the predicted overhead (default: 0.02 for 2% noise).
    --trials : int, optional
        Number of trials to simulate (default: 30).

Outputs
-------
    Prints the predicted overhead, median relative error, 90th percentile
    relative error, and the pass rate under the specified tolerance.
"""

import argparse
import random
import statistics


def simulate_overhead(N: float, C_ms: float, T_sim_min: float, noise: float) -> float:
    """Generate a noisy observed overhead for a single trial."""
    # Compute predicted overhead (dimensionless) from inputs
    predicted = (N * (C_ms / 1000.0 / 60.0)) / T_sim_min
    # Apply multiplicative noise to simulate measurement variability
    factor = random.gauss(1.0, noise)
    observed = predicted * factor
    return predicted, observed


def run_trials(N: float, C_ms: float, T_sim_min: float, tol: float, noise: float, trials: int):
    relative_errors = []
    predicted_ref = None
    passes = 0
    for _ in range(trials):
        predicted, observed = simulate_overhead(N, C_ms, T_sim_min, noise)
        if predicted_ref is None:
            predicted_ref = predicted
        rel_err = abs(observed - predicted) / predicted
        relative_errors.append(rel_err)
        if rel_err <= tol:
            passes += 1
    median_err = statistics.median(relative_errors)
    p90_err = sorted(relative_errors)[int(0.9 * len(relative_errors))]
    pass_rate = passes / trials
    return predicted_ref, median_err, p90_err, pass_rate


def main():
    parser = argparse.ArgumentParser(description="Overhead validation rule demonstration")
    parser.add_argument("--N", type=float, required=True, help="Instrumented call count")
    parser.add_argument("--C_ms", type=float, required=True, help="Average per-call latency in ms")
    parser.add_argument("--T_sim_min", type=float, required=True, help="Simulation baseline duration in minutes")
    parser.add_argument("--tol", type=float, default=0.05, help="Relative error tolerance (default: 0.05)")
    parser.add_argument("--noise", type=float, default=0.02, help="Std dev of multiplicative noise (default: 0.02)")
    parser.add_argument("--trials", type=int, default=30, help="Number of trials (default: 30)")
    parser.add_argument("--seed", type=int, default=None, help="Random seed for reproducibility (default: None)")
    args = parser.parse_args()

    # Set deterministic seed if provided
    if args.seed is not None:
        random.seed(args.seed)
    predicted, median_err, p90_err, pass_rate = run_trials(
        args.N, args.C_ms, args.T_sim_min, args.tol, args.noise, args.trials
    )
    print(f"Predicted overhead (O_pred) = {predicted:.6f}")
    print(f"Median relative error = {median_err*100:.2f}%")
    print(f"90th percentile relative error = {p90_err*100:.2f}%")
    print(f"Pass rate (relative error ≤ {args.tol*100:.1f}%) = {pass_rate:.3f}")


if __name__ == "__main__":
    main()