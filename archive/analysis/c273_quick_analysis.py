#!/usr/bin/env python3
"""
Quick C273 Analysis - Extract population data from cycle_metrics

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Authored-By: Claude <noreply@anthropic.com>
"""

import sqlite3
import numpy as np
from pathlib import Path
from scipy import stats

# Configuration
RESULTS_DIR = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results")
FREQUENCIES = [0.0001, 0.0002, 0.0005, 0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.10]
SEEDS = list(range(42, 62))

print("=" * 80)
print("C273 VARIANCE POWER LAW ANALYSIS")
print("=" * 80)

results = {}

for freq in FREQUENCIES:
    freq_pct = f"{freq * 100:.2f}".replace('.', '_')
    populations = []

    for seed in SEEDS:
        db_path = RESULTS_DIR / f"c273_v6b_EXTENDED_VARIANCE_{freq_pct}pct_seed{seed}.db"

        if db_path.exists():
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT population FROM cycle_metrics ORDER BY cycle DESC LIMIT 1")
                row = cursor.fetchone()
                if row:
                    populations.append(row[0])
                conn.close()
            except Exception as e:
                pass

    if populations:
        mean_pop = np.mean(populations)
        var_pop = np.var(populations)
        results[freq] = {
            'mean': mean_pop,
            'variance': var_pop,
            'n': len(populations)
        }
        print(f"f={freq*100:.2f}%: mean={mean_pop:.1f}, var={var_pop:.1f}, n={len(populations)}")

# Power law fit
if len(results) >= 3:
    freqs = np.array(list(results.keys()))
    variances = np.array([results[f]['variance'] for f in freqs])

    # Filter out zero variances
    mask = variances > 0
    freqs_fit = freqs[mask]
    variances_fit = variances[mask]

    if len(freqs_fit) >= 3:
        # Log-log linear regression
        log_f = np.log10(freqs_fit)
        log_v = np.log10(variances_fit)

        slope, intercept, r_value, p_value, std_err = stats.linregress(log_f, log_v)
        gamma = -slope  # gamma = -slope in log-log

        print("\n" + "=" * 80)
        print("POWER LAW FIT: σ²(f) ∝ f^-γ")
        print("=" * 80)
        print(f"Fitted γ = {gamma:.3f}")
        print(f"Theoretical γ = 3.19")
        print(f"R² = {r_value**2:.3f}")
        print(f"p-value = {p_value:.6f}")

        error = abs(gamma - 3.19) / 3.19 * 100
        print(f"\nError from theory: {error:.1f}%")

        if error < 10:
            print("✅ VALIDATED: γ within 10% of prediction")
        elif error < 20:
            print("⚠ PARTIAL: γ within 20% of prediction")
        else:
            print("❌ NOT VALIDATED: γ differs by >20%")
    else:
        print("\nNot enough non-zero variance points for fit")
else:
    print("\nNot enough frequency points for analysis")
